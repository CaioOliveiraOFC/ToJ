# BASELINE OFICIAL PRE-BALANCE — 3.000 runs

Este é o retrato congelado do jogo **antes** do Balanceamento Global. Existe para
que a rodada seguinte tenha contra o que comparar: sem um "antes" medido, todo
"depois" é opinião.

---

## Parâmetros da execução

| | |
|---|---|
| **Commit que gerou a baseline** | `88190c5f230163718ff1b287bb97ef035f134964` |
| | `88190c5f — Runway em andares e quatro bandas de poder` |
| **Branch de origem** | `audit/new-loop` |
| **Faixa de seeds** | `20260000` a `20260999` (1.000 seeds, fim exclusivo `20261000`) |
| **Classes** | `warrior`, `mage`, `rogue` — **mesma faixa de seeds para as três** |
| **Runs** | 1.000 × 3 = **3.000** |
| **`max_andar`** | 20 |
| **Paralelismo** | 4 shards: `[0,250) [250,500) [500,750) [750,1000)` sobre a faixa |
| **Persistência** | JSONL incremental, uma linha por registro, `buffering=1` |
| **Tempo de parede** | ~1h45 (shards de 4.110 s a 6.186 s) |
| **Exceções** | 0 |
| **Regras de gameplay alteradas durante a coleta** | 0 |
| **Coletor** | `tools/baseline_pre_balance.py` |
| **Agregador** | `tools/baseline_agrega.py` |
| **Agregados** | `reports/baseline_pre_balance_agregados.json` |

### Por que o JSONL bruto não está no Git

A run é **determinística por seed** (`random.seed(seed)` + `random.Random(seed)`),
e isso foi verificado: re-executar as seeds `20260000-20260001` reproduziu as 9
linhas originais **byte a byte**. Com o coletor versionado, o SHA acima e a faixa
de seeds, os 12 MB de bruto (1,2 MB comprimidos) são regeneráveis exatamente:

```
python tools/baseline_pre_balance.py --inicio 20260000 --fim 20261000 --saida bl.jsonl
python tools/baseline_agrega.py 'bl*.jsonl'
```

Versionar bytes que um comando reproduz seria pagar histórico permanente por
conveniência. O que **não** é reproduzível é o número depois que o conteúdo
mudar — e é por isso que os agregados vão para o Git, em JSON diffável.

### O que o coletor observa

Quatro pontos de escuta no `BotPadrao`, todos passivos, nenhum consumindo sorteio:

| ponto | captura |
|---|---|
| `_decidir_no_mapa` | matriz build × runway, por avaliação e por oportunidade única |
| `_escolher_do_nivel` | o que o nível **ofereceu** e o que foi **escolhido**, lido por diferença do estado do herói — nunca reinvocando o picker |
| `_decidir_no_combate` | qual skill o cérebro escolheu no turno |
| `Observador` (subclasse) | o que a skill fez: usos, dano, MP, cura, status |

`overall_power` aparece **apenas quando já foi medido de graça**: o
`poder_relativo` que o portão de extração pagou durante a run, e o cache de
`sim.arena` consultado no fim. Nenhuma medição foi forçada — 21,0% das runs têm
poder medido.

**Telemetria separada, como a auditoria exige:** `avaliação` (cada reconsideração
de um `E`) × `oportunidade única` (chave `(seed, classe, andar)`). 1.621
oportunidades para 10.658 avaliações — fator de inflação **6,58×**.

---

## Agregados principais

### 1. Desfecho por classe (Wilson 95%)

| | MORREU | EXTRAIU | CHEGOU AO 20 | vivo no fim |
|---|---|---|---|---|
| warrior | 94,7% [93,1;95,9] | 1,0% [0,5;1,8] | 5,0% [3,8;6,5] | **5,3%** |
| mage | 97,7% [96,6;98,5] | 0,7% [0,3;1,4] | 2,1% [1,4;3,2] | **2,3%** |
| rogue | 90,0% [88,0;91,7] | 2,7% [1,9;3,9] | 9,3% [7,7;11,3] | **10,0%** |
| **todas** | **94,1%** | **1,5%** (44) | **5,5%** (164) | **5,9%** (176) |

176 sobreviventes = 132 que chegaram ao andar 20 sem extrair + 44 que extraíram
(32 no andar 20, 10 no 19, 2 no 18). Os intervalos não se sobrepõem em nenhum par
de classes.

### 2. Andar final e nível

| | p25 | p50 | p75 | p90 | max |
|---|---|---|---|---|---|
| andar warrior | 1 | 3 | 5 | 9 | 20 |
| andar mage | 1 | 2 | 4 | 7 | 20 |
| andar rogue | 2 | 3 | 5 | **18** | 20 |
| nível (todas) | 1 | 2 | 3 | 6 | 26 |

**A run mediana morre no andar 3, no nível 2.** 48,0% [46,2;49,8] morrem no
andar 1 ou 2.

**Mortalidade condicional** (entrou no andar × morreu nele) — a curva é
**decrescente** depois do andar 6:

```
 1: 26,0%   6: 23,7%   11:  8,1%   16: 2,2%
 2: 29,7%   7: 15,5%   12:  5,3%   17: 0,6%
 3: 29,8%   8: 14,1%   13:  5,6%   18: 0,6%
 4: 26,8%   9: 14,2%   14:  3,4%   19: 1,1%
 5: 27,2%  10: 10,5%   15:  6,6%   20: 0,0% [0;2,3]
```

### 3. Matriz 4×3 de extração

**Primeira avaliação (1.621 oportunidades) — 5 de 12 células ocupadas:**

| | SAUDÁVEL | CURTO | ESGOTADO |
|---|---|---|---|
| ABAIXO | cont 0/1053 | cont 0/490 | — |
| CLOSE_ENOUGH | cont 0/42 | — | — |
| META_BATIDA | cont 0/23 | — | — |
| HARD_STOP | **PRES 13/13** | — | — |

**Todas as avaliações (10.658) — 6 de 12 ocupadas.** Duas células produziram
PRESERVAR: `(HARD_STOP, SAUDÁVEL)` **38/38** e `(CLOSE_ENOUGH, CURTO)` **6/6**.
Nenhuma célula misto: onde a matriz dispara, dispara 100% das vezes.

- **`ESGOTADO`: 0 de 10.658 avaliações.** Zero `runway == 0.0` também.
- `SEM_EVIDENCIA`: 0. `NAO_MEDIDO`: 0.
- Nas oportunidades que extraíram, a banda **mudou entre a primeira avaliação e a
  vencedora em 68,2% [53,4;80,0]** dos casos.

### 4. Poder e runway

**Poder relativo** (régua `overall_power` V2, benchmark ARENA V2,
`PODER_ESPERADO = 29.5205078125`):

| | p10 | p50 | p90 | max |
|---|---|---|---|---|
| warrior | 0,227 | 0,548 | 0,938 | 1,074 |
| mage | 0,190 | 0,466 | 0,931 | 1,078 |
| rogue | 0,283 | 0,626 | 0,953 | **1,223** |

**No andar 20 (373 avaliações): p50 = 0,992, e 48,0% [43,0;53,1] atingem ≥ 1,00.**
A régua está centrada onde deveria — o benchmark saiu da mediana de sobreviventes
do andar 20, e as chegadas ao andar 20 pousam em 0,99. Isso valida a régua, não o
balanceamento.

**Runway em andares** (unidade nova: andares adicionais sustentados, sem divisão
por `mapa.andar`) — mediana geral 1,30, **subindo** com a profundidade:

| faixa | p50 runway | SAUDÁVEL na 1ª aval |
|---|---|---|
| 3–6 | 0,94 | 57% |
| 7–10 | 1,18 | 66% |
| 11–14 | 1,38 | 79% |
| 15–20 | **1,55** | **92%** |

> **Ressalva:** condicionado à sobrevivência. Só quem chega ao andar 15 gera
> avaliação lá. Parte da subida é seleção, não descompressão. O que a mudança do
> commit `88190c5f` garante é que a métrica não cai mais *por construção* — o
> teste F amarra isso.

### 5. Extração por faixa

| faixa | oport | PRESERVA na 1ª | extraiu de fato |
|---|---|---|---|
| 3–6 | 640 | 0,0% [0;0,6] | 0 |
| 7–10 | 386 | 0,0% [0;1,0] | 0 |
| 11–14 | 269 | 0,0% [0;1,4] | 0 |
| 15–17 | 171 | 0,0% [0;2,2] | 0 |
| 18–20 | 155 | **8,4% [5,0;13,8]** | **44** |

**Nos andares 3–14 há 1.295 oportunidades e PRESERVAR aparece em 0.**

### 6. Skills — o picker e o combate discordam

Ordem do picker (`survival`): `heal > damage_reduction > buff > status > damage`.

| effect_type | slots no deck | % dos slots | turnos de uso | % dos turnos |
|---|---|---|---|---|
| damage | 3739 | **80,4%** | 71.516 | **99,5%** |
| buff | 327 | 7,0% | 75 | 0,1% |
| heal | 268 | 5,8% | 100 | 0,1% |
| damage_reduction | 213 | 4,6% | 72 | 0,1% |
| status | 106 | 2,3% | 100 | 0,1% |

- Das **1.666 skills adquiridas** (fora a inicial de classe), apenas
  **47,5% [45,1;49,9] foram acionadas uma vez sequer**.
- **56,6% de todo o dano de skill vem das 3 skills iniciais de classe.**
- 99,6% das runs terminam com a skill inicial ainda no deck.
- 57 skills entraram em decks e **nunca foram pressionadas**.

Os 5 `effect_type` de skill estão **todos** na ordem do picker — aqui a captura
mede uma decisão real.

### 7. Passivas — ressalva obrigatória

O catálogo tem 60 passivas em 23 `effect_type`. `PASSIVE_PRIORITIES["survival"]`
ordena 13. Os outros 10 estão em `PASSIVE_SEM_PREFERENCIA` (tier NEUTRA) e cobrem
**23 das 60 cartas (38%)**. `pick_passive` só alcança uma carta neutra quando **as
três** da oferta são neutras.

> **Captura de passiva não mede força de carta.** `Sangue de Vidente` 0/740 é
> `magic`, um tipo neutro: o zero é comportamento documentado do picker, não
> veredito sobre a carta. E as 5 cartas "dominantes" (`Bênção Divina` 110/110,
> `Alma Eterna` 120/121, `Essência Fluída` 372/382, `Sangue de Guerreiro`
> 719/757, `Coração de Ferro` 648/733) são **todas `max_hp`**, o primeiro item da
> ordem. É a ordem do picker aparecendo no espelho.
>
> **Estas duas listas não devem alimentar decisão de balanceamento no estado
> atual.**

### 8. Equipamento

Ocupação por slot: 8,5%–29,4% no geral, **97%–100% entre os sobreviventes**.

**`Accessory`: 0/3000, inclusive 0/176 sobreviventes** — e **nenhum item do
catálogo declara `slot == "Accessory"`**. O slot existe em
`EQUIPMENT_POSITIONS` e é inalcançável por construção. Não é falha do bot.

- `+N == 0` em 83,3% das runs; `gemas == 0` em 90,9%; `encantos == 0` em 95,8%.
- Raridade equipada: Common 3151, Rare 1781, Epic 339, Legendary 88.
  Entre sobreviventes a ordem inverte: Rare 925 > Common 577.

### 9. Diferenças entre as classes

| mediana | warrior | mage | rogue |
|---|---|---|---|
| hp max | 493 | 414 | 414 |
| mp max | 67 | 157 | 101 |
| ouro final | 63 | 45 | 78 |
| dano dado | 1470 | 1017 | 1911 |
| fugas na ficha | 0 | **1** | 0 |

Verbos de combate: warrior `skill 53,2% / attack 41,7% / flee 4,8%`; mage
`skill 54,6% / attack 36,3% / **flee 8,8%**`; rogue
`**attack 48,9%** / skill 48,3% / flee 2,5%`.

Concentração ofensiva: `Golpe Poderoso` = 72,9% dos turnos de skill do warrior,
`Bola de Fogo` = 72,4% do mage, `Ataque Furtivo` = 63,5% do rogue.

### 10. Morte

`Lich Aprendiz`, `Anomalia Arcana`, `Necromante`, `Aparição`, `Cultista` lideram
nas três classes.

- **33,6% [31,9;35,4] das mortes são contra monstro de nível ≤ o do herói.**
- 18,4% das mortes começam com HP ≥ 80%; só 13,4% com HP ≤ 40%.
- A luta fatal dura 5 turnos (p50), 10 (p90).

### 11. Economia

- Ouro final: mortos p50 **59**; vivos p50 **5.198**.
- **86,4% dos mortos nunca beberam uma poção.** Entre os vivos, 1,7%.
- Apenas 2,8% dos mortos tinham poção de cura no bolso — o problema é não ter.
- Loja em 53,1% das runs, ferreiro em 31,0%, os três eventos em ~7,2–7,7%.

### 12. Cobertura de conteúdo

| | |
|---|---|
| terminou no nível 1 | 41,8% [40,0;43,6] |
| **nunca recebeu oferta de skill** | **64,9% [63,2;66,6]** |
| nunca recebeu oferta de passiva | 41,8% |
| terminou com deck de 1 skill | 64,9% |
| terminou com deck cheio (4) | 7,7% |
| terminou sem nenhuma peça equipada | 39,4% |
| teve alguma oportunidade de extrair | 21,0% |

---

## Corroboração independente: os dois testes `balance` que já falham

`pytest -m balance` fecha em **2 failed, 116 passed**. As duas falhas medem o
jogo por um instrumento **diferente** do desta baseline — `smart_policy` via
`sim.harness`, não o `BotPadrao` — e apontam para as mesmas duas conclusões:

| teste | medido | banda | conclusão |
|---|---|---|---|
| `test_nenhuma_classe_domina_nem_e_inutil` | spread **5,7** andares — Warrior 7,148 / Mage 3,872 / **Rogue 9,576** | `MAX_CLASS_MEAN_FLOOR_SPREAD = 4.0` | Rogue domina, Mage é fraco |
| `test_a_curva_cai_de_verdade[Rogue]` | atrito **41,2%** entre andar 1 e 20 | `MIN_TOTAL_ATTRITION = 0.50` | a curva não cai o suficiente |

**As duas falham de forma idêntica em `master` (`54db0928`) e em `88190c5f`** —
mesmo spread, mesmo `0.412`. Não são regressão dos 33 commits da auditoria: são
dívida de balanceamento que a fase PRE-BALANCE herda e que o Balanceamento Global
existe para resolver. `src/sim/policies.py` ficou 100% intacto durante toda a
auditoria, o que explica por que este instrumento não se moveu.

O comentário de `MIN_TOTAL_ATTRITION` registra a medição de origem — "0.66 no
Guerreiro, 0.79 no Mago, 0.71 no Ladino". O Ladino saiu de 0,71 para 0,412. **Em
que commit isso aconteceu é pergunta aberta**, e não foi investigada aqui para não
misturar arqueologia com a coleta da baseline.

> Estes dois testes são o critério de saída natural do Balanceamento Global: ele
> termina quando eles passam sem que a banda tenha sido afrouxada.

---

## Diagnóstico — o que merece investigação no Balanceamento Global

Em ordem de quanto cada item contamina a medição de tudo o mais. **Nada aqui é
proposta de valor novo** — é o que a estatística aponta como pergunta.

1. **O funil dos andares 1–3 engole o jogo.** Dois terços das 3.000 runs nunca
   tocaram o sistema de progressão. Qualquer ajuste em skill, passiva ou
   equipamento está sendo avaliado por um terço da amostra. Isto vem primeiro,
   porque enquanto estiver assim todo o resto é medido com denominador errado.

2. **A dificuldade é decrescente.** ~30% de mortalidade condicional no andar 3
   contra 0,0% no andar 20. Quem passa do andar 7 praticamente chegou. As curvas
   de ameaça e de poder divergem a favor do herói, e 33,6% das mortes contra
   monstro de nível ≤ ao do herói sugere que a variância no early game pesa mais
   que o nível.

3. **O picker e a política de combate discordam sobre o que é uma skill boa.**
   `heal` é o primeiro da ordem de escolha e responde por 0,1% dos turnos. Isso
   não diz que 96 das 150 cartas são fracas — diz que **o medidor não consegue
   avaliá-las**. Decidir de quem é o defeito antes de mexer em número: da ordem
   do picker, da política de combate, ou das cartas.

4. **Os 10 `effect_type` no tier NEUTRA são um ponto cego, não conteúdo morto.**
   Ver a ressalva da seção 7.

5. **Extrair é mecânica do andar 18+.** 1.295 oportunidades nos andares 3–14 e
   PRESERVAR em 0 [0;0,3]. A pergunta é de design: a extração deve ser uma saída
   disponível durante a run, ou o prêmio de quem já venceu? Hoje é a segunda, por
   consequência aritmética, não por escolha declarada.

6. **`ESGOTADO` é um estado morto — 0 de 10.658.** Ou o corte está no lugar
   errado, ou a condição é inalcançável porque o bot morre antes de chegar nela.

7. **`Accessory` é um slot sem catálogo.** A única "peça morta" que é fato de
   conteúdo e não artefato de medição.

8. **A economia não circula.** Provavelmente sintoma do item 1, não causa
   própria; re-medir **depois** do item 1, não antes.

9. **Mage precisa de investigação própria.** 2,3% contra 10,0% do rogue, com
   intervalos separados. Foge 3,5× mais, tem a única Égide, e ainda assim morre
   mais. Não dá para separar "HP base 414 com a exposição do rogue" de "`Bola de
   Fogo` não compensa o MP" com esta baseline.

### Ressalva metodológica

A comparação vivos × mortos (nível 23 vs 2, 10 peças vs 1, 126 combates vs 5) é
**sobrevivência reversa, não causalidade**. Eles não sobreviveram porque tinham 10
peças; têm 10 peças porque sobreviveram 126 lutas. Essa tabela descreve o estado
terminal e **não serve como alavanca de balanceamento**.
