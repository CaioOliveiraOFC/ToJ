# Ranked offline — Fase 6.1: progressão competitiva, elite e correções

Gerado por `python tools/ranked_progressao.py relatorio`, a partir dos JSONs desta pasta. Todo confronto é uma partida real do motor PvP com seed; as carreiras se refazem sem o motor (`progressao`) com qualquer ciclo de leaderboard. O contrato está em `GAMEPLAY_CONTRACTS.md`.

## 1. Empate técnico por impasse

Nos 1781 confrontos com vencedor da Fase 6 (amostra, calibração e holdout), a duração foi de 18 rodadas na mediana, 44 no p90, 124 no p99 e 474 no máximo; 2 bateram o limite de 500.

Refiz 242 duelos rodada a rodada, guardando HP e MP dos dois lados (`trajetorias.jsonl`): os 15 que bateram o limite na Fase 6 (amostra, calibração e as carreiras), os 27 que terminaram em KO depois de 100 rodadas e 200 comuns, até 1.500 rodadas. Todos os refeitos com vencedor repetiram o vencedor e o número de rodadas gravados.

- Dos 15 "sem resultado" da Fase 6, 8 terminaram em KO depois da rodada 500; 7 (todos R31 × M33) não terminaram em 1.500.
- A maior espera por um mínimo novo de HP ou MP (folga de 1%), por partida que terminou em KO:

| dupla | rodadas até o KO | maior espera |
|---|---|---|
| R31×M32 | 1002 | 826 |
| M33×M27 | 786 | 293 |
| R31×M32 | 957 | 285 |
| R31×M32 | 649 | 242 |
| M32×R31 | 441 | 227 |
| R31×M27 | 509 | 189 |
| R31×M32 | 696 | 177 |
| M27×M33 | 474 | 173 |
| R31×M32 | 811 | 167 |
| M20×W77 | 304 | 159 |
| R31×M32 | 540 | 134 |
| W05×W44 | 242 | 50 |

Há um vão limpo: as partidas que andam até o fim (desgaste contínuo) esperam no máximo 50 rodadas por um mínimo novo; as duplas de sustain em equilíbrio, de 134 a 826. A janela escolhida é o triplo de 50:

| janela | KOs que virariam empate | rodada em que as duplas sem fim empatam |
|---|---|---|
| 100 | 11 | 289, 256, 308, 224, 275, 371, 364 |
| 150 (escolhida) | 10 | 339, 306, 358, 274, 325, 421, 414 |
| 200 | 5 | 389, 356, 408, 774, 870, 471, 464 |
| 250 | 3 | 439, 406, 458, 824, 920, 521, 514 |

**Regra:** empate técnico depois de 150 rodadas sem nenhum mínimo novo (folga de 1% do máximo), ou no teto de 1000 rodadas. Os KOs que viram empate com a janela de 150 são todos de duplas que passaram pelo menos 150 rodadas sem que ninguém fosse desgastado — R31, M27, M32, M33 e M20 × W77 —, e nenhuma partida que terminou com desgaste contínuo é encerrada.

## 2. A fórmula de PR

Antes de jogar qualquer partida nova, a fórmula foi reaplicada às 4 carreiras reais da Fase 6 (resultado, chance do Glicko-2 e percentil de cada partida gravados): `formula.json`. Oscilação = promoção desfeita em até 3 partidas (ou rebaixamento desfeito); distância = |alvo − coordenada visível| média, em PR.

| variante | M03 osc. / trocas de rank / dist. | M11 | W26 | R31 ganho / perda |
|---|---|---|---|---|
| proposta | 10 / 0 / 25 | 6 / 1 / 37 | 4 / 5 / 76 | 37,8 / -4,2 |
| K 30 | 5 / 0 / 28 | 6 / 1 / 47 | 2 / 3 / 84 | 28,4 / -3,2 |
| K 50 | 9 / 0 / 21 | 8 / 3 / 36 | 8 / 7 / 64 | 46,4 / -5,3 |
| β 0,12 | 9 / 0 / 28 | 10 / 1 / 50 | 8 / 9 / 88 | 32,9 / -4,6 |
| β 0,30 | 7 / 0 / 22 | 8 / 1 / 35 | 8 / 11 / 63 | 37,8 / -4,2 |
| sem escudo | 25 / 0 / 37 | 17 / 1 / 47 | 25 / 21 / 76 | 37,8 / -4,2 |
| rebaixa contínuo | 14 / 0 / 26 | 13 / 1 / 39 | 15 / 6 / 80 | 37,8 / -4,2 |
| sem puxar para o alvo | 46 / 0 / 93 | 51 / 21 / 193 | 41 / 0 / 227 | 12,6 / -12,8 |

Na W26, o rank por percentil da Fase 6 trocava 71 vezes; o rank visível com a proposta, 5. Escolhidos: K = 40, β = 0,20, multiplicador até 3, escudo de 3 partidas, rebaixamento pousando em no máximo 75 PR. Ganho ~18 e perda ~18 por partida equilibrada no lugar certo; o R31, de elite e posicionado no teto (Obsidian I), ganha ~38 e perde ~4 até virar candidato.

## 3. Repetição de adversário

Por modelo (`repeticao.json`): o resultado sai da chance do Glicko-2 entre as forças VERDADEIRAS (as da calibração) e o MMR do jogador artificial começa do centro. 300 partidas por jogador com os 186; 100 com uma população sintética de 5.000 (ratings sorteados da calibrada, com ruído). Repetição = adversário que já apareceu nas 10 partidas anteriores; desequilíbrio = |chance − ½| médio.

| população | faixa | Fase 6: repetição / distintos / deseq. | 6.1 |
|---|---|---|---|
| 186 | baixo | 23% / 46 / 0,111 | 0% / 53 / 0,119 |
| 186 | intermediario | 10% / 83 / 0,111 | 0% / 85 / 0,108 |
| 186 | alto | 12% / 67 / 0,114 | 0% / 68 / 0,116 |
| 186 | fronteira | 25% / 47 / 0,117 | 0% / 42 / 0,138 |
| 186 | elite | 56% / 26 / 0,123 | 16% / 29 / 0,176 |
| 5000 | baixo | 0% / 99 / 0,125 | 0% / 96 / 0,124 |
| 5000 | intermediario | 0% / 99 / 0,117 | 0% / 99 / 0,109 |
| 5000 | alto | 2% / 95 / 0,111 | 0% / 99 / 0,111 |
| 5000 | fronteira | 1% / 98 / 0,117 | 0% / 95 / 0,122 |
| 5000 | elite | 7% / 68 / 0,121 | 0% / 84 / 0,125 |

Custo por escolha com 5.000 NPCs: 7,1–12,2 ms. Parâmetros: peso 8, meia-vida 5 partidas, memória 20. **Para 5.000:** a mesma regra serve sem mudança; o que muda é a densidade — a janela da etapa passa a ter dezenas de candidatos, e o custo de repetição quase nunca decide. A memória de 20 partidas por gladiador já está no histórico guardado (50).

## 4. Os jogadores artificiais

Cinco carreiras reais (`carreiras/`), uma por faixa da Ladder calibrada, com o caminho do jogo: matchmaking 6.1, árbitro de impasse, mundo NPC × NPC (2 confrontos por partida do jogador, mais a fila do retorno) e a leaderboard. Relógio injetado: 40 partidas por dia (hipótese de 3 min por partida, 2 h de jogo), a partir das 19h UTC, e o jogo fechado até o dia seguinte. A mesma carreira foi refeita sem o motor com o ciclo de 1 h e com o de 24 h: o MMR é idêntico nas duas (divergência zero em todas), e muda só o que a leaderboard decide.

| faixa (gêmeo) | partidas (h) | V-E-D | posicionado em | 2h | 5h | 10h | final | MMR final (percentil) |
|---|---|---|---|---|---|---|---|---|
| baixo (R01) | 120 (6,0) | 55-0-65 | Iron III 41 PR (p 4,8) | Iron III 23 PR | Iron II 77 PR | — | Iron II 25 PR | 1033 (7,5) |
| intermediario (W26) | 120 (6,0) | 61-0-59 | Platinum V 60 PR (p 49,5) | Platinum V 0 PR | Gold I 0 PR | — | Gold I 67 PR | 1518 (48,4) |
| alto (W80) | 120 (6,0) | 62-0-58 | Sapphire I 42 PR (p 78,0) | Sapphire I 71 PR | Diamond V 67 PR | — | Sapphire I 87 PR | 1849 (78,0) |
| fronteira (W86) | 120 (6,0) | 63-0-57 | Obsidian V 91 PR (p 87,1) | Obsidian IV 62 PR | Obsidian V 0 PR | — | Obsidian V 23 PR | 1960 (86,6) |
| elite (M32) | 120 (6,0) | 85-1-34 | Obsidian I 0 PR (p 97,3) | International Master ★ | International Master ★ | — | International Master ★ | 2495 (98,4) |

| faixa | PR médio vitória / derrota / empate | promoções / rebaixamentos | escudo segurou | oscilações | partidas por promoção | distância média (p90) ao alvo | rank visível = rank do percentil |
|---|---|---|---|---|---|---|---|
| baixo | 20,5 / -16,5 / — | 6 / 5 | 4 | 3 | 18,5 | 38 (74) | 99% |
| intermediario | 16,6 / -17,8 / — | 6 / 7 | 8 | 4 | 18,5 | 45 (84) | 81% |
| alto | 17,5 / -16,8 / — | 4 / 4 | 2 | 1 | 27,8 | 59 (130) | 82% |
| fronteira | 17,5 / -18,6 / — | 7 / 7 | 3 | 5 | 15,9 | 46 (114) | 93% |
| elite | 41,0 / -4,5 / — | 0 / 0 | 0 | 0 | — | — (—) | 0% |

**Matchmaking real:**

| faixa | oponentes distintos | repetidos nas últimas 10 | chance média | desequilíbrio |
|---|---|---|---|---|
| baixo | 35 | 2 (1,7%) | 0,463 | 0,111 |
| intermediario | 57 | 0 (0,0%) | 0,501 | 0,102 |
| alto | 52 | 0 (0,0%) | 0,502 | 0,100 |
| fronteira | 45 | 0 (0,0%) | 0,519 | 0,117 |
| elite | 18 | 39 (32,5%) | 0,653 | 0,277 |

## 5. Candidatura, elite e a leaderboard: 1 h × 24 h

| ciclo | faixa | 1ª vez candidato | partidas como candidato (h de jogo) | avaliações na atualização | entrou na elite | final |
|---|---|---|---|---|---|---|
| 1h | baixo | — | 0 (0,0) | — | — | Iron II 25 PR |
| 1h | intermediario | — | 0 (0,0) | — | — | Gold I 67 PR |
| 1h | alto | — | 0 (0,0) | — | — | Sapphire I 87 PR |
| 1h | fronteira | — | 0 (0,0) | — | — | Obsidian V 23 PR |
| 1h | elite | 13 | 7 (0,3) | promocao a elite (n 20) | 20 | International Master ★ |
| 24h | baixo | — | 0 (0,0) | — | — | Iron II 25 PR |
| 24h | intermediario | — | 0 (0,0) | — | — | Gold I 67 PR |
| 24h | alto | — | 0 (0,0) | — | — | Sapphire I 87 PR |
| 24h | fronteira | — | 0 (0,0) | — | — | Obsidian V 23 PR |
| 24h | elite | 13 | 28 (1,4) | promocao a elite (n 41) | 41 | International Master ★ |

**A leaderboard inteira** (cada carreira tem o próprio mundo; números somados das 5):

| ciclo | atualizações | Top 5 mudou em | nomes trocados no Top 5 | promoções à elite | rebaixamentos da elite | avisos de risco | tamanho da elite |
|---|---|---|---|---|---|---|---|
| 1h | 40 | 0 | 0 | 1 | 5 | 10 | 13–16 |
| 24h | 10 | 0 | 0 | 1 | 2 | 5 | 14–16 |

Regras: promoção com percentil ≥ 92 e RD ≤ 150; risco a menos de 3 pontos abaixo; rebaixamento no segundo retrato abaixo ou de uma vez além da faixa.

## 6. Empates e custo

| faixa | partidas do mundo | empates do mundo (rodada) | empates do jogador | CPU do jogador | CPU do mundo |
|---|---|---|---|---|---|
| baixo | 288 | 1 (279) | 0 | 7,9 min | 28,3 min |
| intermediario | 288 | 1 (279) | 0 | 11,6 min | 28,5 min |
| alto | 288 | 1 (279) | 0 | 10,7 min | 28,1 min |
| fronteira | 288 | 0 (—) | 0 | 7,3 min | 27,5 min |
| elite | 288 | 0 (—) | 1 | 27,0 min | 25,7 min |

## 7. Problemas encontrados e correções

- **O "impasse" da Fase 6 não era um só fenômeno.** Refeitos até 1.500 rodadas, 8 dos 15 confrontos que bateram o limite de 500 terminaram em KO (entre as rodadas 509 e 1.002) e 7 — todos R31 × M33 — não terminaram nunca. Os dois casos são o mesmo equilíbrio: o MP dos dois zera por volta da rodada 100 e o HP passa a oscilar numa faixa estável; o KO, quando vem, é sorte. Por isso o critério é de desgaste (mínimo novo de HP ou MP) e não de duração.
- **Rebaixamento contínuo fazia pisca-pisca.** Com o PR do rebaixamento contínuo (100 − o que faltou), um gladiador na fronteira descia e subia na partida seguinte: 30 oscilações em 390 partidas na carreira W26 da Fase 6. Pousar em no máximo 75 PR e o escudo de 3 partidas derrubaram isso para 4, sem piorar a distância ao alvo.
- **Sem puxar para o alvo, o PR se descola do MMR.** A variante sem o multiplicador (PR puro por resultado contra expectativa) termina a carreira M11 em Diamond V com o MMR de Diamond II, e a W26 três divisões acima do alvo: distância média de 93 a 227 PR, contra 25 a 76 com β = 0,20.
- **Posicionar em 0 PR rebaixava na primeira derrota.** A primeira versão punha o gladiador no começo da divisão do alvo; qualquer derrota logo depois do posicionamento descia uma divisão. O posicionamento agora nasce no PR do alvo e com escudo.
- **Repetição no topo é estrutural com 186.** O custo de repetição zera a repetição nas faixas baixa, média, alta e na fronteira, mas no topo há poucos rivais: o peso 4 deixava 34% de repetição no modelo; o peso 8 deixa 16%, ao custo de partidas um pouco menos equilibradas. Com 5.000, a repetição some nas duas políticas.
- **Títulos com população pequena.** Os Definitive Masters são os cinco primeiros DA ELITE; com menos de ~60 gladiadores competitivos, a elite (percentil ≥ 92) tem menos de cinco membros e sobra título. Com 186 a elite tem 15.

