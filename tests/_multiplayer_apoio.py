"""Apoio comum dos testes do multiplayer: acervo real, servidor determinístico, clientes.

Os gladiadores são os snapshots publicados da Copa Arena 03
(`reports/pvp/copa_03/snapshots/`), extraídos de runs PvE reais. Nenhum teste os
altera: o acervo trabalha em cópias, e `tests/test_multiplayer_servidor.py`
confere o sha256 dos arquivos contra o publicado em `gladiadores.json`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mechanics.pvp_duel import DuelAction, DuelView  # noqa: E402
from src.multiplayer.cliente import ClienteMultiplayer  # noqa: E402
from src.multiplayer.gladiadores import AcervoDeGladiadores  # noqa: E402
from src.multiplayer.manifesto import (  # noqa: E402
    Identidade,
    Manifesto,
    hash_do_conteudo,
    manifesto_da_instalacao,
)
from src.multiplayer.servidor import Resultados, ServidorAutoritativo  # noqa: E402
from src.multiplayer.transporte import RedeLocal  # noqa: E402

COPA_03 = ROOT / "reports" / "pvp" / "copa_03"
SNAPSHOTS = COPA_03 / "snapshots"
# A final publicada da Copa 03: lubatv (W23) × fer (W64), seed oficial.
SEMENTE_DA_FINAL = 6619800792897972838


def snapshot(gladiador: str) -> dict:
    return json.loads((SNAPSHOTS / f"{gladiador}.json").read_text(encoding="utf-8"))


def sha256_do_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def acervo(*ids: str) -> AcervoDeGladiadores:
    return AcervoDeGladiadores.de_snapshots({g: snapshot(g) for g in (ids or ("W23", "W64"))})


def contador(prefixo: str):
    numeros = itertools.count(1)
    return lambda: f"{prefixo}{next(numeros)}"


def servidor(
    acervo_: AcervoDeGladiadores | None = None,
    *,
    manifesto: Manifesto | None = None,
    resultados: Resultados | None = None,
    semente: int = SEMENTE_DA_FINAL,
    nome: str = "a",
) -> ServidorAutoritativo:
    """Uma instância com semente, tokens e ids previsíveis.

    Sem `manifesto`, é o caminho de produção (`da_instalacao`): o manifesto
    conferido contra o código. Com `manifesto`, é uma instância de OUTRA versão,
    só para simular a frota durante uma atualização.
    """
    opcoes = {
        "sementes": lambda: semente,
        "tokens": contador(f"{nome}-token-"),
        "ids": contador(f"{nome}-partida-"),
    }
    gladiadores = acervo_ if acervo_ is not None else acervo()
    if manifesto is None:
        return ServidorAutoritativo.da_instalacao(gladiadores, resultados, **opcoes)
    return ServidorAutoritativo(manifesto, gladiadores, resultados, **opcoes)


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


def manifesto_de_outra_versao(jogo: str = "0.4.0-arena.2", **mudancas) -> Manifesto:
    """Um manifesto de outra versão, para a instância "nova" de uma atualização."""
    oficial = manifesto_da_instalacao()
    return dataclasses.replace(
        oficial,
        identidade=outra_identidade(
            oficial.identidade,
            jogo=jogo,
            grupos={"regras": "f" * 64},
            regras="duelo-2",
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


def cliente(nome: str, controlador=None, identidade: Identidade | None = None):
    return ClienteMultiplayer(identidade or identidade_oficial(), nome, controlador)


def em_fila(rede: RedeLocal, conexao: str, cli: ClienteMultiplayer, gladiador: str) -> None:
    """Conecta, cumprimenta e entra na fila."""
    rede.conectar(conexao, cli)
    rede.enviar(conexao, cli.ola())
    rede.enviar(conexao, cli.entrar_na_fila(gladiador))


def _trace_da_final() -> dict:
    return json.loads((COPA_03 / "final_trace.json").read_text(encoding="utf-8"))


def acoes_da_final() -> dict[str, list[DuelAction]]:
    """As ações de cada lado, rodada a rodada, da final publicada da Copa 03."""
    acoes: dict[str, list[DuelAction]] = {"p1": [], "p2": []}
    for registro in _trace_da_final()["registros"]:
        if registro["kind"] == "rodada_fim":
            for lado, acao in registro["registro"]["actions"]:
                acoes[lado].append(DuelAction(acao["kind"], acao["skill_id"]))
    return acoes


def rodadas_da_final() -> list[dict]:
    return [r["registro"] for r in _trace_da_final()["registros"] if r["kind"] == "rodada_fim"]


def resultado_da_final() -> dict:
    return next(r["resultado"] for r in _trace_da_final()["registros"] if r["kind"] == "resultado")
