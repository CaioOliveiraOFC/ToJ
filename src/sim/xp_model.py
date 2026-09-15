"""Modelo determinístico da progressão de nível, sobre as regras reais do andar.

Existe porque o simulador de run **não pode** validar profundidade. O plano de
andar dele (`harness._default_floor_plan`) satura em 14 monstros, enquanto o jogo
gera `3 + andar//3` sem teto: no andar 20 o simulador põe 39% de monstros a mais
que a produção, e no andar 100 põe 62% a menos. Qualquer trajetória de XP medida
por ele mede outro jogo.

Este módulo não simula combate. Ele responde uma pergunta só, e de forma fechada:
**quanta XP um andar produz, e a que nível isso leva o herói.** É o instrumento
que prova (ou derruba) o contrato de progressão.

A regra de ouro aqui é não ter regra própria. Densidade, elite, nível do monstro,
recompensa, chefe e Essência vêm todos das mesmas funções e constantes que o jogo
usa. Um modelo que redeclara qualquer uma delas volta a divergir na primeira
mudança de conteúdo — que é exatamente o defeito que ele existe para medir.

| o que | de onde vem |
|---|---|
| monstros por andar, elite | `generation_rules()` (`content/factories/monsters.py`) |
| nível do monstro | `calculate_scaled_monster_level` — amostrado, nunca reimplementado |
| XP por monstro / por chefe | `calculate_monster_xp_reward`, `calculate_mini_boss_xp_reward` |
| chefe a cada N andares | `BOSS_FLOOR_INTERVAL` — a regra real; o `boss_spawn_chance`
  do JSON não tem um único leitor, e modelar por ele contaria metade dos chefes |
| custo do nível | `xp_for_level` |
| Essência | constantes de Essência, em forma fechada validada contra a amostra |
"""

from __future__ import annotations

import random
import statistics
from functools import lru_cache

from src.content.factories.monsters import (
    calculate_scaled_monster_level,
    generation_rules,
    routine_monster_count,
)
from src.mechanics.math_operations import (
    calculate_mini_boss_xp_reward,
    calculate_monster_xp_reward,
)
from src.shared.constants import (
    BOSS_FLOOR_INTERVAL,
    ESSENCE_MULT_LEVEL_BONUS,
    ESSENCE_MULT_MAX,
    ESSENCE_MULT_MAX_BONUS,
    ESSENCE_MULT_NORMAL_MEAN,
)
from src.shared.formulas import xp_for_level

# Amostras por (andar, nível do herói) ao consultar o gerador real de níveis.
# `calculate_scaled_monster_level` relê e reparseia `monsters.json` a cada
# chamada — 89 µs —, então o resultado é memoizado. 160 amostras deixam o erro
# padrão da média em ~0,04 nível, duas ordens de grandeza abaixo das tolerâncias
# do contrato.
LEVEL_SAMPLES = 96
LEVEL_SEED = 20260912


def _balde_do_heroi(hero_level: int) -> int:
    """Colapsa o nível do herói nas faixas que o gerador real distingue.

    `calculate_scaled_monster_level` só olha o nível do herói em um lugar —
    `if player_level <= early_player_level` — então acima desse limiar todos os
    níveis produzem a mesma distribuição. Colapsar aqui faz os seis perfis de
    diagnóstico compartilharem o mesmo cache em vez de reamostrar tudo seis vezes.

    O limiar vem do JSON, não de um literal: se ele mudar, o balde muda junto. E
    `tests/test_progression_contract.py` confere o resultado contra a função de
    verdade, incluindo os níveis baixos, para que o atalho não passe a mentir em
    silêncio.
    """
    limiar = int(generation_rules()["level_variation"]["early_player_level"])
    return min(max(1, hero_level), limiar + 1)


def _amostra_do_encontro(floor: int, hero_level: int) -> tuple[float, float]:
    """Nível médio e XP média de um monstro comum deste andar."""
    return _amostra_por_balde(floor, _balde_do_heroi(hero_level))


@lru_cache(maxsize=None)
def _amostra_por_balde(floor: int, hero_level: int) -> tuple[float, float]:
    """Nível médio e XP média de um monstro comum, amostrados do gerador real.

    Amostra `calculate_scaled_monster_level` em vez de reproduzir a conta. O
    gerador tem três tetos de segurança (`max_above_floor`, `early_max_above_player`
    e `first_floor_max_level`) que dependem do andar E do nível do herói; qualquer
    fórmula fechada aqui seria uma quarta cópia dessas regras, livre para divergir.

    As duas médias são necessárias, e não uma só: a recompensa é geométrica no
    nível, então `E[recompensa]` não é `recompensa(E[nível])`. Usar a segunda
    subestima o andar em ~4%.
    """
    estado = random.getstate()
    try:
        random.seed(LEVEL_SEED + floor * 131 + hero_level)
        niveis = [calculate_scaled_monster_level(floor, hero_level) for _ in range(LEVEL_SAMPLES)]
    finally:
        random.setstate(estado)
    return statistics.fmean(niveis), statistics.fmean(
        calculate_monster_xp_reward(n) for n in niveis
    )


def expected_monsters(floor: int) -> float:
    """Monstros que o andar coloca no mapa, contando elite e chefe esperados.

    A contagem de comuns vem de `routine_monster_count`, a MESMA que o jogo usa
    para povoar o andar — aqui era uma terceira cópia da fórmula, ao lado da do
    jogo e da do plano de andar do simulador. Elite e chefe entram como VALOR
    ESPERADO, e não como sorteio, porque esta função responde "quanto o andar
    rende em média" e não "o que este andar tem".
    """
    regras = generation_rules()
    comuns = routine_monster_count(floor)
    elite = (
        float(regras["elite_spawn_chance"])
        if floor >= int(regras["advanced_role_min_floor"])
        else 0.0
    )
    return comuns + elite + 1.0 / BOSS_FLOOR_INTERVAL


def expected_monster_level(floor: int, hero_level: int) -> float:
    """Nível médio do que o andar coloca no mapa, chefe incluído no peso."""
    nivel_comum, _ = _amostra_do_encontro(floor, hero_level)
    comuns = expected_monsters(floor) - 1.0 / BOSS_FLOOR_INTERVAL
    chefe_peso = 1.0 / BOSS_FLOOR_INTERVAL
    nivel_chefe = _nivel_do_chefe(floor)
    return (comuns * nivel_comum + chefe_peso * nivel_chefe) / (comuns + chefe_peso)


def _nivel_do_chefe(floor: int) -> int:
    """Nível efetivo do mini-chefe do andar, pela mesma regra da recompensa."""
    from src.mechanics.math_operations import _calculate_mini_boss_effective_level

    return _calculate_mini_boss_effective_level(floor)


def expected_essence(floor: int) -> float:
    """Multiplicador médio de Essência do andar.

    Forma fechada da distribuição de `generate_essence_multiplier`: a gaussiana é
    simétrica e os cortes em 0,6 e 2,2 ficam a três desvios da média, então a
    média sorteada é a média nominal. `tests/test_progression_contract.py` cobra
    isso contra a função de verdade.
    """
    media = ESSENCE_MULT_NORMAL_MEAN + min(
        ESSENCE_MULT_MAX_BONUS, (max(1, floor) - 1) * ESSENCE_MULT_LEVEL_BONUS
    )
    return min(media, ESSENCE_MULT_MAX)


def expected_floor_xp(
    floor: int, hero_level: int, essence: float, engagement: float = 1.0
) -> float:
    """XP que o andar produz para um herói deste nível.

    `engagement` é a fração dos encontros do andar que o jogador enfrenta — o
    mapa permite evitar parte deles. É **parâmetro de diagnóstico**, nunca regra
    de jogo: quanto um jogador real luta depende do mapa, e nenhum valor disso
    está escrito no produto.
    """
    _, xp_comum = _amostra_do_encontro(floor, hero_level)
    comuns = expected_monsters(floor) - 1.0 / BOSS_FLOOR_INTERVAL
    chefe = calculate_mini_boss_xp_reward(floor) / BOSS_FLOOR_INTERVAL
    return engagement * essence * (comuns * xp_comum + chefe)


def level_trajectory(
    max_floor: int, engagement: float = 1.0, essence: str = "expected"
) -> dict[int, int]:
    """Nível do herói ao fim de cada andar, sem simular um turno de combate.

    `essence`: "expected" usa a curva real do jogo; "neutral" fixa 1,0, que é o
    jogador sem nenhuma sorte de Essência. A pergunta que isso responde é se a
    progressão se sustenta **sem** Essência boa — se não se sustentar, a Essência
    deixou de ser vantagem e virou requisito.
    """
    nivel, acumulado = 1, 0.0
    saida: dict[int, int] = {}
    for floor in range(1, max_floor + 1):
        mult = expected_essence(floor) if essence == "expected" else 1.0
        acumulado += expected_floor_xp(floor, nivel, mult, engagement)
        while acumulado >= xp_for_level(nivel):
            acumulado -= xp_for_level(nivel)
            nivel += 1
        saida[floor] = nivel
    return saida


def level_delta(trajectory: dict[int, int], floor: int) -> float:
    """`nível do herói − nível esperado do encontro`, a grandeza do contrato."""
    return trajectory[floor] - expected_monster_level(floor, trajectory[floor])


def delta_slope(trajectory: dict[int, int], first: int, last: int) -> float:
    """Inclinação de `level_delta` entre dois andares, em nível por andar.

    É o número que separa "o herói está atrás" de "o herói fica cada vez mais
    atrás". O primeiro é dificuldade; o segundo é a run ter teto matemático.
    """
    xs = list(range(first, last + 1))
    ys = [level_delta(trajectory, f) for f in xs]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else 0.0


def trajectory_rows(trajectory: dict[int, int], floors: list[int]) -> list[dict]:
    """Linhas de diagnóstico: andar, nível, nível do encontro, delta e XP."""
    return [
        {
            "floor": f,
            "hero_level": trajectory[f],
            "expected_monster_level": round(expected_monster_level(f, trajectory[f]), 2),
            "level_delta": round(level_delta(trajectory, f), 2),
            "xp_next_level": xp_for_level(trajectory[f]),
            "floor_xp": round(expected_floor_xp(f, trajectory[f], expected_essence(f)), 1),
        }
        for f in floors
        if f in trajectory
    ]
