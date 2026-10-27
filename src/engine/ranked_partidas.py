"""Confrontos NPC × NPC da Ranked: o motor canônico, a IA estratégica dos dois lados.

É o mesmo duelo da Arena: `Duel` com o gerador semeado, `run_round` a cada
rodada, e a `IAEstrategica` decidindo por cada gladiador, só pela visão dele. A
semente decide tudo: a mesma dupla com a mesma semente dá o mesmo resultado, em
qualquer processo.

O lado (p1 ou p2) também sai da semente, para nenhum gladiador lutar sempre do
mesmo lado. Não há vantagem de lado no motor — a ordem de cada rodada é a
iniciativa —, mas a alternância tira a dúvida.

Uma partida que passa de `LIMITE_TECNICO` rodadas sem resultado não conta: o
motor não tem empate, e a Ranked não inventa um. `parar` interrompe entre
rodadas (o mundo orgânico usa isso para não segurar o jogo); a partida
interrompida também não conta.
"""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass

from src.engine.arena_populacao import Populacao
from src.mechanics.pvp_duel import Duel, run_round
from src.sim.ia_estrategica import Configuracao, IAEstrategica

LIMITE_TECNICO = 500


@dataclass(frozen=True)
class Confronto:
    """Uma partida terminada entre dois gladiadores da população."""

    a: str
    b: str
    semente: int
    vencedor: str
    motivo: str
    rodadas: int
    segundos: float

    @property
    def perdedor(self) -> str:
        return self.b if self.vencedor == self.a else self.a

    def para_dict(self) -> dict:
        return asdict(self)


def jogar(
    populacao: Populacao,
    id_a: str,
    id_b: str,
    semente: int,
    *,
    config: Configuracao | None = None,
    parar=None,
) -> Confronto | None:
    """O confronto de `id_a` contra `id_b`. `None` se não terminou (limite ou `parar`)."""
    if id_a == id_b:
        raise ValueError("Um gladiador não enfrenta a si mesmo.")
    inicio = time.perf_counter()
    ids = (id_a, id_b) if semente % 2 == 0 else (id_b, id_a)
    gladiadores = [populacao.gladiador(populacao.get(i)) for i in ids]
    duelo = Duel(gladiadores[0], gladiadores[1], rng=random.Random(semente))
    controladores = {
        "p1": IAEstrategica(gladiadores[0].hero, config),
        "p2": IAEstrategica(gladiadores[1].hero, config),
    }
    while not duelo.finished:
        if duelo.round_number > LIMITE_TECNICO or (parar is not None and parar.is_set()):
            return None
        run_round(duelo, controladores)
    resultado = duelo.result
    return Confronto(
        a=id_a,
        b=id_b,
        semente=semente,
        vencedor=ids[0] if resultado.winner == "p1" else ids[1],
        motivo=resultado.reason,
        rodadas=resultado.rounds,
        segundos=round(time.perf_counter() - inicio, 3),
    )
