# Balanceamento de Classes — PROMPT 14

**Classes reais confirmadas em `src/entities/heroes.py:457,532,607`:** `Warrior`, `Mage`, `Rogue` (3 classes). Não existe outra classe.

**Metodo:** `AutoTester` (`tests/auto_test.py`) com `Quick` (cap 8000 acoes, sem progress bar) — 5 runs completas por classe, seeds fixas `[101,202,303,404,505]` para comparacao justa (mesma sequencia random para todas). Log resumido estilo PROMPT 7 em `reports/balance_*.log` (taxa sobrevivencia, andar medio, causa morte). Inventario/equipamento variado (PROMPT 12) e loja equipar (PROMPT 13) ja presentes.

## Antes (constantes originais)

```
WARRIOR_BASE_HP=104 MP=30 ST=104 AG=5 MG=30 DF=30 | HP growth 20% ST 10%
MAGE_BASE_HP=96 MP=100 ST=32 AG=5 MG=100 DF=23 | MP 18% MG 18% (sem HP growth)
ROGUE_BASE_HP=99 MP=50 ST=75 AG=15 MG=66 DF=20 | HP 8% ST16% AG18%
```

**Resultados 5 runs/classe (mesmas seeds):**

| Classe | Levels (5 seeds) | Avg | Sobreviveu (Lv20) | Causa mais comum |
|--------|------------------|-----|-------------------|------------------|
| Warrior | [5,20,20,20,5] | 14.0 | 3/5 | death_combat 2, victory 3 |
| Mage | [5,10,9,20,5] | 9.8 | 1/5 | death_combat 4, victory 1 |
| Rogue | [5,20,20,20,5] | 14.0 | 3/5 | death_combat 2, victory 3 |

**Diagnostico:** Mage sistematicamente mais fraca: **4.2 andares a menos que Warrior/Rogue** em media, 2 vitorias a menos. Causa morte quase sempre `death_combat` (morre em combate, nao travamento). Sem crescimento de HP, Mage ficava fragil nos andares 5-10.

## Ajuste (sem tocar monstro — PROMPT 16)

- `MAGE_BASE_HP 96 -> 99 (+3)`
- `MAGE_BASE_DF 23 -> 25 (+2)`
- `MAGE_HP_GROWTH_PERCENT 0 -> 8` (novo, `src/shared/constants.py:135`, aplicado em `src/entities/heroes.py:420-422`)
- Warrior/Rogue mantidos (para nao inverter balanceamento). Mage ganhou sobrevivencia sem virar overpower.

## Depois (mesmas 5 seeds, mesmos monstros)

```
MAGE_BASE_HP=99 DF=25 HP growth 8%
```

| Classe | Levels (5 seeds) | Avg | Sobreviveu | Causa |
|--------|------------------|-----|------------|-------|
| Warrior | [5,20,20,20,5] | 14.0 | 3/5 | death_combat 2 |
| Mage | [20,20,5,20,5] | 14.0 | 3/5 | victory 3 / death_combat 2 |
| Rogue | [5,20,20,20,5] | 14.0 | 3/5 | death_combat 2 |

**Resultado:** todas 14.0 avg, 3/5 vitorias — range 0 (antes 4.2). Causa morte ainda `death_combat` (balanceado, nao travamento). Log detalhado em `reports/balance_before.log` (antes) e `reports/balance_after.log` (depois) + `reports/balance_20260828.log` (final).

**Validacao:** `pytest 130 passed`, `AutoTester` 15 runs 0 crashes (5 por classe), loja equipar e inventario continuam funcionando (fix unicode anterior mantido).
