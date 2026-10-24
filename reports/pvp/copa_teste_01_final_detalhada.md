# Copa Arena de Testes 01 — Final detalhada: Geada × Carrasco

Transcrição da final a partir do trace da auditoria (`tools/arena_auditoria.py`), na ordem em que o motor executou. Cada número abaixo foi capturado no momento da execução, pela chamada real da função canônica; os recálculos que explicam um número são feitos com as mesmas funções e constantes e conferidos contra o valor devolvido pelo motor — se divergissem, a auditoria pararia com erro.

## Convenções

- Gerador da partida: `random.Random(14556157636677633696)`, observado por um proxy que delega cada chamada e anota operação, limites, valor e chamador. O proxy não sorteia nada por conta própria.
- Rolagens percentuais do motor: `randrange(1, 101)`, inteiro uniforme em [1, 100]. Não é D20. O desempate de iniciativa usa `random() < 0.5`.
- Acerto: o golpe ERRA quando `rolagem > chance`. Crítico: CRITA quando `rolagem <= chance`. Status: NÃO pega quando `rolagem > chance efetiva`.
- Floats aparecem com `repr`: a precisão total que o motor usou. Nada é arredondado antes de uma comparação.
- Referências de iniciativa: `foundation_reference(nível)` — a média das três classes pelo crescimento canônico. Níveis desta final: [6, 7].
- Golpes de skill são resolvidos por `apply_skill` com `publish=None`; a auditoria os vê porque intercepta a função no módulo, não o EventBus.
- Limite técnico do laço: 500 rodadas (não atingido).

## Referências globais usadas

| Nível | REF_hp | REF_mp | REF_st | REF_mg | REF_ag | REF_df |
|---|---|---|---|---|---|---|
| 6 | 660.0 | 170.66666666666666 | 74.66666666666667 | 67.0 | 26.0 | 48.666666666666664 |
| 7 | 739.3333333333334 | 190.66666666666666 | 83.66666666666667 | 75.0 | 29.0 | 54.333333333333336 |

## Fichas completas antes do duelo

### p1 — Geada (Mago, nível 6)

- HP 652/652, MP 280/280; ST 53, MG 95, AG 14, DF 51
- Arma: +13.0% de dano; Égide de Mana: 15%
- Equipamento: Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Pá de Batalha; Body: Jaqueta de Couro; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Bronze
- Passivas: Mente Serena (max_mp 10), Pele de Sal (status_resistance 8), Sangue de Vidente (magic 3), Olho de Caçador (precision 5), Mente Serena (max_mp 10)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 2.0, precision 5.0, status_resistance 8.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Bola de Fogo (`bola_fogo`) | damage | 0 | 9 | 1 | 3.485 × (1.0×mg) | +0 | 0 | — | target_afflicted +45% | — |
| Lasca de Gelo (`lasca_de_gelo`) | damage | 0 | 10 | 2 | 4.682 × (1.0×mg) | +0 | 0 | slowed 45% por 3 | target_healthy +12% | — |
| Palavra de Torpor (`palavra_de_torpor`) | status | slowed 75% por 3 | 9 | 2 | 0.0 × (—) | +0 | 0 | clouded 50% por 3 | — | — |

### p2 — Carrasco (Guerreiro, nível 7)

- HP 868/868, MP 123/123; ST 103, MG 59, AG 19, DF 74
- Arma: +13.0% de dano; Égide de Mana: 0%
- Equipamento: Helmet: Capacete de Couro; Amulet: Amuleto de Concha; Weapon1: Clava Pesada; Weapon2: Espada Longa; Body: Placa Pesada; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Shoes: Tamancos de Madeira; Ring1: Anel de Ouro; Ring2: Anel de Aço
- Passivas: Músculos de Aço (strength 3), Ódio Baixo (damage_percent 4), Pulso Certeiro (crit_damage 15), Olho de Águia (crit_chance 5), Músculos de Aço (strength 3), Ódio Baixo (damage_percent 4)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 7.0, crit_damage 15.0, damage_percent 8.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Golpe Poderoso (`golpe_poderoso`) | damage | 0 | 8 | 1 | 2.86 × (1.0×st) | +0 | 0 | — | target_healthy +8% | — |
| Grito de Guerra (`grito_guerra`) | buff | 35 st por 3 | 16 | 2 | 0.0 × (—) | +0 | 0 | — | — | — |
| Cutelada (`cutelada`) | damage | 0 | 13 | 2 | 3.294 × (1.0×st) | +0 | 0 | — | target_afflicted +45% | — |

## Rodada 1

### 1.0 Estado no início da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 652/652 | 868/868 |
| MP | 280/280 | 123/123 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 103 / 59 / 19 / 74 |
| Recargas (contador interno) | — | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 1.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Geada (p1)**

- Estado recebido (`DuelView`, rodada 1): eu HP 652/652, MP 280/280, efeitos —, buffs —; adversário Carrasco HP 868/868, MP 123/123, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Bola de Fogo 0, Lasca de Gelo 0, Palavra de Torpor 0
- Ações legais: Ataque básico, Bola de Fogo, Lasca de Gelo, Palavra de Torpor, Rendição
- Escolha: **Palavra de Torpor** — justificativa da política: Palavra de Torpor aplica slowed, que o adversário não carrega (efeitos visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 9

**Carrasco (p2)**

- Estado recebido (`DuelView`, rodada 1): eu HP 868/868, MP 123/123, efeitos —, buffs —; adversário Geada HP 652/652, MP 280/280, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Grito de Guerra 0, Cutelada 0
- Ações legais: Ataque básico, Golpe Poderoso, Grito de Guerra, Cutelada, Rendição
- Escolha: **Grito de Guerra** — justificativa da política: Grito de Guerra é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 16

- Lock: Geada (p1) reserva **9 MP** (sai do caixa livre agora).
- Lock: Carrasco (p2) reserva **16 MP** (sai do caixa livre agora).
- Ações travadas: Geada (p1) = Palavra de Torpor; Carrasco (p2) = Grito de Guerra

### 1.2 Initiative Score

**Geada (p1)** — nível próprio 6, adversário 7; referências globais `foundation_reference(6)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 652.0 | 660.0 | 0.9878787878787879 | 0.9939209163101398 |
| mp | 280.0 | 170.66666666666666 | 1.640625 | 1.2808688457449497 |
| st | 53.0 | 74.66666666666667 | 0.7098214285714285 | 0.8425090080061034 |
| mg | 95.0 | 67.0 | 1.4179104477611941 | 1.190760449360489 |
| ag | 14.0 | 26.0 | 0.5384615384615384 | 0.7337993857053428 |
| df | 51.0 | 48.666666666666664 | 1.047945205479452 | 1.0236919485272178 |

- Soma das seis raízes (`math.fsum`): 6.0655505536542424
- ÷ 6 = build 1.0109250922757071
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0109250922757071 × 0.995 = 1.0058704668143286**
- AG relativa (desempate): 14.0 / 26.0 = 0.5384615384615384

**Carrasco (p2)** — nível próprio 7, adversário 6; referências globais `foundation_reference(7)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 868.0 | 739.3333333333334 | 1.1740306582506763 | 1.083526953172221 |
| mp | 123.0 | 190.66666666666666 | 0.6451048951048951 | 0.8031842223953949 |
| st | 103.0 | 83.66666666666667 | 1.2310756972111554 | 1.1095385064120828 |
| mg | 59.0 | 75.0 | 0.7866666666666666 | 0.886942313043338 |
| ag | 19.0 | 29.0 | 0.6551724137931034 | 0.8094272134003795 |
| df | 74.0 | 54.333333333333336 | 1.361963190184049 | 1.1670317862783555 |

- Soma das seis raízes (`math.fsum`): 5.859650994701772
- ÷ 6 = build 0.976608499116962
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 0.976608499116962 × 1.005 = 0.9814915416125467**
- AG relativa (desempate): 19.0 / 29.0 = 0.6551724137931034

- Comparação: score p1 1.0058704668143286 > score p2 0.9814915416125467 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: Geada (p1) → Carrasco (p2) (`score`).

- **Ordem travada**: Geada (p1) → Carrasco (p2) (critério `score`).

### Oportunidade de Geada (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 280 × 2 / 100) = 5.6; + mana_regen 0.0 → int(0 + 5.6) = **5**; MP livre 271 → min(280, 271 + 5) = 276
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 271 → 276
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 9, teto livre 271 → MP 276 → 271
- Perde a oportunidade por controle: não

**Skill Palavra de Torpor** (`palavra_de_torpor`) de Geada (p1)

- Tipo `status`, valor slowed ; alvo declarado `enemy` → recebe Carrasco (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 9 MP; reserva feita no lock 9; MP disponível na cobrança (livre + reserva liberada) 280
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)
- Status: chance base 75%, duração declarada 3

**Status `slowed`** sobre Carrasco (p2) (via `apply_skill`, fonte `palavra_de_torpor`)

- Chance base 75%; resistência do alvo 0.0% → efetiva 75 × (1 − 0/100) = 75.0%
- sorteio nº 1 [aplicação de status (slowed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 75.0; teste `11 > 75.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `slowed` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'palavra_de_torpor'}]

**Status `clouded`** sobre Carrasco (p2) (via `_aplicar_secundario`, fonte `palavra_de_torpor`)

- Chance base 50%; resistência do alvo 0.0% → efetiva 50 × (1 − 0/100) = 50.0%
- sorteio nº 2 [aplicação de status (clouded)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **24**; chance 50.0; teste `24 > 50.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `clouded` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'palavra_de_torpor'}]

- Resultado da skill: `status`; MP debitado 9; recarga depois 3; status slowed pegou
- Mudanças em quem lançou: mp 280 → 271; recarga Palavra de Torpor — → 3
- Mudanças no adversário: ag 19 → 15; mp_max 123 → 99; efeito clouded entra (dur 3, stacks 1, int 20.0); efeito slowed entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): Geada (p1) executou Palavra de Torpor; MP gasto 9, dano ao adversário 0.

### Oportunidade de Carrasco (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 99 × 2 / 100) = 1.98; + mana_regen 0.0 → int(0 + 1.98) = **1**; MP livre 107 → min(99, 107 + 1) = 99
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 107 → 99; efeito clouded: dur 3 → 2, stacks 1 → 1; efeito slowed: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 16, teto livre 83 → MP 99 → 83
- Perde a oportunidade por controle: não

**Skill Grito de Guerra** (`grito_guerra`) de Carrasco (p2)

- Tipo `buff`, valor 35 st; alvo declarado `self` → recebe Carrasco (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 16 MP; reserva feita no lock 16; MP disponível na cobrança (livre + reserva liberada) 99
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)
- Buff: st declarado 35 → valor gravado 36 (percentual de base_st: max(1, int(base × 35/100)))

- Resultado da skill: `buff`; MP debitado 16; recarga depois 3; buff gravado {'stat': 'st', 'value': 36, 'duration': 3}
- Mudanças em quem lançou: mp 99 → 83; st 103 → 139; recarga Grito de Guerra — → 3; buff Grito de Guerra entra (st 36, dur 3)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Carrasco (p2) executou Grito de Guerra; MP gasto 16, dano ao adversário 0.

### 1.9 Estado ao final da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 652/652 | 868/868 |
| MP | 271/280 | 83/99 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 15 / 74 |
| Recargas (contador interno) | Palavra de Torpor 3 | Grito de Guerra 3 |
| Buffs | — | Grito de Guerra (st 36, dur 3) |
| Efeitos | — | slowed (dur 2, stacks 1, int 20.0, fonte palavra_de_torpor); clouded (dur 2, stacks 1, int 20.0, fonte palavra_de_torpor) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- Geada (p1): Palavra de Torpor — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- Carrasco (p2): Grito de Guerra — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 2

### 2.0 Estado no início da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 652/652 | 868/868 |
| MP | 271/280 | 83/99 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 15 / 74 |
| Recargas (contador interno) | Palavra de Torpor 3 | Grito de Guerra 3 |
| Buffs | — | Grito de Guerra (st 36, dur 3) |
| Efeitos | — | slowed (dur 2, stacks 1, int 20.0, fonte palavra_de_torpor); clouded (dur 2, stacks 1, int 20.0, fonte palavra_de_torpor) |
| death_ignore gasto / vivo | False / True | False / True |

### 2.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Geada (p1)**

- Estado recebido (`DuelView`, rodada 2): eu HP 652/652, MP 271/280, efeitos —, buffs —; adversário Carrasco HP 868/868, MP 83/99, efeitos ['clouded', 'slowed'], buffs ['Grito de Guerra'].
- Recargas vistas no lock (oportunidades que ainda faltam): Bola de Fogo 0, Lasca de Gelo 0, Palavra de Torpor 2
- Ações legais: Ataque básico, Bola de Fogo, Lasca de Gelo, Rendição
- Escolha: **Bola de Fogo** — justificativa da política: primeira skill de dano legal do deck: Bola de Fogo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 9

**Carrasco (p2)**

- Estado recebido (`DuelView`, rodada 2): eu HP 868/868, MP 83/99, efeitos ['clouded', 'slowed'], buffs ['Grito de Guerra']; adversário Geada HP 652/652, MP 271/280, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Grito de Guerra 2, Cutelada 0
- Ações legais: Ataque básico, Golpe Poderoso, Cutelada, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 8

- Lock: Geada (p1) reserva **9 MP** (sai do caixa livre agora).
- Lock: Carrasco (p2) reserva **8 MP** (sai do caixa livre agora).
- Ações travadas: Geada (p1) = Bola de Fogo; Carrasco (p2) = Golpe Poderoso

### 2.2 Initiative Score

**Geada (p1)** — nível próprio 6, adversário 7; referências globais `foundation_reference(6)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 652.0 | 660.0 | 0.9878787878787879 | 0.9939209163101398 |
| mp | 280.0 | 170.66666666666666 | 1.640625 | 1.2808688457449497 |
| st | 53.0 | 74.66666666666667 | 0.7098214285714285 | 0.8425090080061034 |
| mg | 95.0 | 67.0 | 1.4179104477611941 | 1.190760449360489 |
| ag | 14.0 | 26.0 | 0.5384615384615384 | 0.7337993857053428 |
| df | 51.0 | 48.666666666666664 | 1.047945205479452 | 1.0236919485272178 |

- Soma das seis raízes (`math.fsum`): 6.0655505536542424
- ÷ 6 = build 1.0109250922757071
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0109250922757071 × 0.995 = 1.0058704668143286**
- AG relativa (desempate): 14.0 / 26.0 = 0.5384615384615384

**Carrasco (p2)** — nível próprio 7, adversário 6; referências globais `foundation_reference(7)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 868.0 | 739.3333333333334 | 1.1740306582506763 | 1.083526953172221 |
| mp | 99.0 | 190.66666666666666 | 0.5192307692307693 | 0.7205766921228921 |
| st | 139.0 | 83.66666666666667 | 1.6613545816733066 | 1.2889354451148074 |
| mg | 59.0 | 75.0 | 0.7866666666666666 | 0.886942313043338 |
| ag | 15.0 | 29.0 | 0.5172413793103449 | 0.7191949522280763 |
| df | 74.0 | 54.333333333333336 | 1.361963190184049 | 1.1670317862783555 |

- Soma das seis raízes (`math.fsum`): 5.8662081419596905
- ÷ 6 = build 0.9777013569932818
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 0.9777013569932818 × 1.005 = 0.9825898637782481**
- AG relativa (desempate): 15.0 / 29.0 = 0.5172413793103449

- Comparação: score p1 1.0058704668143286 > score p2 0.9825898637782481 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: Geada (p1) → Carrasco (p2) (`score`).

- **Ordem travada**: Geada (p1) → Carrasco (p2) (critério `score`).

### Oportunidade de Geada (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Palavra de Torpor 3 → 2
- Regeneração de MP: max(1, 280 × 2 / 100) = 5.6; + mana_regen 0.0 → int(0 + 5.6) = **5**; MP livre 262 → min(280, 262 + 5) = 267
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 262 → 267; recarga Palavra de Torpor 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 9, teto livre 271 → MP 267 → 267
- Perde a oportunidade por controle: não

**Skill Bola de Fogo** (`bola_fogo`) de Geada (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Carrasco (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 9 MP; reserva feita no lock 9; MP disponível na cobrança (livre + reserva liberada) 276
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #1** — Geada (p1) → Carrasco (p2), skill `bola_fogo`

1. Atributos ofensivos efetivos: mg 95.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 95.0; × arma = 107.35; × power 3.485 = 374.11474999999996; max(1, int(95.0 × (1 + 13/100) × 3.485)) = **374**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.0344827586206897 (30 × (14 − 15) / 29) − evasão 0.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 88.96551724137932 → clamp [20, 95] e int → **88**
7. Rolagem de acerto: sorteio nº 3 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **33**; chance 88; teste `33 > 88` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 2 = 2, teto 75 → **2**
9. Rolagem de crítico: sorteio nº 4 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 2; teste `87 <= 2` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 74
15. Fator de defesa: 100 / (100 + 74) = 0.5747126436781609
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 374.0 × 1.45 × 1.0 × 0.5747126436781609 = 311.66666666666663; max(1, int(bruto)) = 311 → int(anterior × 1.0) = 311 → int(anterior × 1.0) = 311
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **311**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 311
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(311)`; HP do alvo 868 → 557 (retirado 311)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 557 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 9; recarga depois 2
- Mudanças em quem lançou: mp 276 → 267; recarga Bola de Fogo — → 2
- Mudanças no adversário: hp 868 → 557

- Motor (`action_executed`): Geada (p1) executou Bola de Fogo; MP gasto 9, dano ao adversário 311.

### Oportunidade de Carrasco (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Grito de Guerra 3 → 2
- Regeneração de MP: max(1, 99 × 2 / 100) = 1.98; + mana_regen 0.0 → int(0 + 1.98) = **1**; MP livre 75 → min(99, 75 + 1) = 76
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 75 → 76; recarga Grito de Guerra 3 → 2; buff Grito de Guerra dur 3 → 2; efeito clouded: dur 2 → 1, stacks 1 → 1; efeito slowed: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 8, teto livre 91 → MP 76 → 76
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Carrasco (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Geada (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 8 MP; reserva feita no lock 8; MP disponível na cobrança (livre + reserva liberada) 84
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #2** — Carrasco (p2) → Geada (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 139.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 139.0; × arma = 157.07; × power 2.86 = 449.2202; max(1, int(139.0 × (1 + 13/100) × 2.86)) = **449**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.0344827586206897 (30 × (15 − 14) / 29) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.03448275862068 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 5 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **13**; chance 86; teste `13 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 7 = 7, teto 75 → **7**
9. Rolagem de crítico: sorteio nº 6 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **75**; chance 7; teste `75 <= 7` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: damage_percent (passiva, equipamento ou buff) 0.08; condição da carta (target_healthy) 0.08 → 1 + Σ = 1.16
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 51
15. Fator de defesa: 100 / (100 + 51) = 0.6622516556291391
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 449.0 × 1.16 × 1.0 × 0.6622516556291391 = 344.92715231788077; max(1, int(bruto)) = 344 → int(anterior × 1.0) = 344 → int(anterior × 1.0) = 344
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **344**
20. Égide de Mana: desejado int(344 × 15 / 100) = 51; possível min(51, int(267 × 2.0)) = 51; passa max(1, 344 − 51) = 293
21. MP da Égide: max(1, int(51 / 2.0)) = 25
22. Dano aplicado ao HP: `take_damage(293)`; HP do alvo 652 → 359 (retirado 293)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 359 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 8; recarga depois 2
- Mudanças em quem lançou: mp 84 → 76; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 652 → 359; mp 267 → 242

- Motor (`action_executed`): Carrasco (p2) executou Golpe Poderoso; MP gasto 8, dano ao adversário 293.

### 2.9 Estado ao final da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 359/652 | 557/868 |
| MP | 242/280 | 76/99 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 15 / 74 |
| Recargas (contador interno) | Palavra de Torpor 2, Bola de Fogo 2 | Grito de Guerra 2, Golpe Poderoso 2 |
| Buffs | — | Grito de Guerra (st 36, dur 2) |
| Efeitos | — | slowed (dur 1, stacks 1, int 20.0, fonte palavra_de_torpor); clouded (dur 1, stacks 1, int 20.0, fonte palavra_de_torpor) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- Geada (p1): Bola de Fogo — executada; dano causado na rodada 311 (golpes e DoT), recebido 293; cura 0
- Carrasco (p2): Golpe Poderoso — executada; dano causado na rodada 293 (golpes e DoT), recebido 311; cura 0


## Rodada 3

### 3.0 Estado no início da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 359/652 | 557/868 |
| MP | 242/280 | 76/99 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 15 / 74 |
| Recargas (contador interno) | Palavra de Torpor 2, Bola de Fogo 2 | Grito de Guerra 2, Golpe Poderoso 2 |
| Buffs | — | Grito de Guerra (st 36, dur 2) |
| Efeitos | — | slowed (dur 1, stacks 1, int 20.0, fonte palavra_de_torpor); clouded (dur 1, stacks 1, int 20.0, fonte palavra_de_torpor) |
| death_ignore gasto / vivo | False / True | False / True |

### 3.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Geada (p1)**

- Estado recebido (`DuelView`, rodada 3): eu HP 359/652, MP 242/280, efeitos —, buffs —; adversário Carrasco HP 557/868, MP 76/99, efeitos ['clouded', 'slowed'], buffs ['Grito de Guerra'].
- Recargas vistas no lock (oportunidades que ainda faltam): Bola de Fogo 1, Lasca de Gelo 0, Palavra de Torpor 1
- Ações legais: Ataque básico, Lasca de Gelo, Rendição
- Escolha: **Lasca de Gelo** — justificativa da política: primeira skill de dano legal do deck: Lasca de Gelo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 10

**Carrasco (p2)**

- Estado recebido (`DuelView`, rodada 3): eu HP 557/868, MP 76/99, efeitos ['clouded', 'slowed'], buffs ['Grito de Guerra']; adversário Geada HP 359/652, MP 242/280, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Grito de Guerra 1, Cutelada 0
- Ações legais: Ataque básico, Cutelada, Rendição
- Escolha: **Cutelada** — justificativa da política: primeira skill de dano legal do deck: Cutelada
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 13

- Lock: Geada (p1) reserva **10 MP** (sai do caixa livre agora).
- Lock: Carrasco (p2) reserva **13 MP** (sai do caixa livre agora).
- Ações travadas: Geada (p1) = Lasca de Gelo; Carrasco (p2) = Cutelada

### 3.2 Initiative Score

**Geada (p1)** — nível próprio 6, adversário 7; referências globais `foundation_reference(6)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 652.0 | 660.0 | 0.9878787878787879 | 0.9939209163101398 |
| mp | 280.0 | 170.66666666666666 | 1.640625 | 1.2808688457449497 |
| st | 53.0 | 74.66666666666667 | 0.7098214285714285 | 0.8425090080061034 |
| mg | 95.0 | 67.0 | 1.4179104477611941 | 1.190760449360489 |
| ag | 14.0 | 26.0 | 0.5384615384615384 | 0.7337993857053428 |
| df | 51.0 | 48.666666666666664 | 1.047945205479452 | 1.0236919485272178 |

- Soma das seis raízes (`math.fsum`): 6.0655505536542424
- ÷ 6 = build 1.0109250922757071
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0109250922757071 × 0.995 = 1.0058704668143286**
- AG relativa (desempate): 14.0 / 26.0 = 0.5384615384615384

**Carrasco (p2)** — nível próprio 7, adversário 6; referências globais `foundation_reference(7)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 868.0 | 739.3333333333334 | 1.1740306582506763 | 1.083526953172221 |
| mp | 99.0 | 190.66666666666666 | 0.5192307692307693 | 0.7205766921228921 |
| st | 139.0 | 83.66666666666667 | 1.6613545816733066 | 1.2889354451148074 |
| mg | 59.0 | 75.0 | 0.7866666666666666 | 0.886942313043338 |
| ag | 15.0 | 29.0 | 0.5172413793103449 | 0.7191949522280763 |
| df | 74.0 | 54.333333333333336 | 1.361963190184049 | 1.1670317862783555 |

- Soma das seis raízes (`math.fsum`): 5.8662081419596905
- ÷ 6 = build 0.9777013569932818
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 0.9777013569932818 × 1.005 = 0.9825898637782481**
- AG relativa (desempate): 15.0 / 29.0 = 0.5172413793103449

- Comparação: score p1 1.0058704668143286 > score p2 0.9825898637782481 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: Geada (p1) → Carrasco (p2) (`score`).

- **Ordem travada**: Geada (p1) → Carrasco (p2) (critério `score`).

### Oportunidade de Geada (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Palavra de Torpor 2 → 1; Bola de Fogo 2 → 1
- Regeneração de MP: max(1, 280 × 2 / 100) = 5.6; + mana_regen 0.0 → int(0 + 5.6) = **5**; MP livre 232 → min(280, 232 + 5) = 237
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 232 → 237; recarga Bola de Fogo 2 → 1; recarga Palavra de Torpor 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 10, teto livre 270 → MP 237 → 237
- Perde a oportunidade por controle: não

**Skill Lasca de Gelo** (`lasca_de_gelo`) de Geada (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Carrasco (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 10 MP; reserva feita no lock 10; MP disponível na cobrança (livre + reserva liberada) 247
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #3** — Geada (p1) → Carrasco (p2), skill `lasca_de_gelo`

1. Atributos ofensivos efetivos: mg 95.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 95.0; × arma = 107.35; × power 4.682 = 502.6127; max(1, int(95.0 × (1 + 13/100) × 4.682)) = **502**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.0344827586206897 (30 × (14 − 15) / 29) − evasão 0.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 88.96551724137932 → clamp [20, 95] e int → **88**
7. Rolagem de acerto: sorteio nº 7 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **65**; chance 88; teste `65 > 88` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 2 = 2, teto 75 → **2**
9. Rolagem de crítico: sorteio nº 8 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **78**; chance 2; teste `78 <= 2` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 74
15. Fator de defesa: 100 / (100 + 74) = 0.5747126436781609
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 502.0 × 1.0 × 1.0 × 0.5747126436781609 = 288.50574712643675; max(1, int(bruto)) = 288 → int(anterior × 1.0) = 288 → int(anterior × 1.0) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 557 → 269 (retirado 288)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 269 → o alvo segue vivo

**Status `slowed`** sobre Carrasco (p2) (via `_aplicar_secundario`, fonte `lasca_de_gelo`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 9 [aplicação de status (slowed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 45.0; teste `98 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `slowed` no alvo antes: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'palavra_de_torpor'}]; depois: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'palavra_de_torpor'}]

- Resultado da skill: `damage`; MP debitado 10; recarga depois 3
- Mudanças em quem lançou: mp 247 → 237; recarga Lasca de Gelo — → 3
- Mudanças no adversário: hp 557 → 269

- Motor (`action_executed`): Geada (p1) executou Lasca de Gelo; MP gasto 10, dano ao adversário 288.

### Oportunidade de Carrasco (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Grito de Guerra 2 → 1; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 99 × 2 / 100) = 1.98; + mana_regen 0.0 → int(0 + 1.98) = **1**; MP livre 63 → min(99, 63 + 1) = 64
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['slowed', 'clouded'], leis —, pula a vez: False
- Mudanças de estado no início: mp 63 → 64; ag 15 → 19; mp_max 99 → 123; recarga Golpe Poderoso 2 → 1; recarga Grito de Guerra 2 → 1; buff Grito de Guerra dur 2 → 1; efeito clouded sai; efeito slowed sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 13, teto livre 110 → MP 64 → 64
- Perde a oportunidade por controle: não

**Skill Cutelada** (`cutelada`) de Carrasco (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Geada (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 13 MP; reserva feita no lock 13; MP disponível na cobrança (livre + reserva liberada) 77
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #4** — Carrasco (p2) → Geada (p1), skill `cutelada`

1. Atributos ofensivos efetivos: st 139.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 139.0; × arma = 157.07; × power 3.294 = 517.3885799999999; max(1, int(139.0 × (1 + 13/100) × 3.294)) = **517**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_afflicted` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 4.545454545454546 (30 × (19 − 14) / 33) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 89.54545454545455 → clamp [20, 95] e int → **89**
7. Rolagem de acerto: sorteio nº 10 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **69**; chance 89; teste `69 > 89` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 7 = 7, teto 75 → **7**
9. Rolagem de crítico: sorteio nº 11 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **61**; chance 7; teste `61 <= 7` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: damage_percent (passiva, equipamento ou buff) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 51
15. Fator de defesa: 100 / (100 + 51) = 0.6622516556291391
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 517.0 × 1.08 × 1.0 × 0.6622516556291391 = 369.77483443708616; max(1, int(bruto)) = 369 → int(anterior × 1.0) = 369 → int(anterior × 1.0) = 369
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **369**
20. Égide de Mana: desejado int(369 × 15 / 100) = 55; possível min(55, int(237 × 2.0)) = 55; passa max(1, 369 − 55) = 314
21. MP da Égide: max(1, int(55 / 2.0)) = 27
22. Dano aplicado ao HP: `take_damage(314)`; HP do alvo 359 → 45 (retirado 314)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 45 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 13; recarga depois 3
- Mudanças em quem lançou: mp 77 → 64; recarga Cutelada — → 3
- Mudanças no adversário: hp 359 → 45; mp 237 → 210

- Motor (`action_executed`): Carrasco (p2) executou Cutelada; MP gasto 13, dano ao adversário 314.

### 3.9 Estado ao final da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 45/652 | 269/868 |
| MP | 210/280 | 64/123 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 19 / 74 |
| Recargas (contador interno) | Palavra de Torpor 1, Bola de Fogo 1, Lasca de Gelo 3 | Grito de Guerra 1, Golpe Poderoso 1, Cutelada 3 |
| Buffs | — | Grito de Guerra (st 36, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- Geada (p1): Lasca de Gelo — executada; dano causado na rodada 288 (golpes e DoT), recebido 314; cura 0
- Carrasco (p2): Cutelada — executada; dano causado na rodada 314 (golpes e DoT), recebido 288; cura 0


## Rodada 4

### 4.0 Estado no início da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | 45/652 | 269/868 |
| MP | 210/280 | 64/123 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 139 / 59 / 19 / 74 |
| Recargas (contador interno) | Palavra de Torpor 1, Bola de Fogo 1, Lasca de Gelo 3 | Grito de Guerra 1, Golpe Poderoso 1, Cutelada 3 |
| Buffs | — | Grito de Guerra (st 36, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 4.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Geada (p1)**

- Estado recebido (`DuelView`, rodada 4): eu HP 45/652, MP 210/280, efeitos —, buffs —; adversário Carrasco HP 269/868, MP 64/123, efeitos —, buffs ['Grito de Guerra'].
- Recargas vistas no lock (oportunidades que ainda faltam): Bola de Fogo 0, Lasca de Gelo 2, Palavra de Torpor 0
- Ações legais: Ataque básico, Bola de Fogo, Palavra de Torpor, Rendição
- Escolha: **Palavra de Torpor** — justificativa da política: Palavra de Torpor aplica slowed, que o adversário não carrega (efeitos visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 9

**Carrasco (p2)**

- Estado recebido (`DuelView`, rodada 4): eu HP 269/868, MP 64/123, efeitos —, buffs ['Grito de Guerra']; adversário Geada HP 45/652, MP 210/280, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Grito de Guerra 0, Cutelada 2
- Ações legais: Ataque básico, Golpe Poderoso, Grito de Guerra, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 8

- Lock: Geada (p1) reserva **9 MP** (sai do caixa livre agora).
- Lock: Carrasco (p2) reserva **8 MP** (sai do caixa livre agora).
- Ações travadas: Geada (p1) = Palavra de Torpor; Carrasco (p2) = Golpe Poderoso

### 4.2 Initiative Score

**Geada (p1)** — nível próprio 6, adversário 7; referências globais `foundation_reference(6)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 652.0 | 660.0 | 0.9878787878787879 | 0.9939209163101398 |
| mp | 280.0 | 170.66666666666666 | 1.640625 | 1.2808688457449497 |
| st | 53.0 | 74.66666666666667 | 0.7098214285714285 | 0.8425090080061034 |
| mg | 95.0 | 67.0 | 1.4179104477611941 | 1.190760449360489 |
| ag | 14.0 | 26.0 | 0.5384615384615384 | 0.7337993857053428 |
| df | 51.0 | 48.666666666666664 | 1.047945205479452 | 1.0236919485272178 |

- Soma das seis raízes (`math.fsum`): 6.0655505536542424
- ÷ 6 = build 1.0109250922757071
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0109250922757071 × 0.995 = 1.0058704668143286**
- AG relativa (desempate): 14.0 / 26.0 = 0.5384615384615384

**Carrasco (p2)** — nível próprio 7, adversário 6; referências globais `foundation_reference(7)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 868.0 | 739.3333333333334 | 1.1740306582506763 | 1.083526953172221 |
| mp | 123.0 | 190.66666666666666 | 0.6451048951048951 | 0.8031842223953949 |
| st | 139.0 | 83.66666666666667 | 1.6613545816733066 | 1.2889354451148074 |
| mg | 59.0 | 75.0 | 0.7866666666666666 | 0.886942313043338 |
| ag | 19.0 | 29.0 | 0.6551724137931034 | 0.8094272134003795 |
| df | 74.0 | 54.333333333333336 | 1.361963190184049 | 1.1670317862783555 |

- Soma das seis raízes (`math.fsum`): 6.039047933404496
- ÷ 6 = build 1.0065079889007493
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0065079889007493 × 1.005 = 1.011540528845253**
- AG relativa (desempate): 19.0 / 29.0 = 0.6551724137931034

- Comparação: score p1 1.0058704668143286 < score p2 1.011540528845253 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: Carrasco (p2) → Geada (p1) (`score`).

- **Ordem travada**: Carrasco (p2) → Geada (p1) (critério `score`).

### Oportunidade de Carrasco (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Grito de Guerra 1 → livre; Golpe Poderoso 1 → livre; Cutelada 3 → 2
- Regeneração de MP: max(1, 123 × 2 / 100) = 2.46; + mana_regen 0.0 → int(0 + 2.46) = **2**; MP livre 56 → min(123, 56 + 2) = 58
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 56 → 58; st 139 → 103; recarga Cutelada 3 → 2; recarga Golpe Poderoso 1 → livre; recarga Grito de Guerra 1 → livre; buff Grito de Guerra expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 8, teto livre 115 → MP 58 → 58
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Carrasco (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Geada (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 8 MP; reserva feita no lock 8; MP disponível na cobrança (livre + reserva liberada) 66
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #5** — Carrasco (p2) → Geada (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 103.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 103.0; × arma = 116.38999999999999; × power 2.86 = 332.87539999999996; max(1, int(103.0 × (1 + 13/100) × 2.86)) = **332**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 4.545454545454546 (30 × (19 − 14) / 33) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 89.54545454545455 → clamp [20, 95] e int → **89**
7. Rolagem de acerto: sorteio nº 12 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **1**; chance 89; teste `1 > 89` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 7 = 7, teto 75 → **7**
9. Rolagem de crítico: sorteio nº 13 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 7; teste `34 <= 7` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: damage_percent (passiva, equipamento ou buff) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 51
15. Fator de defesa: 100 / (100 + 51) = 0.6622516556291391
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 332.0 × 1.08 × 1.0 × 0.6622516556291391 = 237.45695364238412; max(1, int(bruto)) = 237 → int(anterior × 1.0) = 237 → int(anterior × 1.0) = 237
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **237**
20. Égide de Mana: desejado int(237 × 15 / 100) = 35; possível min(35, int(201 × 2.0)) = 35; passa max(1, 237 − 35) = 202
21. MP da Égide: max(1, int(35 / 2.0)) = 17
22. Dano aplicado ao HP: `take_damage(202)`; HP do alvo 45 → -157 (retirado 202)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final -157 → o alvo morreu

- Resultado da skill: `damage`; MP debitado 8; recarga depois 2
- Mudanças em quem lançou: mp 66 → 58; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 45 → -157; mp 201 → 184; morreu

- Motor (`action_executed`): Carrasco (p2) executou Golpe Poderoso; MP gasto 8, dano ao adversário 202.

- **Fim do duelo**: vence Carrasco (p2), motivo `ko`.

- Devolução: Geada (p1) recebe de volta 9 MP reservados.
- Ação de Geada (p1) **cancelada por morte**.
### 4.9 Estado ao final da rodada

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| HP | -157/652 | 269/868 |
| MP | 193/280 | 58/123 |
| ST / MG / AG / DF | 53 / 95 / 14 / 51 | 103 / 59 / 19 / 74 |
| Recargas (contador interno) | Palavra de Torpor 1, Bola de Fogo 1, Lasca de Gelo 3 | Cutelada 2, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / False | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- Carrasco (p2): Golpe Poderoso — executada; dano causado na rodada 202 (golpes e DoT), recebido 0; cura 0
- Geada (p1): Palavra de Torpor — cancelada por morte; dano causado na rodada 0 (golpes e DoT), recebido 202; cura 0


## Conclusão da final (fatos registrados)

- Campeão: **Carrasco** (p2); vice: **Geada** (p1).
- Rodadas: 4. Motivo exato: `ko` — o HP de Geada chegou a 0 durante a rodada 4.

| | Geada (p1) | Carrasco (p2) |
|---|---|---|
| Dano causado (golpes + DoT) | 599 (599 + 0) | 809 (809 + 0) |
| HP retirado do adversário | 599 | 809 |
| Cura (skill + roubo) | 0 (0 + 0) | 0 (0 + 0) |
| MP consumido em ações | 28 | 45 |
| MP consumido pela Égide | 69 | 0 |
| Skills usadas | 3: Palavra de Torpor ×1, Bola de Fogo ×1, Lasca de Gelo ×1 | 4: Grito de Guerra ×1, Golpe Poderoso ×2, Cutelada ×1 |
| Ataques básicos | 0 | 0 |
| Acertos / erros | 2 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Status aplicados | slowed (rodada 1), clouded (rodada 1) | — |
| Status que falharam na rolagem | slowed (rodada 3) | — |
| Status anulados por resistência / recusados | — | — |
| Ações perdidas por controle | 0 | 0 |
| Rodadas agindo primeiro | 3 | 1 |
| HP / MP restantes | -157/652 · 193/280 | 269/868 · 58/123 |

HP negativo é o valor cru do motor: `take_damage` não corta em zero, e a sobra mostra quanto o último golpe passou do necessário.

## Todas as chamadas ao gerador

13 chamadas, igual ao contador do proxy (13).

| Nº | Rodada | Ator | Mecânica | Operação | Limites | Valor | Chance | Teste | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | p1 | aplicação de status (slowed) | `randrange` | [1, 100] | 11 | 75.0 | `11 > 75.0` → F | aprovado: passou na rolagem |
| 2 | 1 | p1 | aplicação de status (clouded) | `randrange` | [1, 100] | 24 | 50.0 | `24 > 50.0` → F | aprovado: passou na rolagem |
| 3 | 2 | p1 | acerto | `randrange` | [1, 100] | 33 | 88 | `33 > 88` → F | aprovado: ACERTOU |
| 4 | 2 | p1 | crítico | `randrange` | [1, 100] | 87 | 2 | `87 <= 2` → F | recusado: sem crítico |
| 5 | 2 | p2 | acerto | `randrange` | [1, 100] | 13 | 86 | `13 > 86` → F | aprovado: ACERTOU |
| 6 | 2 | p2 | crítico | `randrange` | [1, 100] | 75 | 7 | `75 <= 7` → F | recusado: sem crítico |
| 7 | 3 | p1 | acerto | `randrange` | [1, 100] | 65 | 88 | `65 > 88` → F | aprovado: ACERTOU |
| 8 | 3 | p1 | crítico | `randrange` | [1, 100] | 78 | 2 | `78 <= 2` → F | recusado: sem crítico |
| 9 | 3 | p1 | aplicação de status (slowed) | `randrange` | [1, 100] | 98 | 45.0 | `98 > 45.0` → V | recusado: falhou na rolagem |
| 10 | 3 | p2 | acerto | `randrange` | [1, 100] | 69 | 89 | `69 > 89` → F | aprovado: ACERTOU |
| 11 | 3 | p2 | crítico | `randrange` | [1, 100] | 61 | 7 | `61 <= 7` → F | recusado: sem crítico |
| 12 | 4 | p2 | acerto | `randrange` | [1, 100] | 1 | 89 | `1 > 89` → F | aprovado: ACERTOU |
| 13 | 4 | p2 | crítico | `randrange` | [1, 100] | 34 | 7 | `34 <= 7` → F | recusado: sem crítico |

## Verificação de fidelidade

A final rodou duas vezes com `random.Random(14556157636677633696)`, os mesmos gladiadores (preparação nova a cada vez) e a mesma política: sem nenhuma instrumentação e auditada.

- ✔ ações escolhidas
- ✔ ordem de cada rodada
- ✔ leituras de iniciativa (floats exatos)
- ✔ passos: desfecho, MP reservado, MP gasto e dano
- ✔ HP e MP ao fim de cada rodada
- ✔ estado completo ao fim de cada rodada (efeitos, buffs, recargas)
- ✔ eventos do motor
- ✔ vencedor, motivo e número de rodadas
- ✔ conclusividade
- ✔ posição final do gerador (nenhum sorteio extra)

Coerência do trace com o que o motor registrou:

- ✔ toda chamada ao gerador foi classificada
- ✔ rolagens registradas = chamadas ao gerador
- ✔ toda rolagem de acerto recebeu a chance do motor
- ✔ toda rolagem pertence ao intervalo do motor
- ✔ dano de cada passo = soma do HP retirado pelos golpes registrados
- ✔ MP gasto de cada passo = débito registrado da skill
- ✔ ações executadas = eventos `action_executed`

Limitação conhecida: as parcelas intermediárias (swing de acerto, termos do BASE, buckets do funil, Égide, regeneração) são recalculadas no instante da chamada com as funções do motor e conferidas contra o valor devolvido; a regeneração de MP é descrita pela mesma fórmula de `process_turn_start_effects`, e o valor resultante aparece no estado logo depois.

## Diagnóstico (interpretação — separado dos fatos acima)

As frases abaixo são leitura dos números registrados, não registros do motor. Onde há estimativa, ela está marcada como tal.

- **Geada**: 2 golpes tentados com chance média de acerto 88.0%, 2 conectaram (100.0%); dano médio por golpe conectado 299.5. O fator de defesa médio que os golpes dele enfrentaram foi 0.5747 e a mitigação de entrada do alvo, 1.0000.
- **Carrasco**: 3 golpes tentados com chance média de acerto 88.0%, 3 conectaram (100.0%); dano médio por golpe conectado 269.7. O fator de defesa médio que os golpes dele enfrentaram foi 0.6623 e a mitigação de entrada do alvo, 1.0000.
- Iniciativa: Carrasco agiu primeiro em 1 de 4 rodadas; Geada, em 3. Na rodada final, a ordem foi Carrasco → Geada (`score`).
- Score de iniciativa por rodada (p1 / p2 → quem agiu primeiro):
  - Rodada 1: 1.005870 / 0.981492 → Geada
  - Rodada 2: 1.005870 / 0.982590 → Geada; atributos efetivos diferentes da rodada 1 — Carrasco: mp 123→99, st 103→139, ag 19→15
  - Rodada 3: 1.005870 / 0.982590 → Geada; atributos efetivos diferentes da rodada 1 — Carrasco: mp 123→99, st 103→139, ag 19→15
  - Rodada 4: 1.005870 / 1.011541 → Carrasco **(a ordem virou)**; atributos efetivos diferentes da rodada 1 — Carrasco: st 103→139; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Grito de Guerra de Carrasco
  - Leitura: o vetor da iniciativa usa ST/MG/AG/DF efetivos e os TETOS de HP e MP, então um buff de atributo do próprio lado e um status do adversário que reduz atributo ou teto entram na ordem da rodada seguinte; quando expiram, saem dela.
- Na última rodada, Geada havia travado Palavra de Torpor (skill de tipo `status`, que não causa dano); a ação ficou cancelada por morte, porque Carrasco agiu antes e o golpe dele encerrou o duelo.
- Margem (estimativa, não registro): Carrasco terminou com 269 de HP; o dano médio por golpe conectado de Geada foi 299.5, ou seja, ~0.9 golpe(s) conectado(s) de distância.
- Sustentação de Geada: cura 0 e Égide 141 contra 809 de dano recebido.
- Economia de ação: Carrasco usou 4 skills e 0 ataques básicos; Geada, 3 e 0.

