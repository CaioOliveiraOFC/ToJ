"""Confrontos NPC × NPC da Ranked: o motor canônico, a IA estratégica dos dois lados.

É o mesmo duelo da Arena: `Duel` com o gerador semeado, `run_round` a cada
rodada, e a `IAEstrategica` decidindo por cada gladiador, só pela visão dele. A
semente decide tudo: a mesma dupla com a mesma semente dá o mesmo resultado, em
qualquer processo.

O lado (p1 ou p2) também sai da semente, para nenhum gladiador lutar sempre do
mesmo lado. Não há vantagem de lado no motor — a ordem de cada rodada é a
iniciativa —, mas a alternância tira a dúvida.

Três desfechos, e o terceiro não é resultado:

- **vitória** — KO ou rendição: `vencedor` é o id de quem venceu;
- **empate técnico** — o árbitro de impasse (`ranked/impasse.py`) encerrou a
  partida: os dois pararam de se desgastar, ou ela chegou ao teto de rodadas.
  `vencedor` é `None` e `motivo` diz qual dos dois (`impasse` ou `teto`);
- **interrompida** — `parar` foi acionado entre rodadas (o mundo orgânico usa
  isso para não segurar o jogo): `jogar` devolve `None`, nada aconteceu, e a
  partida é jogada de novo depois.

Um erro técnico (exceção do motor ou da IA) sobe para quem chamou, que decide
anular a partida.
"""

from __future__ import annotations

import random
import time
from dataclasses import asdict, dataclass

from src.engine.arena_populacao import Populacao
from src.mechanics.pvp_duel import Duel, run_round
from src.ranked.impasse import ArbitroDeImpasse
from src.sim.ia_estrategica import Configuracao, IAEstrategica

VITORIA = "vitoria"
EMPATE = "empate"


@dataclass(frozen=True)
class Confronto:
    """Uma partida terminada entre dois gladiadores da população."""

    a: str
    b: str
    semente: int
    vencedor: str | None
    motivo: str
    rodadas: int
    segundos: float

    @property
    def resultado(self) -> str:
        return EMPATE if self.vencedor is None else VITORIA

    @property
    def perdedor(self) -> str | None:
        if self.vencedor is None:
            return None
        return self.b if self.vencedor == self.a else self.a

    def para_dict(self) -> dict:
        return {**asdict(self), "resultado": self.resultado}


def maximos_do_duelo(duelo: Duel, lados) -> list[list[int]]:
    """O HP e o MP máximos de cada lado, na ordem de `lados`: o que o árbitro lê."""
    return [
        [duelo.hero(lado).base_hp for lado in lados],
        [duelo.hero(lado).base_mp for lado in lados],
    ]


def observar(arbitro, duelo: Duel, registro, lados, maximos):
    """Passa o fim da rodada ao árbitro; o veredito, se a partida virou empate."""
    hp, mp = dict(registro.hp_end), dict(registro.mp_end)
    return arbitro.observar(
        registro.number, [hp[lado] for lado in lados], [mp[lado] for lado in lados], maximos
    )


def jogar(
    populacao: Populacao,
    id_a: str,
    id_b: str,
    semente: int,
    *,
    config: Configuracao | None = None,
    parar=None,
    arbitro=None,
) -> Confronto | None:
    """O confronto de `id_a` contra `id_b`: vitória ou empate técnico; `None` se interrompido."""
    if id_a == id_b:
        raise ValueError("Um gladiador não enfrenta a si mesmo.")
    arbitro = ArbitroDeImpasse() if arbitro is None else arbitro
    inicio = time.perf_counter()
    ids = (id_a, id_b) if semente % 2 == 0 else (id_b, id_a)
    gladiadores = [populacao.gladiador(populacao.get(i)) for i in ids]
    duelo = Duel(gladiadores[0], gladiadores[1], rng=random.Random(semente))
    controladores = {
        "p1": IAEstrategica(gladiadores[0].hero, config),
        "p2": IAEstrategica(gladiadores[1].hero, config),
    }
    # O árbitro vê os lados na ordem (a, b), e não (p1, p2).
    lados = ("p1", "p2") if ids[0] == id_a else ("p2", "p1")
    maximos = maximos_do_duelo(duelo, lados)
    while not duelo.finished:
        if parar is not None and parar.is_set():
            return None
        registro = run_round(duelo, controladores)
        if duelo.finished:
            break
        veredito = observar(arbitro, duelo, registro, lados, maximos)
        if veredito is not None:
            return Confronto(
                a=id_a,
                b=id_b,
                semente=semente,
                vencedor=None,
                motivo=veredito.motivo,
                rodadas=veredito.rodada,
                segundos=round(time.perf_counter() - inicio, 3),
            )
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
