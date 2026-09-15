"""Geometria do andar: o que o mapa OBRIGA e o que ele deixa escolher.

O simulador enfrenta todos os monstros do andar. O jogador não: ele anda por um
mapa com paredes, e pode contornar quem não quiser encarar. Quanto disso é
escolha real, ninguém mediu — e o balanceamento está prestes a ser calibrado em
cima do pior caso como se fosse o caso médio.

Este módulo não joga e não decide nada. Ele lê um `MapOfGame` pronto e responde
perguntas de geometria:

    Qual o caminho mais CURTO até a saída?
    Qual o caminho com MENOS combate?
    Quantos inimigos dá para evitar?
    O evento exige desvio? De quantos passos?

Deliberadamente sem política. A pergunta desta rodada é a FORMA do andar, e
inventar comportamento antes de conhecer a forma é como o plano de andar do
simulador divergiu do jogo: um modelo plausível, nunca conferido.

As duas rotas são calculadas com o MESMO algoritmo, mudando só o custo da
aresta: passos para a mais curta, combates para a de menos luta. Dijkstra com
custo `(combates, passos)` responde as duas, e é por isso que "a rota segura tem
mais passos" sai medido em vez de suposto.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.engine.map import MapOfGame

# O jogador anda em cruz, como `move_player` faz.
VIZINHOS = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass(frozen=True)
class Rota:
    """Uma rota possível até a saída."""

    passos: int
    combates: int
    alcancavel: bool = True

    @classmethod
    def impossivel(cls) -> "Rota":
        return cls(passos=0, combates=0, alcancavel=False)


@dataclass(frozen=True)
class Geometria:
    """O retrato de um andar, do ponto de vista de quem precisa atravessá-lo."""

    monstros: int
    curta: Rota
    segura: Rota
    tem_evento: bool
    desvio_do_evento: int
    combates_do_evento: int
    evento_alcancavel: bool

    @property
    def evitaveis(self) -> int:
        """Monstros que a rota de menos combate deixa para trás."""
        return max(0, self.monstros - self.segura.combates)

    @property
    def fracao_evitavel(self) -> float:
        return self.evitaveis / self.monstros if self.monstros else 0.0


def _andavel(game_map: "MapOfGame", y: int, x: int) -> bool:
    """A casa existe e não é parede.

    `D` é corpo de monstro já morto e continua passável, como em `move_player`.
    `X` é a saída, e é destino.
    """
    if not (0 <= y < game_map.height and 0 <= x < game_map.width):
        return False
    return game_map.grid[y][x] in (".", "D", "X")


def _melhor_rota(game_map: "MapOfGame", origem, destino, por_combate: bool) -> Rota:
    """Dijkstra sobre a grade, com o custo que a pergunta pede.

    `por_combate=True` faz cada casa com monstro custar uma unidade cara e o
    passo uma barata, então o caminho ótimo é o que luta menos e, entre os que
    lutam o mesmo, o mais curto. Com `False`, conta só passos.
    """
    if origem == destino:
        return Rota(passos=0, combates=0)

    inimigos = game_map.enemies_pos
    fila = [(0, 0, origem)]
    visto: dict[tuple[int, int], tuple[int, int]] = {origem: (0, 0)}

    while fila:
        custo_a, custo_b, atual = heapq.heappop(fila)
        if atual == destino:
            return (
                Rota(passos=custo_b, combates=custo_a)
                if por_combate
                else Rota(passos=custo_a, combates=custo_b)
            )
        if visto.get(atual, (10**9, 10**9)) < (custo_a, custo_b):
            continue
        y, x = atual
        for dy, dx in VIZINHOS:
            ny, nx = y + dy, x + dx
            if not _andavel(game_map, ny, nx):
                continue
            luta = 1 if (ny, nx) in inimigos else 0
            novo = (custo_a + luta, custo_b + 1) if por_combate else (custo_a + 1, custo_b + luta)
            if novo < visto.get((ny, nx), (10**9, 10**9)):
                visto[(ny, nx)] = novo
                heapq.heappush(fila, (novo[0], novo[1], (ny, nx)))

    return Rota.impossivel()


def analisar(game_map: "MapOfGame") -> Geometria:
    """Mede o andar. Não move ninguém e não altera nada."""
    origem = (game_map.player_pos["y"], game_map.player_pos["x"])
    saida = (game_map.exit_pos["y"], game_map.exit_pos["x"])

    curta = _melhor_rota(game_map, origem, saida, por_combate=False)
    segura = _melhor_rota(game_map, origem, saida, por_combate=True)

    evento = game_map.event_pos
    if evento is None:
        return Geometria(
            monstros=len(game_map.enemies_pos),
            curta=curta,
            segura=segura,
            tem_evento=False,
            desvio_do_evento=0,
            combates_do_evento=0,
            evento_alcancavel=False,
        )

    # Custo de PASSAR pelo evento: ir até ele e de lá até a saída. Comparado com
    # a rota curta, é o preço em passos de querer o Altar.
    ate_evento = _melhor_rota(game_map, origem, evento, por_combate=True)
    do_evento = _melhor_rota(game_map, evento, saida, por_combate=True)
    alcancavel = ate_evento.alcancavel and do_evento.alcancavel

    return Geometria(
        monstros=len(game_map.enemies_pos),
        curta=curta,
        segura=segura,
        tem_evento=True,
        desvio_do_evento=(
            max(0, ate_evento.passos + do_evento.passos - curta.passos) if alcancavel else 0
        ),
        combates_do_evento=(
            max(0, ate_evento.combates + do_evento.combates - segura.combates) if alcancavel else 0
        ),
        evento_alcancavel=alcancavel,
    )
