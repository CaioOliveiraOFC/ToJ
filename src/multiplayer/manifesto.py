"""O manifesto de uma distribuição multiplayer: o que é "a mesma versão".

Cliente e servidor só jogam juntos quando são a MESMA versão, e "a mesma" aqui
não é um número parecido: é o mesmo conteúdo, byte a byte, de tudo o que decide
uma partida. O manifesto registra esse conteúdo:

- os quatro identificadores declarados em `versao.py` (jogo, protocolo, regras de
  combate e esquema do gladiador);
- o sha256 de cada arquivo do escopo do gameplay, agrupados (regras, catálogos,
  persistência, protocolo, servidor), o hash de cada grupo e o hash do conjunto.

O escopo é explícito (`ESCOPO`) e testado: todo módulo de `src/` que o servidor
carrega para jogar uma partida tem de estar nele (`tests/test_multiplayer_manifesto.py`).

Um manifesto publicado não muda. Mudar regra, catálogo ou formato depois de uma
publicação exige uma versão nova, e o gate de publicação
(`tools/multiplayer_manifesto.py verificar`) recusa:

- código que não bate com o manifesto da versão declarada;
- dois manifestos com o mesmo identificador de regras, protocolo ou esquema e
  conteúdo diferente nesse grupo;
- manifesto já publicado (com tag `v<versão>`) alterado ou apagado.

Este módulo é só a conta. Ler git e imprimir é da ferramenta.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from src.multiplayer import versao

FORMATO_DO_MANIFESTO = 1
RAIZ = Path(__file__).resolve().parents[2]
PASTA_DOS_MANIFESTOS = Path(__file__).resolve().parent / "manifestos"

# Os grupos do conteúdo medido. Um arquivo pertence ao grupo do padrão MAIS
# ESPECÍFICO que o alcança (o caminho exato vence a pasta).
ESCOPO: dict[str, tuple[str, ...]] = {
    # A matemática e o estado do combate: dano, efeitos, iniciativa, mana,
    # recargas e o próprio duelo.
    "regras": ("src/mechanics/", "src/shared/", "src/entities/"),
    # O que existe no jogo: cartas, passivas, itens, classes e os JSON.
    "catalogos": ("src/data/", "src/content/", "src/engine/game_logic.py"),
    # Do snapshot ao gladiador: o formato do save e o caminho de reconstrução.
    "persistencia": (
        "src/storage/",
        "src/engine/__init__.py",
        "src/engine/arena_setup.py",
        "src/multiplayer/gladiadores.py",
    ),
    # O formato das mensagens.
    "protocolo": ("src/multiplayer/protocolo.py",),
    # O resto da camada multiplayer: servidor, compatibilidade, manifesto.
    "servidor": ("src/multiplayer/", "src/__init__.py"),
}

# A declaração e os próprios manifestos não se medem: o manifesto não pode
# conter o hash de si mesmo.
FORA_DO_ESCOPO = ("src/multiplayer/versao.py", "src/multiplayer/manifestos/")

# O identificador declarado que responde pelo conteúdo de cada grupo. Mesmo
# identificador com conteúdo diferente é o que o gate proíbe. Catálogo e
# servidor não têm identificador próprio: respondem pela versão do jogo.
IDENTIFICADOR_DO_GRUPO = {
    "regras": "regras",
    "protocolo": "protocolo",
    "persistencia": "esquema_gladiador",
}

CAMPOS_DA_IDENTIDADE = ("jogo", "protocolo", "regras", "esquema_gladiador", "grupos", "conteudo")

# Texto é medido com fim de linha normalizado: o mesmo arquivo em checkout
# Windows e Linux é a mesma versão.
_SUFIXOS_DE_TEXTO = {".py", ".json", ".md", ".txt", ".csv", ".toml", ".yml", ".yaml"}


class IdentidadeInvalidaError(ValueError):
    """A identidade recebida não tem a forma de uma identidade de versão."""


class ManifestoInvalidoError(ValueError):
    """O arquivo de manifesto não tem a forma de um manifesto."""


class InstalacaoDivergenteError(RuntimeError):
    """O código desta instalação não é o que o manifesto da versão declarada mede."""

    def __init__(self, problemas: Iterable[str]) -> None:
        self.problemas = tuple(problemas)
        super().__init__("; ".join(self.problemas) or "instalação divergente")


def _sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def _json_canonico(dados) -> str:
    return json.dumps(dados, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# --- o escopo ----------------------------------------------------------------


def _casa(relativo: str, padrao: str) -> bool:
    """Padrão terminado em `/` é pasta (prefixo); o resto é caminho exato."""
    return relativo.startswith(padrao) if padrao.endswith("/") else relativo == padrao


def _fora(relativo: str) -> bool:
    return any(_casa(relativo, padrao) for padrao in FORA_DO_ESCOPO)


def grupo_de(relativo: str) -> str | None:
    """O grupo de um caminho relativo à raiz (posix), ou `None` se está fora."""
    if _fora(relativo):
        return None
    melhor: tuple[int, str] | None = None
    for grupo, padroes in ESCOPO.items():
        for padrao in padroes:
            if _casa(relativo, padrao) and (melhor is None or len(padrao) > melhor[0]):
                melhor = (len(padrao), grupo)
    return melhor[1] if melhor else None


def _arquivos_do_escopo(raiz: Path) -> list[str]:
    encontrados = []
    for caminho in sorted((raiz / "src").rglob("*")):
        if not caminho.is_file() or "__pycache__" in caminho.parts:
            continue
        if caminho.suffix in {".pyc", ".pyo"}:
            continue
        relativo = caminho.relative_to(raiz).as_posix()
        if grupo_de(relativo) is not None:
            encontrados.append(relativo)
    return encontrados


def hash_do_arquivo(caminho: Path) -> str:
    dados = caminho.read_bytes()
    if caminho.suffix in _SUFIXOS_DE_TEXTO:
        dados = dados.replace(b"\r\n", b"\n")
    return _sha256(dados)


def medir_arquivos(raiz: Path = RAIZ) -> dict[str, str]:
    """`caminho → sha256` de todo arquivo do escopo do gameplay."""
    return {rel: hash_do_arquivo(raiz / rel) for rel in _arquivos_do_escopo(raiz)}


def hashes_dos_grupos(arquivos: Mapping[str, str]) -> dict[str, str]:
    """O hash de cada grupo, sobre os caminhos e os hashes dos seus arquivos."""
    linhas: dict[str, list[str]] = {grupo: [] for grupo in ESCOPO}
    for relativo in sorted(arquivos):
        grupo = grupo_de(relativo)
        if grupo is None:
            raise ManifestoInvalidoError(f"{relativo} não pertence ao escopo do gameplay.")
        linhas[grupo].append(f"{relativo}\0{arquivos[relativo]}\n")
    return {grupo: _sha256("".join(itens).encode()) for grupo, itens in linhas.items()}


def hash_do_conteudo(grupos: Mapping[str, str]) -> str:
    return _sha256("".join(f"{g}\0{grupos[g]}\n" for g in sorted(grupos)).encode())


# --- identidade e manifesto ----------------------------------------------------


@dataclass(frozen=True)
class Identidade:
    """O que um lado afirma ser. Cliente e servidor só jogam se forem IGUAIS.

    Uma identidade declarada pelo cliente não prova nada sobre o cliente: quem
    adultera o código adultera a identidade junto. Ela serve para recusar, com
    uma mensagem útil, quem está honestamente na versão errada; a integridade
    competitiva vem do servidor, que executa o motor e decide tudo.
    """

    jogo: str
    protocolo: int
    regras: str
    esquema_gladiador: int
    grupos: tuple[tuple[str, str], ...]
    conteudo: str

    def como_dict(self) -> dict:
        return {
            "jogo": self.jogo,
            "protocolo": self.protocolo,
            "regras": self.regras,
            "esquema_gladiador": self.esquema_gladiador,
            "grupos": dict(self.grupos),
            "conteudo": self.conteudo,
        }

    @property
    def impressao(self) -> str:
        """sha256 da identidade inteira: a etiqueta que prende uma partida à versão."""
        return _sha256(_json_canonico(self.como_dict()).encode())

    @classmethod
    def de_dict(cls, dados) -> Identidade:
        """Lê uma identidade sem tolerância: campo a mais, a menos ou de tipo errado recusa."""
        if not isinstance(dados, dict):
            raise IdentidadeInvalidaError("A identidade precisa ser um objeto.")
        if set(dados) != set(CAMPOS_DA_IDENTIDADE):
            faltam = sorted(set(CAMPOS_DA_IDENTIDADE) - set(dados))
            sobram = sorted(set(dados) - set(CAMPOS_DA_IDENTIDADE))
            raise IdentidadeInvalidaError(
                f"Campos da identidade: faltam {faltam}, sobram {sobram}."
            )
        for campo in ("jogo", "regras", "conteudo"):
            if not isinstance(dados[campo], str) or not dados[campo]:
                raise IdentidadeInvalidaError(f"`{campo}` precisa ser texto não vazio.")
        for campo in ("protocolo", "esquema_gladiador"):
            if type(dados[campo]) is not int:
                raise IdentidadeInvalidaError(f"`{campo}` precisa ser inteiro.")
        grupos = dados["grupos"]
        if not isinstance(grupos, dict) or set(grupos) != set(ESCOPO):
            raise IdentidadeInvalidaError(f"`grupos` precisa ter exatamente {sorted(ESCOPO)}.")
        if not all(isinstance(v, str) and len(v) == 64 for v in grupos.values()):
            raise IdentidadeInvalidaError("Cada grupo precisa de um sha256.")
        return cls(
            jogo=dados["jogo"],
            protocolo=dados["protocolo"],
            regras=dados["regras"],
            esquema_gladiador=dados["esquema_gladiador"],
            grupos=tuple(sorted(grupos.items())),
            conteudo=dados["conteudo"],
        )


@dataclass(frozen=True)
class Manifesto:
    """A identidade de uma distribuição e o hash de cada arquivo medido."""

    identidade: Identidade
    arquivos: tuple[tuple[str, str], ...]

    @property
    def jogo(self) -> str:
        return self.identidade.jogo

    def como_dict(self) -> dict:
        return {
            "formato": FORMATO_DO_MANIFESTO,
            **self.identidade.como_dict(),
            "arquivos": dict(self.arquivos),
        }

    def texto(self) -> str:
        """O arquivo do manifesto. Determinístico: o mesmo conteúdo dá o mesmo texto."""
        return json.dumps(self.como_dict(), sort_keys=True, ensure_ascii=False, indent=2) + "\n"

    @classmethod
    def de_dict(cls, dados) -> Manifesto:
        if not isinstance(dados, dict) or dados.get("formato") != FORMATO_DO_MANIFESTO:
            raise ManifestoInvalidoError(
                f"Formato de manifesto desconhecido (esperado {FORMATO_DO_MANIFESTO})."
            )
        if set(dados) != {"formato", "arquivos", *CAMPOS_DA_IDENTIDADE}:
            raise ManifestoInvalidoError("O manifesto tem campos a mais ou a menos.")
        arquivos = dados["arquivos"]
        if not isinstance(arquivos, dict) or not arquivos:
            raise ManifestoInvalidoError("O manifesto não lista arquivos.")
        try:
            identidade = Identidade.de_dict({c: dados[c] for c in CAMPOS_DA_IDENTIDADE})
        except IdentidadeInvalidaError as erro:
            raise ManifestoInvalidoError(str(erro)) from erro
        manifesto = cls(identidade, tuple(sorted(arquivos.items())))
        problemas = conferir_consistencia_interna(manifesto)
        if problemas:
            raise ManifestoInvalidoError("; ".join(problemas))
        return manifesto


def construir(declarados: Mapping[str, object] | None = None, raiz: Path = RAIZ) -> Manifesto:
    """O manifesto do código em `raiz`, com os identificadores declarados."""
    declarados = dict(versao.declarados() if declarados is None else declarados)
    arquivos = medir_arquivos(raiz)
    grupos = hashes_dos_grupos(arquivos)
    identidade = Identidade(
        jogo=str(declarados["jogo"]),
        protocolo=int(declarados["protocolo"]),
        regras=str(declarados["regras"]),
        esquema_gladiador=int(declarados["esquema_gladiador"]),
        grupos=tuple(sorted(grupos.items())),
        conteudo=hash_do_conteudo(grupos),
    )
    return Manifesto(identidade, tuple(sorted(arquivos.items())))


def caminho_do_manifesto(jogo: str, pasta: Path = PASTA_DOS_MANIFESTOS) -> Path:
    return pasta / f"{jogo}.json"


def ler(texto: str) -> Manifesto:
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ManifestoInvalidoError(f"JSON ilegível: {erro}") from erro
    return Manifesto.de_dict(dados)


def carregar(jogo: str, pasta: Path = PASTA_DOS_MANIFESTOS) -> Manifesto:
    caminho = caminho_do_manifesto(jogo, pasta)
    if not caminho.is_file():
        raise ManifestoInvalidoError(
            f"Não existe manifesto para a versão {jogo!r} ({caminho.name})."
        )
    manifesto = ler(caminho.read_text(encoding="utf-8"))
    if manifesto.jogo != jogo:
        raise ManifestoInvalidoError(f"{caminho.name} declara a versão {manifesto.jogo!r}.")
    return manifesto


def todos(pasta: Path = PASTA_DOS_MANIFESTOS) -> dict[str, Manifesto]:
    """Todos os manifestos da pasta, pela versão do jogo."""
    return {caminho.stem: carregar(caminho.stem, pasta) for caminho in sorted(pasta.glob("*.json"))}


# --- as conferências do gate -----------------------------------------------------


def conferir_consistencia_interna(manifesto: Manifesto) -> list[str]:
    """Os hashes de grupo e de conteúdo batem com a lista de arquivos do próprio manifesto?"""
    try:
        grupos = hashes_dos_grupos(dict(manifesto.arquivos))
    except ManifestoInvalidoError as erro:
        return [str(erro)]
    problemas = []
    if dict(manifesto.identidade.grupos) != grupos:
        problemas.append("Os hashes de grupo não correspondem aos arquivos listados.")
    if manifesto.identidade.conteudo != hash_do_conteudo(grupos):
        problemas.append("O hash do conteúdo não corresponde aos grupos.")
    return problemas


def divergencias(manifesto: Manifesto, raiz: Path = RAIZ) -> list[str]:
    """O que no código em `raiz` não é o que o manifesto mede. Vazio = idêntico."""
    registrados = dict(manifesto.arquivos)
    atuais = medir_arquivos(raiz)
    problemas = []
    for relativo in sorted(set(registrados) | set(atuais)):
        if relativo not in atuais:
            problemas.append(f"{relativo}: está no manifesto e não existe no código.")
        elif relativo not in registrados:
            problemas.append(f"{relativo}: arquivo novo no escopo do gameplay, fora do manifesto.")
        elif registrados[relativo] != atuais[relativo]:
            problemas.append(f"{relativo}: mudou depois do manifesto.")
    return problemas


def conferir_declaracao(
    manifesto: Manifesto, declarados: Mapping[str, object] | None = None
) -> list[str]:
    """Os identificadores do manifesto são os que `versao.py` declara?"""
    declarados = versao.declarados() if declarados is None else declarados
    atuais = manifesto.identidade.como_dict()
    return [
        f"`{campo}`: versao.py declara {declarados[campo]!r}, "
        f"o manifesto registra {atuais[campo]!r}."
        for campo in declarados
        if atuais[campo] != declarados[campo]
    ]


def conferir_coerencia(manifestos: Iterable[Manifesto]) -> list[str]:
    """Um identificador nomeia exatamente um conteúdo, em todas as versões.

    Duas versões com o mesmo identificador de regras (ou protocolo, ou esquema)
    e conteúdo diferente nesse grupo seriam a mudança silenciosa que o contrato
    proíbe: quem compara só o identificador acharia que são as mesmas regras.
    """
    problemas = []
    lista = list(manifestos)
    vistas: dict[str, int] = {}
    for m in lista:
        vistas[m.jogo] = vistas.get(m.jogo, 0) + 1
    problemas += [f"A versão {j!r} aparece em {n} manifestos." for j, n in vistas.items() if n > 1]
    for grupo, campo in IDENTIFICADOR_DO_GRUPO.items():
        por_identificador: dict[object, dict[str, str]] = {}
        for m in lista:
            ident = m.identidade.como_dict()
            por_identificador.setdefault(ident[campo], {})[m.jogo] = ident["grupos"][grupo]
        for valor, versoes in por_identificador.items():
            if len(set(versoes.values())) > 1:
                problemas.append(
                    f"`{campo}` = {valor!r} nomeia conteúdos diferentes do grupo {grupo!r} "
                    f"nas versões {sorted(versoes)}: mude o identificador."
                )
    return problemas


def conferir_imutabilidade(publicados: Mapping[str, str], atuais: Mapping[str, str]) -> list[str]:
    """Todo manifesto publicado continua existindo, com o mesmo texto.

    `publicados`: versão → texto do manifesto no momento da publicação (a tag).
    `atuais`: versão → texto do manifesto hoje.
    """
    problemas = []
    for jogo, texto in sorted(publicados.items()):
        if jogo not in atuais:
            problemas.append(f"O manifesto publicado da versão {jogo!r} foi apagado.")
        elif atuais[jogo] != texto:
            problemas.append(f"O manifesto publicado da versão {jogo!r} foi alterado.")
    return problemas


def manifesto_da_instalacao(
    raiz: Path = RAIZ,
    pasta: Path = PASTA_DOS_MANIFESTOS,
    declarados: Mapping[str, object] | None = None,
) -> Manifesto:
    """O manifesto desta instalação, CONFERIDO contra o código que está rodando.

    É o único caminho de produção para a identidade de cliente ou servidor:
    código que não bate com o manifesto da versão que declara não entra em
    partida competitiva — bloqueio seguro, nunca execução com regras divergentes.
    """
    declarados = versao.declarados() if declarados is None else declarados
    try:
        manifesto = carregar(str(declarados["jogo"]), pasta)
    except ManifestoInvalidoError as erro:
        raise InstalacaoDivergenteError([str(erro)]) from erro
    problemas = conferir_declaracao(manifesto, declarados) + divergencias(manifesto, raiz)
    if problemas:
        raise InstalacaoDivergenteError(problemas)
    return manifesto
