# Copa Arena 03 v2 — Inteligência Estratégica

Campeão: **fer (W64)**, OP 29,98, Moderado · política sobrevivência. Final: Final — Tenz × fer — 46 rodadas. Na Copa original o campeão foi fer (W64).

Os mesmos 64 Guerreiros extraídos do PvE real da Copa Arena 03, a mesma chave e as mesmas seeds; os dois lados de cada partida conduzidos pela IA estratégica em vez da `PoliticaCopa`. Este relatório compara as duas Copas com a mesma régua e não declara mudança de força real das builds a partir de uma eliminatória — o ranking Bradley-Terry da Copa 03 continua sendo a referência.

## Integridade

- Os mesmos 64 gladiadores publicados em `reports/pvp/copa_03/` — snapshots conferidos pelo `sha256` de `gladiadores.json` antes de cada reconstrução —, com os mesmos IDs, nomes, builds e OP. Nenhuma run PvE, nenhuma extração, nenhum arquivo de `src/` alterado.
- O mesmo sorteio da chave (`sha256("20261025:chave")`) e as mesmas seeds oficiais por posição (`sha256("20261025:fase:índice")`). Só o controlador dos dois lados muda. Da segunda fase em diante os pares dependem de quem venceu, então não são os mesmos.
- Antes da v2, a Copa original foi reproduzida com a `PoliticaCopa` e conferida contra o que está publicado:

  - 63 partidas: ok
  - semente, lados, vencedor, rodadas, HP e golpes de cada partida: ok
  - campeão: ok
  - chave sorteada: ok
  - final_trace.json registro a registro: ok
  - fidelidade e coerência de todas as partidas: ok

- As 63 partidas da v2 jogadas duas vezes (sem e com auditoria): fidelidade e coerência ok em todas; 126 lados medidos. O que a IA simula ao decidir não entra no trace: `ControladorAuditado` devolve as funções canônicas originais enquanto o controlador pensa (`arena_auditoria.fora_do_duelo`).

## A IA, em uma página

`tools/arena_ia_estrategica.py` implementa `DuelController.choose(view)`. Não é lista de prioridade: para cada ação legal ela joga continuações curtas NO PRÓPRIO MOTOR (`Duel.play_round` sobre cópias) e avalia onde cada uma para.

- **Horizonte e orçamento:** 3 rodadas, 10 continuações por ação (20 quando alguém está ao alcance de um golpe letal). As sementes são as mesmas para todas as candidatas, e cada sorteio vem de um fluxo próprio por origem (função do motor, lado, rodada): o golpe do adversário na rodada 1 é o mesmo número em todas as candidatas, e a diferença entre elas não é sorte.
- **Dentro do horizonte** é o motor de verdade: acerto, crítico, status, DoT, controle, buffs, recargas, reserva de MP e iniciativa. A primeira ação é a candidata; depois, uma política base barata (cura quando aperta, senão o maior dano esperado, com o bônus situacional conferido no estado simulado).
- **Depois do horizonte**, uma corrida "quem derruba quem primeiro" com as fórmulas canônicas (`hit_chance`, `crit_chance`, `damage_modifiers`, `_calculate_damage`, `skill_damage_base`, `basic_attack_power`): taxa de dano por oportunidade, DoT e controle dos procs do acerto, roubo de vida, o MP que ainda compra dano ou cura até o fim previsto da luta (ponto fixo por bisseção), temporários pelo que ainda duram e bônus situacional pela fração da luta em que vale. Vira P(vitória) pela normal, com a incerteza do dado e a do modelo (κ de 2.0 a 0.5, ajustado por log-loss em duelos IA × IA).
- **Utilidade:** P(vitória) menos um custo pequeno do tempo que ainda falta para vencer — que só desempata quando a vitória já está decidida. Num impasse (20 rodadas sem que ninguém bata o próprio recorde de HP baixo, ou mais de 60 rodadas) o custo do tempo passa a ser linear e cresce até dominar: a IA larga a cura que só mantém tudo onde está.
- **O que ela sabe:** de si, a própria ficha e o próprio estado (só leitura); do adversário, só a `FighterView` — classe, nível, HP/MP atuais e máximos, nomes de efeitos e buffs — e a história dessas leituras. O adversário é modelado: o herói canônico da classe e do nível com o loadout esperado, os tetos de HP/MP da tela, ofensa e defesa ajustadas pelo dano observado, cartas reveladas pelo custo de MP gasto (catálogo público) e pelos buffs que aparecem pelo nome, e roubo de vida, regeneração e procs inferidos do que a tela mostra. Antes de aparecerem, as cartas dele são supostas iguais às dela (mesma classe).
- **Simultaneidade:** o adversário das simulações escolhe a primeira ação do estado anterior à rodada, igual para todas as candidatas — sem ver a ação candidata.

**O orçamento basta?** Cada variante contra a configuração da Copa, IA × IA em espelho (os 64, lados e duas seeds alternados):

- o dobro de continuações (20 por ação, 40 nos momentos críticos): venceu 51,6% (IC 95% 45,5%–57,6%).
- horizonte de 2 rodadas: venceu 51,6% (IC 95% 45,5%–57,6%).

Nenhuma variante se distingue da configuração da Copa (os intervalos contêm 50%): dobrar as continuações não rende, e encurtar o horizonte também não perde. O que limita a IA no espelho não é o orçamento, é o modelo — do adversário e da corrida depois do horizonte.

## A comparação obrigatória

Original = Copa Arena 03 (`PoliticaCopa`), reproduzida bit a bit; v2 = IA estratégica. As duas medidas pelas mesmas funções.

|  | Original (PoliticaCopa) | v2 (IA estratégica) |
|---|---|---|
| Campeão | fer (W64, OP 29,98) | fer (W64, OP 29,98) |
| Rodadas por partida (média) | 29,06 | 28,29 |
| Rodadas (máximo) | 64 | 105 |
| Rodadas (mínimo) | 10 | 9 |
| Golpes conectados / tentados | 2138 / 2582 (82,8%) | 2481 / 2899 (85,6%) |
| Críticos (por golpe conectado) | 326 (15,2%) | 365 (14,7%) |
| Ações que foram ataque básico | 1300 de 3662 (35,5%) | 1505 de 3564 (42,2%) |
| Maior sequência de básicos (um lado) | 4 | 7 |
| Maior sequência por lado (média) | 1,88 | 2,92 |
| Sequências de 5+ básicos | 0 | 31 |
| Motivo dos básicos | MP insuficiente 70,8%; recarga 16,6%; havia skill legal (escolha do controlador) 12,6% | MP insuficiente 32,1%; recarga 5,0%; havia skill legal (escolha do controlador) 62,9% |
| Rodadas sem skill (lado) / maior trecho | 1397 / 4 | 1558 / 9 |
| Skills usadas (total) | 2362 | 2059 |
| Skills por tipo | buff 443, dano 1402, redução de dano 114, cura 72, status 331 | buff 187, dano 1519, redução de dano 40, cura 189, status 124 |
| MP gasto / disponível | 169.937 / 188.404 (90,2%) | 150.918 / 180.364 (83,7%) |
| MP no fim do duelo (média por lado) | 146,56 | 233,70 |
| Regeneração perdida no teto de MP | 0 MP em 0 rodadas | 268 MP em 14 rodadas |
| Dano de skill por 100 MP | 475,1 | 509,9 |
| Cura além do HP que faltava | 0 de 46.641 (0,0%) | 4.019 de 125.462 (3,2%) |
| Controle em alvo já controlado / status repetido / buff ativo relançado | 0 / 0 / 0 | 0 / 2 / 0 |
| Ações perdidas por controle | 103 | 97 |
| Zebras por OP (venceu o OP menor) | 19 | 27 |

**Primeira fase, os mesmos 32 pares e as mesmas seeds:** 11 dos 32 resultados mudaram com a troca de controlador.

| Partida | Vencia com a PoliticaCopa | Vence com a IA | Rodadas (antes → agora) |
|---|---|---|---|
| fase64-7 | JonVlogs (W58) | Dilera (W05) | 64 → 105 |
| fase64-10 | MeikodRJ (W26) | Tenz (W08) | 36 → 50 |
| fase64-11 | Bisteconee (W49) | alanzoka (W02) | 26 → 14 |
| fase64-15 | babi (W53) | suetam1v4 (W51) | 15 → 24 |
| fase64-18 | bakzera (W30) | furq (W28) | 39 → 25 |
| fase64-21 | xandfps (W20) | PlayHard (W18) | 14 → 14 |
| fase64-23 | YoDa (W33) | casimito (W55) | 12 → 17 |
| fase64-25 | jovirone (W22) | Patriota (W10) | 30 → 27 |
| fase64-26 | yeTz (W39) | dona (W01) | 59 → 51 |
| fase64-28 | Felps (W31) | Hayashii (W45) | 14 → 11 |
| fase64-29 | RazaH (W15) | mount (W25) | 31 → 19 |

## IA × PoliticaCopa em confrontos controlados

- **Espelho** (cada um dos 64 contra si mesmo, IA de um lado e `PoliticaCopa` do outro, lados e duas seeds alternados): a IA venceu 81,6% (IC 95% 76,4%–85,9%) — como p1 102/128, como p2 107/128. Duração média 31,1 rodadas.
- **Cruzado** (os 32 pares da primeira fase, cada gladiador uma vez com a IA e uma vez com a `PoliticaCopa`, lados e seeds alternados): o lado da IA venceu 68,8% (IC 95% 62,8%–74,1%).
- Inconclusivos no limite técnico: 0.

Com a build fixa, o controlador é a única diferença. A IA não foi ajustada para vencer a `PoliticaCopa`: nada nela conhece a política antiga (que ela só consulta para registrar o que a política teria feito), e o único parâmetro ajustado com dados — a incerteza do modelo — foi calibrado em duelos IA × IA.

### Competência medida nos mesmos duelos (espelho)

| Por lado | IA | PoliticaCopa |
|---|---|---|
| Ações que foram básico | 44,7% | 37,0% |
| Maior sequência de básicos (média) | 3,08 | 1,79 |
| Skills por duelo | 17,2 | 19,6 |
| MP gasto / disponível | 83,2% | 88,0% |
| MP no fim do duelo | 244 | 174 |
| Regeneração perdida no teto | 1,6 | 0,0 |
| Dano de skill por 100 MP | 485,0 | 518,7 |
| Cura além do HP que faltava | 6,7% | 0,0% |
| Controle/status/buff redundantes (total) | 11 | 0 |
| Ações perdidas por controle (sofridas) | 0,74 | 0,84 |

Nas 7955 decisões da IA nesses duelos, ela escolheu o mesmo que a `PoliticaCopa` escolheria na mesma visão em 35,2% delas (contando as rodadas em que só o básico era legal).

### As estimativas da IA batem com o que acontece?

Brier 0,194 em 12269 estimativas de P(vitória) da ação escolhida (0,25 é o chute de 50%).

| P estimada | Decisões | P média estimada | Vitórias de fato |
|---|---|---|---|
| 0,0–0,2 | 1717 | 0,11 | 26,4% |
| 0,2–0,4 | 2824 | 0,30 | 72,4% |
| 0,4–0,6 | 2206 | 0,50 | 85,3% |
| 0,6–0,8 | 2146 | 0,70 | 91,1% |
| 0,8–1,0 | 3380 | 0,92 | 95,8% |

A estimativa ordena bem — quanto maior a P que ela dá, mais ela vence —, mas contra a `PoliticaCopa` ela é pessimista: a IA modela o adversário como alguém que gasta o MP tão bem quanto ela e tem um deck como o dela, e a política antiga não joga assim. A incerteza do modelo foi calibrada em duelos IA × IA, onde esse viés é menor.

## A economia de recursos (§2): por que ainda há tanto básico

Nos 64, o MP máximo médio é 798, a regeneração média 21,2 por turno (2% do teto mais passivas e equipamento) e o custo médio de uma carta 79,9. O caixa inicial paga cerca de 10,2 cartas; depois dele, a regeneração paga uma carta a cada 4,2 rodadas. Numa luta de 30 rodadas isso dá, no máximo, perto de 17 cartas por lado — o resto é básico, faça o controlador o que fizer. Nenhum custo, regeneração ou regra foi mudado.

Motivo de cada ataque básico, lido da visão e da ficha de quem atacou:

| Motivo | Original (PoliticaCopa) | v2 (IA) |
|---|---|---|
| MP insuficiente | 920 (70,8%) | 483 (32,1%) |
| recarga | 216 (16,6%) | 76 (5,0%) |
| requisito de equipamento | 0 (0,0%) | 0 (0,0%) |
| havia skill legal (escolha do controlador) | 164 (12,6%) | 946 (62,9%) |

"Havia skill legal" é a escolha do controlador: na `PoliticaCopa`, nenhuma regra dela pedia carta (buff ativo, status já no alvo, nenhuma carta de dano legal); na IA, a avaliação preferiu o básico. Os básicos da IA com carta legal na mão, pelos números dela no momento:

| Por quê | Básicos |
|---|---|
| as opções valiam o mesmo (diferença de utilidade abaixo de 0,002) | 367 (38,8%) |
| guardou MP e curou nas 5 rodadas seguintes | 100 (10,6%) |
| o básico valia mais que qualquer carta legal | 479 (50,6%) |

Quando o básico valia mais, a melhor carta legal que ficou na mão era: dano (221), buff (128), status (107), cura (13), redução de dano (10). Com carta de dano, é o MP guardado para algo que rende mais depois — a cura, a carta condicional, a recarga da melhor carta —, ou o alvo que o básico já derruba.

No empate as opções valiam o mesmo para o modelo — o MP guardado compra a mesma coisa depois —, e o básico vem primeiro na lista de ações legais. Um desempate a favor de gastar mudaria o número de básicos sem mudar o valor das decisões; ele não foi feito, para não otimizar a métrica no lugar da luta.

**Impasse entre builds de sustento.** Entre builds com cura de 10–12% do HP, roubo de vida e redução de dano, a cura por MP rende cerca de quatro vezes o dano por MP (no espelho de W05: 852 de HP por 74 MP contra cerca de 2,8 de dano extra por MP nas cartas de dano), e a recarga da cura sustenta mais HP por rodada do que o básico do outro tira. Com as duas IAs curando bem, os espelhos de W05 e W23 chegavam a 500 rodadas — o limite técnico, sem vencedor. É uma propriedade da economia, não da IA, e a regra não foi tocada: a IA ganhou a urgência de impasse descrita acima, e esses espelhos passaram a terminar.

## Desempenho por tipo de build

Na Copa: vitórias sobre partidas disputadas. Num mata-mata cada derrota elimina, então os números são pequenos e dependem da chave — por isso a coluna dos confrontos controlados, que mede o quanto a MESMA build rende a mais com a IA do que com a `PoliticaCopa`, lado e seed alternados.

| Build | Gladiadores | Copa original | Copa v2 | Fase média alcançada | Espelho: IA vence a PoliticaCopa |
|---|---|---|---|---|---|
| controle | 19 | 11/30 (36,7%) | 11/30 (36,7%) | 1,05 → 0,95 | 78,9% (IC 95% 68,5%–86,6%) |
| crítico | 18 | 14/32 (43,8%) | 14/32 (43,8%) | 1,17 → 1,11 | 80,6% (IC 95% 70,0%–88,0%) |
| defesa | 26 | 21/46 (45,7%) | 28/53 (52,8%) | 1,23 → 1,65 | 84,6% (IC 95% 76,5%–90,3%) |
| sustento | 40 | 46/85 (54,1%) | 45/84 (53,6%) | 1,68 → 1,68 | 85,0% (IC 95% 78,7%–89,7%) |
| política ofensiva | 21 | 13/34 (38,2%) | 13/34 (38,2%) | 1,05 → 0,95 | — |
| política sobrevivência | 22 | 24/45 (53,3%) | 30/51 (58,8%) | 1,45 → 2,00 | — |
| política economia | 21 | 26/47 (55,3%) | 20/41 (48,8%) | 1,95 → 1,48 | — |

Fase média alcançada: 0 = caiu na fase de 64, 6 = campeão.

**Controle, crítico e política ofensiva.**

- **Controle** (19 builds): No todos contra todos com a `PoliticaCopa`, essas builds rendiam 11,2 pontos percentuais abaixo do que o OP previa. Na Copa v2 venceram 11 de 30 partidas (36,7%; eram 36,7%) e a fase média foi de 1,05 para 0,95. Com a build fixa, a IA vence a `PoliticaCopa` em 78,9% dos espelhos dessas builds (81,6% no geral) e em 64,5% dos cruzados: o ganho do controlador nelas é igual ao geral.
- **Crítico** (18 builds): No todos contra todos com a `PoliticaCopa`, essas builds rendiam 6,1 pontos percentuais abaixo do que o OP previa. Na Copa v2 venceram 14 de 32 partidas (43,8%; eram 43,8%) e a fase média foi de 1,17 para 1,11. Com a build fixa, a IA vence a `PoliticaCopa` em 80,6% dos espelhos dessas builds (81,6% no geral) e em 65,3% dos cruzados: o ganho do controlador nelas é igual ao geral.
- **Política ofensiva** (21 builds geradas com a agenda de risco ofensiva): No todos contra todos, 11,8 pontos abaixo do previsto pelo OP. Na Copa v2, 13 de 34 (38,2%; eram 38,2%), fase média 1,05 → 0,95.

Uma parte do resíduo negativo de controle e de política ofensiva no todos contra todos vinha da `PoliticaCopa`, que lança todo status antes do dano. Os espelhos isolam o controlador e mostram quanto a mesma build ganha com a IA; a Copa, sozinha, não separa isso da chave. Para afirmar que essas builds ficaram mais fortes, seria preciso um novo todos contra todos com a IA — que não foi feito aqui.

## O ranking Bradley-Terry original, como referência histórica

O todos contra todos da Copa 03 (`round_robin.json`, `PoliticaCopa` nos dois lados) segue sendo a medida de força das builds. Uma eliminatória de 63 partidas, uma seed cada, não mede força: aqui ela só mostra onde a troca de controlador mudou caminhos.

- Copa original: campeão fer (W64), 1º no Bradley-Terry; posição média dos que chegaram às quartas: 13,7.
- Copa v2: campeão fer (W64), 1º no Bradley-Terry; posição média dos que chegaram às quartas: 15,8.

## Três lutas em detalhe

### Final — Tenz × fer

Tenz (W08), OP 28,71, contra fer (W64), OP 29,98. Seed 6619800792897972838. Venceu fer (W64) em 46 rodadas, com 2232 de 5977 de HP.
Na Copa original, a mesma posição era lubatv (W23) × fer (W64): venceu fer (W64) em 37 rodadas.

**Momentos decisivos**

- Maior mudança na estimativa de fer: +0,14 na rodada 18 (P(vitória) 0,43 → 0,56).
- Maior crítico: Tenz, 620 de dano com Soco de Placa na rodada 37.
- Golpe final: fer, Ataque básico, 258 de dano na rodada 46 (crítico).
- Curas: Tenz 8, fer 3.
- A iniciativa trocou de mãos 0 vez(es).

**Rodada a rodada** (P = a estimativa de vitória da IA para a ação que ela escolheu; Init = Initiative Score lido no início da rodada):

| Rod. | Age primeiro | Tenz: ação | HP / MP | fer: ação | HP / MP |
|---|---|---|---|---|---|
| 1 | fer | Golpe Poderoso · 0 dano · P 0,40 · Init 1,022 | 5046 / 998 | Golpe Poderoso · 473 dano · P 0,48 · Init 1,059 | 5977 / 1051 |
| 2 | fer | Tomar Fôlego · 0 dano · P 0,29 · Init 1,022 | 5420 / 926 | Soco de Placa · 288 dano · P 0,56 · Init 1,059 | 5977 / 1012 |
| 3 | fer | Ataque básico · 0 dano · P 0,25 · Init 1,022 | 5125 / 947 | Golpe Poderoso · 295 dano · P 0,57 · Init 1,059 | 5977 / 982 |
| 4 | fer | Golpe Poderoso · 331 dano · P 0,20 · Init 1,022 | 5033 / 916 | Ataque básico · 161 dano · P 0,52 · Init 1,059 | 5646 / 1004 |
| 5 | fer | Soco de Placa · 0 dano · P 0,20 · Init 1,022 | 4572 / 876 | Soco de Placa · 461 dano · P 0,48 · Init 1,059 | 5705 / 965 |
| 6 | fer | Golpe Poderoso · 331 dano · P 0,17 · Init 1,022 | 4346 / 845 | Golpe Poderoso · 295 dano · P 0,59 · Init 1,059 | 5412 / 935 |
| 7 | fer | Tomar Fôlego · 0 dano · P 0,17 · Init 1,022 | 4547 / 773 | Soco de Placa · 461 dano · P 0,55 · Init 1,059 | 5471 / 896 |
| 8 | fer | Golpe Poderoso · 331 dano · P 0,16 · Init 1,022 | 4321 / 742 | Golpe Poderoso · 295 dano · P 0,54 · Init 1,059 | 5178 / 866 |
| 9 | fer | Ataque básico · 179 dano · P 0,16 · Init 1,022 | 4070 / 763 | Soco de Placa · 288 dano · P 0,51 · Init 1,059 | 5036 / 827 |
| 10 | fer | Golpe Poderoso · 529 dano · P 0,15 · Init 1,022 | 3908 / 732 | Golpe Poderoso · 273 dano · P 0,46 · Init 1,059 | 4542 / 797 |
| 11 | fer | Soco de Placa · 323 dano · P 0,19 · Init 1,022 | 3717 / 692 | Ataque básico · 258 dano · P 0,40 · Init 1,059 | 4252 / 819 |
| 12 | fer | Golpe Poderoso · 306 dano · P 0,20 · Init 1,022 | 3493 / 661 | Soco de Placa · 288 dano · P 0,43 · Init 1,059 | 3983 / 780 |
| 13 | fer | Tomar Fôlego · 0 dano · P 0,18 · Init 1,022 | 3717 / 589 | Golpe Poderoso · 438 dano · P 0,38 · Init 1,059 | 4039 / 750 |
| 14 | fer | Ataque básico · 148 dano · P 0,18 · Init 1,022 | 3460 / 610 | Soco de Placa · 288 dano · P 0,36 · Init 1,059 | 3928 / 711 |
| 15 | fer | Golpe Poderoso · 306 dano · P 0,17 · Init 1,003 | 3086 / 579 | Golpe Poderoso · 438 dano · P 0,37 · Init 1,059 | 3678 / 681 |
| 16 | fer | Gancho e Corda · 0 dano · P 0,15 · Init 1,022 | 2798 / 483 | Soco de Placa · 288 dano · P 0,47 · Init 1,059 | 3715 / 642 |
| 17 | fer | Golpe Poderoso · 0 dano · P 0,17 · Init 1,003 | 2798 / 452 | Ataque básico (cancelled_control) · 0 dano · P 0,43 · Init 1,059 | 3715 / 664 |
| 18 | fer | Tomar Fôlego · 0 dano · P 0,13 · Init 1,022 | 3299 / 380 | Ataque básico · 161 dano · P 0,56 · Init 1,059 | 3735 / 686 |
| 19 | fer | Ataque básico · 288 dano · P 0,14 · Init 1,022 | 2898 / 401 | Soco de Placa · 461 dano · P 0,48 · Init 1,059 | 3506 / 647 |
| 20 | fer | Soco de Placa · 323 dano · P 0,15 · Init 1,022 | 2527 / 361 | Golpe Poderoso · 438 dano · P 0,55 · Init 1,059 | 3239 / 617 |
| 21 | fer | Ataque básico · 179 dano · P 0,13 · Init 1,022 | 2564 / 382 | Respirar Fundo · 0 dano · P 0,58 · Init 1,059 | 3657 / 557 |
| 22 | fer | Soco de Placa · 323 dano · P 0,12 · Init 1,022 | 2470 / 342 | Ataque básico · 161 dano · P 0,62 · Init 1,059 | 3354 / 579 |
| 23 | fer | Tomar Fôlego · 0 dano · P 0,13 · Init 1,022 | 2999 / 270 | Ataque básico · 133 dano · P 0,58 · Init 1,039 | 3371 / 601 |
| 24 | fer | Ataque básico · 179 dano · P 0,15 · Init 1,022 | 2778 / 291 | Ataque básico · 258 dano · P 0,48 · Init 1,039 | 3225 / 623 |
| 25 | fer | Soco de Placa · 323 dano · P 0,14 · Init 1,022 | 2684 / 251 | Ataque básico · 161 dano · P 0,56 · Init 1,059 | 2922 / 645 |
| 26 | fer | Golpe Poderoso · 306 dano · P 0,13 · Init 1,022 | 2748 / 220 | Respirar Fundo · 0 dano · P 0,58 · Init 1,059 | 3213 / 585 |
| 27 | fer | Soco de Placa · 0 dano · P 0,13 · Init 1,022 | 2475 / 180 | Golpe Poderoso · 273 dano · P 0,57 · Init 1,059 | 3248 / 555 |
| 28 | fer | Tomar Fôlego · 0 dano · P 0,11 · Init 1,022 | 2849 / 108 | Soco de Placa · 288 dano · P 0,63 · Init 1,059 | 3285 / 516 |
| 29 | fer | Ataque básico · 179 dano · P 0,12 · Init 1,022 | 2613 / 129 | Golpe Poderoso · 273 dano · P 0,54 · Init 1,059 | 3141 / 486 |
| 30 | fer | Soco de Placa · 0 dano · P 0,11 · Init 1,022 | 2325 / 89 | Soco de Placa · 288 dano · P 0,55 · Init 1,059 | 3178 / 447 |
| 31 | fer | Ataque básico · 0 dano · P 0,09 · Init 1,022 | 2052 / 110 | Golpe Poderoso · 273 dano · P 0,62 · Init 1,059 | 3213 / 417 |
| 32 | fer | Ataque básico · 179 dano · P 0,09 · Init 1,022 | 1801 / 131 | Soco de Placa · 288 dano · P 0,67 · Init 1,059 | 3071 / 378 |
| 33 | fer | Tomar Fôlego · 0 dano · P 0,09 · Init 1,022 | 2302 / 59 | Ataque básico · 161 dano · P 0,68 · Init 1,059 | 3091 / 400 |
| 34 | fer | Golpe Poderoso · 306 dano · P 0,10 · Init 1,022 | 1928 / 28 | Golpe Poderoso · 438 dano · P 0,62 · Init 1,059 | 2841 / 370 |
| 35 | fer | Ataque básico · 0 dano · P — · Init 1,022 | 1640 / 49 | Soco de Placa · 288 dano · P 0,69 · Init 1,059 | 2878 / 331 |
| 36 | fer | Ataque básico · 179 dano · P — · Init 1,003 | 1404 / 70 | Golpe Poderoso · 273 dano · P 0,73 · Init 1,059 | 2734 / 301 |
| 37 | fer | Soco de Placa · 620 dano · P 0,07 · Init 1,022 | 1534 / 30 | Respirar Fundo · 0 dano · P 0,77 · Init 1,059 | 2711 / 241 |
| 38 | fer | Ataque básico · 0 dano · P — · Init 1,022 | 1096 / 51 | Golpe Poderoso · 438 dano · P 0,80 · Init 1,059 | 2767 / 211 |
| 39 | fer | Ataque básico · 0 dano · P — · Init 1,022 | 808 / 72 | Soco de Placa · 288 dano · P 0,89 · Init 1,059 | 2804 / 172 |
| 40 | fer | Ataque básico · 0 dano · P 0,04 · Init 1,022 | 535 / 93 | Golpe Poderoso · 273 dano · P 0,90 · Init 1,059 | 2839 / 142 |
| 41 | fer | Ataque básico · 288 dano · P 0,03 · Init 1,022 | 307 / 114 | Soco de Placa · 288 dano · P 0,92 · Init 1,059 | 2588 / 103 |
| 42 | fer | Tomar Fôlego · 0 dano · P 0,05 · Init 1,022 | 663 / 42 | Golpe Poderoso · 306 dano · P 0,98 · Init 1,059 | 2644 / 73 |
| 43 | fer | Ataque básico · 179 dano · P — · Init 1,022 | 412 / 63 | Soco de Placa · 288 dano · P 0,95 · Init 1,059 | 2502 / 34 |
| 44 | fer | Ataque básico · 179 dano · P 0,01 · Init 1,022 | 288 / 84 | Ataque básico · 161 dano · P — · Init 1,059 | 2343 / 56 |
| 45 | fer | Ataque básico · 179 dano · P 0,00 · Init 1,022 | 52 / 105 | Golpe Poderoso · 273 dano · P 0,96 · Init 1,059 | 2199 / 26 |
| 46 | fer | Ataque básico (cancelled_death) · 0 dano · P 0,00 · Init 1,022 | -206 / 105 | Ataque básico · 258 dano · P — · Init 1,059 | 2232 / 48 |

**Avaliação das escolhas**

- Rodada 38, fer (HP 2711/5977, MP 241; o outro com HP 1534/5519): escolheu **Golpe Poderoso**. Opções: Golpe Poderoso P 0,803, 52 MP; Soco de Placa P 0,800, 61 MP; ataque básico P 0,794; Juramento da Muralha P 0,657, 152 MP. A `PoliticaCopa` faria Juramento da Muralha (Juramento da Muralha é legal e não está ativo (buffs visíveis: [])).
- Rodada 39, fer (HP 2767/5977, MP 211; o outro com HP 1096/5519): escolheu **Soco de Placa**. Opções: Soco de Placa P 0,892, 61 MP; ataque básico P 0,877; Juramento da Muralha P 0,771, 152 MP. A `PoliticaCopa` faria Juramento da Muralha (Juramento da Muralha é legal e não está ativo (buffs visíveis: [])).
- Rodada 37, fer (HP 2734/5977, MP 301; o outro com HP 1404/5519): escolheu **Respirar Fundo**. Opções: Respirar Fundo P 0,774, 82 MP; Soco de Placa P 0,747, 61 MP; ataque básico P 0,744; Juramento da Muralha P 0,652, 152 MP. A `PoliticaCopa` faria Respirar Fundo (HP 2734/5977 (45.7%) ≤ 50% e há cura legal: Respirar Fundo).
- Rodada 36, fer (HP 2878/5977, MP 331; o outro com HP 1640/5519): escolheu **Golpe Poderoso**. Opções: Golpe Poderoso P 0,728, 52 MP; ataque básico P 0,712; Respirar Fundo P 0,704, 82 MP; Juramento da Muralha P 0,612, 152 MP. A `PoliticaCopa` faria Respirar Fundo (HP 2878/5977 (48.2%) ≤ 50% e há cura legal: Respirar Fundo).

### Fase de 64 28 — Felps × Hayashii

Felps (W31), OP 29,64, contra Hayashii (W45), OP 27,91. Seed 14407454639189636163. Venceu Hayashii (W45) em 11 rodadas, com 1713 de 4939 de HP.
Na Copa original, a mesma posição era Felps (W31) × Hayashii (W45): venceu Felps (W31) em 14 rodadas.

**Momentos decisivos**

- Maior mudança na estimativa de Hayashii: +0,21 na rodada 7 (P(vitória) 0,60 → 0,81).
- Maior crítico: Felps, 859 de dano com Marca do Açougueiro na rodada 7.
- Golpe final: Hayashii, Golpe Poderoso, 394 de dano na rodada 11.
- A iniciativa trocou de mãos 2 vez(es).

**Rodada a rodada** (P = a estimativa de vitória da IA para a ação que ela escolheu; Init = Initiative Score lido no início da rodada):

| Rod. | Age primeiro | Felps: ação | HP / MP | Hayashii: ação | HP / MP |
|---|---|---|---|---|---|
| 1 | Hayashii | Quebra-Guarda · 774 dano · P 0,46 · Init 1,006 | 3734 / 568 | Golpe Poderoso · 425 dano · P 0,54 · Init 1,031 | 4165 / 851 |
| 2 | Hayashii | Sangue nos Olhos · 0 dano · P 0,54 · Init 1,006 | 3393 / 530 | Ataque básico · 341 dano · P 0,57 · Init 1,031 | 4280 / 868 |
| 3 | Hayashii | Marca do Açougueiro · 576 dano · P 0,56 · Init 1,006 | 3014 / 498 | Golpe Poderoso · 425 dano · P 0,66 · Init 1,031 | 3848 / 838 |
| 4 | Hayashii | Ataque básico · 313 dano · P 0,58 · Init 1,006 | 2812 / 510 | Ataque básico · 227 dano · P 0,75 · Init 1,031 | 3612 / 855 |
| 5 | Hayashii | Quebra-Guarda · 356 dano · P 0,54 · Init 1,006 | 2283 / 472 | Golpe Poderoso · 394 dano · P 0,73 · Init 1,031 | 3389 / 825 |
| 6 | Hayashii | Sangue nos Olhos · 0 dano · P 0,71 · Init 1,006 | 1893 / 434 | Ataque básico · 227 dano · P 0,60 · Init 1,009 | 3195 / 842 |
| 7 | Felps | Marca do Açougueiro · 859 dano · P 0,68 · Init 1,006 | 1370 / 402 | Golpe Poderoso · 591 dano · P 0,81 · Init 0,984 | 2265 / 812 |
| 8 | Felps | Ataque básico · 239 dano · P 0,63 · Init 1,006 | 1162 / 414 | Ataque básico · 227 dano · P 0,77 · Init 0,984 | 2029 / 829 |
| 9 | Hayashii | Quebra-Guarda · 356 dano · P 0,38 · Init 1,006 | 599 / 376 | Golpe Poderoso · 591 dano · P 0,92 · Init 1,009 | 1799 / 799 |
| 10 | Hayashii | Travar o Pulso · 0 dano · P 0,10 · Init 1,006 | 372 / 338 | Ataque básico · 227 dano · P 1,00 · Init 1,009 | 1728 / 816 |
| 11 | Hayashii | Ataque básico (cancelled_death) · 0 dano · P 0,00 · Init 1,006 | -22 / 338 | Golpe Poderoso · 394 dano · P 1,00 · Init 1,009 | 1713 / 786 |

**Avaliação das escolhas**

- Rodada 7, Felps (HP 1893/4098, MP 434; o outro com HP 3195/4939): escolheu **Marca do Açougueiro**. Opções: Marca do Açougueiro P 0,683, 44 MP; ataque básico P 0,582; Travar o Pulso P 0,465, 50 MP. A `PoliticaCopa` faria Travar o Pulso (Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['bleed', 'poison', 'vulnerable', 'vulnerable'])).
- Rodada 8, Felps (HP 1370/4098, MP 402; o outro com HP 2265/4939): escolheu **ataque básico**. Opções: ataque básico P 0,628; Quebra-Guarda P 0,471, 50 MP; Travar o Pulso P 0,431, 50 MP. A `PoliticaCopa` faria Travar o Pulso (Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['poison', 'vulnerable', 'vulnerable'])).
- Rodada 9, Felps (HP 1162/4098, MP 414; o outro com HP 2029/4939): escolheu **Quebra-Guarda**. Opções: Quebra-Guarda P 0,378, 50 MP; ataque básico P 0,315; Travar o Pulso P 0,218, 50 MP. A `PoliticaCopa` faria Travar o Pulso (Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['poison', 'vulnerable'])).
- Rodada 6, Felps (HP 2283/4098, MP 472; o outro com HP 3389/4939): escolheu **Sangue nos Olhos**. Opções: Sangue nos Olhos P 0,708, 50 MP; ataque básico P 0,683; Marca do Açougueiro P 0,581, 44 MP; Travar o Pulso P 0,554, 50 MP. A `PoliticaCopa` faria Travar o Pulso (Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['bleed', 'poison', 'vulnerable'])).

### Fase de 64 7 — Dilera × JonVlogs

Dilera (W05), OP 27,91, contra JonVlogs (W58), OP 28,60. Seed 17893717569376441782. Venceu Dilera (W05) em 105 rodadas, com 469 de 5077 de HP.
Na Copa original, a mesma posição era Dilera (W05) × JonVlogs (W58): venceu JonVlogs (W58) em 64 rodadas.

**Momentos decisivos**

- Maior mudança na estimativa de Dilera: +0,44 na rodada 105 (P(vitória) 0,39 → 0,83).
- Maior crítico: JonVlogs, 254 de dano com Ataque básico na rodada 33.
- Golpe final: Dilera, Investida, 198 de dano na rodada 105.
- Curas: Dilera 18.
- A iniciativa trocou de mãos 2 vez(es).
- A urgência de impasse entrou na rodada 61: a luta já não andava.

**Rodada a rodada** (P = a estimativa de vitória da IA para a ação que ela escolheu; Init = Initiative Score lido no início da rodada):

| Rod. | Age primeiro | Dilera: ação | HP / MP | JonVlogs: ação | HP / MP |
|---|---|---|---|---|---|
| 1 | Dilera | Investida · 242 dano · P 0,35 · Init 1,048 | 4768 / 821 | Golpe Poderoso · 309 dano · P 0,51 · Init 1,043 | 6143 / 661 |
| 2 | Dilera | Couraça Improvisada · 0 dano · P 0,27 · Init 1,048 | 4501 / 793 | Investida · 267 dano · P 0,56 · Init 1,043 | 6204 / 629 |
| 3 | Dilera | Ataque básico (cancelled_control) · 0 dano · P 0,22 · Init 1,048 | 4265 / 821 | Golpe Poderoso · 236 dano · P 0,62 · Init 1,043 | 6258 / 603 |
| 4 | Dilera | Tomar Fôlego · 0 dano · P 0,19 · Init 1,048 | 4727 / 775 | Investida · 350 dano · P 0,65 · Init 1,043 | 6314 / 571 |
| 5 | Dilera | Investida · 242 dano · P 0,16 · Init 1,048 | 4466 / 756 | Golpe Poderoso · 309 dano · P 0,53 · Init 1,043 | 6143 / 545 |
| 6 | Dilera | Golpe Poderoso · 210 dano · P 0,14 · Init 1,048 | 4158 / 742 | Investida · 350 dano · P 0,56 · Init 1,043 | 6013 / 513 |
| 7 | Dilera | Couraça Improvisada · 0 dano · P 0,12 · Init 1,048 | 3922 / 714 | Golpe Poderoso · 236 dano · P 0,57 · Init 1,043 | 6067 / 487 |
| 8 | Dilera | Golpe Poderoso · 210 dano · P 0,11 · Init 1,048 | 3964 / 700 | Investida · 0 dano · P 0,58 · Init 1,043 | 5857 / 455 |
| 9 | Dilera | Tomar Fôlego · 0 dano · P 0,12 · Init 1,048 | 4507 / 654 | Golpe Poderoso · 309 dano · P 0,51 · Init 1,043 | 5928 / 429 |
| 10 | Dilera | Golpe Poderoso · 210 dano · P 0,11 · Init 1,048 | 4199 / 640 | Investida · 350 dano · P 0,47 · Init 1,043 | 5798 / 397 |
| 11 | Dilera | Investida · 242 dano · P 0,10 · Init 1,048 | 3938 / 621 | Golpe Poderoso · 309 dano · P 0,48 · Init 1,043 | 5627 / 371 |
| 12 | Dilera | Couraça Improvisada · 0 dano · P 0,10 · Init 1,048 | 3716 / 593 | Investida · 222 dano · P 0,48 · Init 1,043 | 5678 / 339 |
| 13 | Dilera | Investida · 242 dano · P 0,09 · Init 1,048 | 3764 / 574 | Ataque básico · 0 dano · P 0,49 · Init 1,043 | 5436 / 360 |
| 14 | Dilera | Tomar Fôlego · 0 dano · P 0,15 · Init 1,048 | 4447 / 528 | Ataque básico · 169 dano · P 0,42 · Init 1,043 | 5474 / 381 |
| 15 | Dilera | Investida · 242 dano · P 0,13 · Init 1,048 | 4186 / 509 | Golpe Poderoso · 309 dano · P 0,37 · Init 1,043 | 5303 / 355 |
| 16 | Dilera | Golpe Poderoso · 210 dano · P 0,12 · Init 1,048 | 3878 / 495 | Investida · 350 dano · P 0,40 · Init 1,043 | 5173 / 323 |
| 17 | Dilera | Investida · 242 dano · P 0,11 · Init 1,048 | 3638 / 476 | Golpe Poderoso · 288 dano · P 0,38 · Init 1,043 | 4997 / 297 |
| 18 | Dilera | Golpe Poderoso · 195 dano · P 0,11 · Init 1,048 | 3508 / 462 | Ataque básico · 169 dano · P 0,40 · Init 1,043 | 4840 / 318 |
| 19 | Dilera | Tomar Fôlego · 0 dano · P 0,13 · Init 1,048 | 4010 / 416 | Investida · 350 dano · P 0,38 · Init 1,043 | 4920 / 286 |
| 20 | Dilera | Ataque básico · 114 dano · P 0,13 · Init 1,048 | 3744 / 444 | Golpe Poderoso · 288 dano · P 0,34 · Init 1,043 | 4872 / 260 |
| 21 | Dilera | Investida · 0 dano · P 0,13 · Init 1,048 | 3744 / 425 | Investida · 0 dano · P 0,57 · Init 1,043 | 4872 / 228 |
| 22 | Dilera | Golpe Poderoso · 195 dano · P 0,10 · Init 1,048 | 3495 / 411 | Golpe Poderoso · 288 dano · P 0,44 · Init 1,043 | 4743 / 202 |
| 23 | Dilera | Couraça Improvisada · 0 dano · P 0,10 · Init 1,048 | 3273 / 383 | Investida · 222 dano · P 0,42 · Init 1,043 | 4794 / 170 |
| 24 | Dilera | Tomar Fôlego · 0 dano · P 0,12 · Init 1,048 | 3996 / 337 | Ataque básico · 129 dano · P 0,44 · Init 1,043 | 4823 / 191 |
| 25 | Dilera | Investida · 0 dano · P 0,11 · Init 1,048 | 3996 / 318 | Guarda Alta · 0 dano · P 0,17 · Init 1,043 | 4823 / 155 |
| 26 | JonVlogs | Golpe Poderoso · 161 dano · P 0,09 · Init 1,048 | 3738 / 304 | Investida · 290 dano · P 0,18 · Init 1,068 | 4728 / 123 |
| 27 | JonVlogs | Couraça Improvisada · 0 dano · P 0,09 · Init 1,048 | 3450 / 276 | Golpe Poderoso · 288 dano · P 0,18 · Init 1,068 | 4794 / 97 |
| 28 | JonVlogs | Golpe Poderoso · 161 dano · P 0,10 · Init 1,048 | 3482 / 262 | Guarda Alta · 0 dano · P 0,19 · Init 1,068 | 4633 / 61 |
| 29 | JonVlogs | Tomar Fôlego · 0 dano · P 0,11 · Init 1,048 | 4205 / 216 | Ataque básico · 129 dano · P 0,19 · Init 1,068 | 4662 / 82 |
| 30 | JonVlogs | Golpe Poderoso · 161 dano · P 0,10 · Init 1,048 | 3887 / 202 | Investida · 350 dano · P 0,18 · Init 1,068 | 4581 / 50 |
| 31 | JonVlogs | Investida · 198 dano · P 0,10 · Init 1,048 | 3926 / 183 | Golpe Poderoso · 0 dano · P 0,17 · Init 1,068 | 4383 / 24 |
| 32 | Dilera | Golpe Poderoso · 195 dano · P 0,11 · Init 1,048 | 3796 / 169 | Ataque básico · 169 dano · P — · Init 1,043 | 4226 / 45 |
| 33 | Dilera | Ataque básico · 114 dano · P 0,13 · Init 1,048 | 3564 / 197 | Ataque básico · 254 dano · P — · Init 1,043 | 4170 / 66 |
| 34 | Dilera | Tomar Fôlego · 0 dano · P 0,11 · Init 1,048 | 4066 / 151 | Investida · 350 dano · P 0,21 · Init 1,043 | 4250 / 34 |
| 35 | Dilera | Investida · 198 dano · P 0,12 · Init 1,048 | 3936 / 132 | Ataque básico · 169 dano · P — · Init 1,043 | 4090 / 55 |
| 36 | Dilera | Golpe Poderoso · 195 dano · P 0,13 · Init 1,048 | 3806 / 118 | Ataque básico · 169 dano · P 0,19 · Init 1,043 | 3933 / 76 |
| 37 | Dilera | Ataque básico · 114 dano · P 0,14 · Init 1,048 | 3540 / 146 | Golpe Poderoso · 288 dano · P 0,19 · Init 1,043 | 3885 / 50 |
| 38 | Dilera | Investida · 198 dano · P 0,13 · Init 1,048 | 3410 / 127 | Ataque básico · 169 dano · P — · Init 1,043 | 3725 / 71 |
| 39 | Dilera | Tomar Fôlego · 0 dano · P 0,17 · Init 1,048 | 4093 / 81 | Ataque básico · 169 dano · P 0,23 · Init 1,043 | 3763 / 92 |
| 40 | Dilera | Investida · 198 dano · P 0,15 · Init 1,048 | 3782 / 62 | Investida · 350 dano · P 0,21 · Init 1,043 | 3645 / 60 |
| 41 | Dilera | Ataque básico · 114 dano · P 0,15 · Init 1,048 | 3516 / 90 | Golpe Poderoso · 288 dano · P 0,21 · Init 1,043 | 3597 / 34 |
| 42 | Dilera | Investida · 198 dano · P 0,14 · Init 1,048 | 3386 / 71 | Ataque básico · 169 dano · P — · Init 1,043 | 3437 / 55 |
| 43 | Dilera | Golpe Poderoso · 195 dano · P 0,14 · Init 1,048 | 3256 / 57 | Ataque básico · 169 dano · P 0,24 · Init 1,043 | 3280 / 76 |
| 44 | Dilera | Investida · 198 dano · P 0,15 · Init 1,048 | 3041 / 38 | Ataque básico · 254 dano · P 0,25 · Init 1,043 | 3140 / 97 |
| 45 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 2773 / 66 | Investida · 290 dano · P 0,27 · Init 1,043 | 3092 / 65 |
| 46 | Dilera | Ataque básico · 114 dano · P 0,12 · Init 1,048 | 2626 / 94 | Ataque básico · 169 dano · P 0,29 · Init 1,043 | 3016 / 86 |
| 47 | Dilera | Tomar Fôlego · 0 dano · P 0,14 · Init 1,048 | 3224 / 48 | Ataque básico · 254 dano · P 0,36 · Init 1,043 | 3074 / 107 |
| 48 | Dilera | Investida · 198 dano · P 0,13 · Init 1,048 | 2975 / 29 | Golpe Poderoso · 288 dano · P 0,29 · Init 1,043 | 2942 / 81 |
| 49 | Dilera | Ataque básico · 0 dano · P — · Init 1,048 | 2685 / 57 | Investida · 290 dano · P 0,32 · Init 1,043 | 3008 / 49 |
| 50 | Dilera | Investida · 198 dano · P 0,11 · Init 1,048 | 2555 / 38 | Ataque básico · 169 dano · P 0,45 · Init 1,043 | 2848 / 70 |
| 51 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 2287 / 66 | Investida · 290 dano · P 0,48 · Init 1,043 | 2800 / 38 |
| 52 | Dilera | Ataque básico · 0 dano · P 0,13 · Init 1,048 | 2118 / 94 | Ataque básico · 169 dano · P — · Init 1,043 | 2838 / 59 |
| 53 | Dilera | Tomar Fôlego · 0 dano · P 0,11 · Init 1,048 | 2680 / 48 | Investida · 290 dano · P 0,63 · Init 1,043 | 2904 / 27 |
| 54 | Dilera | Investida · 198 dano · P 0,11 · Init 1,048 | 2550 / 29 | Ataque básico · 169 dano · P — · Init 1,043 | 2744 / 48 |
| 55 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 2284 / 57 | Golpe Poderoso · 288 dano · P 0,54 · Init 1,043 | 2696 / 22 |
| 56 | Dilera | Ataque básico · 114 dano · P 0,11 · Init 1,048 | 2137 / 85 | Ataque básico · 169 dano · P — · Init 1,043 | 2620 / 43 |
| 57 | Dilera | Ataque básico · 0 dano · P 0,13 · Init 1,048 | 1968 / 113 | Ataque básico · 169 dano · P — · Init 1,043 | 2658 / 64 |
| 58 | Dilera | Tomar Fôlego · 0 dano · P 0,12 · Init 1,048 | 2530 / 67 | Investida · 290 dano · P 0,68 · Init 1,043 | 2724 / 32 |
| 59 | Dilera | Golpe Poderoso · 195 dano · P 0,12 · Init 1,048 | 2400 / 53 | Ataque básico · 169 dano · P — · Init 1,043 | 2567 / 53 |
| 60 | Dilera | Ataque básico · 114 dano · P 0,11 · Init 1,048 | 2134 / 81 | Golpe Poderoso · 288 dano · P 0,67 · Init 1,043 | 2519 / 27 |
| 61 | Dilera | Ataque básico · 114 dano · P 0,13 · Init 1,048 | 1987 / 109 | Ataque básico · 169 dano · P — · Init 1,043 | 2443 / 48 |
| 62 | Dilera | Investida · 198 dano · P 0,14 · Init 1,048 | 1857 / 90 | Ataque básico · 169 dano · P 0,62 · Init 1,043 | 2283 / 69 |
| 63 | Dilera | Tomar Fôlego · 0 dano · P 0,15 · Init 1,048 | 2419 / 44 | Investida · 290 dano · P 0,60 · Init 1,043 | 2349 / 37 |
| 64 | Dilera | Golpe Poderoso · 195 dano · P 0,14 · Init 1,048 | 2289 / 30 | Ataque básico · 169 dano · P — · Init 1,043 | 2192 / 58 |
| 65 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 2142 / 58 | Ataque básico · 169 dano · P 0,53 · Init 1,043 | 2116 / 79 |
| 66 | Dilera | Golpe Poderoso · 0 dano · P 0,12 · Init 1,048 | 1854 / 44 | Golpe Poderoso · 288 dano · P 0,59 · Init 1,043 | 2182 / 53 |
| 67 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 1876 / 72 | Investida · 0 dano · P 0,76 · Init 1,043 | 2068 / 21 |
| 68 | Dilera | Ataque básico · 114 dano · P 0,17 · Init 1,048 | 1729 / 100 | Ataque básico · 169 dano · P — · Init 1,043 | 1992 / 42 |
| 69 | Dilera | Tomar Fôlego · 0 dano · P 0,17 · Init 1,048 | 2412 / 54 | Ataque básico · 169 dano · P — · Init 1,043 | 2030 / 63 |
| 70 | Dilera | Ataque básico · 0 dano · P 0,15 · Init 1,048 | 2412 / 82 | Golpe Poderoso · 0 dano · P 0,47 · Init 1,043 | 2030 / 37 |
| 71 | Dilera | Investida · 198 dano · P 0,18 · Init 1,048 | 2282 / 63 | Ataque básico · 169 dano · P — · Init 1,043 | 1870 / 58 |
| 72 | Dilera | Golpe Poderoso · 195 dano · P 0,18 · Init 1,048 | 2033 / 49 | Golpe Poderoso · 288 dano · P 0,33 · Init 1,043 | 1741 / 32 |
| 73 | Dilera | Ataque básico · 114 dano · P 0,22 · Init 1,048 | 1886 / 77 | Ataque básico · 169 dano · P — · Init 1,043 | 1665 / 53 |
| 74 | Dilera | Tomar Fôlego · 0 dano · P 0,24 · Init 1,048 | 2450 / 31 | Golpe Poderoso · 288 dano · P 0,31 · Init 1,043 | 1731 / 27 |
| 75 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 2303 / 59 | Ataque básico · 169 dano · P — · Init 1,043 | 1655 / 48 |
| 76 | Dilera | Investida · 0 dano · P 0,22 · Init 1,048 | 2015 / 40 | Golpe Poderoso · 288 dano · P 0,30 · Init 1,043 | 1721 / 22 |
| 77 | Dilera | Ataque básico · 0 dano · P — · Init 1,048 | 1846 / 68 | Ataque básico · 169 dano · P — · Init 1,043 | 1759 / 43 |
| 78 | Dilera | Ataque básico · 114 dano · P 0,21 · Init 1,048 | 1699 / 96 | Ataque básico · 169 dano · P — · Init 1,043 | 1683 / 64 |
| 79 | Dilera | Investida · 198 dano · P 0,21 · Init 1,048 | 1569 / 77 | Ataque básico · 169 dano · P 0,47 · Init 1,043 | 1523 / 85 |
| 80 | Dilera | Tomar Fôlego · 0 dano · P 0,20 · Init 1,048 | 2131 / 31 | Investida · 290 dano · P 0,46 · Init 1,043 | 1589 / 53 |
| 81 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 1865 / 59 | Golpe Poderoso · 288 dano · P 0,42 · Init 1,043 | 1541 / 27 |
| 82 | Dilera | Golpe Poderoso · 0 dano · P 0,18 · Init 1,048 | 1696 / 45 | Ataque básico · 169 dano · P — · Init 1,043 | 1579 / 48 |
| 83 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 1430 / 73 | Golpe Poderoso · 288 dano · P 0,54 · Init 1,043 | 1531 / 22 |
| 84 | Dilera | Golpe Poderoso · 195 dano · P 0,12 · Init 1,048 | 1300 / 59 | Ataque básico · 169 dano · P — · Init 1,043 | 1374 / 43 |
| 85 | Dilera | Ataque básico · 0 dano · P 0,22 · Init 1,048 | 1131 / 87 | Ataque básico · 169 dano · P — · Init 1,043 | 1412 / 64 |
| 86 | Dilera | Investida · 198 dano · P 0,08 · Init 1,048 | 880 / 68 | Investida · 290 dano · P 0,72 · Init 1,043 | 1280 / 32 |
| 87 | Dilera | Ataque básico (cancelled_control) · 0 dano · P 0,13 · Init 1,048 | 711 / 96 | Ataque básico · 169 dano · P — · Init 1,043 | 1318 / 53 |
| 88 | Dilera | Investida · 198 dano · P 0,12 · Init 1,048 | 462 / 77 | Golpe Poderoso · 288 dano · P 0,89 · Init 1,043 | 1186 / 27 |
| 89 | Dilera | Tomar Fôlego · 0 dano · P 0,07 · Init 1,048 | 1145 / 31 | Ataque básico · 169 dano · P — · Init 1,043 | 1224 / 48 |
| 90 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 998 / 59 | Ataque básico · 169 dano · P 0,86 · Init 1,043 | 1148 / 69 |
| 91 | Dilera | Ataque básico · 0 dano · P 0,06 · Init 1,048 | 710 / 87 | Golpe Poderoso · 288 dano · P 0,79 · Init 1,043 | 1214 / 43 |
| 92 | Dilera | Golpe Poderoso · 195 dano · P 0,05 · Init 1,048 | 749 / 73 | Ataque básico · 0 dano · P — · Init 1,043 | 1019 / 64 |
| 93 | Dilera | Ataque básico · 114 dano · P 0,19 · Init 1,048 | 483 / 101 | Golpe Poderoso · 288 dano · P 0,94 · Init 1,043 | 971 / 38 |
| 94 | Dilera | Tomar Fôlego · 0 dano · P 0,14 · Init 1,048 | 1166 / 55 | Ataque básico · 169 dano · P — · Init 1,043 | 1009 / 59 |
| 95 | Dilera | Golpe Poderoso · 195 dano · P 0,11 · Init 1,048 | 915 / 41 | Investida · 290 dano · P 0,81 · Init 1,043 | 880 / 27 |
| 96 | Dilera | Ataque básico · 0 dano · P — · Init 1,048 | 746 / 69 | Ataque básico · 169 dano · P — · Init 1,043 | 918 / 48 |
| 97 | Dilera | Golpe Poderoso · 195 dano · P 0,06 · Init 1,048 | 497 / 55 | Golpe Poderoso · 288 dano · P 0,88 · Init 1,043 | 789 / 22 |
| 98 | Dilera | Ataque básico · 114 dano · P 0,15 · Init 1,048 | 350 / 83 | Ataque básico · 169 dano · P — · Init 1,043 | 713 / 43 |
| 99 | Dilera | Tomar Fôlego · 0 dano · P 0,17 · Init 1,048 | 1202 / 37 | Ataque básico · 0 dano · P — · Init 1,043 | 713 / 64 |
| 100 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 1055 / 65 | Ataque básico · 169 dano · P 0,57 · Init 1,043 | 637 / 85 |
| 101 | Dilera | Investida · 198 dano · P 0,14 · Init 1,048 | 806 / 46 | Golpe Poderoso · 288 dano · P 0,40 · Init 1,043 | 505 / 59 |
| 102 | Dilera | Golpe Poderoso · 195 dano · P 0,19 · Init 1,048 | 555 / 32 | Investida · 290 dano · P 0,55 · Init 1,043 | 376 / 27 |
| 103 | Dilera | Ataque básico · 114 dano · P — · Init 1,048 | 408 / 60 | Ataque básico · 169 dano · P — · Init 1,043 | 300 / 48 |
| 104 | Dilera | Ataque básico · 114 dano · P 0,39 · Init 1,048 | 430 / 88 | Ataque básico · 0 dano · P 0,81 · Init 1,043 | 186 / 69 |
| 105 | Dilera | Investida · 198 dano · P 0,83 · Init 1,048 | 469 / 69 | Investida (cancelled_death) · 0 dano · P 0,24 · Init 1,043 | -12 / 69 |

**Avaliação das escolhas**

- Rodada 104, Dilera (HP 408/5077, MP 60; o outro com HP 300/6314): escolheu **ataque básico**. Opções: ataque básico P 0,393; Golpe Poderoso P 0,104, 42 MP; Investida P 0,071, 47 MP; Couraça Improvisada P 0,023, 56 MP. A `PoliticaCopa` faria Couraça Improvisada (Couraça Improvisada é legal e não está ativo (buffs visíveis: [])).
- Rodada 105, Dilera (HP 430/5077, MP 88; o outro com HP 186/6314): escolheu **Investida**. Opções: Investida P 0,829, 47 MP; Tomar Fôlego P 0,777, 74 MP; Golpe Poderoso P 0,672, 42 MP; ataque básico P 0,667; Couraça Improvisada P 0,354, 56 MP. A `PoliticaCopa` faria Tomar Fôlego (HP 430/5077 (8.5%) ≤ 50% e há cura legal: Tomar Fôlego).
- Rodada 99, Dilera (HP 350/5077, MP 83; o outro com HP 713/6314): escolheu **Tomar Fôlego**. Opções: Tomar Fôlego P 0,172, 74 MP; Investida P 0,021, 47 MP; ataque básico P 0,067; Golpe Poderoso P 0,016, 42 MP; Couraça Improvisada P 0,012, 56 MP. A `PoliticaCopa` faria Tomar Fôlego (HP 350/5077 (6.9%) ≤ 50% e há cura legal: Tomar Fôlego).
- Rodada 98, Dilera (HP 497/5077, MP 55; o outro com HP 789/6314): escolheu **ataque básico**. Opções: ataque básico P 0,149; Investida P 0,017, 47 MP. A `PoliticaCopa` faria Investida (primeira skill de dano legal do deck: Investida).

## As 63 partidas da v2

| Partida | Lado 1 | Lado 2 | Vencedor | Rod. | HP final | ΔOP |
|---|---|---|---|---|---|---|
| fase64-1 | Smzinho (W35) | G0ularte (W14) | Smzinho (W35) | 17 | 2687/5701 | +1,73 |
| fase64-2 | sofiaespanha (W56) | brino (W09) | sofiaespanha (W56) | 19 | 1682/7757 | +1,27 |
| fase64-3 | gafallen (W37) | blackoutz (W12) | gafallen (W37) | 9 | 1119/3973 | +2,07 |
| fase64-4 | Bagi (W48) | loud_thurzin (W32) | loud_thurzin (W32) | 30 | 2382/5110 | +2,07 |
| fase64-5 | fnxLNTC (W24) | hastad (W50) | fnxLNTC (W24) | 13 | 3433/5355 | +0,92 |
| fase64-6 | yayahuz (W07) | k13tv (W17) | yayahuz (W07) | 32 | 1510/6296 | −0,12 (zebra) |
| fase64-7 | Dilera (W05) | JonVlogs (W58) | Dilera (W05) | 105 | 469/5077 | −0,69 (zebra) |
| fase64-8 | Coringa (W57) | LuquEt4 (W34) | LuquEt4 (W34) | 21 | 3790/7257 | +2,07 |
| fase64-9 | liminhag0d (W59) | tioorochitwitch (W63) | tioorochitwitch (W63) | 23 | 661/7189 | −0,23 (zebra) |
| fase64-10 | MeikodRJ (W26) | Tenz (W08) | Tenz (W08) | 50 | 276/5519 | −1,04 (zebra) |
| fase64-11 | alanzoka (W02) | Bisteconee (W49) | alanzoka (W02) | 14 | 3067/7387 | −0,23 (zebra) |
| fase64-12 | TheBurntPeanut (W54) | DavyJones (W29) | DavyJones (W29) | 15 | 2674/5333 | +0,35 |
| fase64-13 | SkipNhO (W52) | Tealzlol (W61) | SkipNhO (W52) | 22 | 2299/7167 | −0,12 (zebra) |
| fase64-14 | boltz (W21) | lubatv (W23) | lubatv (W23) | 17 | 3809/5275 | +1,38 |
| fase64-15 | suetam1v4 (W51) | babi (W53) | suetam1v4 (W51) | 24 | 322/5734 | −0,58 (zebra) |
| fase64-16 | aXtLOL (W43) | brtt (W13) | aXtLOL (W43) | 10 | 3150/5454 | −0,23 (zebra) |
| fase64-17 | frttt (W60) | belrodrigues (W04) | frttt (W60) | 17 | 2999/5379 | +1,61 |
| fase64-18 | bakzera (W30) | furq (W28) | furq (W28) | 25 | 640/7593 | −0,46 (zebra) |
| fase64-19 | calango (W44) | NOBRU (W40) | NOBRU (W40) | 30 | 4067/5469 | +1,15 |
| fase64-20 | coldzin (W41) | Neskwga (W38) | Neskwga (W38) | 30 | 1631/6216 | −0,23 (zebra) |
| fase64-21 | PlayHard (W18) | xandfps (W20) | PlayHard (W18) | 14 | 1695/4339 | −0,46 (zebra) |
| fase64-22 | Gaules (W36) | tteuw (W19) | Gaules (W36) | 17 | 945/5209 | +0,81 |
| fase64-23 | casimito (W55) | YoDa (W33) | casimito (W55) | 17 | 1668/7113 | +0,35 |
| fase64-24 | Forever (W11) | XANDAOOGOD (W47) | XANDAOOGOD (W47) | 18 | 1933/5684 | +0,92 |
| fase64-25 | Patriota (W10) | jovirone (W22) | Patriota (W10) | 27 | 203/4779 | +0,35 |
| fase64-26 | yeTz (W39) | dona (W01) | dona (W01) | 51 | 3024/7574 | −0,81 (zebra) |
| fase64-27 | fer (W64) | Baiano (W06) | fer (W64) | 14 | 3794/5977 | +2,07 |
| fase64-28 | Felps (W31) | Hayashii (W45) | Hayashii (W45) | 11 | 1713/4939 | −1,73 (zebra) |
| fase64-29 | RazaH (W15) | mount (W25) | mount (W25) | 19 | 558/7863 | +0,46 |
| fase64-30 | jukes (W03) | gabepeixe (W62) | jukes (W03) | 15 | 1197/5515 | −0,46 (zebra) |
| fase64-31 | aspaszin (W27) | sacy (W16) | sacy (W16) | 46 | 2335/7520 | +0,23 |
| fase64-32 | RNakano (W42) | PaulinhoLOKObr (W46) | RNakano (W42) | 56 | 3416/8159 | +1,15 |
| fase32-1 | Smzinho (W35) | sofiaespanha (W56) | Smzinho (W35) | 12 | 4307/5701 | +0,46 |
| fase32-2 | gafallen (W37) | loud_thurzin (W32) | gafallen (W37) | 28 | 598/3973 | +0,00 |
| fase32-3 | fnxLNTC (W24) | yayahuz (W07) | fnxLNTC (W24) | 64 | 1883/5355 | +1,73 |
| fase32-4 | Dilera (W05) | LuquEt4 (W34) | LuquEt4 (W34) | 16 | 5369/7257 | +1,96 |
| fase32-5 | tioorochitwitch (W63) | Tenz (W08) | Tenz (W08) | 43 | 1011/5519 | −0,69 (zebra) |
| fase32-6 | alanzoka (W02) | DavyJones (W29) | DavyJones (W29) | 57 | 698/5333 | +1,61 |
| fase32-7 | SkipNhO (W52) | lubatv (W23) | lubatv (W23) | 32 | 3103/5275 | +1,15 |
| fase32-8 | suetam1v4 (W51) | aXtLOL (W43) | aXtLOL (W43) | 10 | 3993/5454 | +1,84 |
| fase32-9 | frttt (W60) | furq (W28) | frttt (W60) | 21 | 3036/5379 | +0,00 |
| fase32-10 | NOBRU (W40) | Neskwga (W38) | Neskwga (W38) | 32 | 714/6216 | −0,35 (zebra) |
| fase32-11 | PlayHard (W18) | Gaules (W36) | Gaules (W36) | 13 | 1231/5209 | +1,96 |
| fase32-12 | casimito (W55) | XANDAOOGOD (W47) | XANDAOOGOD (W47) | 22 | 1032/5684 | −0,12 (zebra) |
| fase32-13 | Patriota (W10) | dona (W01) | dona (W01) | 30 | 1935/7574 | −0,81 (zebra) |
| fase32-14 | fer (W64) | Hayashii (W45) | fer (W64) | 14 | 2989/5977 | +2,07 |
| fase32-15 | mount (W25) | jukes (W03) | mount (W25) | 43 | 4719/7863 | +1,38 |
| fase32-16 | sacy (W16) | RNakano (W42) | sacy (W16) | 52 | 641/7520 | −0,12 (zebra) |
| oitavas-1 | Smzinho (W35) | gafallen (W37) | Smzinho (W35) | 15 | 899/5701 | −0,12 (zebra) |
| oitavas-2 | fnxLNTC (W24) | LuquEt4 (W34) | LuquEt4 (W34) | 22 | 1399/7257 | +0,35 |
| oitavas-3 | Tenz (W08) | DavyJones (W29) | Tenz (W08) | 44 | 1173/5519 | −1,27 (zebra) |
| oitavas-4 | lubatv (W23) | aXtLOL (W43) | aXtLOL (W43) | 36 | 1005/5454 | +0,58 |
| oitavas-5 | frttt (W60) | Neskwga (W38) | Neskwga (W38) | 18 | 626/6216 | −0,12 (zebra) |
| oitavas-6 | Gaules (W36) | XANDAOOGOD (W47) | XANDAOOGOD (W47) | 14 | 1273/5684 | −0,35 (zebra) |
| oitavas-7 | dona (W01) | fer (W64) | fer (W64) | 49 | 2360/5977 | +0,92 |
| oitavas-8 | mount (W25) | sacy (W16) | sacy (W16) | 56 | 188/7520 | +0,00 |
| quartas-1 | Smzinho (W35) | LuquEt4 (W34) | Smzinho (W35) | 12 | 2067/5701 | −0,12 (zebra) |
| quartas-2 | Tenz (W08) | aXtLOL (W43) | Tenz (W08) | 29 | 458/5519 | −1,04 (zebra) |
| quartas-3 | Neskwga (W38) | XANDAOOGOD (W47) | Neskwga (W38) | 17 | 2176/6216 | −0,23 (zebra) |
| quartas-4 | fer (W64) | sacy (W16) | fer (W64) | 49 | 48/5977 | +0,46 |
| semifinal-1 | Smzinho (W35) | Tenz (W08) | Tenz (W08) | 27 | 937/5519 | −1,04 (zebra) |
| semifinal-2 | Neskwga (W38) | fer (W64) | fer (W64) | 31 | 1130/5977 | +0,58 |
| final-1 | Tenz (W08) | fer (W64) | fer (W64) | 46 | 2232/5977 | +1,27 |

## Limitações

- O adversário é modelado: até as cartas dele aparecerem, a IA supõe um deck como o dela; até a tela revelar procs e roubo de vida, supõe metade dos dela. Contra uma build muito diferente, as primeiras rodadas são decididas com um modelo errado.
- A corrida depois do horizonte é uma estimativa: ela supõe o MP gasto da melhor forma e não conta cartas de buff e de status depois do horizonte. As estimativas de P(vitória) ordenam bem, mas não são probabilidades calibradas no começo da luta.
- Uma Copa eliminatória com uma seed por partida não mede força de build. Os confrontos controlados medem o controlador; o Bradley-Terry da Copa 03, as builds.

