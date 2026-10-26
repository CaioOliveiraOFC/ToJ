"""Contas e autenticação do multiplayer: quem é o jogador, segundo o servidor.

Independente do motor PvP: o duelo não sabe que existem contas. O servidor
autoritativo pergunta a um `Autenticador` quem é o dono de um token, e é essa
resposta — nunca um nome que o cliente declara — que vira a identidade da sessão.

`ContasLocais` é a implementação mínima e segura para desenvolvimento:

- **senha**: scrypt com sal aleatório por conta; o arquivo guarda só o hash. A
  comparação é em tempo constante, e usuário inexistente custa o mesmo scrypt que
  senha errada (não dá para descobrir quem existe pelo tempo de resposta);
- **token**: `v1.<conteúdo>.<assinatura>`, com HMAC-SHA256 sobre o conteúdo. A
  assinatura é conferida ANTES de qualquer leitura do conteúdo; o conteúdo leva a
  conta, a emissão e a expiração. Token alterado, de outra chave ou vencido é
  recusado;
- **chave**: 32 bytes aleatórios num arquivo com permissão 0600 na pasta de dados
  do servidor (ou a variável `TOJ_CHAVE_DOS_TOKENS`). Trocar a chave invalida
  todos os tokens;
- **conta**: criada só pelo administrador do servidor (`tools/toj_multiplayer.py
  conta criar`), nunca por mensagem de rede.

Nada aqui registra senha ou token em log, e os objetos que carregam token não o
mostram no `repr`. Um provedor externo entra implementando `Autenticador`.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

VERSAO_DO_TOKEN = "v1"
VALIDADE_PADRAO = 8 * 3600  # segundos
TAMANHO_MAXIMO_DO_TOKEN = 2048
SENHA_MINIMA = 10
USUARIO_VALIDO = re.compile(r"^[a-z0-9_]{3,24}$")

# scrypt: 16 MiB de memória e algumas dezenas de milissegundos por tentativa.
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}
_TAMANHO_DO_HASH = 32
_MEMORIA_DO_SCRYPT = 64 * 1024 * 1024

ARQUIVO_DE_CONTAS = "contas.json"
ARQUIVO_DA_CHAVE = "chave_dos_tokens"
VARIAVEL_DA_CHAVE = "TOJ_CHAVE_DOS_TOKENS"


class CredenciaisInvalidasError(ValueError):
    """Usuário ou senha não conferem. A mensagem não diz qual dos dois."""


class TokenInvalidoError(ValueError):
    """O token não identifica ninguém: malformado, adulterado, expirado ou órfão."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(f"Token inválido: {motivo}.")


class ContaInvalidaError(ValueError):
    """Usuário ou senha fora da política, ou usuário já existente."""


@dataclass(frozen=True)
class Conta:
    """A identidade de um jogador. `id` é do servidor; `usuario` é o nome público."""

    id: str
    usuario: str


@dataclass(frozen=True)
class Credencial:
    """O que o login devolve. O token não aparece no `repr`."""

    conta: Conta
    token: str = field(repr=False)
    expira_em: int = 0


class Autenticador(Protocol):
    """A interface que o servidor usa. Outro provedor entra implementando isto."""

    def entrar(self, usuario: str, senha: str) -> Credencial: ...

    def validar(self, token: str) -> tuple[Conta, int]:
        """A conta dona do token e o instante (epoch) em que ele expira."""
        ...


# --- senha ---------------------------------------------------------------------


def hash_de_senha(senha: str, sal: bytes | None = None) -> str:
    sal = sal if sal is not None else secrets.token_bytes(16)
    derivada = hashlib.scrypt(
        senha.encode("utf-8"),
        salt=sal,
        dklen=_TAMANHO_DO_HASH,
        maxmem=_MEMORIA_DO_SCRYPT,
        **_SCRYPT,
    )
    return f"scrypt${_SCRYPT['n']}${_SCRYPT['r']}${_SCRYPT['p']}${sal.hex()}${derivada.hex()}"


def senha_confere(senha: str, guardado: str) -> bool:
    try:
        nome, n, r, p, sal, esperado = guardado.split("$")
        if nome != "scrypt":
            return False
        derivada = hashlib.scrypt(
            senha.encode("utf-8"),
            salt=bytes.fromhex(sal),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(bytes.fromhex(esperado)),
            maxmem=_MEMORIA_DO_SCRYPT,
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(derivada.hex(), esperado)


# Para gastar o mesmo scrypt quando o usuário não existe.
_HASH_DE_ENGANO = hash_de_senha(secrets.token_hex(16))


# --- token ---------------------------------------------------------------------


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def _de_b64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


class TokensAssinados:
    """Tokens com assinatura HMAC-SHA256 e expiração."""

    def __init__(
        self,
        chave: bytes,
        validade: int = VALIDADE_PADRAO,
        relogio: Callable[[], float] = time.time,
    ) -> None:
        if len(chave) < 32:
            raise ValueError("A chave dos tokens precisa de pelo menos 32 bytes.")
        self._chave = chave
        self._validade = int(validade)
        self._relogio = relogio

    def __repr__(self) -> str:
        return f"TokensAssinados(validade={self._validade})"

    def _assinatura(self, corpo: str) -> str:
        mensagem = f"{VERSAO_DO_TOKEN}.{corpo}".encode("ascii")
        return _b64(hmac.new(self._chave, mensagem, hashlib.sha256).digest())

    def emitir(self, conta_id: str) -> tuple[str, int]:
        agora = int(self._relogio())
        expira = agora + self._validade
        conteudo = {"sub": conta_id, "iat": agora, "exp": expira, "jti": secrets.token_hex(8)}
        corpo = _b64(json.dumps(conteudo, sort_keys=True, separators=(",", ":")).encode())
        return f"{VERSAO_DO_TOKEN}.{corpo}.{self._assinatura(corpo)}", expira

    def ler(self, token) -> tuple[str, int]:
        """A conta e a expiração. Levanta `TokenInvalidoError` com o motivo."""
        if not isinstance(token, str) or not token or len(token) > TAMANHO_MAXIMO_DO_TOKEN:
            raise TokenInvalidoError("malformado")
        if not token.isascii():
            raise TokenInvalidoError("malformado")
        partes = token.split(".")
        if len(partes) != 3 or partes[0] != VERSAO_DO_TOKEN:
            raise TokenInvalidoError("malformado")
        _, corpo, assinatura = partes
        if not hmac.compare_digest(self._assinatura(corpo), assinatura):
            raise TokenInvalidoError("adulterado")
        try:
            conteudo = json.loads(_de_b64(corpo))
        except (ValueError, UnicodeDecodeError) as erro:
            raise TokenInvalidoError("malformado") from erro
        if (
            not isinstance(conteudo, dict)
            or set(conteudo) != {"sub", "iat", "exp", "jti"}
            or not isinstance(conteudo["sub"], str)
            or type(conteudo["exp"]) is not int
            or type(conteudo["iat"]) is not int
        ):
            raise TokenInvalidoError("malformado")
        if self._relogio() >= conteudo["exp"]:
            raise TokenInvalidoError("expirado")
        return conteudo["sub"], conteudo["exp"]


# --- contas locais -----------------------------------------------------------------


def gravar_privado(caminho: Path, texto: str) -> None:
    """Escrita atômica, legível só pelo dono do processo (0600)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(f".{caminho.name}.{secrets.token_hex(4)}")
    descritor = os.open(temporario, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
    os.replace(temporario, caminho)


def chave_da_pasta(pasta: Path) -> bytes:
    """A chave dos tokens: da variável de ambiente, do arquivo, ou nova (0600)."""
    do_ambiente = os.environ.get(VARIAVEL_DA_CHAVE)
    if do_ambiente:
        return bytes.fromhex(do_ambiente)
    arquivo = pasta / ARQUIVO_DA_CHAVE
    if arquivo.exists():
        return bytes.fromhex(arquivo.read_text(encoding="ascii").strip())
    chave = secrets.token_bytes(32)
    gravar_privado(arquivo, chave.hex() + "\n")
    return chave


class ContasLocais:
    """Contas num arquivo JSON da pasta de dados do servidor (`None` = só em memória)."""

    def __init__(self, arquivo: Path | None, tokens: TokensAssinados) -> None:
        self._arquivo = arquivo
        self._tokens = tokens
        self._contas: dict[str, dict] = {}
        if arquivo is not None and arquivo.exists():
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            if dados.get("formato") != 1:
                raise ValueError(f"{arquivo.name}: formato desconhecido.")
            self._contas = dict(dados["contas"])

    @classmethod
    def na_pasta(cls, pasta: Path, *, validade: int = VALIDADE_PADRAO) -> ContasLocais:
        return cls(pasta / ARQUIVO_DE_CONTAS, TokensAssinados(chave_da_pasta(pasta), validade))

    def __repr__(self) -> str:
        return f"ContasLocais({len(self._contas)} contas)"

    def _gravar(self) -> None:
        if self._arquivo is not None:
            texto = json.dumps({"formato": 1, "contas": self._contas}, indent=2, sort_keys=True)
            gravar_privado(self._arquivo, texto + "\n")

    def criar(self, usuario: str, senha: str) -> Conta:
        """Cria a conta. Só o administrador chama isto; não há mensagem de rede para tal."""
        usuario = usuario.strip().lower()
        if not USUARIO_VALIDO.match(usuario):
            raise ContaInvalidaError("Usuário: 3 a 24 caracteres entre a-z, 0-9 e _.")
        if len(senha) < SENHA_MINIMA:
            raise ContaInvalidaError(f"A senha precisa de pelo menos {SENHA_MINIMA} caracteres.")
        if usuario in self._contas:
            raise ContaInvalidaError(f"O usuário {usuario!r} já existe.")
        conta = Conta(id=f"c_{secrets.token_hex(8)}", usuario=usuario)
        self._contas[usuario] = {"id": conta.id, "usuario": usuario, "senha": hash_de_senha(senha)}
        self._gravar()
        return conta

    def conta(self, conta_id: str) -> Conta | None:
        dados = next((c for c in self._contas.values() if c["id"] == conta_id), None)
        return None if dados is None else Conta(dados["id"], dados["usuario"])

    def conta_do_usuario(self, usuario: str) -> Conta | None:
        dados = self._contas.get(str(usuario).strip().lower())
        return None if dados is None else Conta(dados["id"], dados["usuario"])

    def entrar(self, usuario: str, senha: str) -> Credencial:
        dados = self._contas.get(str(usuario).strip().lower())
        guardado = dados["senha"] if dados else _HASH_DE_ENGANO
        confere = senha_confere(str(senha), guardado)
        if dados is None or not confere:
            raise CredenciaisInvalidasError("Usuário ou senha incorretos.")
        token, expira = self._tokens.emitir(dados["id"])
        return Credencial(Conta(dados["id"], dados["usuario"]), token, expira)

    def validar(self, token: str) -> tuple[Conta, int]:
        conta_id, expira = self._tokens.ler(token)
        conta = self.conta(conta_id)
        if conta is None:
            raise TokenInvalidoError("conta_desconhecida")
        return conta, expira
