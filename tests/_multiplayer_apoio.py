"""Apoio comum dos testes do multiplayer: acervo real, contas, servidor determinístico, clientes.

Os gladiadores são os snapshots publicados da Copa Arena 03
(`reports/pvp/copa_03/snapshots/`), extraídos de runs PvE reais e importados pelo
caminho confiável (`registro.importar_da_copa`, conferido pelo sha256 publicado).
Nenhum teste os altera: `tests/test_multiplayer_servidor.py` confere o sha256 dos
arquivos contra o publicado em `gladiadores.json`.

As contas de teste vivem só em memória, com uma chave de token fixa e senhas
inventadas para o teste.
"""

from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mechanics.pvp_duel import DuelAction, DuelView  # noqa: E402
from src.multiplayer.cliente import ClienteMultiplayer  # noqa: E402
from src.multiplayer.contas import ContasLocais, TokensAssinados  # noqa: E402
from src.multiplayer.gladiadores import AcervoDeGladiadores  # noqa: E402
from src.multiplayer.manifesto import (  # noqa: E402
    Identidade,
    Manifesto,
    hash_do_conteudo,
    manifesto_da_instalacao,
)
from src.multiplayer.registro import RegistroDeGladiadores, importar_da_copa  # noqa: E402
from src.multiplayer.servidor import Resultados, ServidorAutoritativo  # noqa: E402
from src.multiplayer.transporte import RedeLocal  # noqa: E402

COPA_03 = ROOT / "reports" / "pvp" / "copa_03"
SNAPSHOTS = COPA_03 / "snapshots"
# A final publicada da Copa 03: lubatv (W23) × fer (W64), seed oficial.
SEMENTE_DA_FINAL = 6619800792897972838

CHAVE_DE_TESTE = bytes(range(32))
SENHAS = {
    "ana": "senha-de-teste-da-ana",
    "bia": "senha-de-teste-da-bia",
    "caio": "senha-de-teste-do-caio",
}


def snapshot(gladiador: str) -> dict:
    return json.loads((SNAPSHOTS / f"{gladiador}.json").read_text(encoding="utf-8"))


def sha256_do_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def acervo(*ids: str) -> AcervoDeGladiadores:
    return AcervoDeGladiadores.de_snapshots({g: snapshot(g) for g in (ids or ("W23", "W64"))})


@lru_cache(maxsize=1)
def contas() -> ContasLocais:
    """As contas de teste (scrypt é caro: criadas uma vez por processo)."""
    locais = ContasLocais(None, TokensAssinados(CHAVE_DE_TESTE))
    for usuario, senha in SENHAS.items():
        locais.criar(usuario, senha)
    return locais


def conta_id(usuario: str) -> str:
    return contas().conta_do_usuario(usuario).id


def registro(**donos: tuple[str, ...] | str) -> RegistroDeGladiadores:
    """Gladiadores da Copa 03 por usuário: `registro(ana="W23", bia=("W64", "W01"))`.

    Sem argumentos: W23 da ana e W64 da bia — a final publicada da Copa 03.
    """
    donos = donos or {"ana": "W23", "bia": "W64"}
    gladiadores = RegistroDeGladiadores()
    for usuario, ids in donos.items():
        for gladiador in (ids,) if isinstance(ids, str) else ids:
            importar_da_copa(gladiadores, COPA_03, gladiador, conta_id(usuario))
    return gladiadores


def contador(prefixo: str):
    numeros = itertools.count(1)
    return lambda: f"{prefixo}{next(numeros)}"


def servidor(
    gladiadores: RegistroDeGladiadores | None = None,
    *,
    manifesto: Manifesto | None = None,
    resultados: Resultados | None = None,
    semente: int = SEMENTE_DA_FINAL,
    nome: str = "a",
    relogio=None,
) -> ServidorAutoritativo:
    """Uma instância com semente, sessões, ids e salas previsíveis.

    Sem `manifesto`, é o caminho de produção (`da_instalacao`): o manifesto
    conferido contra o código. Com `manifesto`, é uma instância de OUTRA versão,
    só para simular a frota durante uma atualização.
    """
    opcoes = {
        "sementes": lambda: semente,
        "sessoes": contador(f"{nome}-sessao-"),
        "ids": contador(f"{nome}-partida-"),
        "salas": contador(f"{nome.upper()}SALA"),
    }
    if relogio is not None:
        opcoes["relogio"] = relogio
    gladiadores = gladiadores if gladiadores is not None else registro()
    if manifesto is None:
        return ServidorAutoritativo.da_instalacao(gladiadores, contas(), resultados, **opcoes)
    return ServidorAutoritativo(manifesto, gladiadores, contas(), resultados, **opcoes)


def identidade_oficial() -> Identidade:
    return manifesto_da_instalacao().identidade


def outra_identidade(base: Identidade | None = None, **mudancas) -> Identidade:
    """A identidade oficial com campos trocados; `grupos` aceita um dict parcial."""
    base = base or identidade_oficial()
    grupos = dict(base.grupos)
    grupos.update(mudancas.pop("grupos", {}))
    nova = dataclasses.replace(base, grupos=tuple(sorted(grupos.items())), **mudancas)
    if "conteudo" not in mudancas:
        nova = dataclasses.replace(nova, conteudo=hash_do_conteudo(dict(nova.grupos)))
    return nova


def manifesto_de_outra_versao(jogo: str = "0.5.0-arena.teste", **mudancas) -> Manifesto:
    """Um manifesto de outra versão, para a instância "nova" de uma atualização."""
    oficial = manifesto_da_instalacao()
    return dataclasses.replace(
        oficial,
        identidade=outra_identidade(
            oficial.identidade,
            jogo=jogo,
            grupos={"regras": "f" * 64},
            regras="duelo-teste",
            **mudancas,
        ),
    )


class Ataca:
    """Sempre o ataque básico: o controlador mais simples que termina um duelo."""

    def choose(self, view: DuelView) -> DuelAction:
        return DuelAction.attack()


class Roteiro:
    """As ações de uma lista, rodada a rodada (para rejogar um trace publicado)."""

    def __init__(self, acoes: list[DuelAction]) -> None:
        self.acoes = acoes

    def choose(self, view: DuelView) -> DuelAction:
        return self.acoes[view.round_number - 1]


class PrimeiraSkill:
    """A primeira carta legal, senão o ataque: gasta MP e usa recarga."""

    def choose(self, view: DuelView) -> DuelAction:
        cartas = [a for a in view.legal_actions if a.kind == "skill"]
        return cartas[0] if cartas else DuelAction.attack()


def cliente(usuario: str, controlador=None, identidade: Identidade | None = None):
    """Um cliente que sabe a própria senha de teste (`entrar` a usa)."""
    cli = ClienteMultiplayer(identidade or identidade_oficial(), controlador)
    cli.usuario_de_teste = usuario
    return cli


def entrar(rede: RedeLocal, conexao: str, cli: ClienteMultiplayer, servidor_=None) -> None:
    """Conecta, faz login e abre a sessão."""
    rede.conectar(conexao, cli, servidor_)
    rede.enviar(conexao, cli.login(cli.usuario_de_teste, SENHAS[cli.usuario_de_teste]))
    if cli.token is not None:
        rede.enviar(conexao, cli.ola())


def em_fila(rede: RedeLocal, conexao: str, cli: ClienteMultiplayer, gladiador: str) -> None:
    """Conecta, autentica e entra na fila."""
    entrar(rede, conexao, cli)
    rede.enviar(conexao, cli.entrar_na_fila(gladiador))


def em_sala(rede, anfitriao, convidado, gladiadores=("W23", "W64"), conexoes=("c1", "c2")):
    """Partida direta: o anfitrião cria a sala, o convidado entra com o código."""
    entrar(rede, conexoes[0], anfitriao)
    rede.enviar(conexoes[0], anfitriao.criar_sala(gladiadores[0]))
    entrar(rede, conexoes[1], convidado)
    rede.enviar(conexoes[1], convidado.entrar_na_sala(anfitriao.sala, gladiadores[1]))


def _trace_da_final() -> dict:
    return json.loads((COPA_03 / "final_trace.json").read_text(encoding="utf-8"))


def acoes_da_final() -> dict[str, list[DuelAction]]:
    """As ações de cada lado, rodada a rodada, da final publicada da Copa 03."""
    acoes: dict[str, list[DuelAction]] = {"p1": [], "p2": []}
    for registro_ in _trace_da_final()["registros"]:
        if registro_["kind"] == "rodada_fim":
            for lado, acao in registro_["registro"]["actions"]:
                acoes[lado].append(DuelAction(acao["kind"], acao["skill_id"]))
    return acoes


def rodadas_da_final() -> list[dict]:
    return [r["registro"] for r in _trace_da_final()["registros"] if r["kind"] == "rodada_fim"]


def resultado_da_final() -> dict:
    return next(r["resultado"] for r in _trace_da_final()["registros"] if r["kind"] == "resultado")
