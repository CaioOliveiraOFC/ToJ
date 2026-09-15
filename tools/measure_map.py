"""Mede a GEOMETRIA dos andares reais. Não faz parte do jogo.

O simulador enfrenta todos os monstros do andar. O jogador anda por um mapa com
paredes e pode contornar. A diferença entre essas duas coisas nunca foi medida,
e o balanceamento global está prestes a ser calibrado em cima dela.

Esta ferramenta monta andares pelo MESMO caminho que o jogo monta — mesmas
dimensões, mesma densidade de parede, mesma população, mesma chance de evento —
e pergunta ao analisador quanto do andar é obrigatório e quanto é escolha.

Não decide política nenhuma. Primeiro os números; o modelo de mapa do simulador
vem depois deles.

Uso: `python tools/measure_map.py [amostras]`
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.dungeons import roll_random_event  # noqa: E402
from src.content.factories.monsters import (  # noqa: E402
    create_boss_for_level,
    generate_monsters_for_level,
)
from src.engine.loop import _calculate_map_dimensions, _calculate_wall_percentage  # noqa: E402
from src.engine.map import MapOfGame  # noqa: E402
from src.engine.map_analysis import analisar  # noqa: E402
from src.shared.constants import BOSS_FLOOR_INTERVAL  # noqa: E402

ANDARES = (1, 5, 10, 15, 20, 30, 50)


def montar_andar(floor: int, seed: int) -> MapOfGame:
    """Um andar como `engine/loop.py` o monta, com semente conhecida."""
    random.seed(seed)
    altura, largura = _calculate_map_dimensions(floor)
    game_map = MapOfGame(height=altura, width=largura)
    game_map.generate_map(percent_of_walls=_calculate_wall_percentage(floor))
    game_map.place_player()
    game_map.place_exit()
    for monstro in generate_monsters_for_level(floor, floor):
        game_map.place_enemy(monstro)
    if floor % BOSS_FLOOR_INTERVAL == 0:
        game_map.place_enemy(create_boss_for_level(floor))
    game_map.place_event(roll_random_event())
    return game_map


def medir(floor: int, amostras: int) -> dict:
    dados = [analisar(montar_andar(floor, 9000 + i)) for i in range(amostras)]
    alcancaveis = [g for g in dados if g.curta.alcancavel]
    com_evento = [g for g in dados if g.tem_evento and g.evento_alcancavel]

    def media(f, fonte=None):
        fonte = alcancaveis if fonte is None else fonte
        return statistics.fmean([f(g) for g in fonte]) if fonte else 0.0

    return {
        "andar": floor,
        "amostras": len(dados),
        "saida_inalcancavel": len(dados) - len(alcancaveis),
        "monstros": media(lambda g: g.monstros),
        "passos_curta": media(lambda g: g.curta.passos),
        "lutas_curta": media(lambda g: g.curta.combates),
        "passos_segura": media(lambda g: g.segura.passos),
        "lutas_segura": media(lambda g: g.segura.combates),
        "evitavel": media(lambda g: g.fracao_evitavel),
        "zero_lutas": (
            sum(1 for g in alcancaveis if g.segura.combates == 0) / len(alcancaveis)
            if alcancaveis
            else 0.0
        ),
        "andares_com_evento": sum(1 for g in dados if g.tem_evento) / len(dados),
        "evento_desvio": media(lambda g: g.desvio_do_evento, com_evento),
        "evento_lutas": media(lambda g: g.combates_do_evento, com_evento),
    }


def main(amostras: int = 300) -> None:
    linhas = [medir(f, amostras) for f in ANDARES]

    print(f"=== GEOMETRIA DO ANDAR ({amostras} mapas por andar) ===\n")
    print(
        f"{'andar':>5} {'monstros':>9} {'rota curta':>18} {'rota segura':>18} "
        f"{'evitável':>9} {'sem luta':>9}"
    )
    print(f"{'':>5} {'':>9} {'passos/lutas':>18} {'passos/lutas':>18} {'':>9} {'':>9}")
    for d in linhas:
        print(
            f"{d['andar']:>5} {d['monstros']:>9.1f} "
            f"{d['passos_curta']:>9.1f} /{d['lutas_curta']:>7.2f} "
            f"{d['passos_segura']:>9.1f} /{d['lutas_segura']:>7.2f} "
            f"{d['evitavel']:>8.0%} {d['zero_lutas']:>8.0%}"
        )

    print(f"\n=== EVENTO ({amostras} mapas por andar) ===\n")
    print(f"{'andar':>5} {'andares com evento':>19} {'desvio (passos)':>17} {'lutas a mais':>13}")
    for d in linhas:
        print(
            f"{d['andar']:>5} {d['andares_com_evento']:>18.0%} "
            f"{d['evento_desvio']:>17.1f} {d['evento_lutas']:>13.2f}"
        )

    inalcancavel = sum(d["saida_inalcancavel"] for d in linhas)
    print(f"\nmapas com saída inalcançável: {inalcancavel}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
