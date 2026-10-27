# Ranked offline — Fase 6

Gerado por `python tools/ranked_experimentos.py relatorio` a partir dos JSON desta pasta. Todo confronto é uma partida real do motor PvP (IA estratégica dos dois lados, gerador semeado).

## 1. Custo

- Um confronto NPC × NPC custa em média 2,94 s de CPU e dura 22,8 rodadas (amostra de 516 partidas).
- Com 4 processos, ~1 partida por segundo de relógio.

## 2. Glicko-2 × TrueSkill na amostra pequena

396 partidas de treino e 120 de holdout, estratificadas (OP próximo e distante, classes, estilos, repetições). 30 ordens diferentes do treino; média do holdout.

| sistema | log-loss holdout | Brier | acerto | ECE | estabilidade (Spearman) |
|---|---|---|---|---|---|
| *moeda* | 0,693 | 0,250 | 0,000 | 0,500 | — |
| *OP logístico* | 0,490 | 0,168 | 0,777 | 0,041 | — |
| *Bradley-Terry em lote* | 0,686 | 0,242 | 0,642 | 0,120 | — |
| Glicko-2 τ=0.3 plano | 0,703 ± 0,013 | 0,247 | 0,609 | 0,107 | 0,955 |
| Glicko-2 τ=0.3 OP | 0,612 ± 0,010 | 0,210 | 0,692 | 0,073 | 0,983 |
| Glicko-2 τ=0.6 plano | 0,703 ± 0,013 | 0,247 | 0,609 | 0,107 | 0,955 |
| Glicko-2 τ=0.6 OP | 0,612 ± 0,010 | 0,210 | 0,692 | 0,073 | 0,983 |
| Glicko-2 τ=1.0 plano | 0,703 ± 0,013 | 0,247 | 0,609 | 0,107 | 0,955 |
| Glicko-2 τ=1.0 OP | 0,612 ± 0,010 | 0,210 | 0,692 | 0,073 | 0,983 |
| TrueSkill β=σ/2 plano | 0,727 ± 0,014 | 0,252 | 0,606 | 0,120 | 0,958 |
| TrueSkill β=σ/2 OP | 0,647 ± 0,011 | 0,220 | 0,682 | 0,099 | 0,980 |
| TrueSkill β=σ/4 plano | 0,805 ± 0,027 | 0,264 | 0,609 | 0,163 | 0,925 |
| TrueSkill β=σ/4 OP | 0,751 ± 0,024 | 0,245 | 0,644 | 0,140 | 0,947 |
| TrueSkill β=σ/8 plano | 0,860 ± 0,038 | 0,270 | 0,611 | 0,183 | 0,907 |
| TrueSkill β=σ/8 OP | 0,827 ± 0,035 | 0,260 | 0,626 | 0,168 | 0,921 |

- O OP prevê bem quando a diferença é grande: k = 1,42 logit por ponto de OP.
- Nas 30 duplas repetidas com três seeds, só 13 tiveram o mesmo vencedor nas três: entre builds parecidas, a sorte pesa muito.

## 3. Calibração dos 186

A amostra e depois 12 rodadas suíças com Glicko-2 (cada NPC contra um vizinho de rating que ele não enfrentou nas últimas 8; a cada 3 rodadas, a vizinhança dobra).

| rodada | RD médio | Spearman com a anterior | Top 5 |
|---|---|---|---|
| 1 | 177,0 | 0,9737 | R34, W96, W94, M32, R44 |
| 2 | 161,7 | 0,9817 | R34, W96, W94, R39, R31 |
| 3 | 150,0 | 0,9869 | R34, W96, W94, R39, M32 |
| 4 | 140,1 | 0,9892 | R34, W96, W94, R39, M32 |
| 5 | 131,9 | 0,9916 | W96, R34, M32, W95, R39 |
| 6 | 125,1 | 0,9926 | W96, R34, M32, W95, W94 |
| 7 | 119,1 | 0,9941 | W96, R34, M32, W95, R39 |
| 8 | 114,0 | 0,9954 | W96, R34, M32, W95, R31 |
| 9 | 109,6 | 0,9959 | W96, R34, W95, M32, R31 |
| 10 | 105,6 | 0,9960 | W96, R34, W95, M32, R31 |
| 11 | 102,1 | 0,9966 | W96, R34, W95, M32, R31 |
| 12 | 99,1 | 0,9972 | W96, R34, W95, R31, M32 |

### A classificação calibrada

| # | id | nome | classe | nível | OP | rating ± 2RD | V-D | rank |
|---|---|---|---|---|---|---|---|---|
| 1 | W96 | Iago do Abismo | Warrior | 29 | 42,4 | 2688 ± 260 | 16-0 | Distinguished Master ★ |
| 2 | R34 | Faro da Torre | Rogue | 29 | 37,5 | 2631 ± 249 | 15-1 | Distinguished Master ★ |
| 3 | W95 | Rana da Geada | Warrior | 29 | 37,5 | 2439 ± 214 | 13-3 | Distinguished Master ★ |
| 4 | R31 | Tália do Eclipse | Rogue | 27 | 36,1 | 2367 ± 222 | 11-4 | International Master ★ |
| 5 | M32 | Oriel do Espinho | Mage | 27 | 35,7 | 2324 ± 214 | 9-6 | International Master ★ |
| 6 | W90 | Kael do Lume | Warrior | 28 | 34,1 | 2277 ± 212 | 11-5 | International Master |
| 7 | R39 | Dália da Brasa | Rogue | 26 | 35,4 | 2268 ± 207 | 11-7 | International Master |
| 8 | W94 | Ébano do Junco | Warrior | 25 | 35,9 | 2202 ± 219 | 11-7 | International Master |
| 9 | M33 | Quila da Fenda | Mage | 25 | 35,3 | 2201 ± 222 | 8-7 | Master |
| 10 | M31 | Esra da Pedra | Mage | 26 | 34,4 | 2200 ± 202 | 14-8 | Master |
| 11 | R44 | Dália da Geada | Rogue | 28 | 34,8 | 2200 ± 207 | 15-6 | Master |
| 12 | R45 | Iago do Sal | Rogue | 28 | 33,9 | 2188 ± 194 | 13-9 | Master |
| 13 | W92 | Gael do Sal | Warrior | 23 | 34,7 | 2182 ± 208 | 10-8 | Master |
| 14 | W91 | Cirro do Abismo | Warrior | 26 | 34,2 | 2177 ± 189 | 13-6 | Master |
| 15 | R11 | Faro do Lobo | Rogue | 25 | 35,4 | 2140 ± 210 | 9-7 | Master |
| 16 | M27 | Brisa do Rochedo | Mage | 24 | 35,4 | 2139 ± 204 | 9-7 | Obsidian |
| 17 | W87 | Kael da Areia | Warrior | 25 | 33,2 | 2090 ± 198 | 13-8 | Obsidian |
| 18 | M45 | Wren do Trovão | Mage | 25 | 33,6 | 2086 ± 193 | 15-7 | Obsidian |
| 19 | W86 | Oriel do Lobo | Warrior | 24 | 32,9 | 2075 ± 193 | 11-7 | Obsidian |
| 20 | W88 | Bruma do Abismo | Warrior | 26 | 33,6 | 2031 ± 199 | 13-8 | Obsidian |
| 40 | M16 | Dorin da Lança | Mage | 24 | 32,1 | 1874 ± 191 | 9-9 | Sapphire |
| 60 | W78 | Bruma do Ermo | Warrior | 24 | 31,5 | 1716 ± 201 | 11-6 | Emerald |
| 80 | W67 | Caeli do Junco | Warrior | 21 | 30,7 | 1606 ± 197 | 8-10 | Platinum |
| 100 | R35 | Tália do Trovão | Rogue | 23 | 30,7 | 1504 ± 191 | 10-9 | Gold |
| 120 | W02 | Bruma da Aurora | Warrior | 23 | 28,4 | 1413 ± 197 | 8-9 | Gold |
| 140 | W15 | Faro do Sal | Warrior | 20 | 29,1 | 1278 ± 200 | 7-9 | Silver |
| 160 | W52 | Cirro do Ermo | Warrior | 23 | 28,0 | 1157 ± 186 | 7-14 | Bronze |
| 177 | W57 | Caeli do Penhasco | Warrior | 20 | 27,8 | 995 ± 202 | 6-12 | Iron |
| 178 | R02 | Vesna do Lume | Rogue | 21 | 28,8 | 983 ± 203 | 8-11 | Iron |
| 179 | W44 | Cirro do Vau | Warrior | 22 | 28,6 | 969 ± 199 | 7-12 | Iron |
| 180 | W14 | Fírio da Maré | Warrior | 21 | 28,0 | 967 ± 204 | 6-11 | Iron |
| 181 | W05 | Nilo do Rochedo | Warrior | 21 | 27,9 | 925 ± 202 | 3-13 | Iron |
| 182 | W12 | Jora da Geada | Warrior | 20 | 27,8 | 892 ± 210 | 6-10 | Iron |
| 183 | W51 | Maren da Brasa | Warrior | 21 | 27,9 | 875 ± 211 | 5-11 | Iron |
| 184 | W09 | Wren do Lume | Warrior | 18 | 28,0 | 727 ± 215 | 3-17 | Iron |
| 185 | W65 | Gael da Areia | Warrior | 3 | 5,6 | 720 ± 222 | 4-12 | Iron |
| 186 | M09 | Vesna do Eclipse | Mage | 2 | 4,3 | 430 ± 263 | 0-15 | Iron |

(Top 20, uma a cada 20 posições e os 10 últimos. ★ = Definitive Master.)

### Proposta de limites percentuais

| rank | percentil mínimo | gladiadores com 186 | classes |
|---|---|---|---|
| Iron | 0,0 | 19 | M3 R4 W12 |
| Bronze | 10,0 | 22 | M1 R7 W14 |
| Silver | 22,0 | 24 | M7 R3 W14 |
| Gold | 35,0 | 24 | M1 R4 W19 |
| Platinum | 48,0 | 22 | M8 R7 W7 |
| Emerald | 60,0 | 19 | M4 R6 W9 |
| Sapphire | 70,0 | 17 | M7 R5 W5 |
| Diamond | 79,0 | 13 | M6 R3 W4 |
| Obsidian | 86,0 | 11 | M5 W6 |
| Master | 92,0 | 7 | M2 R3 W2 |
| International Master | 96,0 | 5 | M1 R2 W2 |
| Distinguished Master | 98,5 | 3 | R1 W2 |

## 4. Comparação ampliada (holdout novo)

Treino: as 1631 partidas da amostra e da calibração, na ordem em que aconteceram (e em 29 ordens embaralhadas). Holdout: 150 duplas que nunca tinham jogado.

| sistema | log-loss holdout | Brier | acerto | ECE | estabilidade (Spearman) |
|---|---|---|---|---|---|
| *moeda* | 0,693 | 0,250 | 0,000 | 0,500 | — |
| *OP logístico* | 0,567 | 0,200 | 0,651 | 0,122 | — |
| *Bradley-Terry em lote* | 0,572 | 0,198 | 0,673 | 0,059 | — |
| Glicko-2 τ=0.3 plano | 0,603 ± 0,009 | 0,210 | 0,651 | 0,060 | 0,968 |
| Glicko-2 τ=0.3 OP | 0,549 ± 0,007 | 0,190 | 0,683 | 0,057 | 0,991 |
| Glicko-2 τ=0.6 plano | 0,603 ± 0,009 | 0,210 | 0,651 | 0,060 | 0,968 |
| Glicko-2 τ=0.6 OP | 0,549 ± 0,007 | 0,190 | 0,683 | 0,057 | 0,991 |
| Glicko-2 τ=1.0 plano | 0,603 ± 0,009 | 0,210 | 0,651 | 0,060 | 0,968 |
| Glicko-2 τ=1.0 OP | 0,549 ± 0,007 | 0,190 | 0,683 | 0,057 | 0,991 |
| TrueSkill β=σ/2 plano | 0,592 ± 0,010 | 0,207 | 0,651 | 0,064 | 0,970 |
| TrueSkill β=σ/2 OP | 0,547 ± 0,009 | 0,190 | 0,685 | 0,058 | 0,990 |
| TrueSkill β=σ/4 plano | 0,564 ± 0,016 | 0,198 | 0,664 | 0,062 | 0,968 |
| TrueSkill β=σ/4 OP | 0,544 ± 0,015 | 0,191 | 0,680 | 0,051 | 0,981 |
| TrueSkill β=σ/8 plano | 0,570 ± 0,024 | 0,200 | 0,673 | 0,081 | 0,970 |
| TrueSkill β=σ/8 OP | 0,569 ± 0,024 | 0,198 | 0,677 | 0,082 | 0,976 |

### Log-loss do holdout por estrato (ordem cronológica)

| sistema | h2_aleatorio | h2_classes | h2_vizinhos |
|---|---|---|---|
| Glicko-2 τ=0.6 plano | 0,376 | 0,659 | 0,698 |
| Glicko-2 τ=0.6 OP | 0,309 | 0,633 | 0,682 |
| TrueSkill β=σ/2 plano | 0,347 | 0,653 | 0,696 |
| TrueSkill β=σ/2 OP | 0,295 | 0,629 | 0,680 |

### Convergência (log-loss prequencial por janela de partidas, ordem cronológica)

- Glicko-2 τ=0.6 plano (janelas de 203): 0,745 → 0,792 → 0,784 → 0,759 → 0,726 → 0,706 → 0,688 → 0,668 → 0,653
- Glicko-2 τ=0.6 OP (janelas de 203): 0,649 → 0,681 → 0,684 → 0,664 → 0,641 → 0,631 → 0,616 → 0,598 → 0,570
- TrueSkill β=σ/2 plano (janelas de 203): 0,752 → 0,816 → 0,814 → 0,781 → 0,738 → 0,712 → 0,689 → 0,664 → 0,647
- TrueSkill β=σ/2 OP (janelas de 203): 0,670 → 0,718 → 0,724 → 0,698 → 0,666 → 0,648 → 0,628 → 0,605 → 0,577

### Sensibilidade a sequências (resultados injetados sobre o estado calibrado)

| sistema | 5 vitórias contra iguais | 5 contra muito mais fracos | 6 alternados | 5 derrotas e 5 vitórias |
|---|---|---|---|---|
| Glicko-2 τ=0.6 plano | 0,42 dp (93º → 62º) | 0,05 dp (93º → 91º) | 0,00 dp (93º → 93º) | 0,03 dp (93º → 92º) |
| Glicko-2 τ=0.6 OP | 0,26 dp (93º → 71º) | 0,01 dp (93º → 90º) | -0,00 dp (93º → 93º) | 0,02 dp (93º → 90º) |
| TrueSkill β=σ/2 plano | 0,34 dp (93º → 69º) | 0,02 dp (93º → 92º) | 0,00 dp (93º → 93º) | 0,00 dp (93º → 93º) |
| TrueSkill β=σ/2 OP | 0,27 dp (93º → 71º) | 0,00 dp (93º → 92º) | 0,00 dp (93º → 93º) | 0,01 dp (93º → 92º) |

### Incerteza

- Glicko-2 τ=0.6 plano: Spearman entre incerteza final e menos partidas jogadas = 0,859; ECE do holdout 0,060.
- Glicko-2 τ=0.6 OP: Spearman entre incerteza final e menos partidas jogadas = 0,734; ECE do holdout 0,057.
- TrueSkill β=σ/2 plano: Spearman entre incerteza final e menos partidas jogadas = 0,838; ECE do holdout 0,064.
- TrueSkill β=σ/2 OP: Spearman entre incerteza final e menos partidas jogadas = 0,755; ECE do holdout 0,058.

## 5. Jogadores artificiais

Hipótese de tempo humano: 3 minutos por partida ranqueada (o CPU real está na coluna própria). Cada jogador pega um gladiador legítimo da população (o gêmeo NPC fica fora do matchmaking), começa do centro sem priori e joga com a IA estratégica; entre as partidas dele, o mundo joga NPC × NPC.

| carreira | gladiador | partidas (h) | V-D | posicionamento | 2h | 5h | 10h | 20h | final | CPU |
|---|---|---|---|---|---|---|---|---|---|---|
| carreira_M03 | M03 mage nv 19 OP 28,3 | 400 (20,0) | 199-201 | 4V → Bronze (12) | Bronze (16) | Bronze (16) | Bronze (16) | Bronze (15) | Bronze (15), 1144 ± 123 | 47 min |
| carreira_M11 | M11 mage nv 25 OP 32,2 | 400 (20,0) | 204-196 | 7V → Sapphire (78) | Diamond (81) | Diamond (80) | Diamond (83) | Diamond (82) | Diamond (82), 1918 ± 123 | 50 min |
| carreira_R31 | R31 rogue nv 27 OP 36,1 | 100 (5,0) | 52-35 (13 sem resultado) | 8V → International Master (97) | International Master (97) | International Master (98) | — | — | International Master (98), 2364 ± 132 | 36 min |
| carreira_W26 | W26 warrior nv 22 OP 29,8 | 400 (20,0) | 198-202 | 5V → Platinum (58) | Platinum (53) | Platinum (52) | Platinum (54) | Gold (47) | Gold (47), 1529 ± 123 | 47 min |

| carreira | gêmeo NPC calibrado | P(vitória) média depois do posicionamento | oponentes distintos | repetidos nas últimas 10 | subidas / descidas de rank | percentil depois do posicionamento | DP do rating na 2ª metade | partidas até a faixa |
|---|---|---|---|---|---|---|---|---|
| carreira_M03 | Iron (9), 1027 ± 208 | 0,500 | 62 | 73 | 0 / 0 | 12–20 (Bronze) | 28,8 | 11 |
| carreira_M11 | Diamond (84), 1928 ± 198 | 0,500 | 46 | 102 | 1 / 0 | 76–86 (Sapphire, Diamond) | 20,3 | 11 |
| carreira_R31 | International Master (98), 2367 ± 222 | 0,523 | 18 | 54 | 0 / 0 | 96–98 (International Master) | 12,2 | 11 |
| carreira_W26 | Platinum (50), 1555 ± 192 | 0,503 | 82 | 62 | 34 / 36 | 45–66 (Gold, Platinum, Emerald) | 19,6 | 13 |

## 6. A decisão

**Glicko-2, com a priori fraca do OP** (`src/ranked/sistema.py`).

- Previsão: empate com o TrueSkill no holdout ampliado (diferença dentro do ruído entre as ordens de treino).
- Convergência: o Glicko-2 erra menos nas primeiras janelas prequenciais — é o trecho que importa nas 10 partidas de posicionamento.
- Estabilidade: levemente maior com o Glicko-2.
- Incerteza: o RD é em pontos de rating (a tela mostra ± 2 RD); a inatividade cresce a incerteza pela volatilidade de cada gladiador.
- Sequências: os dois reagem igual — sobem com vitórias contra iguais e quase nada contra muito mais fracos.
- Complexidade: o TrueSkill 1 × 1 é mais curto (forma fechada); o Glicko-2 tem uma iteração (Illinois), conferida contra o exemplo publicado. O TrueSkill foi feito para times e o nome é marca da Microsoft; nada disso pesa num duelo 1 × 1, mas também não há ganho.
- A priori fraca do OP ajuda os dois: sem ela, o holdout ampliado piora de 0,549 para 0,603 (Glicko-2).

## 7. Problemas encontrados

- **Volatilidade inerte.** Com uma partida por período, o τ do Glicko-2 não muda nada (0,3, 0,6 e 1,0 dão o mesmo resultado): na prática ele funciona como Glicko-1.
- **Entre builds parecidas, a sorte manda.** Nas duplas de OP muito próximo (|ΔOP| < 0,5) o favorito venceu 51%; nas repetidas com três seeds, menos da metade teve o mesmo vencedor. O meio da Ladder é ruidoso: 1 RD cobre ~19 posições.
- **Custo concentrado no topo.** Duelos entre builds fortes são mais longos e os impasses custam ~60 s cada: a carreira do R31 custou ~3× mais CPU por partida, e por isso parou em 100 partidas (5 h) em vez de 400.
- **Duplas que nunca terminam.** Uma partida da amostra e uma da calibração bateram o limite técnico (500 rodadas). No topo é frequente: na carreira do R31, 13 de 100 partidas terminaram sem vencedor, todas contra Magos de topo (M32 e M33 seis vezes cada, M27 uma), e R31 × M33 bateu o limite em todas as seeds testadas (~60 s de CPU cada). Isso travava duas coisas, corrigidas nesta fase: o jogador artificial, que repetia a dupla com outra seed, e o mundo orgânico, que replanejava a mesma dupla para sempre. Agora a partida sem vencedor não muda rating, fica no histórico e consome a vaga.
- **Rank piscando na fronteira.** No meio da Ladder, um gladiador que mora perto de um limite troca de rank a toda hora (W26: 70 trocas em 390 partidas, entre Gold, Platinum e Emerald). Uma histerese — só mudar de rank ao passar o limite com folga — resolveria; não está no contrato aprovado e fica proposta.
- **Repetição de adversários.** Com 186 gladiadores, 15–25% das partidas repetem um oponente das últimas 10, e 400 partidas veem 46–82 adversários distintos. No topo é pior: o R31 viu 18 adversários em 100 partidas (o M32, várias vezes seguidas).
- **Piso da incerteza.** Com uma partida por período o RD estabiliza em ~62 (a tela mostra ± 123) e não cai mais: é a volatilidade somada a cada partida.
- **Contra o jogador, a partida sem fim não tem regra.** O duelo humano × IA não tem limite de rodadas; só a rendição encerra uma dupla que não termina. O motor não tem empate, e a regra é decisão de design pendente.
