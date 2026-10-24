# Copa Arena de Testes 01

Minicampeonato técnico da Arena PvP, gerado por `tools/arena_copa_teste.py`. Experimento de auditoria da matemática do duelo — não é medição de balanceamento nem população ranked.

- Oito bonecos descartáveis, montados em memória a partir do catálogo real e marcados como extraídos só para a interface da Arena. Nenhum save, slot ou coleção de gladiadores foi tocado.
- Seed principal: `20261023`. Chave: `random.Random(seed).shuffle` dos IDs. Seed de cada partida: os 8 primeiros bytes (big-endian) de `sha256(f"{seed}:{fase}:{índice}")`.
- Cada partida começa de uma preparação nova (`prepare_gladiator`): HP e MP cheios, sem recarga, sem efeito, sem consumível; nada atravessa de uma partida para outra.
- Política dos dois lados (`PoliticaCopa`): cura se HP ≤ 50%; senão buff ou redução ainda não ativos; senão status que o adversário não carrega; senão a primeira skill de dano legal; senão ataque básico. Lê só a `DuelView` e o próprio deck.
- Limite técnico do laço: 500 rodadas (inconclusivo, nunca empate). Nenhuma partida chegou perto.
- Cada partida rodou duas vezes, sem instrumentação e auditada, com a mesma seed; as duas coincidem em todas as verificações listadas no fim.

## Participantes

Atributos efetivos lidos do gladiador preparado. Overall Power: `src/sim/arena.py::overall_power(personagem).nivel_equivalente`, medido sem cache.

| ID | Nome | Classe | Nível | Overall Power | HP máx | MP máx | ST | MG | AG | DF | Equipamento | Skills | Passivas | Característica |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | Muralha | Guerreiro | 7 | 9.79 | 908 | 123 | 97 | 59 | 19 | 82 | Helmet: Capacete de Couro; Amulet: Amuleto de Concha; Weapon1: Clava Pesada; Weapon2: Espada Longa; Body: Placa Pesada; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Aço | Golpe Poderoso, Couraça Improvisada, Baluarte | Pele Grossa ×2, Postura Fechada ×2, Coração de Ferro, Sangue de Guerreiro | defesa: duas reduções de dano, Defesa e HP |
| G2 | Carrasco | Guerreiro | 7 | 10.54 | 868 | 123 | 103 | 59 | 19 | 74 | Helmet: Capacete de Couro; Amulet: Amuleto de Concha; Weapon1: Clava Pesada; Weapon2: Espada Longa; Body: Placa Pesada; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Aço | Golpe Poderoso, Grito de Guerra, Cutelada | Músculos de Aço ×2, Ódio Baixo ×2, Pulso Certeiro, Olho de Águia | dano físico: buff de Força, +MULT e crítico |
| G3 | Sentinela | Guerreiro | 6 | 9.79 | 790 | 111 | 89 | 53 | 18 | 64 | Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Clava Pesada; Weapon2: Lâmina Veloz; Body: Armadura de Couro; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Bronze | Golpe Poderoso, Investida, Pisada de Ferro | Olho de Caçador ×2, Pele de Sal, Músculos de Aço, Coração de Ferro | precisão e controle leve: atordoar e lentidão, resistência a status |
| G4 | Piromante | Mago | 6 | 9.79 | 652 | 259 | 53 | 98 | 14 | 51 | Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Pá de Batalha; Body: Jaqueta de Couro; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Bronze | Bola de Fogo, Míssil Mágico, Marca Ardente | Sangue de Vidente ×2, Ódio Baixo, Pulso Certeiro, Olho de Águia | dano mágico: Magia, +MULT, crítico e veneno |
| G5 | Curandeira | Mago | 7 | 9.96 | 760 | 310 | 59 | 113 | 16 | 58 | Helmet: Capacete de Couro; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Cajado Arcano; Body: Jaqueta de Couro; Legs: Bermuda de Couro; Hands: Escudo de Ferro; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Aço | Bola de Fogo, Drenar Vida, Pele de Quartzo | Coração de Ferro ×2, Respiração Contada ×2, Boca de Sangue, Reserva Arcana | sustentação: cura, roubo de vida, regeneração e reserva de MP |
| G6 | Geada | Mago | 6 | 9.79 | 652 | 280 | 53 | 95 | 14 | 51 | Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Pá de Batalha; Body: Jaqueta de Couro; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Bronze | Bola de Fogo, Lasca de Gelo, Palavra de Torpor | Mente Serena ×2, Pele de Sal, Sangue de Vidente, Olho de Caçador | controle: lentidão e névoa, com reserva de MP |
| G7 | Navalha | Ladino | 6 | 10.77 | 553 | 166 | 85 | 56 | 55 | 49 | Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Pá de Batalha; Body: Túnica do Fluxo; Legs: Saia de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Bronze; Ring2: Anel de Ouro | Ataque Furtivo, Respiração de Ladrão, Corte de Tendão | Olho de Águia ×2, Pulso Certeiro, Passo de Corça, Passos Leves | agilidade e crítico |
| G8 | Peçonha | Ladino | 7 | 10.07 | 635 | 186 | 95 | 63 | 57 | 55 | Helmet: Capacete de Couro; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Adaga do Assassino; Body: Manto de Sombra; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Bronze | Ataque Furtivo, Faro de Rua, Envenenar | Fio Serrilhado ×2, Boca de Sangue ×2, Passo de Corça, Coração de Ferro | atrito: veneno, sangramento e roubo de vida |

Overall Power — média **10.06**, mínimo **9.79**, máximo **10.77**; faixa pedida [9, 11]: todos dentro.

## Chave sorteada

```
Q1: Piromante (G4) × Geada (G6)
Q2: Muralha (G1) × Navalha (G7)
Q3: Peçonha (G8) × Carrasco (G2)
Q4: Sentinela (G3) × Curandeira (G5)
S1: vencedor Q1 × vencedor Q2
S2: vencedor Q3 × vencedor Q4
F: vencedor S1 × vencedor S2
```

## Quartas

### Quartas 1 — Piromante × Geada

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G4 | Piromante | Mago | 6 | 9.79 | Bola de Fogo, Míssil Mágico, Marca Ardente | dano mágico: Magia, +MULT, crítico e veneno |
| p2 | G6 | Geada | Mago | 6 | 9.79 | Bola de Fogo, Lasca de Gelo, Palavra de Torpor | controle: lentidão e névoa, com reserva de MP |

- Seed da partida: `7347509823717725885`
- Rodadas: **5**
- Vencedor: **Geada** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 12/652 (1.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Piromante | Geada |
|---|---|---|
| Dano causado (golpes + DoT) | 640 (640 + 0) | 895 (895 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 34 | 46 |
| Skills / ataques básicos | 4 / 0 | 5 / 0 |
| Acertos / erros | 3 / 1 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 5 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Égide de Piromante: absorveu 155 de dano por 76 MP
- Geada aplicou: slowed (rodada 1), slowed (rodada 4), clouded (rodada 4)
- Geada tentou sem sucesso: clouded (rodada 1), slowed (rodada 3)
- Égide de Geada: absorveu 111 de dano por 55 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Piromante (p1) | Geada (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Bola de Fogo — executada, dano 226, MP −9 | Palavra de Torpor — executada, dano 0, MP −9 | 652 / 426 | 250 / 252 |
| 2 | p2 → p1 (score) | Míssil Mágico — executada, dano 207, MP −8 | Bola de Fogo — executada, dano 306, MP −9 | 346 / 219 | 221 / 230 |
| 3 | p2 → p1 (score) | Bola de Fogo — executada, dano 0, MP −9 | Lasca de Gelo — executada, dano 283, MP −10 | 63 / 219 | 193 / 225 |
| 4 | p2 → p1 (score) | Míssil Mágico — executada, dano 207, MP −8 | Palavra de Torpor — executada, dano 0, MP −9 | 63 / 12 | 189 / 203 |
| 5 | p2 → p1 (score) | Bola de Fogo — cancelada por morte | Bola de Fogo — executada, dano 306, MP −9 | -243 / 12 | 163 / 199 |

### Quartas 2 — Muralha × Navalha

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G1 | Muralha | Guerreiro | 7 | 9.79 | Golpe Poderoso, Couraça Improvisada, Baluarte | defesa: duas reduções de dano, Defesa e HP |
| p2 | G7 | Navalha | Ladino | 6 | 10.77 | Ataque Furtivo, Respiração de Ladrão, Corte de Tendão | agilidade e crítico |

- Seed da partida: `2030327944903717010`
- Rodadas: **6**
- Vencedor: **Muralha** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 294/908 (32.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Muralha | Navalha |
|---|---|---|
| Dano causado (golpes + DoT) | 557 (557 + 0) | 614 (614 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 55 | 54 |
| Skills / ataques básicos | 5 / 1 | 5 / 1 |
| Acertos / erros | 3 / 0 | 4 / 0 |
| Críticos (dano) | 0 (0) | 2 (445) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Muralha ativou: Couraça Improvisada ×2, Baluarte ×1
- Navalha aplicou: slowed (rodada 3)
- Navalha ativou: Respiração de Ladrão ×2

Rodada a rodada:

| Rodada | Ordem (critério) | Muralha (p1) | Navalha (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −11 | Respiração de Ladrão — executada, dano 0, MP −10 | 908 / 553 | 112 / 156 |
| 2 | p2 → p1 (score) | Baluarte — executada, dano 0, MP −17 | Ataque Furtivo — executada, dano 258, MP −11 | 650 / 553 | 97 / 148 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 226, MP −8 | Corte de Tendão — executada, dano 106, MP −12 | 544 / 327 | 91 / 139 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 121 | Ataque básico — executada, dano 63 | 481 / 206 | 93 / 142 |
| 5 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −11 | Respiração de Ladrão — executada, dano 0, MP −10 | 481 / 206 | 84 / 135 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 210, MP −8 | Ataque Furtivo — executada, dano 187, MP −11 | 294 / -4 | 78 / 127 |

### Quartas 3 — Peçonha × Carrasco

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G8 | Peçonha | Ladino | 7 | 10.07 | Ataque Furtivo, Faro de Rua, Envenenar | atrito: veneno, sangramento e roubo de vida |
| p2 | G2 | Carrasco | Guerreiro | 7 | 10.54 | Golpe Poderoso, Grito de Guerra, Cutelada | dano físico: buff de Força, +MULT e crítico |

- Seed da partida: `4785977635327490906`
- Rodadas: **3**
- Vencedor: **Carrasco** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 481/868 (55.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Peçonha | Carrasco |
|---|---|---|
| Dano causado (golpes + DoT) | 387 (361 + 26) | 696 (696 + 0) |
| Cura (skill + roubo de vida) | 28 (0 + 28) | 0 (0 + 0) |
| MP gasto em ações | 48 | 37 |
| Skills / ataques básicos | 3 / 0 | 3 / 0 |
| Acertos / erros | 1 / 0 | 2 / 0 |
| Críticos (dano) | 1 (361) | 0 (0) |
| Agiu primeiro (rodadas) | 3 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Peçonha aplicou: poison (rodada 2)
- Peçonha tentou sem sucesso: bleed (rodada 3), poison (rodada 3)
- Peçonha ativou: Faro de Rua ×1
- Carrasco ativou: Grito de Guerra ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Peçonha (p1) | Carrasco (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Faro de Rua — executada, dano 0, MP −9 | Grito de Guerra — executada, dano 0, MP −16 | 635 / 868 | 177 / 107 |
| 2 | p1 → p2 (score) | Envenenar — executada, dano 0, MP −27 | Golpe Poderoso — executada, dano 336, MP −8 | 299 / 855 | 159 / 101 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 361, MP −12 | Cutelada — executada, dano 360, MP −13 | -33 / 481 | 162 / 90 |

### Quartas 4 — Sentinela × Curandeira

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G3 | Sentinela | Guerreiro | 6 | 9.79 | Golpe Poderoso, Investida, Pisada de Ferro | precisão e controle leve: atordoar e lentidão, resistência a status |
| p2 | G5 | Curandeira | Mago | 7 | 9.96 | Bola de Fogo, Drenar Vida, Pele de Quartzo | sustentação: cura, roubo de vida, regeneração e reserva de MP |

- Seed da partida: `7843339256714053718`
- Rodadas: **8**
- Vencedor: **Curandeira** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 202/760 (26.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Sentinela | Curandeira |
|---|---|---|
| Dano causado (golpes + DoT) | 821 (821 + 0) | 953 (953 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 263 (228 + 35) |
| MP gasto em ações | 52 | 74 |
| Skills / ataques básicos | 7 / 0 | 7 / 1 |
| Acertos / erros | 6 / 1 | 4 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 8 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Sentinela tentou sem sucesso: stun (rodada 2), stun (rodada 4), stun (rodada 6)
- Curandeira ativou: Pele de Quartzo ×2
- Égide de Curandeira: absorveu 143 de dano por 69 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Sentinela (p1) | Curandeira (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Golpe Poderoso — executada, dano 129, MP −7 | Pele de Quartzo — executada, dano 0, MP −12 | 790 / 631 | 104 / 287 |
| 2 | p2 → p1 (score) | Investida — executada, dano 146, MP −8 | Bola de Fogo — executada, dano 270, MP −10 | 520 / 495 | 98 / 279 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 153, MP −7 | Ataque básico — executada, dano 143 | 377 / 347 | 93 / 280 |
| 4 | p2 → p1 (score) | Investida — executada, dano 154, MP −8 | Drenar Vida — executada, dano 0, MP −10 | 377 / 307 | 87 / 271 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 119, MP −7 | Pele de Quartzo — executada, dano 0, MP −12 | 377 / 188 | 82 / 263 |
| 6 | p2 → p1 (score) | Investida — executada, dano 120, MP −8 | Bola de Fogo — executada, dano 270, MP −10 | 107 / 78 | 76 / 257 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −7 | Drenar Vida — executada, dano 0, MP −10 | 107 / 192 | 71 / 261 |
| 8 | p2 → p1 (score) | Investida — cancelada por morte | Bola de Fogo — executada, dano 270, MP −10 | -163 / 202 | 71 / 265 |

Chave após quartas:

```
Q1: Piromante (G4) × Geada (G6)  →  Geada
Q2: Muralha (G1) × Navalha (G7)  →  Muralha
Q3: Peçonha (G8) × Carrasco (G2)  →  Carrasco
Q4: Sentinela (G3) × Curandeira (G5)  →  Curandeira
S1: Geada × Muralha
S2: Carrasco × Curandeira
F: vencedor S1 × vencedor S2
```

## Semifinal

### Semifinal 1 — Geada × Muralha

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G6 | Geada | Mago | 6 | 9.79 | Bola de Fogo, Lasca de Gelo, Palavra de Torpor | controle: lentidão e névoa, com reserva de MP |
| p2 | G1 | Muralha | Guerreiro | 7 | 9.79 | Golpe Poderoso, Couraça Improvisada, Baluarte | defesa: duas reduções de dano, Defesa e HP |

- Seed da partida: `3183643387711164141`
- Rodadas: **8**
- Vencedor: **Geada** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 184/652 (28.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Geada | Muralha |
|---|---|---|
| Dano causado (golpes + DoT) | 973 (973 + 0) | 468 (468 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 65 | 72 |
| Skills / ataques básicos | 7 / 1 | 6 / 1 |
| Acertos / erros | 6 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 8 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Geada aplicou: slowed (rodada 1), slowed (rodada 3), slowed (rodada 6), clouded (rodada 6)
- Geada tentou sem sucesso: clouded (rodada 1), slowed (rodada 8)
- Égide de Geada: absorveu 81 de dano por 39 MP
- Muralha ativou: Couraça Improvisada ×2, Baluarte ×2

Rodada a rodada:

| Rodada | Ordem (critério) | Geada (p1) | Muralha (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Palavra de Torpor — executada, dano 0, MP −9 | Couraça Improvisada — executada, dano 0, MP −11 | 652 / 908 | 271 / 112 |
| 2 | p1 → p2 (score) | Bola de Fogo — executada, dano 219, MP −9 | Baluarte — executada, dano 0, MP −17 | 652 / 689 | 267 / 97 |
| 3 | p1 → p2 (score) | Lasca de Gelo — executada, dano 115, MP −10 | Golpe Poderoso — executada, dano 190, MP −8 | 462 / 574 | 246 / 91 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 184, MP −9 | Ataque básico — executada, dano 102 | 360 / 390 | 234 / 93 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 66 | Couraça Improvisada — executada, dano 0, MP −11 | 360 / 324 | 239 / 84 |
| 6 | p1 → p2 (score) | Palavra de Torpor — executada, dano 0, MP −9 | Golpe Poderoso — executada, dano 176, MP −8 | 184 / 324 | 220 / 77 |
| 7 | p1 → p2 (score) | Bola de Fogo — executada, dano 219, MP −9 | Baluarte — executada, dano 0, MP −17 | 184 / 105 | 216 / 61 |
| 8 | p1 → p2 (score) | Lasca de Gelo — executada, dano 170, MP −10 | Golpe Poderoso — cancelada por morte | 184 / -65 | 211 / 61 |

### Semifinal 2 — Carrasco × Curandeira

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G2 | Carrasco | Guerreiro | 7 | 10.54 | Golpe Poderoso, Grito de Guerra, Cutelada | dano físico: buff de Força, +MULT e crítico |
| p2 | G5 | Curandeira | Mago | 7 | 9.96 | Bola de Fogo, Drenar Vida, Pele de Quartzo | sustentação: cura, roubo de vida, regeneração e reserva de MP |

- Seed da partida: `15166320183835291332`
- Rodadas: **7**
- Vencedor: **Carrasco** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 478/868 (55.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Carrasco | Curandeira |
|---|---|---|
| Dano causado (golpes + DoT) | 1013 (1013 + 0) | 390 (390 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 243 (228 + 15) |
| MP gasto em ações | 82 | 64 |
| Skills / ataques básicos | 7 / 0 | 6 / 1 |
| Acertos / erros | 4 / 1 | 2 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 7 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Carrasco ativou: Grito de Guerra ×2
- Curandeira ativou: Pele de Quartzo ×2
- Égide de Curandeira: absorveu 175 de dano por 87 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Carrasco (p1) | Curandeira (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −16 | Pele de Quartzo — executada, dano 0, MP −12 | 868 / 760 | 107 / 298 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 218, MP −8 | Bola de Fogo — executada, dano 0, MP −10 | 868 / 542 | 101 / 281 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 301, MP −13 | Ataque básico — executada, dano 135 | 733 / 246 | 90 / 269 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 193, MP −8 | Drenar Vida — executada, dano 0, MP −10 | 733 / 167 | 84 / 257 |
| 5 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −16 | Pele de Quartzo — executada, dano 0, MP −12 | 733 / 167 | 70 / 259 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −8 | Bola de Fogo — executada, dano 255, MP −10 | 478 / 177 | 64 / 263 |
| 7 | p2 → p1 (score) | Cutelada — executada, dano 301, MP −13 | Drenar Vida — executada, dano 0, MP −10 | 478 / -10 | 53 / 241 |

Chave após semifinal:

```
Q1: Piromante (G4) × Geada (G6)  →  Geada
Q2: Muralha (G1) × Navalha (G7)  →  Muralha
Q3: Peçonha (G8) × Carrasco (G2)  →  Carrasco
Q4: Sentinela (G3) × Curandeira (G5)  →  Curandeira
S1: Geada × Muralha  →  Geada
S2: Carrasco × Curandeira  →  Carrasco
F: Geada × Carrasco
```

## Final

### Final — Geada × Carrasco

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G6 | Geada | Mago | 6 | 9.79 | Bola de Fogo, Lasca de Gelo, Palavra de Torpor | controle: lentidão e névoa, com reserva de MP |
| p2 | G2 | Carrasco | Guerreiro | 7 | 10.54 | Golpe Poderoso, Grito de Guerra, Cutelada | dano físico: buff de Força, +MULT e crítico |

- Seed da partida: `14556157636677633696`
- Rodadas: **4**
- Vencedor: **Carrasco** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 269/868 (31.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Geada | Carrasco |
|---|---|---|
| Dano causado (golpes + DoT) | 599 (599 + 0) | 809 (809 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 28 | 45 |
| Skills / ataques básicos | 3 / 0 | 4 / 0 |
| Acertos / erros | 2 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 3 | 1 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Geada aplicou: slowed (rodada 1), clouded (rodada 1)
- Geada tentou sem sucesso: slowed (rodada 3)
- Égide de Geada: absorveu 141 de dano por 69 MP
- Carrasco ativou: Grito de Guerra ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Geada (p1) | Carrasco (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Palavra de Torpor — executada, dano 0, MP −9 | Grito de Guerra — executada, dano 0, MP −16 | 652 / 868 | 271 / 83 |
| 2 | p1 → p2 (score) | Bola de Fogo — executada, dano 311, MP −9 | Golpe Poderoso — executada, dano 293, MP −8 | 359 / 557 | 242 / 76 |
| 3 | p1 → p2 (score) | Lasca de Gelo — executada, dano 288, MP −10 | Cutelada — executada, dano 314, MP −13 | 45 / 269 | 210 / 64 |
| 4 | p2 → p1 (score) | Palavra de Torpor — cancelada por morte | Golpe Poderoso — executada, dano 202, MP −8 | -157 / 269 | 193 / 58 |

A transcrição completa, com todos os cálculos e sorteios, está em [`copa_teste_01_final_detalhada.md`](copa_teste_01_final_detalhada.md); o trace estruturado, em [`copa_teste_01_trace.json`](copa_teste_01_trace.json).

Chave após final:

```
Q1: Piromante (G4) × Geada (G6)  →  Geada
Q2: Muralha (G1) × Navalha (G7)  →  Muralha
Q3: Peçonha (G8) × Carrasco (G2)  →  Carrasco
Q4: Sentinela (G3) × Curandeira (G5)  →  Curandeira
S1: Geada × Muralha  →  Geada
S2: Carrasco × Curandeira  →  Carrasco
F: Geada × Carrasco  →  Carrasco
Campeão: Carrasco
```

## Estatísticas do campeão

**Carrasco** (G2, Guerreiro nível 7, OP 10.54).

| Fase | Adversário | Rodadas | Dano causado | Dano recebido | Cura | MP gasto | HP final |
|---|---|---|---|---|---|---|---|
| Quartas | Peçonha | 3 | 696 | 387 | 0 | 37 | 481/868 |
| Semifinal | Curandeira | 7 | 1013 | 390 | 0 | 82 | 478/868 |
| Final | Geada | 4 | 809 | 599 | 0 | 45 | 269/868 |

- Dano causado: 2518 (golpes 2518, DoT 0); recebido: 1376.
- Cura: 0 (skill 0, roubo de vida 0).
- MP gasto: 164; skills 14, ataques básicos 0.
- Golpes: 9 acertos e 1 erros (90.0% de acerto); 0 críticos.
- Skills usadas: Golpe Poderoso ×6, Grito de Guerra ×4, Cutelada ×4
- Status aplicados: 0; ações perdidas por controle: 0.

## Estatísticas do torneio

- Partidas: 7; rodadas por partida: [5, 6, 3, 8, 8, 7, 4] (média 5.9, total 41).
- Vitórias por classe: {'Mago': 3, 'Guerreiro': 4}.
- Critério que decidiu a ordem, por rodada: {'score': 41}.
- Em 3 de 7 partidas venceu quem agiu primeiro na maior parte das rodadas.
- Golpes: 50, conectados 46 (92.0%), críticos 3.
- Chamadas ao gerador, por mecânica: {'aplicação de status': 21, 'acerto': 50, 'crítico': 46}.

## Verificações

| Partida | Seed | Rodadas | Fidelidade com × sem auditoria | Coerência trace × motor | Sorteios |
|---|---|---|---|---|---|
| Quartas 1 — Piromante × Geada | `7347509823717725885` | 5 | 10/10 | 7/7 | 18 |
| Quartas 2 — Muralha × Navalha | `2030327944903717010` | 6 | 10/10 | 7/7 | 15 |
| Quartas 3 — Peçonha × Carrasco | `4785977635327490906` | 3 | 10/10 | 7/7 | 9 |
| Quartas 4 — Sentinela × Curandeira | `7843339256714053718` | 8 | 10/10 | 7/7 | 24 |
| Semifinal 1 — Geada × Muralha | `3183643387711164141` | 8 | 10/10 | 7/7 | 24 |
| Semifinal 2 — Carrasco × Curandeira | `15166320183835291332` | 7 | 10/10 | 7/7 | 14 |
| Final — Geada × Carrasco | `14556157636677633696` | 4 | 10/10 | 7/7 | 13 |

Verificações de fidelidade (iguais em todas as partidas):

- ações escolhidas
- ordem de cada rodada
- leituras de iniciativa (floats exatos)
- passos: desfecho, MP reservado, MP gasto e dano
- HP e MP ao fim de cada rodada
- estado completo ao fim de cada rodada (efeitos, buffs, recargas)
- eventos do motor
- vencedor, motivo e número de rodadas
- conclusividade
- posição final do gerador (nenhum sorteio extra)

Verificações de coerência do trace:

- toda chamada ao gerador foi classificada
- rolagens registradas = chamadas ao gerador
- toda rolagem de acerto recebeu a chance do motor
- toda rolagem pertence ao intervalo do motor
- dano de cada passo = soma do HP retirado pelos golpes registrados
- MP gasto de cada passo = débito registrado da skill
- ações executadas = eventos `action_executed`

