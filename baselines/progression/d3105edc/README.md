# Auditoria do primeiro level-up — Run Progression @ `d3105edc`

| | |
|---|---|
| **Commit medido ("depois")** | `d3105edc` — o primeiro level-up com custo próprio |
| **"Antes"** | `4d0a9a0a` — a [auditoria da dungeon](../4d0a9a0a/README.md). `antes.jsonl` é cópia byte a byte do `depois.jsonl` dela, coletado pelo mesmo coletor |
| **Tipo** | auditoria de progressão, sobre a régua de `Run/Progression Balance` |

A última correção localizada antes da decisão de release. O BotPadrão está
congelado desde `0ab837b9`.

---

## O que mudou

Só o custo do primeiro level-up.
- `FIRST_LEVEL_XP_COST = 100`, e `xp_for_level(1)` devolve essa constante.
- Do nível 2 em diante, a fórmula é exatamente a de `eba37d01`: `XP_BASE_COST`
  140, `XP_LEVEL_SOFTENER` 6, inclinação e crescimento iguais.
- O custo acumulado de qualquer nível posterior fica exatamente 40 abaixo do de
  antes.

**A tentativa descartada.** `32a0a5d9` baixou o nível 1 mexendo na fórmula
(`XP_BASE_COST` 100, amortecedor 4). Como a fórmula tem dois parâmetros, os
níveis 2-20 ficaram de 8% a 25% mais baratos junto. A auditoria de 300 runs
mostrou regressão estrutural:
- o herói passou a ficar à frente do andar (atraso médio no andar 10: +1,0 → −0,8);
- as extrações foram de 52 para 141;
- o `-m balance` estourou, com chegar ao 20 em 0,95 sob expected loadout e
  `MAX_GREEDY_REACH_20` também falhando.

A mudança foi desfeita em `d3105edc`. Os dados daquela coleta não foram
versionados.

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `antes.jsonl` | As 300 runs do `4d0a9a0a`, cópia do `depois.jsonl` daquela auditoria. 387.553 bytes, sha256 `c449dbf357f958a88b76c54d023e71d747e1c3ace2fde4c658a162217c17ff24` |
| `depois.jsonl` | As 300 runs do `d3105edc`. 396.384 bytes, sha256 `02ddfa8ef0c836c5ce06c2c896cd81fb161e8172d178105216e1c938a357894d` |
| `run_auditoria.py` | O coletor, idêntico ao de `4d0a9a0a` |
| `agrega_auditoria.py` | O agregador de `4d0a9a0a`, mais o nível 1 ao entrar no andar 2 e o nível por andar |

```
python baselines/progression/d3105edc/agrega_auditoria.py
```

Protocolo: o mesmo das réguas anteriores.
- 300 runs, seeds 1–100 × 3 classes;
- BotPadrão conservador e congelado;
- Starter Kit real;
- teto de 200 andares;
- um processo por run.

---

## Resultado — as três classes (n = 300)

| Métrica | antes (`4d0a9a0a`) | depois (`d3105edc`) |
|---|---:|---:|
| **Nível 1 ao entrar no andar 2** | 178/266 | **103/268** |
| Mortes / extrações | 248 / 52 | 227 / 73 |
| Andar médio · mediana · P90 · máx | 7,74 · 5 · 21 · 26 | 9,18 · 6 · 22 · 28 |
| Morte no andar 1 / até 3 / até 5 | 34 / 93 / 165 | 32 / 85 / 145 |
| Das mortes, fração até o andar 5 | 67% | 64% |
| Chegou ao 10 / ao 20 | 77 / 46 | 94 / 67 |
| Morte na 1ª luta do andar 1 com HP cheio | 4 | 4 |
| Atraso ao entrar no andar 5 · 10 · 15 (média) | 1,38 · 1,00 · −0,44 | 1,08 · 0,47 · −0,39 |
| Maior atraso da run (mediana · P90 · máx) | 1 · 4 · 11 | 1 · 4 · 14 |
| Caíram 3+ atrás · voltaram a ≤ 1 | 79 · 3 | 63 · 0 |
| Caíram 2+ atrás · voltaram a ≤ 1 | 139 · 19 | 102 · 8 |
| Chegou ao 10 com nível ≤ 5 (extraíram) | 7 (0) | 11 (0) |
| Mortes sublevel | 178 | 142 |
| Combates por run | 33,1 | 43,8 |
| Poções bebidas no mapa · runs que nunca tiveram uma | 523 · 133 | 577 · 121 |

### Nível ao entrar no andar (n · P25 · mediana · P75)

| Andar | antes | depois |
|---|---|---|
| 2 | 266 · 1 · 1 · 2 | 268 · 1 · 2 · 2 |
| 3 | 230 · 1 · 2 · 2 | 237 · 2 · 2 · 3 |
| 5 | 169 · 3 · 4 · 5 | 185 · 3 · 4 · 5 |
| 8 | 93 · 6 · 7 · 8 | 120 · 6 · 8 · 8 |
| 10 | 77 · 8 · 10 · 10 | 94 · 10 · 10 · 11 |
| 15 | 55 · 15 · 16 · 16 | 77 · 15 · 16 · 16 |
| 20 | 46 · 21 · 21 · 21 | 67 · 21 · 21 · 22 |

### Por classe

| Métrica | Warrior | Mage | Rogue |
|---|---:|---:|---:|
| Mortes / extrações | 79/21 → 74/26 | 81/19 → 68/32 | 88/12 → 85/15 |
| Andar médio | 9,26 → 10,25 | 7,79 → 10,10 | 6,18 → 7,19 |
| Morte até o andar 5 | 43 → 34 | 55 → 49 | 67 → 62 |
| Chegou ao 10 / ao 20 | 34/21 → 37/25 | 25/17 → 36/26 | 18/8 → 21/16 |
| Nível 1 ao entrar no andar 2 | 61/90 → 35/90 | 56/90 → 29/93 | 61/86 → 39/85 |
| Atraso no andar 5 · 10 | 1,28 · 1,18 → 1,17 · 0,95 | 1,32 · 1,12 → 0,92 · 0,22 | 1,62 · 0,50 → 1,14 · 0,05 |

---

## Leitura

**A largada melhorou.**
- Entrar no andar 2 ainda no nível 1: 67% → 38%.
- Mortes até o andar 5: 165 → 145.
- A fração das mortes até o andar 5 continua perto de dois terços (67% → 64%).
  Ela fica como característica da dificuldade, por decisão do usuário.

**O comportamento profundo ficou o de antes.**
- Quem chega aos andares 15 e 20 chega no mesmo nível (mediana 16 e 21).
- O herói continua atrás do andar nos andares 5 e 10, como a curva prevê, sem
  inversão.
- O que cresceu foi quantas runs chegam lá:
  - chegaram ao 20: 46 → 67;
  - extrações: 52 → 73 (17% → 24%).
- O máximo foi de 26 para 28.

**Nenhuma classe disparou.** O Mage foi quem mais ganhou (andar médio +2,3). A
distância entre a melhor e a pior classe na jornada real ficou em 3,1 andares,
igual a antes.

**Recuperar de muito atrás continua raro** (0 de 63 runs que caíram 3+ níveis).
Por decisão do usuário, isso é característica de alto risco da progressão.

**Determinismo.**
- 17 runs reexecutadas em processos novos saíram idênticas campo a campo:
  - as 6 fixtures da primeira luta;
  - os casos históricos;
  - 6 extrações.

---

## O `-m balance`

O `-m balance` do `d3105edc` deu 114 passed e 4 falhas, todas nas três bandas de
dificuldade global já liberadas:

| Teste | Banda | Observado | Antes | Agora |
|---|---|---|---|---|
| `test_nenhuma_classe_domina_nem_e_inutil` | `MAX_CLASS_MEAN_FLOOR` | W 16,05 | 16,0 | 17,5 |
| `test_chegar_ao_20_e_conquista_mas_e_possivel` | `MAX_SMART_REACH_20` | W 0,728 · M 0,664 · R 0,772 | 0,72 | 0,85 |
| `test_a_curva_cai_de_verdade[Rogue]` | `MIN_TOTAL_ATTRITION` | R 0,212 | 0,25 | 0,15 |
| `test_reduzir_a_sorte_nao_mudou_o_ritmo_do_jogo` | `MAX_CLASS_MEAN_FLOOR` | W 16,05 | 16,0 | 17,5 |

Nenhuma outra banda falhou, inclusive `MAX_GREEDY_REACH_20`.

As três foram atualizadas em `tests/balance/thresholds.py` com os valores
observados nesse `-m balance`.

**O `-m balance` não foi rodado de novo depois da atualização.** Por regra do
usuário, nenhuma simulação grande roda sem uma pergunta nova que exija
estatística.
- Os 4 testes acima são determinísticos (seed 1337, código de jogo inalterado) e
  passam com os valores novos por construção.
- O que **não** foi verificado é a asserção de spread entre classes (≤ 4,0, a
  paridade). Ela fica no mesmo teste da primeira linha e não chegou a rodar,
  porque a asserção anterior falhou.
