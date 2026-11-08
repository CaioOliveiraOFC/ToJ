"""Conta, no `simulate_run` real, bênçãos do Altar e combates que começam com ela.

Só observa: embrulha `apply_altar_blessing`, `apply_fountain_heal` e `run_battle`
dentro do módulo `src.sim.harness`, chama as originais e conta. Nada sorteia.
Roda o tamanho do teste de bandas (3 classes × 250 runs, teto 20, política
`smart`, equipamento esperado). Rodar da raiz do repositório:
    python reports/etapa1_plano/altar_na_regua.py
"""

import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.sim import harness as h  # noqa: E402

BENCAO = "Benção do Altar"  # a chave gravada por `apply_altar_blessing`
conta = collections.Counter()
orig_altar, orig_fonte, orig_luta = h.apply_altar_blessing, h.apply_fountain_heal, h.run_battle


def altar(hero):
    conta["bencao_aplicada"] += 1
    return orig_altar(hero)


def fonte(hero):
    antes = hero.get_hp()
    curou = orig_fonte(hero)
    conta["fonte_visitas"] += 1
    conta["fonte_hp_curado"] += hero.get_hp() - antes
    return curou


def luta(hero, monsters, decide, **k):
    conta["combates"] += 1
    if BENCAO in getattr(hero, "active_buffs", {}):
        conta["combates_com_bencao_ativa"] += 1
    return orig_luta(hero, monsters, decide, **k)


h.apply_altar_blessing, h.apply_fountain_heal, h.run_battle = altar, fonte, luta
for classe in ("Warrior", "Mage", "Rogue"):
    h.simulate_run(classe, 20, 250, "smart", loadout="expected")
for chave in (
    "combates",
    "bencao_aplicada",
    "combates_com_bencao_ativa",
    "fonte_visitas",
    "fonte_hp_curado",
):
    print(f"{chave}: {conta[chave]}")
