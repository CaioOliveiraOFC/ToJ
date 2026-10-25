# Copa Arena 03 — todos contra todos

Gerado por `tools/arena_copa_03_round_robin.py`. Os 64 gladiadores da Copa 03, reconstruídos dos snapshots, em todos os 2016 pares, 40 duelos por par (metade com os lados trocados), com a mesma `PoliticaCopa` e o mesmo motor da Copa. 80640 duelos, 0 inconclusivos no limite técnico, 28.2 rodadas por duelo em média.

> Correlação não é causa: perfil, política, RNG da jornada e build vêm juntos em cada gladiador. O OP é o medido na geração, contra o boneco fixo da Arena.

## Resumo

- **O OP explica 48% da variação da força real** (R² linear da taxa de vitória contra o OP; Spearman 0.65). Cada ponto de OP vale +21.0% de taxa de vitória.
- O de OP maior vence 69.7% dos duelos, em média, nos pares de OP diferente.
- 1326 dos 2016 pares (66%) são decididos pela build (um lado vence 80% ou mais); 245 (12%) são moeda (40–60%).
- 343 confrontos têm o OP menor vencendo 70% ou mais; 510 ciclos pedra-papel-tesoura (A vence B, B vence C, C vence A, cada um com 60% ou mais).
- A Copa MD1 e o todos-contra-todos concordam em parte: Spearman 0.61 entre vitórias na Copa e taxa aqui. O campeão, fer (W64), é o 1º mais forte; 4 dos 8 mais fortes chegaram às quartas.

## O ranking robusto

Força de Bradley-Terry (log, média zero) e taxa de vitória contra os outros 63. "Previsto" é a taxa que o OP prevê pelo ajuste linear; "resíduo" é o que a build rende acima (+) ou abaixo (−) disso.

| # | Gladiador | Perfil/política | OP | Taxa | Previsto | Resíduo | Força BT | Canais | Deck |
|---|---|---|---|---|---|---|---|---|---|
| 1 | fer (W64) | Moderado/survival · preench. | 29.98 | 94.4% | 70.9% | +23.5% | +3.39 | defesa, sustento | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo |
| 2 | gafallen (W37) | Moderado/economy | 29.87 | 89.5% | 68.5% | +21.0% | +2.73 | sustento | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda |
| 3 | lubatv (W23) | Moderado/survival | 29.17 | 88.5% | 53.9% | +34.5% | +2.62 | crítico, sustento | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável |
| 4 | MeikodRJ (W26) | Moderado/survival | 29.75 | 87.7% | 66.1% | +21.6% | +2.54 | sustento | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno |
| 5 | DavyJones (W29) | Moderado/survival | 29.98 | 85.3% | 70.9% | +14.4% | +2.31 | defesa, sustento | Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo |
| 6 | Smzinho (W35) | Moderado/offense | 29.75 | 82.9% | 66.1% | +16.9% | +2.10 | controle | Cutelada, Mira Calma, Veterania, Estocada Seca |
| 7 | tioorochitwitch (W63) | Moderado/economy · preench. | 29.41 | 80.5% | 58.8% | +21.7% | +1.91 | defesa, sustento | Golpe Poderoso, Investida, Postura de Muro, Baluarte |
| 8 | jovirone (W22) | Conservador/economy | 29.52 | 80.0% | 61.2% | +18.8% | +1.87 | sustento | Marca do Açougueiro, Quebra-Guarda, Disciplina de Forja, Sangue nos Olhos |
| 9 | RNakano (W42) | Moderado/economy | 29.64 | 77.9% | 63.6% | +14.2% | +1.70 | sustento | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja |
| 10 | sofiaespanha (W56) | Moderado/economy · preench. | 29.29 | 77.3% | 56.4% | +21.0% | +1.67 | defesa, controle | Soco de Placa, Passo Lateral, Quebra-Guarda, Baluarte |
| 11 | XANDAOOGOD (W47) | Hardcore/survival | 29.64 | 76.9% | 63.6% | +13.3% | +1.64 | defesa | Esmagar, Mira Calma, Leitura de Terreno, Veterania |
| 12 | LuquEt4 (W34) | Moderado/offense | 29.87 | 76.4% | 68.5% | +7.9% | +1.60 | crítico | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão |
| 13 | liminhag0d (W59) | Moderado/offense · preench. | 29.64 | 75.4% | 63.6% | +11.7% | +1.53 | crítico, controle | Golpe Poderoso, Investida, Estocada Seca, Guarda Alta |
| 14 | frttt (W60) | Moderado/economy · preench. | 29.52 | 72.5% | 61.2% | +11.2% | +1.33 | sustento | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca |
| 15 | Neskwga (W38) | Moderado/economy | 29.41 | 71.7% | 58.8% | +12.9% | +1.28 | defesa, sustento | Golpe Poderoso, Mira Calma, Escudo Protetor, Baluarte |
| 16 | NOBRU (W40) | Moderado/economy | 29.75 | 70.2% | 66.1% | +4.1% | +1.18 | sustento | Cutelada, Investida, Postura de Muro, Imortal |
| 17 | Tenz (W08) | Conservador/survival | 28.71 | 70.0% | 44.2% | +25.8% | +1.17 | crítico, sustento | Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego |
| 18 | furq (W28) | Moderado/survival | 29.52 | 69.0% | 61.2% | +7.8% | +1.11 | defesa, controle, sustento | Golpe Poderoso, Quebra-Guarda, Guarda Cruzada, Areia no Chão |
| 19 | PaulinhoLOKObr (W46) | Hardcore/survival | 28.48 | 68.5% | 39.4% | +29.1% | +1.07 | defesa, sustento | Tremor de Bigorna, Quebra-Guarda, Respirar Fundo, Baluarte |
| 20 | yeTz (W39) | Moderado/economy | 29.87 | 66.8% | 68.5% | -1.7% | +0.97 | sustento | Paciência do Coveiro, Quebra-Guarda, Postura de Muro, Cutelada |
| 21 | mount (W25) | Moderado/survival | 29.52 | 64.2% | 61.2% | +3.0% | +0.82 | defesa, sustento | Golpe Poderoso, Soco de Placa, Couro Batido, Disciplina de Forja |
| 22 | dona (W01) | Conservador/survival | 29.06 | 63.8% | 51.5% | +12.3% | +0.79 | sustento | Cutelada, Investida, Respirar Fundo, Grito de Guerra |
| 23 | brtt (W13) | Conservador/offense | 29.98 | 62.3% | 70.9% | -8.6% | +0.70 | controle, sustento | Respirar Fundo, Mira Calma, Estocada Seca, Soco de Placa |
| 24 | aspaszin (W27) | Moderado/survival | 29.29 | 59.6% | 56.4% | +3.2% | +0.54 | crítico, defesa, sustento | Golpe Poderoso, Quebra-Guarda, Fôlego de Marcha, Respirar Fundo |
| 25 | Gaules (W36) | Moderado/offense | 29.98 | 57.0% | 70.9% | -13.9% | +0.39 | crítico, controle | Mão Dupla, Peso do Machado, Estocada Seca, Fúria |
| 26 | aXtLOL (W43) | Moderado/economy | 29.75 | 56.3% | 66.1% | -9.8% | +0.35 | sustento | Travar o Pulso, Mira Calma, Ferro Contra Ferro, Ritmo de Duelo |
| 27 | alanzoka (W02) | Conservador/survival | 28.37 | 55.0% | 37.0% | +18.0% | +0.27 | defesa, sustento | Golpe Poderoso, Respirar Fundo, Soco de Placa, Guarda Cruzada |
| 28 | tteuw (W19) | Conservador/economy | 29.17 | 53.6% | 53.9% | -0.3% | +0.20 | defesa, sustento | Golpe Poderoso, Mira Calma, Tomar Fôlego, Escudo Protetor |
| 29 | babi (W53) | Hardcore/economy | 28.48 | 53.0% | 39.4% | +13.6% | +0.16 | sustento | Rasgo de Gancho, Postura de Muro, Sangue nos Olhos, Marca do Açougueiro |
| 30 | bakzera (W30) | Moderado/offense | 29.98 | 51.7% | 70.9% | -19.2% | +0.09 | crítico, controle | Golpe Duplo, Mira Calma, Provocação, Veterania |
| 31 | xandfps (W20) | Conservador/economy | 28.48 | 50.6% | 39.4% | +11.2% | +0.03 | sustento | Mão Dupla, Mira Calma, Escudo Protetor, Peso do Machado |
| 32 | Felps (W31) | Moderado/offense | 29.64 | 50.2% | 63.6% | -13.5% | +0.00 | crítico, controle | Sangue nos Olhos, Quebra-Guarda, Travar o Pulso, Marca do Açougueiro |
| 33 | calango (W44) | Hardcore/survival | 28.60 | 49.9% | 41.8% | +8.1% | -0.01 | sustento | Golpe Poderoso, Quebra-Guarda, Imortal, Tomar Fôlego |
| 34 | fnxLNTC (W24) | Moderado/survival | 29.52 | 49.8% | 61.2% | -11.4% | -0.02 | defesa, sustento | Golpe Poderoso, Investida, Couraça Improvisada, Berro de Ferro |
| 35 | YoDa (W33) | Moderado/offense | 29.41 | 48.8% | 58.8% | -10.0% | -0.07 | controle | Mão Dupla, Tremor de Bigorna, Estocada Seca, Lâmina Assentada |
| 36 | casimito (W55) | Moderado/offense · preench. | 29.75 | 48.5% | 66.1% | -17.6% | -0.09 | crítico, controle | Peso do Machado, Esmagar, Provocação, Disciplina de Forja |
| 37 | SkipNhO (W52) | Hardcore/economy | 28.02 | 47.1% | 29.7% | +17.4% | -0.17 | defesa, sustento | Golpe Poderoso, Postura de Muro, Pisada de Ferro, Juramento da Muralha |
| 38 | coldzin (W41) | Moderado/economy | 29.64 | 46.3% | 63.6% | -17.3% | -0.22 | sustento | Pancada na Nuca, Postura de Muro, Cutelada, Tremor de Bigorna |
| 39 | sacy (W16) | Conservador/economy | 29.52 | 41.9% | 61.2% | -19.4% | -0.47 | sustento | Golpe Devastador, Mira Calma, Escudo Protetor, Silêncio do Veterano |
| 40 | yayahuz (W07) | Conservador/survival | 27.79 | 39.6% | 24.8% | +14.7% | -0.60 | defesa, sustento | Golpe Poderoso, Mira Calma, Sede de Batalha, Tomar Fôlego |
| 41 | PlayHard (W18) | Conservador/economy | 28.02 | 39.1% | 29.7% | +9.4% | -0.63 | — | Resistência Heróica, Mira Calma, Quebra-Guarda, Gancho e Corda |
| 42 | TheBurntPeanut (W54) | Conservador/economy · preench. | 29.64 | 37.0% | 63.6% | -26.7% | -0.76 | — | Mão Dupla, Mira Calma, Provocação, Grito de Guerra |
| 43 | jukes (W03) | Conservador/survival | 28.14 | 36.8% | 32.1% | +4.7% | -0.76 | defesa, sustento | Golpe Poderoso, Respirar Fundo, Mira Calma, Leitura de Terreno |
| 44 | hastad (W50) | Hardcore/offense | 28.60 | 36.5% | 41.8% | -5.3% | -0.78 | crítico, defesa, controle | Mão Dupla, Mira Calma, Estocada Seca, Couro Batido |
| 45 | Bisteconee (W49) | Hardcore/offense | 28.60 | 36.4% | 41.8% | -5.4% | -0.79 | controle | Cutelada, Mira Calma, Areia no Chão, Leitura de Terreno |
| 46 | blackoutz (W12) | Conservador/offense | 27.79 | 31.8% | 24.8% | +7.0% | -1.07 | crítico, defesa | Golpe Duplo, Mira Calma, Baluarte, Encarar |
| 47 | loud_thurzin (W32) | Moderado/offense | 29.87 | 31.2% | 68.5% | -37.3% | -1.11 | crítico, controle | Marca do Caçador, Golpe Devastador, Guarda Alta, Grito Curto |
| 48 | Tealzlol (W61) | Conservador/survival · preench. | 28.14 | 29.7% | 32.1% | -2.4% | -1.20 | crítico, sustento | Golpe Poderoso, Mira Calma, Fôlego de Marcha, Ritmo de Duelo |
| 49 | Hayashii (W45) | Hardcore/survival | 27.91 | 29.2% | 27.3% | +2.0% | -1.23 | defesa, sustento | Golpe Poderoso, Quebra-Guarda, Quebra-Ossos, Baluarte |
| 50 | Bagi (W48) | Hardcore/survival | 27.79 | 28.6% | 24.8% | +3.7% | -1.27 | defesa, sustento | Golpe Poderoso, Respirar Fundo, Mira Calma, Olho Treinado |
| 51 | gabepeixe (W62) | Conservador/offense · preench. | 28.60 | 25.8% | 41.8% | -16.0% | -1.46 | crítico, controle | Fúria, Soco de Placa, Travar o Pulso, Tremor de Bigorna |
| 52 | RazaH (W15) | Conservador/offense | 29.06 | 24.1% | 51.5% | -27.4% | -1.57 | crítico, controle | Marca do Caçador, Grito Curto, Pausa Útil, Mão Dupla |
| 53 | suetam1v4 (W51) | Hardcore/offense | 27.91 | 24.0% | 27.3% | -3.2% | -1.58 | — | Golpe Duplo, Tremor de Bigorna, Areia no Chão, Postura de Muro |
| 54 | Forever (W11) | Conservador/offense | 28.71 | 21.7% | 44.2% | -22.6% | -1.75 | crítico, defesa, controle | Grito Curto, Peso do Machado, Couro Batido, Última Carta |
| 55 | JonVlogs (W58) | Conservador/economy · preench. | 28.60 | 21.1% | 41.8% | -20.7% | -1.79 | defesa, sustento | Golpe Poderoso, Investida, Guarda Alta, Couraça Improvisada |
| 56 | belrodrigues (W04) | Conservador/survival | 27.91 | 20.4% | 27.3% | -6.9% | -1.84 | defesa | Fúria, Investida, Fôlego de Marcha, Mira Calma |
| 57 | G0ularte (W14) | Conservador/offense | 28.02 | 20.0% | 29.7% | -9.6% | -1.87 | crítico, controle, sustento | Mira Calma, Investida, Tomar Fôlego, Areia no Chão |
| 58 | Patriota (W10) | Conservador/offense | 29.87 | 19.0% | 68.5% | -49.5% | -1.95 | controle | Pisada de Ferro, Investida de Aríete, Pancada na Nuca, Pausa Útil |
| 59 | k13tv (W17) | Conservador/economy | 27.91 | 15.3% | 27.3% | -12.0% | -2.26 | defesa, sustento | Golpe Poderoso, Mira Calma, Fio no Rebite, Guarda Cruzada |
| 60 | brino (W09) | Conservador/offense | 28.02 | 14.8% | 29.7% | -14.9% | -2.30 | crítico, controle | Cutelada, Investida, Areia no Chão, Fúria |
| 61 | Baiano (W06) | Conservador/survival | 27.91 | 14.0% | 27.3% | -13.3% | -2.38 | defesa, sustento | Tomar Fôlego, Mira Calma, Ritmo de Duelo, Cutelada |
| 62 | boltz (W21) | Conservador/economy | 27.79 | 13.7% | 24.8% | -11.1% | -2.40 | sustento | Investida, Soco de Placa, Leitura de Terreno, Olho de Ferreiro |
| 63 | Dilera (W05) | Conservador/survival | 27.91 | 11.2% | 27.3% | -16.1% | -2.65 | defesa, sustento | Golpe Poderoso, Investida, Couraça Improvisada, Tomar Fôlego |
| 64 | Coringa (W57) | Conservador/offense · preench. | 27.79 | 8.3% | 24.8% | -16.6% | -2.99 | — | Cutelada, Golpe Devastador, Areia no Chão, Escudo Protetor |

## A sinergia: quem rende acima e abaixo do próprio OP

### Mais acima do OP

- **lubatv (W23)**, OP 29.17: taxa 88.5% contra 53.9% previstos (+34.5%). HP 5275, MP 908, ST 547, DF 527, AG 114; crítico, sustento; Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável.
- **PaulinhoLOKObr (W46)**, OP 28.48: taxa 68.5% contra 39.4% previstos (+29.1%). HP 5803, MP 766, ST 552, DF 484, AG 133; defesa, sustento; Tremor de Bigorna, Quebra-Guarda, Respirar Fundo, Baluarte.
- **Tenz (W08)**, OP 28.71: taxa 70.0% contra 44.2% previstos (+25.8%). HP 5519, MP 1050, ST 601, DF 509, AG 121; crítico, sustento; Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego.
- **fer (W64)**, OP 29.98: taxa 94.4% contra 70.9% previstos (+23.5%). HP 5977, MP 1103, ST 654, DF 503, AG 142; defesa, sustento; Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo.
- **tioorochitwitch (W63)**, OP 29.41: taxa 80.5% contra 58.8% previstos (+21.7%). HP 7189, MP 736, ST 599, DF 604, AG 134; defesa, sustento; Golpe Poderoso, Investida, Postura de Muro, Baluarte.
- **MeikodRJ (W26)**, OP 29.75: taxa 87.7% contra 66.1% previstos (+21.6%). HP 4969, MP 829, ST 611, DF 530, AG 106; sustento; Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno.
- **gafallen (W37)**, OP 29.87: taxa 89.5% contra 68.5% previstos (+21.0%). HP 3973, MP 763, ST 422, DF 369, AG 93; sustento; Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda.
- **sofiaespanha (W56)**, OP 29.29: taxa 77.3% contra 56.4% previstos (+21.0%). HP 7757, MP 836, ST 593, DF 529, AG 121; defesa, controle; Soco de Placa, Passo Lateral, Quebra-Guarda, Baluarte.

### Mais abaixo do OP

- **Patriota (W10)**, OP 29.87: taxa 19.0% contra 68.5% previstos (-49.5%). HP 4779, MP 855, ST 621, DF 473, AG 110; controle; Pisada de Ferro, Investida de Aríete, Pancada na Nuca, Pausa Útil.
- **loud_thurzin (W32)**, OP 29.87: taxa 31.2% contra 68.5% previstos (-37.3%). HP 5110, MP 963, ST 538, DF 477, AG 135; crítico, controle; Marca do Caçador, Golpe Devastador, Guarda Alta, Grito Curto.
- **RazaH (W15)**, OP 29.06: taxa 24.1% contra 51.5% previstos (-27.4%). HP 5285, MP 537, ST 497, DF 400, AG 93; crítico, controle; Marca do Caçador, Grito Curto, Pausa Útil, Mão Dupla.
- **TheBurntPeanut (W54)**, OP 29.64: taxa 37.0% contra 63.6% previstos (-26.7%). HP 5364, MP 1053, ST 593, DF 506, AG 132; sem canal; Mão Dupla, Mira Calma, Provocação, Grito de Guerra.
- **Forever (W11)**, OP 28.71: taxa 21.7% contra 44.2% previstos (-22.6%). HP 5225, MP 842, ST 623, DF 457, AG 110; crítico, defesa, controle; Grito Curto, Peso do Machado, Couro Batido, Última Carta.
- **JonVlogs (W58)**, OP 28.60: taxa 21.1% contra 41.8% previstos (-20.7%). HP 6314, MP 708, ST 538, DF 485, AG 116; defesa, sustento; Golpe Poderoso, Investida, Guarda Alta, Couraça Improvisada.
- **sacy (W16)**, OP 29.52: taxa 41.9% contra 61.2% previstos (-19.4%). HP 7520, MP 786, ST 593, DF 522, AG 132; sustento; Golpe Devastador, Mira Calma, Escudo Protetor, Silêncio do Veterano.
- **bakzera (W30)**, OP 29.98: taxa 51.7% contra 70.9% previstos (-19.2%). HP 5860, MP 1020, ST 629, DF 520, AG 134; crítico, controle; Golpe Duplo, Mira Calma, Provocação, Veterania.

### O que acompanha o resíduo

Spearman de cada característica da build com a taxa de vitória, com o resíduo (o que sobra depois do OP) e com o próprio OP. Ordenado pelo peso no resíduo.

| Característica | Com a taxa | Com o resíduo | Com o OP |
|---|---|---|---|
| Passivas de vida | +0.32 | +0.45 | -0.04 |
| Cartas de status | -0.10 | -0.40 | +0.30 |
| Cartas de cura | +0.18 | +0.38 | -0.10 |
| Passivas de força | -0.25 | -0.36 | +0.08 |
| Passivas de roubo de vida | +0.22 | +0.33 | -0.03 |
| DF | +0.57 | +0.30 | +0.47 |
| Nível | +0.51 | +0.28 | +0.43 |
| HP máximo | +0.37 | +0.27 | +0.19 |
| MG | +0.47 | +0.25 | +0.40 |
| Passivas sem efeito no duelo | +0.23 | +0.24 | +0.01 |
| Passivas de defesa e redução | +0.08 | +0.23 | -0.19 |
| MP máximo | +0.33 | +0.22 | +0.31 |
| AG | +0.35 | +0.21 | +0.29 |
| Passivas de crítico | -0.02 | -0.19 | +0.19 |
| ST | +0.41 | +0.15 | +0.47 |
| Cartas de redução de dano | -0.01 | +0.14 | -0.21 |
| Passivas de mana | +0.17 | +0.13 | +0.04 |
| Cartas de dano | +0.01 | +0.08 | -0.09 |
| Cartas de buff | -0.04 | -0.07 | -0.01 |
| Passivas de agilidade e esquiva | -0.06 | -0.00 | -0.06 |

### Canais da build

| Canal | Builds | Taxa com | Taxa sem | Resíduo com | Resíduo sem |
|---|---|---|---|---|---|
| crítico | 18 | 45.2% | 51.9% | -6.1% | +2.4% |
| defesa | 26 | 48.4% | 51.1% | +4.2% | -2.9% |
| controle | 19 | 44.9% | 52.2% | -11.2% | +4.7% |
| sustento | 40 | 54.6% | 42.3% | +5.5% | -9.1% |

### Perfil e política

| Grupo | n | OP médio | Taxa | Resíduo |
|---|---|---|---|---|
| Conservador | 27 | 28.53 | 34.1% | -6.4% |
| Moderado | 27 | 29.66 | 67.8% | +3.7% |
| Hardcore | 10 | 28.40 | 45.0% | +7.3% |
| survival | 22 | 28.78 | 54.2% | +8.6% |
| offense | 21 | 29.09 | 40.3% | -11.8% |
| economy | 21 | 29.11 | 55.3% | +2.8% |

## Confrontos

Os 10 confrontos em que o OP menor vence com mais folga (343 no total com 70% ou mais):

| Vencedor (OP) | Perdedor (OP) | ΔOP contra | Taxa |
|---|---|---|---|
| yayahuz (27.79) | Patriota (29.87) | 2.07 | 95.0% |
| blackoutz (27.79) | Patriota (29.87) | 2.07 | 92.5% |
| Bagi (27.79) | Patriota (29.87) | 2.07 | 90.0% |
| blackoutz (27.79) | loud_thurzin (29.87) | 2.07 | 75.0% |
| Hayashii (27.91) | Patriota (29.87) | 1.96 | 75.0% |
| PlayHard (28.02) | Patriota (29.87) | 1.84 | 97.5% |
| SkipNhO (28.02) | Patriota (29.87) | 1.84 | 82.5% |
| G0ularte (28.02) | Patriota (29.87) | 1.84 | 75.0% |
| yayahuz (27.79) | Felps (29.64) | 1.84 | 70.0% |
| yayahuz (27.79) | TheBurntPeanut (29.64) | 1.84 | 70.0% |

Exemplos de ciclo:

- dona (W01) > yayahuz (W07) > brtt (W13) > dona (W01)
- dona (W01) > Tenz (W08) > brtt (W13) > dona (W01)
- dona (W01) > Tenz (W08) > Gaules (W36) > dona (W01)
- dona (W01) > Tenz (W08) > frttt (W60) > dona (W01)
- dona (W01) > PlayHard (W18) > brtt (W13) > dona (W01)
