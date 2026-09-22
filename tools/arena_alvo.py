"""ARENA BENCHMARK V1: o gladiador que a run precisa igualar.

Não é um personagem montado. É o SNAPSHOT de uma run real do `BotPadrao`,
capturado na entrada do andar 20, escolhido por ser o mais próximo da mediana de
`overall_power` de 54 sobreviventes em 900 runs (6,00% chegaram vivos). A
mediana só escolheu QUAL snapshot representa a população — um "personagem médio"
com o elmo de um e a arma de outro nunca atravessou 19 andares e não serve de
alvo para nada.

Mora em `tools/` porque a Arena ainda não é feature do jogo: nada em `src/` a
consulta, e `sim/` não pode importar `storage/` — a regra que mantém a simulação
headless. Quando a Arena virar jogo, mover isto para a camada certa é decisão
deliberada, não acidente de import.

Congelado e recarregado pelo caminho CANÔNICO do save do jogo
(`storage.save_manager`), nunca reconstruído campo a campo. Uma segunda
reidratação em paralelo perderia em silêncio o próximo campo que o save
aprendesse a guardar — foi exatamente o que aconteceu com `+N`, socket e
encantamento quando o formato era só o nome.

`overall_power` dele é medido pela mesma régua de todo mundo, com HP/MP cheios:
o HP e o MP da chegada ficam no arquivo como telemetria e não entram no poder.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from src.content.items import get_all_items
from src.entities.heroes import Mage, Rogue, Warrior
from src.sim.arena import Comparacao, comparar, overall_power
from src.storage.save_manager import player_from_save_data

ARQUIVO = Path(__file__).resolve().parents[1] / "src" / "data" / "arena_benchmark_v1.json"

# `overall_power` do benchmark, medido uma vez e congelado AQUI, ao lado do que
# ele verifica. Não é usado no lugar da medição: `poder_do_benchmark()` mede de
# novo e o teste falha se divergir. Um alvo que se desloca em silêncio
# recalibraria a decisão de extrair sem ninguém perceber.
#
# O snapshot é um Rogue nível 22, seed 20261007, capturado na entrada do andar
# 20. Escolhido por ser o mais próximo da MEDIANA de 54 sobreviventes em 900
# runs (6,00% chegaram vivos), e as três classes convergiram para perto de 30
# apesar de taxas de sobrevivência 9x diferentes.
#
# 29,98 -> 29,87 na V2, quando consumível saiu da régua. Este snapshot cai pouco
# porque não carrega poção de CURA: são 4 elixires e 1 poção de mana, e nenhum
# dos dois muda muito um duelo 1x1 curto. Sobreviventes com poção de cura caíram
# de 3,8% a 5,0%.
PODER_ESPERADO = 29.87

_FABRICA = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


class BenchmarkIndisponivelError(RuntimeError):
    """O benchmark não carregou. É bug de código, nunca estado de jogo.

    Falha alto de propósito: um benchmark que não carrega e devolve `None`
    faria a Gestão da Run comparar contra nada e chamar o resultado de veredito.
    """


def _carregar():
    if not ARQUIVO.exists():
        raise BenchmarkIndisponivelError(f"Benchmark da Arena não encontrado em {ARQUIVO}")
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    heroi, _, _ = player_from_save_data(dados, get_all_items(), _FABRICA)
    if heroi is None:
        raise BenchmarkIndisponivelError(f"Benchmark da Arena ilegível em {ARQUIVO}")
    return heroi, dados.get("_benchmark", {})


@lru_cache(maxsize=1)
def _cache():
    return _carregar()


def benchmark():
    """O personagem de referência da Arena, recarregado do snapshot congelado."""
    return _cache()[0]


def procedencia() -> dict:
    """De onde veio este snapshot: versão, classe, seed, andar e a chegada."""
    return dict(_cache()[1])


def poder_do_benchmark() -> float:
    """`overall_power` do benchmark, medido pela régua de todo mundo."""
    return overall_power(benchmark()).nivel_equivalente


def comparar_com_benchmark(personagem, **kwargs) -> Comparacao:
    """`bot_power / benchmark_power`, com a guarda de kit na frente.

    O valor esperado está congelado em `PODER_ESPERADO` e é verificado por
    teste: se a régua ou o conteúdo mudarem, é ali que se descobre, e não numa
    decisão de extrair silenciosamente calibrada contra outro alvo.
    """
    return comparar(personagem, benchmark(), **kwargs)
