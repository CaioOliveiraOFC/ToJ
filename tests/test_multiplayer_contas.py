"""Autenticação do multiplayer: senha, token e contas (Fase 4, §3).

- A senha é guardada como scrypt com sal; o arquivo não tem a senha.
- O token é assinado (HMAC-SHA256) e expira; alterado, de outra chave, vencido ou
  malformado é recusado, com o motivo.
- O cliente não escolhe a conta: ela sai do token, no servidor.
- Nada que carrega segredo mostra o segredo no `repr`.
"""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multiplayer import contas as c  # noqa: E402

CHAVE = bytes(range(32))


class Relogio:
    def __init__(self, agora: float = 1_000_000.0) -> None:
        self.agora = agora

    def __call__(self) -> float:
        return self.agora


def _contas(relogio=None, validade=3600) -> c.ContasLocais:
    tokens = c.TokensAssinados(CHAVE, validade, relogio or Relogio())
    contas = c.ContasLocais(None, tokens)
    contas.criar("ana", "uma-senha-longa")
    return contas


# --- senha ---------------------------------------------------------------------


def test_senha_confere_e_o_hash_nao_contem_a_senha():
    guardado = c.hash_de_senha("uma-senha-longa")
    assert guardado.startswith("scrypt$")
    assert "uma-senha-longa" not in guardado
    assert c.senha_confere("uma-senha-longa", guardado)
    assert not c.senha_confere("outra-senha", guardado)
    assert not c.senha_confere("uma-senha-longa", "lixo")
    # Sal por conta: a mesma senha dá hashes diferentes.
    assert c.hash_de_senha("uma-senha-longa") != guardado


def test_login_certo_e_errado_e_usuario_inexistente_dao_a_mesma_recusa():
    contas = _contas()
    credencial = contas.entrar("ana", "uma-senha-longa")
    assert credencial.conta.usuario == "ana"
    with pytest.raises(c.CredenciaisInvalidasError) as errado:
        contas.entrar("ana", "senha-errada")
    with pytest.raises(c.CredenciaisInvalidasError) as inexistente:
        contas.entrar("ninguem", "uma-senha-longa")
    assert str(errado.value) == str(inexistente.value)


@pytest.mark.parametrize(
    "usuario, senha",
    [("an", "uma-senha-longa"), ("Ana Maria", "uma-senha-longa"), ("bia", "curta")],
)
def test_politica_de_conta(usuario, senha):
    with pytest.raises(c.ContaInvalidaError):
        _contas().criar(usuario, senha)


def test_usuario_repetido_e_recusado():
    with pytest.raises(c.ContaInvalidaError, match="já existe"):
        _contas().criar("ANA", "outra-senha-longa")


# --- token ---------------------------------------------------------------------


def test_token_valido_identifica_a_conta_e_a_expiracao():
    relogio = Relogio()
    contas = _contas(relogio, validade=600)
    credencial = contas.entrar("ana", "uma-senha-longa")
    conta, expira = contas.validar(credencial.token)
    assert conta == credencial.conta
    assert expira == int(relogio.agora) + 600 == credencial.expira_em


def test_token_expirado_e_recusado():
    relogio = Relogio()
    contas = _contas(relogio, validade=600)
    token = contas.entrar("ana", "uma-senha-longa").token
    relogio.agora += 599
    contas.validar(token)
    relogio.agora += 1
    with pytest.raises(c.TokenInvalidoError) as erro:
        contas.validar(token)
    assert erro.value.motivo == "expirado"


def _troca(texto: str, posicao: int) -> str:
    novo = "A" if texto[posicao] != "A" else "B"
    return texto[:posicao] + novo + texto[posicao + 1 :]


@pytest.mark.parametrize("parte", ["conteudo", "assinatura"])
def test_token_adulterado_e_recusado(parte):
    contas = _contas()
    token = contas.entrar("ana", "uma-senha-longa").token
    versao, corpo, assinatura = token.split(".")
    if parte == "conteudo":
        adulterado = f"{versao}.{_troca(corpo, 5)}.{assinatura}"
    else:
        adulterado = f"{versao}.{corpo}.{_troca(assinatura, 3)}"
    with pytest.raises(c.TokenInvalidoError) as erro:
        contas.validar(adulterado)
    assert erro.value.motivo == "adulterado"


def test_token_forjado_para_outra_conta_e_recusado():
    """Trocar a conta no conteúdo exige a chave: sem ela, a assinatura não bate."""
    contas = _contas()
    bia = contas.criar("bia", "senha-da-bia-longa")
    token = contas.entrar("ana", "uma-senha-longa").token
    versao, corpo, assinatura = token.split(".")
    conteudo = json.loads(c._de_b64(corpo))
    conteudo["sub"] = bia.id
    forjado = f"{versao}.{c._b64(json.dumps(conteudo).encode())}.{assinatura}"
    with pytest.raises(c.TokenInvalidoError) as erro:
        contas.validar(forjado)
    assert erro.value.motivo == "adulterado"


def test_token_de_outra_chave_e_recusado():
    contas = _contas()
    outra = c.TokensAssinados(bytes(reversed(range(32))))
    token, _ = outra.emitir(contas.conta_do_usuario("ana").id)
    with pytest.raises(c.TokenInvalidoError) as erro:
        contas.validar(token)
    assert erro.value.motivo == "adulterado"


@pytest.mark.parametrize(
    "token", ["", "v1", "v1.a", "v2.a.b", "v1.a.b.c", 123, None, "v1." + "x" * 3000, "v1.é.b"]
)
def test_token_malformado_e_recusado(token):
    with pytest.raises(c.TokenInvalidoError) as erro:
        _contas().validar(token)
    assert erro.value.motivo == "malformado"


def test_token_de_conta_removida_e_recusado():
    contas = _contas()
    token = contas.entrar("ana", "uma-senha-longa").token
    contas._contas.clear()
    with pytest.raises(c.TokenInvalidoError) as erro:
        contas.validar(token)
    assert erro.value.motivo == "conta_desconhecida"


def test_chave_curta_e_recusada():
    with pytest.raises(ValueError):
        c.TokensAssinados(b"curta")


# --- persistência e segredo -----------------------------------------------------------


def test_contas_persistem_sem_senha_e_com_permissao_restrita(tmp_path, monkeypatch):
    monkeypatch.delenv(c.VARIAVEL_DA_CHAVE, raising=False)
    contas = c.ContasLocais.na_pasta(tmp_path)
    conta = contas.criar("ana", "uma-senha-longa")
    token = contas.entrar("ana", "uma-senha-longa").token

    texto = (tmp_path / c.ARQUIVO_DE_CONTAS).read_text()
    assert "uma-senha-longa" not in texto
    for arquivo in (c.ARQUIVO_DE_CONTAS, c.ARQUIVO_DA_CHAVE):
        modo = stat.S_IMODE(os.stat(tmp_path / arquivo).st_mode)
        assert modo == 0o600, (arquivo, oct(modo))

    # Reabrir a pasta reconhece a conta e o token emitido antes.
    reaberta = c.ContasLocais.na_pasta(tmp_path)
    assert reaberta.validar(token)[0] == conta
    assert reaberta.entrar("ana", "uma-senha-longa").conta == conta


def test_nada_que_carrega_segredo_mostra_o_segredo():
    contas = _contas()
    credencial = contas.entrar("ana", "uma-senha-longa")
    for objeto in (credencial, contas, contas._tokens):
        assert credencial.token not in repr(objeto)
        assert "uma-senha-longa" not in repr(objeto)
        assert CHAVE.hex() not in repr(objeto)
