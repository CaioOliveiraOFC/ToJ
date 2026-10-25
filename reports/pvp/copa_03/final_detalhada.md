# Copa Arena 03 — Final detalhada: lubatv × fer

Transcrição da final a partir do trace da auditoria (`tools/arena_auditoria.py`), na ordem em que o motor executou. Cada número abaixo foi capturado no momento da execução, pela chamada real da função canônica; os recálculos que explicam um número são feitos com as mesmas funções e constantes e conferidos contra o valor devolvido pelo motor — se divergissem, a auditoria pararia com erro.

## Convenções

- Gerador da partida: `random.Random(6619800792897972838)`, observado por um proxy que delega cada chamada e anota operação, limites, valor e chamador. O proxy não sorteia nada por conta própria.
- Rolagens percentuais do motor: `randrange(1, 101)`, inteiro uniforme em [1, 100]. Não é D20. O desempate de iniciativa usa `random() < 0.5`.
- Acerto: o golpe ERRA quando `rolagem > chance`. Crítico: CRITA quando `rolagem <= chance`. Status: NÃO pega quando `rolagem > chance efetiva`.
- Floats aparecem com `repr`: a precisão total que o motor usou. Nada é arredondado antes de uma comparação.
- Referências de iniciativa: `foundation_reference(nível)` — a média das três classes pelo crescimento canônico. Níveis desta final: [22, 23].
- Golpes de skill são resolvidos por `apply_skill` com `publish=None`; a auditoria os vê porque intercepta a função no módulo, não o EventBus.
- Limite técnico do laço: 500 rodadas (não atingido).

## Referências globais usadas

| Nível | REF_hp | REF_mp | REF_st | REF_mg | REF_ag | REF_df |
|---|---|---|---|---|---|---|
| 22 | 4047.6666666666665 | 1044.3333333333333 | 457.3333333333333 | 410.6666666666667 | 158.33333333333334 | 299.0 |
| 23 | 4533.333333333333 | 1169.6666666666667 | 512.3333333333334 | 459.6666666666667 | 177.66666666666666 | 335.0 |

## Fichas completas antes do duelo

### p1 — lubatv (Guerreiro, nível 22)

- HP 5275/5275, MP 908/908; ST 547, MG 337, AG 114, DF 527
- Arma: +14.0% de dano; Égide de Mana: 0%
- Equipamento: Helmet: Elmo de Dragão; Amulet: Amuleto da Mana +1; Weapon1: Gládio de Ferro; Weapon2: Lança de Madeira +1; Body: Armadura Titânica; Legs: Calça de Cota; Hands: Martelo de Mão; Shoes: Chinelos de Pano; Ring1: Anel Vegetal +1; Ring2: Anel de Palha
- Passivas: Músculos de Aço (strength 3), Postura Fechada (damage_reduction 3), Reserva Arcana (max_mp 20), Olho de Caçador (precision 5), Vulto (evasion 15), Postura Fechada (damage_reduction 3), Pele Grossa (defense 3), Casco Calejado (defense 8), Alma Eterna (max_hp 100), Toque do Dragão (strength 15), Sangue de Guerreiro (max_hp 25), Postura Fechada (damage_reduction 3), Passo de Corça (agility 4), Lâmina Afiada (crit_chance 10), Reserva Arcana (max_mp 20), Olho de Águia (crit_chance 5), Vulto (evasion 15), Lâmina Afiada (crit_chance 10), Lâmina Afiada (crit_chance 10), Bênção Divina (max_hp 70), Passos Leves (agility 2)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 35.0, damage_reduction 29.0, evasion 30.0, precision 5.0, stun_chance 2.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Esmagar (`esmagar`) | damage | 0 | 144 | 4 | 4.24 × (0.8×st + 0.2×df) | -10 | 0 | stun 30% por 1 | target_wounded +70% | — |
| Quebra-Guarda (`quebra_guarda`) | damage | 0 | 63 | 2 | 3.619 × (1.0×st) | +0 | 0 | vulnerable 45% por 3 | target_healthy +12% | uma espada |
| Tomar Fôlego (`tomar_folego`) | heal | 12 | 83 | 4 | 0.0 × (—) | +0 | 0 | — | — | — |
| Postura Impecável (`n_postura_impecavel`) | buff | 55 st por 4 | 131 | 5 | 0.0 × (—) | +0 | 0 | — | — | — |

### p2 — fer (Guerreiro, nível 23)

- HP 5977/5977, MP 1103/1103; ST 654, MG 446, AG 142, DF 503
- Arma: +13.0% de dano; Égide de Mana: 0%
- Equipamento: Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +2; Weapon1: Cajado de Cristal; Weapon2: Porrete +1; Body: Placa Pesada; Legs: Calça de Cota; Hands: Luvas de Aço +1; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante +1; Accessory: Talismã do Viajante +1
- Passivas: Sangue de Guerreiro (max_hp 25), Essência Fluída (max_hp 40), Coração de Ferro (max_hp 15), Instinto Frio (precision 10), Olho de Águia (crit_chance 5), Herança do Abismo (magic 8), Bênção Divina (max_hp 70), Postura Fechada (damage_reduction 3), Boca de Sangue (life_steal 4), Pele Grossa (defense 3), Coração de Ferro (max_hp 15), Fúria Berserker (strength 8), Coração de Ferro (max_hp 15), Essência Fluída (max_hp 40), Vulto (evasion 15), Essência Fluída (max_hp 40), Coração de Ferro (max_hp 15), Boca de Sangue (life_steal 4), Músculos de Aço (strength 3), Essência Fluída (max_hp 40), Sede de Sangue (crit_chance 18), Escudo da Fé (damage_reduction 5)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 30.0, crit_damage 10.0, damage_reduction 11.0, evasion 15.0, precision 10.0, life_steal 13.0, stun_chance 2.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Golpe Poderoso (`golpe_poderoso`) | damage | 0 | 52 | 1 | 2.86 × (1.0×st) | +0 | 0 | — | target_healthy +8% | — |
| Juramento da Muralha (`juramento_da_muralha`) | damage_reduction | 45 por 4 | 152 | 5 | 0.0 × (—) | +0 | 0 | — | — | as duas mãos ocupadas |
| Soco de Placa (`soco_de_placa`) | damage | 0 | 61 | 1 | 3.012 × (1.0×st) | +0 | 0 | weakened 35% por 2 | caster_wounded +20% | — |
| Respirar Fundo (`n_respirar_fundo`) | heal | 10 | 82 | 4 | 0.0 × (—) | +0 | 0 | — | — | — |

## Rodada 1

### 1.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5275/5275 | 5977/5977 |
| MP | 908/908 | 1103/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 1.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 1): eu HP 5275/5275, MP 908/908, efeitos —, buffs —; adversário fer HP 5977/5977, MP 1103/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável, Rendição
- Escolha: **Postura Impecável** — justificativa da política: Postura Impecável é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**fer (p2)**

- Estado recebido (`DuelView`, rodada 1): eu HP 5977/5977, MP 1103/1103, efeitos —, buffs —; adversário lubatv HP 5275/5275, MP 908/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 152

- Lock: lubatv (p1) reserva **131 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **152 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Postura Impecável; fer (p2) = Juramento da Muralha

### 1.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 951 → min(1103, 951 + 22) = 973
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 951 → 973
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 152, teto livre 951 → MP 973 → 951
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de fer (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 152 MP; reserva feita no lock 152; MP disponível na cobrança (livre + reserva liberada) 1103
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 152; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 1103 → 951; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Juramento da Muralha; MP gasto 152, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 777 → min(908, 777 + 18) = 795
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 777 → 795
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 777 → MP 795 → 777
- Perde a oportunidade por controle: não

**Skill Postura Impecável** (`n_postura_impecavel`) de lubatv (p1)

- Tipo `buff`, valor 55 st; alvo declarado `self` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 908
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Buff: st declarado 55 → valor gravado 300 (percentual de base_st: max(1, int(base × 55/100)))

- Resultado da skill: `buff`; MP debitado 131; recarga depois 6; buff gravado {'stat': 'st', 'value': 300, 'duration': 4}
- Mudanças em quem lançou: mp 908 → 777; st 547 → 847; recarga Postura Impecável — → 6; buff Postura Impecável entra (st 300, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Postura Impecável; MP gasto 131, dano ao adversário 0.

### 1.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5275/5275 | 5977/5977 |
| MP | 777/908 | 951/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 6 | Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- lubatv (p1): Postura Impecável — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 2

### 2.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5275/5275 | 5977/5977 |
| MP | 777/908 | 951/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 6 | Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 2.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 2): eu HP 5275/5275, MP 777/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 5977/5977, MP 951/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 5
- Ações legais: Ataque básico, Esmagar, Quebra-Guarda, Tomar Fôlego, Rendição
- Escolha: **Esmagar** — justificativa da política: primeira skill de dano legal do deck: Esmagar
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 144

**fer (p2)**

- Estado recebido (`DuelView`, rodada 2): eu HP 5977/5977, MP 951/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 5275/5275, MP 777/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 5, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: lubatv (p1) reserva **144 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Esmagar; fer (p2) = Golpe Poderoso

### 2.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 6 → 5
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 633 → min(908, 633 + 18) = 651
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 633 → 651; recarga Postura Impecável 6 → 5; buff Postura Impecável dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 144, teto livre 764 → MP 651 → 651
- Perde a oportunidade por controle: não

**Skill Esmagar** (`esmagar`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 144 MP; reserva feita no lock 144; MP disponível na cobrança (livre + reserva liberada) 795
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #1** — lubatv (p1) → fer (p2), skill `esmagar`

1. Atributos ofensivos efetivos: st 847.0, df 527.0
2. Pesos (da carta): st 0.8, df 0.2
3. Poder básico da ação: Σ = 783.0; × arma = 892.6200000000001; × power 4.24 = 3784.708800000001; max(1, int(783.0 × (1 + 14/100) × 4.24)) = **3784**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação -10 − ocultação 0 = 61.71875 → clamp [20, 95] e int → **61**
7. Rolagem de acerto: sorteio nº 1 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 61; teste `9 > 61` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 2 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 35; teste `14 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3784.0 × 1.0 × 1.5 × 0.16583747927031509 = 941.2935323383084; max(1, int(bruto)) = 941 → int(anterior × 1.0) = 941 → int(anterior × 0.43999999999999995) = 414
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **414**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 414
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(414)`; HP do alvo 5977 → 5563 (retirado 414)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 5563 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 3 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 2.0; teste `81 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `stun`** sobre fer (p2) (via `_aplicar_secundario`, fonte `esmagar`)

- Chance base 30%; resistência do alvo 0.0% → efetiva 30 × (1 − 0/100) = 30.0%
- sorteio nº 4 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **86**; chance 30.0; teste `86 > 30.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 144; recarga depois 5
- Mudanças em quem lançou: mp 795 → 651; recarga Esmagar — → 5
- Mudanças no adversário: hp 5977 → 5563

- Motor (`action_executed`): lubatv (p1) executou Esmagar; MP gasto 144, dano ao adversário 414.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 899 → min(1103, 899 + 22) = 921
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 899 → 921; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 921 → 921
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 973
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #2** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 5 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 68; teste `30 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 6 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 30; teste `98 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.1594896331738437 = 363.9617224880383; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.71) = 257
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **257**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 257
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(257)`; HP do alvo 5275 → 5018 (retirado 257)
23. Roubo de vida: 13.0% → max(1, int(257 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final 5018 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 7 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 2.0; teste `44 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5563 → 5596; mp 973 → 921; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5275 → 5018

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 257.

### 2.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5018/5275 | 5596/5977 |
| MP | 651/908 | 921/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Esmagar — executada; dano causado na rodada 414 (golpes e DoT), recebido 257; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 257 (golpes e DoT), recebido 414; cura 33


## Rodada 3

### 3.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5018/5275 | 5596/5977 |
| MP | 651/908 | 921/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 3.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 3): eu HP 5018/5275, MP 651/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 5596/5977, MP 921/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 4, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 4
- Ações legais: Ataque básico, Quebra-Guarda, Tomar Fôlego, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 3): eu HP 5596/5977, MP 921/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 5018/5275, MP 651/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 4, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Soco de Placa

### 3.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 5 → 4; Esmagar 5 → 4
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 588 → min(908, 588 + 18) = 606
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 588 → 606; recarga Esmagar 5 → 4; recarga Postura Impecável 5 → 4; buff Postura Impecável dur 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 606 → 606
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 669
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #3** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 847.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 847.0; × arma = 965.5800000000002; × power 3.619 = 3494.4340200000006; max(1, int(847.0 × (1 + 14/100) × 3.619)) = **3494**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 8 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 71; teste `70 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 9 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 35; teste `71 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.12 → 1 + Σ = 1.12
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3494.0 × 1.12 × 1.0 × 0.16583747927031509 = 648.9684908789386; max(1, int(bruto)) = 648 → int(anterior × 1.0) = 648 → int(anterior × 0.43999999999999995) = 285
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **285**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 285
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(285)`; HP do alvo 5596 → 5311 (retirado 285)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 5311 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 10 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 2.0; teste `88 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 11 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 45.0; teste `94 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 669 → 606; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 5596 → 5311

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 285.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 860 → min(1103, 860 + 22) = 882
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 860 → 882; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 5 → 4; buff Juramento da Muralha dur 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 882 → 882
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 943
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #4** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 12 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 68; teste `79 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 5018 → 5018)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 943 → 882; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 3.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5018/5275 | 5311/5977 |
| MP | 606/908 | 882/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 285 (golpes e DoT), recebido 0; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 285; cura 0


## Rodada 4

### 4.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 5018/5275 | 5311/5977 |
| MP | 606/908 | 882/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 4.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 4): eu HP 5018/5275, MP 606/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 5311/5977, MP 882/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 3, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 3
- Ações legais: Ataque básico, Tomar Fôlego, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 4): eu HP 5311/5977, MP 882/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 5018/5275, MP 606/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 3, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 4.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 4 → 3; Esmagar 4 → 3; Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 606 → min(908, 606 + 18) = 624
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 606 → 624; recarga Esmagar 4 → 3; recarga Postura Impecável 4 → 3; recarga Quebra-Guarda 3 → 2; buff Postura Impecável dur 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 624 → 624
- Perde a oportunidade por controle: não

**Golpe #5** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 847.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1490.0; dano médio max(1, int(1490.0 × (1 + 14/100))) = 1698; BASE do básico = max(1, int(1698 × 0.9)) = **1528** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 13 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **17**; chance 71; teste `17 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 14 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **92**; chance 35; teste `92 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1528.0 × 1.0 × 1.0 × 0.16583747927031509 = 253.39966832504146; max(1, int(bruto)) = 253 → int(anterior × 1.0) = 253 → int(anterior × 0.43999999999999995) = 111
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **111**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 111
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(111)`; HP do alvo 5311 → 5200 (retirado 111)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 5200 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 15 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **47**; chance 2.0; teste `47 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 111.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 830 → min(1103, 830 + 22) = 852
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 830 → 852; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 4 → 3; recarga Soco de Placa 2 → 1; buff Juramento da Muralha dur 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 852 → 852
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 904
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #6** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 16 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 68; teste `11 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 17 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 30; teste `94 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.1594896331738437 = 363.9617224880383; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.71) = 257
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **257**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 257
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(257)`; HP do alvo 5018 → 4761 (retirado 257)
23. Roubo de vida: 13.0% → max(1, int(257 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final 4761 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 18 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **72**; chance 2.0; teste `72 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5200 → 5233; mp 904 → 852; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5018 → 4761

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 257.

### 4.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4761/5275 | 5233/5977 |
| MP | 624/908 | 852/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 111 (golpes e DoT), recebido 257; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 257 (golpes e DoT), recebido 111; cura 33


## Rodada 5

### 5.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4761/5275 | 5233/5977 |
| MP | 624/908 | 852/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 5.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 5): eu HP 4761/5275, MP 624/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 5233/5977, MP 852/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 2, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 2
- Ações legais: Ataque básico, Tomar Fôlego, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 5): eu HP 5233/5977, MP 852/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 4761/5275, MP 624/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 2, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Soco de Placa

### 5.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 3 → 2; Esmagar 3 → 2; Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 624 → min(908, 624 + 18) = 642
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 624 → 642; st 847 → 547; recarga Esmagar 3 → 2; recarga Postura Impecável 3 → 2; recarga Quebra-Guarda 2 → 1; buff Postura Impecável expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 642 → 642
- Perde a oportunidade por controle: não

**Golpe #7** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 19 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 71; teste `20 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 20 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **93**; chance 35; teste `93 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.16583747927031509 = 171.6417910447761; max(1, int(bruto)) = 171 → int(anterior × 1.0) = 171 → int(anterior × 0.43999999999999995) = 75
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **75**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 75
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(75)`; HP do alvo 5233 → 5158 (retirado 75)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 5158 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 21 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 2.0; teste `60 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 75.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 791 → min(1103, 791 + 22) = 813
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 791 → 813; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 3 → 2; recarga Soco de Placa 1 → livre; buff Juramento da Muralha expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 813 → 813
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 874
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #8** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 22 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **84**; chance 68; teste `84 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4761 → 4761)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 874 → 813; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 5.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4761/5275 | 5158/5977 |
| MP | 642/908 | 813/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 75 (golpes e DoT), recebido 0; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 75; cura 0


## Rodada 6

### 6.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4761/5275 | 5158/5977 |
| MP | 642/908 | 813/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 6.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 6): eu HP 4761/5275, MP 642/908, efeitos —, buffs —; adversário fer HP 5158/5977, MP 813/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 1, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 1
- Ações legais: Ataque básico, Quebra-Guarda, Tomar Fôlego, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 6): eu HP 5158/5977, MP 813/1103, efeitos —, buffs —; adversário lubatv HP 4761/5275, MP 642/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 1, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Golpe Poderoso

### 6.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 761 → min(1103, 761 + 22) = 783
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 761 → 783; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 2 → 1; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 783 → 783
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 835
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #9** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 23 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 68; teste `9 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 24 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 30; teste `50 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.1594896331738437 = 363.9617224880383; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.71) = 257
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **257**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 257
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(257)`; HP do alvo 4761 → 4504 (retirado 257)
23. Roubo de vida: 13.0% → max(1, int(257 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final 4504 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 25 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 2.0; teste `12 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5158 → 5191; mp 835 → 783; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4761 → 4504

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 257.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 2 → 1; Esmagar 2 → 1; Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 579 → min(908, 579 + 18) = 597
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 579 → 597; recarga Esmagar 2 → 1; recarga Postura Impecável 2 → 1; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 597 → 597
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 660
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #10** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 26 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 71; teste `50 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 27 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 35; teste `89 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.12 → 1 + Σ = 1.12
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.12 × 1.0 × 0.16583747927031509 = 419.0248756218906; max(1, int(bruto)) = 419 → int(anterior × 1.0) = 419 → int(anterior × 0.89) = 372
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **372**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 372
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(372)`; HP do alvo 5191 → 4819 (retirado 372)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4819 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 28 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 2.0; teste `71 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 29 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 45.0; teste `29 > 45.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'quebra_guarda'}]

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 660 → 597; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 5191 → 4819; df 503 → 402; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 372.

### 6.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4504/5275 | 4819/5977 |
| MP | 597/908 | 783/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1, Quebra-Guarda 3 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 3, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 257 (golpes e DoT), recebido 372; cura 33
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 372 (golpes e DoT), recebido 257; cura 0


## Rodada 7

### 7.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4504/5275 | 4819/5977 |
| MP | 597/908 | 783/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1, Quebra-Guarda 3 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 3, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 7.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 7): eu HP 4504/5275, MP 597/908, efeitos —, buffs —; adversário fer HP 4819/5977, MP 783/1103, efeitos ['vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Esmagar, Tomar Fôlego, Postura Impecável, Rendição
- Escolha: **Postura Impecável** — justificativa da política: Postura Impecável é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**fer (p2)**

- Estado recebido (`DuelView`, rodada 7): eu HP 4819/5977, MP 783/1103, efeitos ['vulnerable'], buffs —; adversário lubatv HP 4504/5275, MP 597/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 152

- Lock: lubatv (p1) reserva **131 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **152 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Postura Impecável; fer (p2) = Juramento da Muralha

### 7.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 631 → min(1103, 631 + 22) = 653
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 631 → 653; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 1 → livre; recarga Soco de Placa 1 → livre; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 152, teto livre 951 → MP 653 → 653
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de fer (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 152 MP; reserva feita no lock 152; MP disponível na cobrança (livre + reserva liberada) 805
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 152; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 805 → 653; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Juramento da Muralha; MP gasto 152, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 1 → livre; Esmagar 1 → livre; Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 466 → min(908, 466 + 18) = 484
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 466 → 484; recarga Esmagar 1 → livre; recarga Postura Impecável 1 → livre; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 777 → MP 484 → 484
- Perde a oportunidade por controle: não

**Skill Postura Impecável** (`n_postura_impecavel`) de lubatv (p1)

- Tipo `buff`, valor 55 st; alvo declarado `self` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 615
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Buff: st declarado 55 → valor gravado 300 (percentual de base_st: max(1, int(base × 55/100)))

- Resultado da skill: `buff`; MP debitado 131; recarga depois 6; buff gravado {'stat': 'st', 'value': 300, 'duration': 4}
- Mudanças em quem lançou: mp 615 → 484; st 547 → 847; recarga Postura Impecável — → 6; buff Postura Impecável entra (st 300, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Postura Impecável; MP gasto 131, dano ao adversário 0.

### 7.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4504/5275 | 4819/5977 |
| MP | 484/908 | 653/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 2, Postura Impecável 6 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- lubatv (p1): Postura Impecável — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 8

### 8.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4504/5275 | 4819/5977 |
| MP | 484/908 | 653/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 2, Postura Impecável 6 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 8.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 8): eu HP 4504/5275, MP 484/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4819/5977, MP 653/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 5
- Ações legais: Ataque básico, Esmagar, Tomar Fôlego, Rendição
- Escolha: **Esmagar** — justificativa da política: primeira skill de dano legal do deck: Esmagar
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 144

**fer (p2)**

- Estado recebido (`DuelView`, rodada 8): eu HP 4819/5977, MP 653/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 4504/5275, MP 484/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 5, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: lubatv (p1) reserva **144 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Esmagar; fer (p2) = Golpe Poderoso

### 8.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1; Postura Impecável 6 → 5
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 340 → min(908, 340 + 18) = 358
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 340 → 358; recarga Postura Impecável 6 → 5; recarga Quebra-Guarda 2 → 1; buff Postura Impecável dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 144, teto livre 764 → MP 358 → 358
- Perde a oportunidade por controle: não

**Skill Esmagar** (`esmagar`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 144 MP; reserva feita no lock 144; MP disponível na cobrança (livre + reserva liberada) 502
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #11** — lubatv (p1) → fer (p2), skill `esmagar`

1. Atributos ofensivos efetivos: st 847.0, df 527.0
2. Pesos (da carta): st 0.8, df 0.2
3. Poder básico da ação: Σ = 783.0; × arma = 892.6200000000001; × power 4.24 = 3784.708800000001; max(1, int(783.0 × (1 + 14/100) × 4.24)) = **3784**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação -10 − ocultação 0 = 61.71875 → clamp [20, 95] e int → **61**
7. Rolagem de acerto: sorteio nº 30 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 61; teste `85 > 61` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4819 → 4819)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 144; recarga depois 5
- Mudanças em quem lançou: mp 502 → 358; recarga Esmagar — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Esmagar; MP gasto 144, dano ao adversário 0.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 601 → min(1103, 601 + 22) = 623
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 601 → 623; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 623 → 623
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 675
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #12** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 31 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 68; teste `64 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 32 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 30; teste `25 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.6 × 0.1594896331738437 = 582.3387559808613; max(1, int(bruto)) = 582 → int(anterior × 1.0) = 582 → int(anterior × 0.71) = 413
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **413**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 413
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(413)`; HP do alvo 4504 → 4091 (retirado 413)
23. Roubo de vida: 13.0% → max(1, int(413 × 13 / 100)) = 53; HP do atacante +53 (teto do HP máximo)
24. Morte e death_ignore: HP final 4091 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 33 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 2.0; teste `55 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4819 → 4872; mp 675 → 623; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4504 → 4091

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 413.

### 8.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4091/5275 | 4872/5977 |
| MP | 358/908 | 623/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 1, Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Esmagar — executada; dano causado na rodada 0 (golpes e DoT), recebido 413; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 413 (golpes e DoT), recebido 0; cura 53


## Rodada 9

### 9.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4091/5275 | 4872/5977 |
| MP | 358/908 | 623/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 1, Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 9.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 9): eu HP 4091/5275, MP 358/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4872/5977, MP 623/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 4, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 4
- Ações legais: Ataque básico, Quebra-Guarda, Tomar Fôlego, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 9): eu HP 4872/5977, MP 623/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 4091/5275, MP 358/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 4, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Soco de Placa

### 9.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre; Postura Impecável 5 → 4; Esmagar 5 → 4
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 295 → min(908, 295 + 18) = 313
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 295 → 313; recarga Esmagar 5 → 4; recarga Postura Impecável 5 → 4; recarga Quebra-Guarda 1 → livre; buff Postura Impecável dur 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 313 → 313
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 376
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #13** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 847.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 847.0; × arma = 965.5800000000002; × power 3.619 = 3494.4340200000006; max(1, int(847.0 × (1 + 14/100) × 3.619)) = **3494**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 34 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 71; teste `48 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 35 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **13**; chance 35; teste `13 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: condição da carta (target_healthy) 0.12 → 1 + Σ = 1.12
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 402
15. Fator de defesa: 100 / (100 + 402) = 0.199203187250996
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3494.0 × 1.12 × 1.5 × 0.199203187250996 = 1169.3067729083664; max(1, int(bruto)) = 1169 → int(anterior × 1.0) = 1169 → int(anterior × 0.43999999999999995) = 514
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **514**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 514
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(514)`; HP do alvo 4872 → 4358 (retirado 514)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4358 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 36 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **93**; chance 2.0; teste `93 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 37 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 45.0; teste `9 > 45.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'quebra_guarda'}]; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'quebra_guarda'}]

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 376 → 313; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 4872 → 4358; efeito vulnerable: dur 1 → 3, stacks 1 → 1

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 514.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 562 → min(1103, 562 + 22) = 584
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 562 → 584; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 5 → 4; buff Juramento da Muralha dur 3 → 2; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 584 → 584
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 645
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #14** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 38 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **73**; chance 68; teste `73 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4091 → 4091)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 645 → 584; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 9.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4091/5275 | 4358/5977 |
| MP | 313/908 | 584/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 514 (golpes e DoT), recebido 0; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 514; cura 0


## Rodada 10

### 10.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 4091/5275 | 4358/5977 |
| MP | 313/908 | 584/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 10.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 10): eu HP 4091/5275, MP 313/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4358/5977, MP 584/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 3, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 3
- Ações legais: Ataque básico, Tomar Fôlego, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 10): eu HP 4358/5977, MP 584/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 4091/5275, MP 313/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 3, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 10.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 4 → 3; Esmagar 4 → 3; Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 313 → min(908, 313 + 18) = 331
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 313 → 331; recarga Esmagar 4 → 3; recarga Postura Impecável 4 → 3; recarga Quebra-Guarda 3 → 2; buff Postura Impecável dur 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 331 → 331
- Perde a oportunidade por controle: não

**Golpe #15** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 847.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1490.0; dano médio max(1, int(1490.0 × (1 + 14/100))) = 1698; BASE do básico = max(1, int(1698 × 0.9)) = **1528** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 39 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 71; teste `85 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4358 → 4358)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 532 → min(1103, 532 + 22) = 554
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 532 → 554; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 4 → 3; recarga Soco de Placa 2 → 1; buff Juramento da Muralha dur 2 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 554 → 554
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 606
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #16** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 40 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 68; teste `53 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 41 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 30; teste `34 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.1594896331738437 = 337.00159489633177; max(1, int(bruto)) = 337 → int(anterior × 1.0) = 337 → int(anterior × 0.71) = 239
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **239**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 239
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(239)`; HP do alvo 4091 → 3852 (retirado 239)
23. Roubo de vida: 13.0% → max(1, int(239 × 13 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 3852 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 42 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **36**; chance 2.0; teste `36 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4358 → 4389; mp 606 → 554; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4091 → 3852

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 239.

### 10.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3852/5275 | 4389/5977 |
| MP | 331/908 | 554/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 239; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 239 (golpes e DoT), recebido 0; cura 31


## Rodada 11

### 11.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3852/5275 | 4389/5977 |
| MP | 331/908 | 554/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 11.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 11): eu HP 3852/5275, MP 331/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4389/5977, MP 554/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 2, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 2
- Ações legais: Ataque básico, Tomar Fôlego, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 11): eu HP 4389/5977, MP 554/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 3852/5275, MP 331/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 2, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Soco de Placa

### 11.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 3 → 2; Esmagar 3 → 2; Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 331 → min(908, 331 + 18) = 349
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 331 → 349; st 847 → 547; recarga Esmagar 3 → 2; recarga Postura Impecável 3 → 2; recarga Quebra-Guarda 2 → 1; buff Postura Impecável expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 349 → 349
- Perde a oportunidade por controle: não

**Golpe #17** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 43 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 71; teste `44 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 44 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 35; teste `48 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 402
15. Fator de defesa: 100 / (100 + 402) = 0.199203187250996
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.199203187250996 = 206.17529880478088; max(1, int(bruto)) = 206 → int(anterior × 1.0) = 206 → int(anterior × 0.43999999999999995) = 90
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **90**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 90
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(90)`; HP do alvo 4389 → 4299 (retirado 90)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4299 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 45 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 2.0; teste `63 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 90.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 493 → min(1103, 493 + 22) = 515
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 493 → 515; df 402 → 503; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 3 → 2; recarga Soco de Placa 1 → livre; buff Juramento da Muralha expira; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 515 → 515
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 576
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #18** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 46 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **24**; chance 68; teste `24 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 47 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **5**; chance 30; teste `5 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.6 × 0.1594896331738437 = 567.7830940988836; max(1, int(bruto)) = 567 → int(anterior × 1.0) = 567 → int(anterior × 0.71) = 402
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **402**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 402
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(402)`; HP do alvo 3852 → 3450 (retirado 402)
23. Roubo de vida: 13.0% → max(1, int(402 × 13 / 100)) = 52; HP do atacante +52 (teto do HP máximo)
24. Morte e death_ignore: HP final 3450 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 48 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 2.0; teste `35 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre lubatv (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 49 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 35.0; teste `14 > 35.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 2 → após leis (nenhuma) 2; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `weakened` no alvo antes: —; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'soco_de_placa'}]

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 4299 → 4351; mp 576 → 515; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3852 → 3450; st 547 → 437; efeito weakened entra (dur 2, stacks 1, int 20.0)

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 402.

### 11.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3450/5275 | 4351/5977 |
| MP | 349/908 | 515/1103 |
| ST / MG / AG / DF | 437 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 2, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 90 (golpes e DoT), recebido 402; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 402 (golpes e DoT), recebido 90; cura 52


## Rodada 12

### 12.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3450/5275 | 4351/5977 |
| MP | 349/908 | 515/1103 |
| ST / MG / AG / DF | 437 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 2, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

### 12.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 12): eu HP 3450/5275, MP 349/908, efeitos ['weakened'], buffs —; adversário fer HP 4351/5977, MP 515/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 1, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 1
- Ações legais: Ataque básico, Quebra-Guarda, Tomar Fôlego, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 12): eu HP 4351/5977, MP 515/1103, efeitos —, buffs —; adversário lubatv HP 3450/5275, MP 349/908, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 1, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Golpe Poderoso

### 12.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 437.0 | 457.3333333333333 | 0.9555393586005831 | 0.9775169351988656 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.133563565849716
- ÷ 6 = build 1.022260594308286
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.022260594308286 × 0.995 = 1.0171492913367446**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0171492913367446 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 463 → min(1103, 463 + 22) = 485
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 463 → 485; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 2 → 1; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 485 → 485
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 537
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #19** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 50 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 68; teste `3 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 51 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 30; teste `2 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.1594896331738437 = 539.2025518341309; max(1, int(bruto)) = 539 → int(anterior × 1.0) = 539 → int(anterior × 0.71) = 382
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **382**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 382
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(382)`; HP do alvo 3450 → 3068 (retirado 382)
23. Roubo de vida: 13.0% → max(1, int(382 × 13 / 100)) = 49; HP do atacante +49 (teto do HP máximo)
24. Morte e death_ignore: HP final 3068 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 52 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 2.0; teste `20 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4351 → 4400; mp 537 → 485; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3450 → 3068

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 382.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 2 → 1; Esmagar 2 → 1; Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 286 → min(908, 286 + 18) = 304
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 286 → 304; recarga Esmagar 2 → 1; recarga Postura Impecável 2 → 1; recarga Quebra-Guarda 1 → livre; efeito weakened: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 304 → 304
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 367
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #20** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 437.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 437.0; × arma = 498.18000000000006; × power 3.619 = 1802.9134200000003; max(1, int(437.0 × (1 + 14/100) × 3.619)) = **1802**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 53 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **76**; chance 71; teste `76 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4400 → 4400)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 367 → 304; recarga Quebra-Guarda — → 3
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 0.

### 12.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3068/5275 | 4400/5977 |
| MP | 304/908 | 485/1103 |
| ST / MG / AG / DF | 437 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1, Quebra-Guarda 3 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 382 (golpes e DoT), recebido 0; cura 49
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 0 (golpes e DoT), recebido 382; cura 0


## Rodada 13

### 13.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3068/5275 | 4400/5977 |
| MP | 304/908 | 485/1103 |
| ST / MG / AG / DF | 437 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1, Quebra-Guarda 3 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

### 13.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 13): eu HP 3068/5275, MP 304/908, efeitos ['weakened'], buffs —; adversário fer HP 4400/5977, MP 485/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Esmagar, Tomar Fôlego, Postura Impecável, Rendição
- Escolha: **Postura Impecável** — justificativa da política: Postura Impecável é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**fer (p2)**

- Estado recebido (`DuelView`, rodada 13): eu HP 4400/5977, MP 485/1103, efeitos —, buffs —; adversário lubatv HP 3068/5275, MP 304/908, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 152

- Lock: lubatv (p1) reserva **131 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **152 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Postura Impecável; fer (p2) = Juramento da Muralha

### 13.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 437.0 | 457.3333333333333 | 0.9555393586005831 | 0.9775169351988656 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.133563565849716
- ÷ 6 = build 1.022260594308286
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.022260594308286 × 0.995 = 1.0171492913367446**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0171492913367446 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 333 → min(1103, 333 + 22) = 355
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 333 → 355; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 1 → livre; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 152, teto livre 951 → MP 355 → 355
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de fer (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 152 MP; reserva feita no lock 152; MP disponível na cobrança (livre + reserva liberada) 507
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 152; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 507 → 355; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Juramento da Muralha; MP gasto 152, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 1 → livre; Esmagar 1 → livre; Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 173 → min(908, 173 + 18) = 191
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['weakened'], leis —, pula a vez: False
- Mudanças de estado no início: mp 173 → 191; st 437 → 547; recarga Esmagar 1 → livre; recarga Postura Impecável 1 → livre; recarga Quebra-Guarda 3 → 2; efeito weakened sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 777 → MP 191 → 191
- Perde a oportunidade por controle: não

**Skill Postura Impecável** (`n_postura_impecavel`) de lubatv (p1)

- Tipo `buff`, valor 55 st; alvo declarado `self` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 322
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Buff: st declarado 55 → valor gravado 300 (percentual de base_st: max(1, int(base × 55/100)))

- Resultado da skill: `buff`; MP debitado 131; recarga depois 6; buff gravado {'stat': 'st', 'value': 300, 'duration': 4}
- Mudanças em quem lançou: mp 322 → 191; st 547 → 847; recarga Postura Impecável — → 6; buff Postura Impecável entra (st 300, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Postura Impecável; MP gasto 131, dano ao adversário 0.

### 13.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3068/5275 | 4400/5977 |
| MP | 191/908 | 355/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2, Postura Impecável 6 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- lubatv (p1): Postura Impecável — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 14

### 14.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 3068/5275 | 4400/5977 |
| MP | 191/908 | 355/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2, Postura Impecável 6 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | Postura Impecável (st 300, dur 4) | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 14.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 14): eu HP 3068/5275, MP 191/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4400/5977, MP 355/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 5
- Ações legais: Ataque básico, Esmagar, Tomar Fôlego, Rendição
- Escolha: **Esmagar** — justificativa da política: primeira skill de dano legal do deck: Esmagar
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 144

**fer (p2)**

- Estado recebido (`DuelView`, rodada 14): eu HP 4400/5977, MP 355/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 3068/5275, MP 191/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 5, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: lubatv (p1) reserva **144 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Esmagar; fer (p2) = Golpe Poderoso

### 14.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1; Postura Impecável 6 → 5
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 47 → min(908, 47 + 18) = 65
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 47 → 65; recarga Postura Impecável 6 → 5; recarga Quebra-Guarda 2 → 1; buff Postura Impecável dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 144, teto livre 764 → MP 65 → 65
- Perde a oportunidade por controle: não

**Skill Esmagar** (`esmagar`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 144 MP; reserva feita no lock 144; MP disponível na cobrança (livre + reserva liberada) 209
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #21** — lubatv (p1) → fer (p2), skill `esmagar`

1. Atributos ofensivos efetivos: st 847.0, df 527.0
2. Pesos (da carta): st 0.8, df 0.2
3. Poder básico da ação: Σ = 783.0; × arma = 892.6200000000001; × power 4.24 = 3784.708800000001; max(1, int(783.0 × (1 + 14/100) × 4.24)) = **3784**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação -10 − ocultação 0 = 61.71875 → clamp [20, 95] e int → **61**
7. Rolagem de acerto: sorteio nº 54 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **65**; chance 61; teste `65 > 61` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4400 → 4400)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 144; recarga depois 5
- Mudanças em quem lançou: mp 209 → 65; recarga Esmagar — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Esmagar; MP gasto 144, dano ao adversário 0.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 303 → min(1103, 303 + 22) = 325
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 303 → 325; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 325 → 325
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 377
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #22** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 55 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 68; teste `56 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 56 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 30; teste `29 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.1594896331738437 = 539.2025518341309; max(1, int(bruto)) = 539 → int(anterior × 1.0) = 539 → int(anterior × 0.71) = 382
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **382**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 382
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(382)`; HP do alvo 3068 → 2686 (retirado 382)
23. Roubo de vida: 13.0% → max(1, int(382 × 13 / 100)) = 49; HP do atacante +49 (teto do HP máximo)
24. Morte e death_ignore: HP final 2686 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 57 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **68**; chance 2.0; teste `68 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4400 → 4449; mp 377 → 325; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3068 → 2686

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 382.

### 14.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2686/5275 | 4449/5977 |
| MP | 65/908 | 325/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1, Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Esmagar — executada; dano causado na rodada 0 (golpes e DoT), recebido 382; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 382 (golpes e DoT), recebido 0; cura 49


## Rodada 15

### 15.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2686/5275 | 4449/5977 |
| MP | 65/908 | 325/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1, Postura Impecável 5, Esmagar 5 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 3) | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 15.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 15): eu HP 2686/5275, MP 65/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4449/5977, MP 325/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 4, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 4
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 15): eu HP 4449/5977, MP 325/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 2686/5275, MP 65/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 4, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Soco de Placa

### 15.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre; Postura Impecável 5 → 4; Esmagar 5 → 4
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 2 → min(908, 2 + 18) = 20
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 2 → 20; recarga Esmagar 5 → 4; recarga Postura Impecável 5 → 4; recarga Quebra-Guarda 1 → livre; buff Postura Impecável dur 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 20 → 20
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 83
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #23** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 847.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 847.0; × arma = 965.5800000000002; × power 3.619 = 3494.4340200000006; max(1, int(847.0 × (1 + 14/100) × 3.619)) = **3494**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 58 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 71; teste `64 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 59 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **76**; chance 35; teste `76 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3494.0 × 1.0 × 1.0 × 0.16583747927031509 = 579.4361525704809; max(1, int(bruto)) = 579 → int(anterior × 1.0) = 579 → int(anterior × 0.43999999999999995) = 254
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **254**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 254
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(254)`; HP do alvo 4449 → 4195 (retirado 254)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4195 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 60 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **28**; chance 2.0; teste `28 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 61 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **6**; chance 45.0; teste `6 > 45.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'quebra_guarda'}]

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 83 → 20; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 4449 → 4195; df 503 → 402; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 254.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 264 → min(1103, 264 + 22) = 286
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 264 → 286; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 5 → 4; buff Juramento da Muralha dur 3 → 2; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 286 → 286
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 347
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #24** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 62 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 68; teste `88 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 2686 → 2686)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 347 → 286; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 15.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2686/5275 | 4195/5977 |
| MP | 20/908 | 286/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 254 (golpes e DoT), recebido 0; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 254; cura 0


## Rodada 16

### 16.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2686/5275 | 4195/5977 |
| MP | 20/908 | 286/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 4, Esmagar 4, Quebra-Guarda 3 | Juramento da Muralha 4, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | Postura Impecável (st 300, dur 2) | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 16.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 16): eu HP 2686/5275, MP 20/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4195/5977, MP 286/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 3, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 3
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 16): eu HP 4195/5977, MP 286/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 2686/5275, MP 20/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 3, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 16.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 4 → 3; Esmagar 4 → 3; Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 20 → min(908, 20 + 18) = 38
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 20 → 38; recarga Esmagar 4 → 3; recarga Postura Impecável 4 → 3; recarga Quebra-Guarda 3 → 2; buff Postura Impecável dur 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 38 → 38
- Perde a oportunidade por controle: não

**Golpe #25** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 847.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1490.0; dano médio max(1, int(1490.0 × (1 + 14/100))) = 1698; BASE do básico = max(1, int(1698 × 0.9)) = **1528** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 63 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 71; teste `85 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 4195 → 4195)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 234 → min(1103, 234 + 22) = 256
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 234 → 256; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 4 → 3; recarga Soco de Placa 2 → 1; buff Juramento da Muralha dur 2 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 256 → 256
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 308
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #26** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 64 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 68; teste `54 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 65 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **100**; chance 30; teste `100 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.1594896331738437 = 337.00159489633177; max(1, int(bruto)) = 337 → int(anterior × 1.0) = 337 → int(anterior × 0.71) = 239
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **239**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 239
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(239)`; HP do alvo 2686 → 2447 (retirado 239)
23. Roubo de vida: 13.0% → max(1, int(239 × 13 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 2447 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 66 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 2.0; teste `12 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4195 → 4226; mp 308 → 256; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2686 → 2447

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 239.

### 16.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2447/5275 | 4226/5977 |
| MP | 38/908 | 256/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 239; cura 0
- fer (p2): Golpe Poderoso — executada; dano causado na rodada 239 (golpes e DoT), recebido 0; cura 31


## Rodada 17

### 17.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2447/5275 | 4226/5977 |
| MP | 38/908 | 256/1103 |
| ST / MG / AG / DF | 847 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Postura Impecável 3, Esmagar 3, Quebra-Guarda 2 | Juramento da Muralha 3, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | Postura Impecável (st 300, dur 1) | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 17.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 17): eu HP 2447/5275, MP 38/908, efeitos —, buffs ['Postura Impecável']; adversário fer HP 4226/5977, MP 256/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 2, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 2
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 17): eu HP 4226/5977, MP 256/1103, efeitos ['vulnerable'], buffs ['Juramento da Muralha']; adversário lubatv HP 2447/5275, MP 38/908, efeitos —, buffs ['Postura Impecável'].
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 2, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: primeira skill de dano legal do deck: Soco de Placa
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Soco de Placa

### 17.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 847.0 | 457.3333333333333 | 1.8520408163265307 | 1.3608970630898323 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.516943693740682
- ÷ 6 = build 1.0861572822901138
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0861572822901138 × 0.995 = 1.080726495878663**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.080726495878663 > score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: lubatv (p1) → fer (p2) (`score`).

- **Ordem travada**: lubatv (p1) → fer (p2) (critério `score`).

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 3 → 2; Esmagar 3 → 2; Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 38 → min(908, 38 + 18) = 56
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 38 → 56; st 847 → 547; recarga Esmagar 3 → 2; recarga Postura Impecável 3 → 2; recarga Quebra-Guarda 2 → 1; buff Postura Impecável expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 56 → 56
- Perde a oportunidade por controle: não

**Golpe #27** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 67 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **18**; chance 71; teste `18 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 68 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 35; teste `97 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 402
15. Fator de defesa: 100 / (100 + 402) = 0.199203187250996
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.199203187250996 = 206.17529880478088; max(1, int(bruto)) = 206 → int(anterior × 1.0) = 206 → int(anterior × 0.43999999999999995) = 90
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **90**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 90
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(90)`; HP do alvo 4226 → 4136 (retirado 90)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4136 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 69 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 2.0; teste `55 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 90.

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 195 → min(1103, 195 + 22) = 217
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 195 → 217; df 402 → 503; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 3 → 2; recarga Soco de Placa 1 → livre; buff Juramento da Muralha expira; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 217 → 217
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 278
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #28** — fer (p2) → lubatv (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 70 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 68; teste `12 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 71 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 30; teste `87 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.1594896331738437 = 354.86443381180226; max(1, int(bruto)) = 354 → int(anterior × 1.0) = 354 → int(anterior × 0.71) = 251
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **251**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 251
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(251)`; HP do alvo 2447 → 2196 (retirado 251)
23. Roubo de vida: 13.0% → max(1, int(251 × 13 / 100)) = 32; HP do atacante +32 (teto do HP máximo)
24. Morte e death_ignore: HP final 2196 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 72 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 2.0; teste `53 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre lubatv (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 73 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **90**; chance 35.0; teste `90 > 35.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 4136 → 4168; mp 278 → 217; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 2447 → 2196

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 251.

### 17.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 4168/5977 |
| MP | 56/908 | 217/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- lubatv (p1): Ataque básico — executada; dano causado na rodada 90 (golpes e DoT), recebido 251; cura 0
- fer (p2): Soco de Placa — executada; dano causado na rodada 251 (golpes e DoT), recebido 90; cura 32


## Rodada 18

### 18.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 4168/5977 |
| MP | 56/908 | 217/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 2, Esmagar 2, Quebra-Guarda 1 | Juramento da Muralha 2, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 18.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 18): eu HP 2196/5275, MP 56/908, efeitos —, buffs —; adversário fer HP 4168/5977, MP 217/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 1, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 1
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 18): eu HP 4168/5977, MP 217/1103, efeitos —, buffs —; adversário lubatv HP 2196/5275, MP 56/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 1, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 18.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 165 → min(1103, 165 + 22) = 187
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 165 → 187; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 2 → 1; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 187 → 187
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 239
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #29** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 74 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 68; teste `91 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 2196 → 2196)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 239 → 187; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 2 → 1; Esmagar 2 → 1; Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 56 → min(908, 56 + 18) = 74
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 56 → 74; recarga Esmagar 2 → 1; recarga Postura Impecável 2 → 1; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 74 → 74
- Perde a oportunidade por controle: não

**Golpe #30** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 75 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **49**; chance 71; teste `49 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 76 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 35; teste `12 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.5 × 0.16583747927031509 = 257.46268656716416; max(1, int(bruto)) = 257 → int(anterior × 1.0) = 257 → int(anterior × 0.89) = 228
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **228**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 228
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(228)`; HP do alvo 4168 → 3940 (retirado 228)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3940 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 77 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 2.0; teste `3 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 228.

### 18.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3940/5977 |
| MP | 74/908 | 187/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 228; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 228 (golpes e DoT), recebido 0; cura 0


## Rodada 19

### 19.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3940/5977 |
| MP | 74/908 | 187/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Postura Impecável 1, Esmagar 1 | Juramento da Muralha 1, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 19.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 19): eu HP 2196/5275, MP 74/908, efeitos —, buffs —; adversário fer HP 3940/5977, MP 187/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 19): eu HP 3940/5977, MP 187/1103, efeitos —, buffs —; adversário lubatv HP 2196/5275, MP 74/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 152

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **152 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Juramento da Muralha

### 19.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 35 → min(1103, 35 + 22) = 57
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 35 → 57; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 1 → livre; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 152, teto livre 951 → MP 57 → 57
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de fer (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 152 MP; reserva feita no lock 152; MP disponível na cobrança (livre + reserva liberada) 209
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 152; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 209 → 57; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Juramento da Muralha; MP gasto 152, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Postura Impecável 1 → livre; Esmagar 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 11 → min(908, 11 + 18) = 29
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 11 → 29; recarga Esmagar 1 → livre; recarga Postura Impecável 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 29 → 29
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 92
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #31** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 78 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 71; teste `9 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 79 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 35; teste `79 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.0 × 1.0 × 0.16583747927031509 = 374.12935323383084; max(1, int(bruto)) = 374 → int(anterior × 1.0) = 374 → int(anterior × 0.43999999999999995) = 164
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **164**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 164
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(164)`; HP do alvo 3940 → 3776 (retirado 164)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3776 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 80 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 2.0; teste `88 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 81 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **46**; chance 45.0; teste `46 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 92 → 29; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 3940 → 3776

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 164.

### 19.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3776/5977 |
| MP | 29/908 | 57/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 164; cura 0
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 164 (golpes e DoT), recebido 0; cura 0


## Rodada 20

### 20.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3776/5977 |
| MP | 29/908 | 57/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 20.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 20): eu HP 2196/5275, MP 29/908, efeitos —, buffs —; adversário fer HP 3776/5977, MP 57/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 20): eu HP 3776/5977, MP 57/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 2196/5275, MP 29/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 5, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 20.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 5 → min(1103, 5 + 22) = 27
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 5 → 27; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 27 → 27
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 79
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #32** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 82 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 68; teste `89 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 2196 → 2196)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 79 → 27; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 29 → min(908, 29 + 18) = 47
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 29 → 47; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 47 → 47
- Perde a oportunidade por controle: não

**Golpe #33** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 83 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **8**; chance 71; teste `8 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 84 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 35; teste `54 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.16583747927031509 = 171.6417910447761; max(1, int(bruto)) = 171 → int(anterior × 1.0) = 171 → int(anterior × 0.43999999999999995) = 75
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **75**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 75
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(75)`; HP do alvo 3776 → 3701 (retirado 75)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3701 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 85 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 2.0; teste `16 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 75.

### 20.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3701/5977 |
| MP | 47/908 | 27/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 75; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 75 (golpes e DoT), recebido 0; cura 0


## Rodada 21

### 21.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2196/5275 | 3701/5977 |
| MP | 47/908 | 27/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 21.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 21): eu HP 2196/5275, MP 47/908, efeitos —, buffs —; adversário fer HP 3701/5977, MP 27/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 21): eu HP 3701/5977, MP 27/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 2196/5275, MP 47/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 4, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Ataque básico

### 21.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 27 → min(1103, 27 + 22) = 49
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 27 → 49; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 5 → 4; buff Juramento da Muralha dur 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 49 → 49
- Perde a oportunidade por controle: não

**Golpe #34** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 86 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 68; teste `31 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 87 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **43**; chance 30; teste `43 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 2196 → 2056 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 2056 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 88 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **41**; chance 2.0; teste `41 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 47 → min(908, 47 + 18) = 65
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 47 → 65; recarga Quebra-Guarda 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 65 → 65
- Perde a oportunidade por controle: não

**Golpe #35** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 89 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 71; teste `14 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 90 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 35; teste `60 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.16583747927031509 = 171.6417910447761; max(1, int(bruto)) = 171 → int(anterior × 1.0) = 171 → int(anterior × 0.43999999999999995) = 75
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **75**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 75
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(75)`; HP do alvo 3719 → 3644 (retirado 75)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3644 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 91 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **7**; chance 2.0; teste `7 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 75.

### 21.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2056/5275 | 3644/5977 |
| MP | 65/908 | 49/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Juramento da Muralha 4, Golpe Poderoso 1 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 75; cura 18
- lubatv (p1): Ataque básico — executada; dano causado na rodada 75 (golpes e DoT), recebido 140; cura 0


## Rodada 22

### 22.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 2056/5275 | 3644/5977 |
| MP | 65/908 | 49/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Juramento da Muralha 4, Golpe Poderoso 1 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 22.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 22): eu HP 2056/5275, MP 65/908, efeitos —, buffs —; adversário fer HP 3644/5977, MP 49/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 22): eu HP 3644/5977, MP 49/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 2056/5275, MP 65/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 3, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Ataque básico

### 22.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 49 → min(1103, 49 + 22) = 71
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 49 → 71; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 4 → 3; buff Juramento da Muralha dur 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 71 → 71
- Perde a oportunidade por controle: não

**Golpe #36** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 92 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 68; teste `31 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 93 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **37**; chance 30; teste `37 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 2056 → 1916 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 1916 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 94 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 2.0; teste `85 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 2 → min(908, 2 + 18) = 20
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 2 → 20; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 20 → 20
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 83
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #37** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 95 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 71; teste `53 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 96 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 35; teste `20 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.43999999999999995 (damage_reduction 56.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.0 × 1.5 × 0.16583747927031509 = 561.1940298507462; max(1, int(bruto)) = 561 → int(anterior × 1.0) = 561 → int(anterior × 0.43999999999999995) = 246
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **246**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 246
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(246)`; HP do alvo 3662 → 3416 (retirado 246)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3416 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 97 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **74**; chance 2.0; teste `74 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 98 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **82**; chance 45.0; teste `82 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 83 → 20; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 3662 → 3416

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 246.

### 22.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1916/5275 | 3416/5977 |
| MP | 20/908 | 71/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Juramento da Muralha 3 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 246; cura 18
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 246 (golpes e DoT), recebido 140; cura 0


## Rodada 23

### 23.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1916/5275 | 3416/5977 |
| MP | 20/908 | 71/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Juramento da Muralha 3 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 23.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 23): eu HP 1916/5275, MP 20/908, efeitos —, buffs —; adversário fer HP 3416/5977, MP 71/1103, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 23): eu HP 3416/5977, MP 71/1103, efeitos —, buffs ['Juramento da Muralha']; adversário lubatv HP 1916/5275, MP 20/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 2, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 23.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 19 → min(1103, 19 + 22) = 41
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 19 → 41; recarga Juramento da Muralha 3 → 2; buff Juramento da Muralha expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 41 → 41
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 93
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #38** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 99 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **90**; chance 68; teste `90 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1916 → 1916)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 93 → 41; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 20 → min(908, 20 + 18) = 38
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 20 → 38; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 38 → 38
- Perde a oportunidade por controle: não

**Golpe #39** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 100 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **92**; chance 71; teste `92 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 3416 → 3416)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 23.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1916/5275 | 3416/5977 |
| MP | 38/908 | 41/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Juramento da Muralha 2, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 24

### 24.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1916/5275 | 3416/5977 |
| MP | 38/908 | 41/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Juramento da Muralha 2, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 24.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 24): eu HP 1916/5275, MP 38/908, efeitos —, buffs —; adversário fer HP 3416/5977, MP 41/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 24): eu HP 3416/5977, MP 41/1103, efeitos —, buffs —; adversário lubatv HP 1916/5275, MP 38/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 1, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Ataque básico

### 24.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 41 → min(1103, 41 + 22) = 63
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 41 → 63; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 63 → 63
- Perde a oportunidade por controle: não

**Golpe #40** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 101 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 68; teste `25 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 102 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 30; teste `70 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 1916 → 1776 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 1776 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 103 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 2.0; teste `35 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 38 → min(908, 38 + 18) = 56
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 38 → 56; recarga Quebra-Guarda 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 56 → 56
- Perde a oportunidade por controle: não

**Golpe #41** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 104 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 71; teste `71 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 105 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 35; teste `44 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.16583747927031509 = 171.6417910447761; max(1, int(bruto)) = 171 → int(anterior × 1.0) = 171 → int(anterior × 0.89) = 152
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **152**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 152
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(152)`; HP do alvo 3434 → 3282 (retirado 152)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3282 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 106 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 2.0; teste `70 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 152.

### 24.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1776/5275 | 3282/5977 |
| MP | 56/908 | 63/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Juramento da Muralha 1, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 152; cura 18
- lubatv (p1): Ataque básico — executada; dano causado na rodada 152 (golpes e DoT), recebido 140; cura 0


## Rodada 25

### 25.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1776/5275 | 3282/5977 |
| MP | 56/908 | 63/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Juramento da Muralha 1, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 25.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 25): eu HP 1776/5275, MP 56/908, efeitos —, buffs —; adversário fer HP 3282/5977, MP 63/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 25): eu HP 3282/5977, MP 63/1103, efeitos —, buffs —; adversário lubatv HP 1776/5275, MP 56/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 25.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 11 → min(1103, 11 + 22) = 33
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 11 → 33; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 33 → 33
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 85
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #42** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 107 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 68; teste `71 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1776 → 1776)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 85 → 33; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 56 → min(908, 56 + 18) = 74
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 56 → 74; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 74 → 74
- Perde a oportunidade por controle: não

**Golpe #43** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 108 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 71; teste `25 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 109 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 35; teste `3 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.5 × 0.16583747927031509 = 257.46268656716416; max(1, int(bruto)) = 257 → int(anterior × 1.0) = 257 → int(anterior × 0.89) = 228
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **228**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 228
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(228)`; HP do alvo 3282 → 3054 (retirado 228)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3054 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 110 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 2.0; teste `48 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 228.

### 25.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1776/5275 | 3054/5977 |
| MP | 74/908 | 33/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 228; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 228 (golpes e DoT), recebido 0; cura 0


## Rodada 26

### 26.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1776/5275 | 3054/5977 |
| MP | 74/908 | 33/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 26.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 26): eu HP 1776/5275, MP 74/908, efeitos —, buffs —; adversário fer HP 3054/5977, MP 33/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 26): eu HP 3054/5977, MP 33/1103, efeitos —, buffs —; adversário lubatv HP 1776/5275, MP 74/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Ataque básico

### 26.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 33 → min(1103, 33 + 22) = 55
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 33 → 55; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 55 → 55
- Perde a oportunidade por controle: não

**Golpe #44** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 111 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 68; teste `67 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 112 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **73**; chance 30; teste `73 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 1776 → 1636 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 1636 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 113 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 2.0; teste `89 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 11 → min(908, 11 + 18) = 29
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 11 → 29
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 29 → 29
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 92
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #45** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 114 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 71; teste `25 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 115 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **15**; chance 35; teste `15 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.0 × 1.5 × 0.16583747927031509 = 561.1940298507462; max(1, int(bruto)) = 561 → int(anterior × 1.0) = 561 → int(anterior × 0.89) = 499
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **499**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 499
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(499)`; HP do alvo 3072 → 2573 (retirado 499)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2573 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 116 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 2.0; teste `88 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 117 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 45.0; teste `64 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 92 → 29; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 3072 → 2573

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 499.

### 26.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1636/5275 | 2573/5977 |
| MP | 29/908 | 55/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 499; cura 18
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 499 (golpes e DoT), recebido 140; cura 0


## Rodada 27

### 27.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1636/5275 | 2573/5977 |
| MP | 29/908 | 55/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 27.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 27): eu HP 1636/5275, MP 29/908, efeitos —, buffs —; adversário fer HP 2573/5977, MP 55/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 27): eu HP 2573/5977, MP 55/1103, efeitos —, buffs —; adversário lubatv HP 1636/5275, MP 29/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 27.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 3 → min(1103, 3 + 22) = 25
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 3 → 25; recarga Golpe Poderoso 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 25 → 25
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 77
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #46** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 118 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **6**; chance 68; teste `6 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 119 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 30; teste `63 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.1594896331738437 = 337.00159489633177; max(1, int(bruto)) = 337 → int(anterior × 1.0) = 337 → int(anterior × 0.71) = 239
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **239**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 239
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(239)`; HP do alvo 1636 → 1397 (retirado 239)
23. Roubo de vida: 13.0% → max(1, int(239 × 13 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 1397 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 120 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 2.0; teste `91 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2573 → 2604; mp 77 → 25; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 1636 → 1397

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 239.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 29 → min(908, 29 + 18) = 47
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 29 → 47; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 47 → 47
- Perde a oportunidade por controle: não

**Golpe #47** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 121 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 71; teste `67 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 122 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 35; teste `16 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.5 × 0.16583747927031509 = 257.46268656716416; max(1, int(bruto)) = 257 → int(anterior × 1.0) = 257 → int(anterior × 0.89) = 228
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **228**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 228
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(228)`; HP do alvo 2604 → 2376 (retirado 228)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2376 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 123 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **99**; chance 2.0; teste `99 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 228.

### 27.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1397/5275 | 2376/5977 |
| MP | 47/908 | 25/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 239 (golpes e DoT), recebido 228; cura 31
- lubatv (p1): Ataque básico — executada; dano causado na rodada 228 (golpes e DoT), recebido 239; cura 0


## Rodada 28

### 28.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1397/5275 | 2376/5977 |
| MP | 47/908 | 25/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 28.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 28): eu HP 1397/5275, MP 47/908, efeitos —, buffs —; adversário fer HP 2376/5977, MP 25/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 28): eu HP 2376/5977, MP 25/1103, efeitos —, buffs —; adversário lubatv HP 1397/5275, MP 47/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Ataque básico

### 28.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 25 → min(1103, 25 + 22) = 47
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 25 → 47; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 47 → 47
- Perde a oportunidade por controle: não

**Golpe #48** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 124 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 68; teste `87 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1397 → 1397)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 47 → min(908, 47 + 18) = 65
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 47 → 65; recarga Quebra-Guarda 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 65 → 65
- Perde a oportunidade por controle: não

**Golpe #49** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 125 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 71; teste `71 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 126 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **7**; chance 35; teste `7 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.5 × 0.16583747927031509 = 257.46268656716416; max(1, int(bruto)) = 257 → int(anterior × 1.0) = 257 → int(anterior × 0.89) = 228
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **228**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 228
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(228)`; HP do alvo 2376 → 2148 (retirado 228)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2148 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 127 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 2.0; teste `81 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 228.

### 28.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1397/5275 | 2148/5977 |
| MP | 65/908 | 47/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 228; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 228 (golpes e DoT), recebido 0; cura 0


## Rodada 29

### 29.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1397/5275 | 2148/5977 |
| MP | 65/908 | 47/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 29.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 29): eu HP 1397/5275, MP 65/908, efeitos —, buffs —; adversário fer HP 2148/5977, MP 47/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 29): eu HP 2148/5977, MP 47/1103, efeitos —, buffs —; adversário lubatv HP 1397/5275, MP 65/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Ataque básico

### 29.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 47 → min(1103, 47 + 22) = 69
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 47 → 69; recarga Golpe Poderoso 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 69 → 69
- Perde a oportunidade por controle: não

**Golpe #50** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 128 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 68; teste `2 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 129 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **36**; chance 30; teste `36 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 1397 → 1257 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 1257 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 130 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **77**; chance 2.0; teste `77 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 2 → min(908, 2 + 18) = 20
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 2 → 20; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 20 → 20
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 83
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #51** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 131 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **32**; chance 71; teste `32 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 132 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **59**; chance 35; teste `59 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.0 × 1.0 × 0.16583747927031509 = 374.12935323383084; max(1, int(bruto)) = 374 → int(anterior × 1.0) = 374 → int(anterior × 0.89) = 332
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **332**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 332
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(332)`; HP do alvo 2166 → 1834 (retirado 332)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 1834 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 133 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 2.0; teste `85 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 134 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **82**; chance 45.0; teste `82 > 45.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 83 → 20; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 2166 → 1834

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 332.

### 29.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1257/5275 | 1834/5977 |
| MP | 20/908 | 69/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 332; cura 18
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 332 (golpes e DoT), recebido 140; cura 0


## Rodada 30

### 30.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1257/5275 | 1834/5977 |
| MP | 20/908 | 69/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 30.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 30): eu HP 1257/5275, MP 20/908, efeitos —, buffs —; adversário fer HP 1834/5977, MP 69/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 30): eu HP 1834/5977, MP 69/1103, efeitos —, buffs —; adversário lubatv HP 1257/5275, MP 20/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 30.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 17 → min(1103, 17 + 22) = 39
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 17 → 39
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 39 → 39
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 91
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #52** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 135 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **22**; chance 68; teste `22 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 136 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **86**; chance 30; teste `86 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.1594896331738437 = 337.00159489633177; max(1, int(bruto)) = 337 → int(anterior × 1.0) = 337 → int(anterior × 0.71) = 239
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **239**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 239
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(239)`; HP do alvo 1257 → 1018 (retirado 239)
23. Roubo de vida: 13.0% → max(1, int(239 × 13 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 1018 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 137 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 2.0; teste `98 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 1834 → 1865; mp 91 → 39; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 1257 → 1018

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 239.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 20 → min(908, 20 + 18) = 38
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 20 → 38; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 38 → 38
- Perde a oportunidade por controle: não

**Golpe #53** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 138 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **72**; chance 71; teste `72 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1865 → 1865)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 30.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1865/5977 |
| MP | 38/908 | 39/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 239 (golpes e DoT), recebido 0; cura 31
- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 239; cura 0


## Rodada 31

### 31.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1865/5977 |
| MP | 38/908 | 39/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 31.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 31): eu HP 1018/5275, MP 38/908, efeitos —, buffs —; adversário fer HP 1865/5977, MP 39/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 31): eu HP 1865/5977, MP 39/1103, efeitos —, buffs —; adversário lubatv HP 1018/5275, MP 38/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Ataque básico

### 31.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 39 → min(1103, 39 + 22) = 61
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 39 → 61; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 61 → 61
- Perde a oportunidade por controle: não

**Golpe #54** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 139 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **96**; chance 68; teste `96 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1018 → 1018)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 38 → min(908, 38 + 18) = 56
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 38 → 56; recarga Quebra-Guarda 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 56 → 56
- Perde a oportunidade por controle: não

**Golpe #55** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 140 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 71; teste `91 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1865 → 1865)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 31.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1865/5977 |
| MP | 56/908 | 61/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 32

### 32.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1865/5977 |
| MP | 56/908 | 61/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 32.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 32): eu HP 1018/5275, MP 56/908, efeitos —, buffs —; adversário fer HP 1865/5977, MP 61/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 32): eu HP 1865/5977, MP 61/1103, efeitos —, buffs —; adversário lubatv HP 1018/5275, MP 56/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 32.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 9 → min(1103, 9 + 22) = 31
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 9 → 31; recarga Golpe Poderoso 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 31 → 31
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 83
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #56** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 141 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 68; teste `81 > 68` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1018 → 1018)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 83 → 31; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 56 → min(908, 56 + 18) = 74
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 56 → 74; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 74 → 74
- Perde a oportunidade por controle: não

**Golpe #57** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 142 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **22**; chance 71; teste `22 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 143 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 35; teste `45 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.16583747927031509 = 171.6417910447761; max(1, int(bruto)) = 171 → int(anterior × 1.0) = 171 → int(anterior × 0.89) = 152
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **152**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 152
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(152)`; HP do alvo 1865 → 1713 (retirado 152)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 1713 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 144 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 2.0; teste `30 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 152.

### 32.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1713/5977 |
| MP | 74/908 | 31/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 152; cura 0
- lubatv (p1): Ataque básico — executada; dano causado na rodada 152 (golpes e DoT), recebido 0; cura 0


## Rodada 33

### 33.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 1018/5275 | 1713/5977 |
| MP | 74/908 | 31/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 33.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 33): eu HP 1018/5275, MP 74/908, efeitos —, buffs —; adversário fer HP 1713/5977, MP 31/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 33): eu HP 1713/5977, MP 31/1103, efeitos —, buffs —; adversário lubatv HP 1018/5275, MP 74/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Ataque básico

### 33.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 31 → min(1103, 31 + 22) = 53
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 31 → 53; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 53 → 53
- Perde a oportunidade por controle: não

**Golpe #58** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 145 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **37**; chance 68; teste `37 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 146 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **61**; chance 30; teste `61 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 1018 → 878 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 878 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 147 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **27**; chance 2.0; teste `27 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 11 → min(908, 11 + 18) = 29
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 11 → 29
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 29 → 29
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 92
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #59** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 148 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 71; teste `35 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 149 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 35; teste `35 <= 35` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 0/100 = 1.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.5
13. Produto ×MULT bruto 1.5; `XMULT_CAP` 5.0 → aplicado 1.5
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2256.0 × 1.0 × 1.5 × 0.16583747927031509 = 561.1940298507462; max(1, int(bruto)) = 561 → int(anterior × 1.0) = 561 → int(anterior × 0.89) = 499
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **499**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 499
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(499)`; HP do alvo 1731 → 1232 (retirado 499)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 1232 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 150 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 2.0; teste `3 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `quebra_guarda`)

- Chance base 45%; resistência do alvo 0.0% → efetiva 45 × (1 − 0/100) = 45.0%
- sorteio nº 151 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **23**; chance 45.0; teste `23 > 45.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'quebra_guarda'}]

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 92 → 29; recarga Quebra-Guarda — → 3
- Mudanças no adversário: hp 1731 → 1232; df 503 → 402; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 499.

### 33.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 878/5275 | 1232/5977 |
| MP | 29/908 | 53/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 3, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 499; cura 18
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 499 (golpes e DoT), recebido 140; cura 0


## Rodada 34

### 34.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 878/5275 | 1232/5977 |
| MP | 29/908 | 53/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 3, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 34.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 34): eu HP 878/5275, MP 29/908, efeitos —, buffs —; adversário fer HP 1232/5977, MP 53/1103, efeitos ['vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 34): eu HP 1232/5977, MP 53/1103, efeitos ['vulnerable'], buffs —; adversário lubatv HP 878/5275, MP 29/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 34.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 1 → min(1103, 1 + 22) = 23
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1 → 23; recarga Golpe Poderoso 1 → livre; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 23 → 23
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 75
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #60** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 152 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 68; teste `11 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 153 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 30; teste `85 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.1594896331738437 = 337.00159489633177; max(1, int(bruto)) = 337 → int(anterior × 1.0) = 337 → int(anterior × 0.71) = 239
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **239**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 239
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(239)`; HP do alvo 878 → 639 (retirado 239)
23. Roubo de vida: 13.0% → max(1, int(239 × 13 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 639 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 154 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **51**; chance 2.0; teste `51 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 1232 → 1263; mp 75 → 23; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 878 → 639

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 239.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 3 → 2
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 29 → min(908, 29 + 18) = 47
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 29 → 47; recarga Quebra-Guarda 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 47 → 47
- Perde a oportunidade por controle: não

**Golpe #61** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 155 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **99**; chance 71; teste `99 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1263 → 1263)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 34.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 639/5275 | 1263/5977 |
| MP | 47/908 | 23/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 239 (golpes e DoT), recebido 0; cura 31
- lubatv (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 239; cura 0


## Rodada 35

### 35.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 639/5275 | 1263/5977 |
| MP | 47/908 | 23/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 2, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 35.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 35): eu HP 639/5275, MP 47/908, efeitos —, buffs —; adversário fer HP 1263/5977, MP 23/1103, efeitos ['vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 1, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 35): eu HP 1263/5977, MP 23/1103, efeitos ['vulnerable'], buffs —; adversário lubatv HP 639/5275, MP 47/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Ataque básico

### 35.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 23 → min(1103, 23 + 22) = 45
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 23 → 45; recarga Golpe Poderoso 2 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 45 → 45
- Perde a oportunidade por controle: não

**Golpe #62** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 156 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **65**; chance 68; teste `65 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 157 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **75**; chance 30; teste `75 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 639 → 499 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 499 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 158 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **100**; chance 2.0; teste `100 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 2 → 1
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 47 → min(908, 47 + 18) = 65
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 47 → 65; recarga Quebra-Guarda 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 908 → MP 65 → 65
- Perde a oportunidade por controle: não

**Golpe #63** — lubatv (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 547.0, mg 337.0, ag 114.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1010.0; dano médio max(1, int(1010.0 × (1 + 14/100))) = 1151; BASE do básico = max(1, int(1151 × 0.9)) = **1035** (multiplicador do básico 0.9)
4. Bônus de arma: +14.0% → fator 1.1400000000000001 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 159 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 71; teste `11 > 71` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 35 = 35, teto 75 → **35**
9. Rolagem de crítico: sorteio nº 160 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 35; teste `91 <= 35` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 402
15. Fator de defesa: 100 / (100 + 402) = 0.199203187250996
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1035.0 × 1.0 × 1.0 × 0.199203187250996 = 206.17529880478088; max(1, int(bruto)) = 206 → int(anterior × 1.0) = 206 → int(anterior × 0.89) = 183
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **183**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 183
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(183)`; HP do alvo 1281 → 1098 (retirado 183)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 1098 → o alvo segue vivo

**Status `stun`** sobre fer (p2) (via `_aplicar_procs_on_hit`, fonte `lubatv`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 161 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 2.0; teste `48 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): lubatv (p1) executou Ataque básico; MP gasto 0, dano ao adversário 183.

### 35.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 499/5275 | 1098/5977 |
| MP | 65/908 | 45/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 183; cura 18
- lubatv (p1): Ataque básico — executada; dano causado na rodada 183 (golpes e DoT), recebido 140; cura 0


## Rodada 36

### 36.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 499/5275 | 1098/5977 |
| MP | 65/908 | 45/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 402 |
| Recargas (contador interno) | Quebra-Guarda 1 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte quebra_guarda) |
| death_ignore gasto / vivo | False / True | False / True |

### 36.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 36): eu HP 499/5275, MP 65/908, efeitos —, buffs —; adversário fer HP 1098/5977, MP 45/1103, efeitos ['vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 0, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Quebra-Guarda, Rendição
- Escolha: **Quebra-Guarda** — justificativa da política: primeira skill de dano legal do deck: Quebra-Guarda
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 63

**fer (p2)**

- Estado recebido (`DuelView`, rodada 36): eu HP 1098/5977, MP 45/1103, efeitos ['vulnerable'], buffs —; adversário lubatv HP 499/5275, MP 65/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Juramento da Muralha', 'Soco de Placa', 'Respirar Fundo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: lubatv (p1) reserva **63 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Quebra-Guarda; fer (p2) = Ataque básico

### 36.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 402.0 | 335.0 | 1.2 | 1.0954451150103321 |

- Soma das seis raízes (`math.fsum`): 6.223627397098506
- ÷ 6 = build 1.0372712328497509
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0372712328497509 × 1.005 = 1.0424575890139995**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0424575890139995 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 45 → min(1103, 45 + 22) = 67
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 45 → 67; df 402 → 503; recarga Golpe Poderoso 1 → livre; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 67 → 67
- Perde a oportunidade por controle: não

**Golpe #64** — fer (p2) → lubatv (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 162 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 68; teste `56 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 163 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 30; teste `45 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.1594896331738437 = 198.56459330143542; max(1, int(bruto)) = 198 → int(anterior × 1.0) = 198 → int(anterior × 0.71) = 140
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **140**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 140
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(140)`; HP do alvo 499 → 359 (retirado 140)
23. Roubo de vida: 13.0% → max(1, int(140 × 13 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 359 → o alvo segue vivo

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 164 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 2.0; teste `11 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 140.

### Oportunidade de lubatv (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Quebra-Guarda 1 → livre
- Regeneração de MP: max(1, 908 × 2 / 100) = 18.16; + mana_regen 0.0 → int(0 + 18.16) = **18**; MP livre 2 → min(908, 2 + 18) = 20
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 2 → 20; recarga Quebra-Guarda 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 63, teto livre 845 → MP 20 → 20
- Perde a oportunidade por controle: não

**Skill Quebra-Guarda** (`quebra_guarda`) de lubatv (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: uma espada → atendido: True
- Custo 63 MP; reserva feita no lock 63; MP disponível na cobrança (livre + reserva liberada) 83
- Recarga antes do uso: 0; declarada 2 (o motor grava declarada + 1)

**Golpe #65** — lubatv (p1) → fer (p2), skill `quebra_guarda`

1. Atributos ofensivos efetivos: st 547.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 547.0; × arma = 623.58; × power 3.619 = 2256.7360200000003; max(1, int(547.0 × (1 + 14/100) × 3.619)) = **2256**
4. Bônus de arma: +14.0% → fator 1.1400000000000001
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -3.28125 (30 × (114 − 142) / 256) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 71.71875 → clamp [20, 95] e int → **71**
7. Rolagem de acerto: sorteio nº 165 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **84**; chance 71; teste `84 > 71` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: inaplicável — o golpe errou e o motor parou aqui.
9. Rolagem de crítico: inaplicável — o golpe errou e o motor parou aqui.
10. Multiplicador de crítico: inaplicável — o golpe errou e o motor parou aqui.
11. +MULT: inaplicável — o golpe errou e o motor parou aqui.
12. ×MULT: inaplicável — o golpe errou e o motor parou aqui.
13. Produto bruto e XMULT_CAP: inaplicável — o golpe errou e o motor parou aqui.
14. Defesa efetiva do alvo: inaplicável — o golpe errou e o motor parou aqui.
15. Fator de defesa: inaplicável — o golpe errou e o motor parou aqui.
16. Mitigação: inaplicável — o golpe errou e o motor parou aqui.
17. Valores intermediários: inaplicável — o golpe errou e o motor parou aqui.
18. Truncamentos: inaplicável — o golpe errou e o motor parou aqui.
19. Dano final do funil: inaplicável — o golpe errou e o motor parou aqui.
20. Égide de Mana: inaplicável — o golpe errou e o motor parou aqui.
21. MP da Égide: inaplicável — o golpe errou e o motor parou aqui.
22. Dano aplicado ao HP: 0 (HP do alvo 1116 → 1116)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 63; recarga depois 3
- Mudanças em quem lançou: mp 83 → 20; recarga Quebra-Guarda — → 3
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): lubatv (p1) executou Quebra-Guarda; MP gasto 63, dano ao adversário 0.

### 36.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 359/5275 | 1116/5977 |
| MP | 20/908 | 67/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 140 (golpes e DoT), recebido 0; cura 18
- lubatv (p1): Quebra-Guarda — executada; dano causado na rodada 0 (golpes e DoT), recebido 140; cura 0


## Rodada 37

### 37.0 Estado no início da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | 359/5275 | 1116/5977 |
| MP | 20/908 | 67/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 37.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**lubatv (p1)**

- Estado recebido (`DuelView`, rodada 37): eu HP 359/5275, MP 20/908, efeitos —, buffs —; adversário fer HP 1116/5977, MP 67/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Esmagar 0, Quebra-Guarda 2, Tomar Fôlego 0, Postura Impecável 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Esmagar', 'Quebra-Guarda', 'Tomar Fôlego', 'Postura Impecável']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 37): eu HP 1116/5977, MP 67/1103, efeitos —, buffs —; adversário lubatv HP 359/5275, MP 20/908, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: lubatv (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 37.2 Initiative Score

**lubatv (p1)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5275.0 | 4047.6666666666665 | 1.3032199621180929 | 1.141586598606559 |
| mp | 908.0 | 1044.3333333333333 | 0.8694541972550272 | 0.9324452784239015 |
| st | 547.0 | 457.3333333333333 | 1.196064139941691 | 1.0936471734255482 |
| mg | 337.0 | 410.6666666666667 | 0.8206168831168831 | 0.9058790664966726 |
| ag | 114.0 | 158.33333333333334 | 0.72 | 0.848528137423857 |
| df | 527.0 | 299.0 | 1.7625418060200668 | 1.3276075496998603 |

- Soma das seis raízes (`math.fsum`): 6.249693804076399
- ÷ 6 = build 1.0416156340127332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.0416156340127332 × 0.995 = 1.0364075558426695**
- AG relativa (desempate): 114.0 / 158.33333333333334 = 0.72

**fer (p2)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 654.0 | 512.3333333333334 | 1.2765126870527 | 1.1298286095920478 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.353536327788204
- ÷ 6 = build 1.0589227212980339
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0589227212980339 × 1.005 = 1.0642173349045239**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0364075558426695 < score p2 1.0642173349045239 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → lubatv (p1) (`score`).

- **Ordem travada**: fer (p2) → lubatv (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 15 → min(1103, 15 + 22) = 37
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 15 → 37
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 37 → 37
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe lubatv (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 89
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #66** — fer (p2) → lubatv (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 3.28125 (30 × (142 − 114) / 256) − evasão 30.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 68.28125 → clamp [20, 95] e int → **68**
7. Rolagem de acerto: sorteio nº 166 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 68; teste `54 > 68` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 167 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 30; teste `14 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 527
15. Fator de defesa: 100 / (100 + 527) = 0.1594896331738437
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.71 (damage_reduction 29.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.1594896331738437 = 539.2025518341309; max(1, int(bruto)) = 539 → int(anterior × 1.0) = 539 → int(anterior × 0.71) = 382
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **382**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 382
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(382)`; HP do alvo 359 → -23 (retirado 382)
23. Roubo de vida: 13.0% → max(1, int(382 × 13 / 100)) = 49; HP do atacante +49 (teto do HP máximo)
24. Morte e death_ignore: HP final -23 → o alvo morreu

**Status `stun`** sobre lubatv (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 0.0% → efetiva 2 × (1 − 0/100) = 2.0%
- sorteio nº 168 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 2.0; teste `79 > 2.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 1116 → 1165; mp 89 → 37; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 359 → -23; morreu

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 382.

- **Fim do duelo**: vence fer (p2), motivo `ko`.

- Ação de lubatv (p1) **cancelada por morte**.
### 37.9 Estado ao final da rodada

| | lubatv (p1) | fer (p2) |
|---|---|---|
| HP | -23/5275 | 1165/5977 |
| MP | 20/908 | 37/1103 |
| ST / MG / AG / DF | 547 / 337 / 114 / 527 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Quebra-Guarda 3 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / False | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 382 (golpes e DoT), recebido 0; cura 49
- lubatv (p1): Ataque básico — cancelada por morte; dano causado na rodada 0 (golpes e DoT), recebido 382; cura 0


## Conclusão da final (fatos registrados)

- Campeão: **fer** (p2); vice: **lubatv** (p1).
- Rodadas: 37. Motivo exato: `ko` — o HP de lubatv chegou a 0 durante a rodada 37.

| | lubatv (p1) | fer (p2) |
|---|---|---|
| Dano causado (golpes + DoT) | 5494 (5494 + 0) | 5298 (5298 + 0) |
| HP retirado do adversário | 5494 | 5298 |
| Cura (skill + roubo) | 0 (0 + 0) | 682 (0 + 682) |
| MP consumido em ações | 1518 | 1858 |
| MP consumido pela Égide | 0 | 0 |
| Skills usadas | 17: Postura Impecável ×3, Esmagar ×3, Quebra-Guarda ×11 | 27: Juramento da Muralha ×4, Golpe Poderoso ×17, Soco de Placa ×6 |
| Ataques básicos | 19 | 10 |
| Acertos / erros | 23 / 10 | 22 / 11 |
| Críticos (dano) | 9 (3084) | 5 (1961) |
| Status aplicados | vulnerable (rodada 6), vulnerable (rodada 9), vulnerable (rodada 15), vulnerable (rodada 33) | weakened (rodada 11) |
| Status que falharam na rolagem | stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 9), stun (rodada 11), stun (rodada 15), stun (rodada 17), stun (rodada 18), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 22), vulnerable (rodada 22), stun (rodada 24), stun (rodada 25), stun (rodada 26), vulnerable (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), vulnerable (rodada 29), stun (rodada 32), stun (rodada 33), stun (rodada 35) | stun (rodada 2), stun (rodada 4), stun (rodada 6), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 14), stun (rodada 16), stun (rodada 17), weakened (rodada 17), stun (rodada 21), stun (rodada 22), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 29), stun (rodada 30), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 37) |
| Status anulados por resistência / recusados | — | — |
| Ações perdidas por controle | 0 | 0 |
| Rodadas agindo primeiro | 12 | 25 |
| HP / MP restantes | -23/5275 · 20/908 | 1165/5977 · 37/1103 |

HP negativo é o valor cru do motor: `take_damage` não corta em zero, e a sobra mostra quanto o último golpe passou do necessário.

## Todas as chamadas ao gerador

168 chamadas, igual ao contador do proxy (168).

| Nº | Rodada | Ator | Mecânica | Operação | Limites | Valor | Chance | Teste | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | p1 | acerto | `randrange` | [1, 100] | 9 | 61 | `9 > 61` → F | aprovado: ACERTOU |
| 2 | 2 | p1 | crítico | `randrange` | [1, 100] | 14 | 35 | `14 <= 35` → V | aprovado: CRÍTICO |
| 3 | 2 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 81 | 2.0 | `81 > 2.0` → V | recusado: falhou na rolagem |
| 4 | 2 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 86 | 30.0 | `86 > 30.0` → V | recusado: falhou na rolagem |
| 5 | 2 | p2 | acerto | `randrange` | [1, 100] | 30 | 68 | `30 > 68` → F | aprovado: ACERTOU |
| 6 | 2 | p2 | crítico | `randrange` | [1, 100] | 98 | 30 | `98 <= 30` → F | recusado: sem crítico |
| 7 | 2 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 44 | 2.0 | `44 > 2.0` → V | recusado: falhou na rolagem |
| 8 | 3 | p1 | acerto | `randrange` | [1, 100] | 70 | 71 | `70 > 71` → F | aprovado: ACERTOU |
| 9 | 3 | p1 | crítico | `randrange` | [1, 100] | 71 | 35 | `71 <= 35` → F | recusado: sem crítico |
| 10 | 3 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 88 | 2.0 | `88 > 2.0` → V | recusado: falhou na rolagem |
| 11 | 3 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 94 | 45.0 | `94 > 45.0` → V | recusado: falhou na rolagem |
| 12 | 3 | p2 | acerto | `randrange` | [1, 100] | 79 | 68 | `79 > 68` → V | recusado: ERROU |
| 13 | 4 | p1 | acerto | `randrange` | [1, 100] | 17 | 71 | `17 > 71` → F | aprovado: ACERTOU |
| 14 | 4 | p1 | crítico | `randrange` | [1, 100] | 92 | 35 | `92 <= 35` → F | recusado: sem crítico |
| 15 | 4 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 47 | 2.0 | `47 > 2.0` → V | recusado: falhou na rolagem |
| 16 | 4 | p2 | acerto | `randrange` | [1, 100] | 11 | 68 | `11 > 68` → F | aprovado: ACERTOU |
| 17 | 4 | p2 | crítico | `randrange` | [1, 100] | 94 | 30 | `94 <= 30` → F | recusado: sem crítico |
| 18 | 4 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 72 | 2.0 | `72 > 2.0` → V | recusado: falhou na rolagem |
| 19 | 5 | p1 | acerto | `randrange` | [1, 100] | 20 | 71 | `20 > 71` → F | aprovado: ACERTOU |
| 20 | 5 | p1 | crítico | `randrange` | [1, 100] | 93 | 35 | `93 <= 35` → F | recusado: sem crítico |
| 21 | 5 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 60 | 2.0 | `60 > 2.0` → V | recusado: falhou na rolagem |
| 22 | 5 | p2 | acerto | `randrange` | [1, 100] | 84 | 68 | `84 > 68` → V | recusado: ERROU |
| 23 | 6 | p2 | acerto | `randrange` | [1, 100] | 9 | 68 | `9 > 68` → F | aprovado: ACERTOU |
| 24 | 6 | p2 | crítico | `randrange` | [1, 100] | 50 | 30 | `50 <= 30` → F | recusado: sem crítico |
| 25 | 6 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 12 | 2.0 | `12 > 2.0` → V | recusado: falhou na rolagem |
| 26 | 6 | p1 | acerto | `randrange` | [1, 100] | 50 | 71 | `50 > 71` → F | aprovado: ACERTOU |
| 27 | 6 | p1 | crítico | `randrange` | [1, 100] | 89 | 35 | `89 <= 35` → F | recusado: sem crítico |
| 28 | 6 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 71 | 2.0 | `71 > 2.0` → V | recusado: falhou na rolagem |
| 29 | 6 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 29 | 45.0 | `29 > 45.0` → F | aprovado: passou na rolagem |
| 30 | 8 | p1 | acerto | `randrange` | [1, 100] | 85 | 61 | `85 > 61` → V | recusado: ERROU |
| 31 | 8 | p2 | acerto | `randrange` | [1, 100] | 64 | 68 | `64 > 68` → F | aprovado: ACERTOU |
| 32 | 8 | p2 | crítico | `randrange` | [1, 100] | 25 | 30 | `25 <= 30` → V | aprovado: CRÍTICO |
| 33 | 8 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 55 | 2.0 | `55 > 2.0` → V | recusado: falhou na rolagem |
| 34 | 9 | p1 | acerto | `randrange` | [1, 100] | 48 | 71 | `48 > 71` → F | aprovado: ACERTOU |
| 35 | 9 | p1 | crítico | `randrange` | [1, 100] | 13 | 35 | `13 <= 35` → V | aprovado: CRÍTICO |
| 36 | 9 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 93 | 2.0 | `93 > 2.0` → V | recusado: falhou na rolagem |
| 37 | 9 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 9 | 45.0 | `9 > 45.0` → F | aprovado: passou na rolagem |
| 38 | 9 | p2 | acerto | `randrange` | [1, 100] | 73 | 68 | `73 > 68` → V | recusado: ERROU |
| 39 | 10 | p1 | acerto | `randrange` | [1, 100] | 85 | 71 | `85 > 71` → V | recusado: ERROU |
| 40 | 10 | p2 | acerto | `randrange` | [1, 100] | 53 | 68 | `53 > 68` → F | aprovado: ACERTOU |
| 41 | 10 | p2 | crítico | `randrange` | [1, 100] | 34 | 30 | `34 <= 30` → F | recusado: sem crítico |
| 42 | 10 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 36 | 2.0 | `36 > 2.0` → V | recusado: falhou na rolagem |
| 43 | 11 | p1 | acerto | `randrange` | [1, 100] | 44 | 71 | `44 > 71` → F | aprovado: ACERTOU |
| 44 | 11 | p1 | crítico | `randrange` | [1, 100] | 48 | 35 | `48 <= 35` → F | recusado: sem crítico |
| 45 | 11 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 63 | 2.0 | `63 > 2.0` → V | recusado: falhou na rolagem |
| 46 | 11 | p2 | acerto | `randrange` | [1, 100] | 24 | 68 | `24 > 68` → F | aprovado: ACERTOU |
| 47 | 11 | p2 | crítico | `randrange` | [1, 100] | 5 | 30 | `5 <= 30` → V | aprovado: CRÍTICO |
| 48 | 11 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 35 | 2.0 | `35 > 2.0` → V | recusado: falhou na rolagem |
| 49 | 11 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 14 | 35.0 | `14 > 35.0` → F | aprovado: passou na rolagem |
| 50 | 12 | p2 | acerto | `randrange` | [1, 100] | 3 | 68 | `3 > 68` → F | aprovado: ACERTOU |
| 51 | 12 | p2 | crítico | `randrange` | [1, 100] | 2 | 30 | `2 <= 30` → V | aprovado: CRÍTICO |
| 52 | 12 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 20 | 2.0 | `20 > 2.0` → V | recusado: falhou na rolagem |
| 53 | 12 | p1 | acerto | `randrange` | [1, 100] | 76 | 71 | `76 > 71` → V | recusado: ERROU |
| 54 | 14 | p1 | acerto | `randrange` | [1, 100] | 65 | 61 | `65 > 61` → V | recusado: ERROU |
| 55 | 14 | p2 | acerto | `randrange` | [1, 100] | 56 | 68 | `56 > 68` → F | aprovado: ACERTOU |
| 56 | 14 | p2 | crítico | `randrange` | [1, 100] | 29 | 30 | `29 <= 30` → V | aprovado: CRÍTICO |
| 57 | 14 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 68 | 2.0 | `68 > 2.0` → V | recusado: falhou na rolagem |
| 58 | 15 | p1 | acerto | `randrange` | [1, 100] | 64 | 71 | `64 > 71` → F | aprovado: ACERTOU |
| 59 | 15 | p1 | crítico | `randrange` | [1, 100] | 76 | 35 | `76 <= 35` → F | recusado: sem crítico |
| 60 | 15 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 28 | 2.0 | `28 > 2.0` → V | recusado: falhou na rolagem |
| 61 | 15 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 6 | 45.0 | `6 > 45.0` → F | aprovado: passou na rolagem |
| 62 | 15 | p2 | acerto | `randrange` | [1, 100] | 88 | 68 | `88 > 68` → V | recusado: ERROU |
| 63 | 16 | p1 | acerto | `randrange` | [1, 100] | 85 | 71 | `85 > 71` → V | recusado: ERROU |
| 64 | 16 | p2 | acerto | `randrange` | [1, 100] | 54 | 68 | `54 > 68` → F | aprovado: ACERTOU |
| 65 | 16 | p2 | crítico | `randrange` | [1, 100] | 100 | 30 | `100 <= 30` → F | recusado: sem crítico |
| 66 | 16 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 12 | 2.0 | `12 > 2.0` → V | recusado: falhou na rolagem |
| 67 | 17 | p1 | acerto | `randrange` | [1, 100] | 18 | 71 | `18 > 71` → F | aprovado: ACERTOU |
| 68 | 17 | p1 | crítico | `randrange` | [1, 100] | 97 | 35 | `97 <= 35` → F | recusado: sem crítico |
| 69 | 17 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 55 | 2.0 | `55 > 2.0` → V | recusado: falhou na rolagem |
| 70 | 17 | p2 | acerto | `randrange` | [1, 100] | 12 | 68 | `12 > 68` → F | aprovado: ACERTOU |
| 71 | 17 | p2 | crítico | `randrange` | [1, 100] | 87 | 30 | `87 <= 30` → F | recusado: sem crítico |
| 72 | 17 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 53 | 2.0 | `53 > 2.0` → V | recusado: falhou na rolagem |
| 73 | 17 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 90 | 35.0 | `90 > 35.0` → V | recusado: falhou na rolagem |
| 74 | 18 | p2 | acerto | `randrange` | [1, 100] | 91 | 68 | `91 > 68` → V | recusado: ERROU |
| 75 | 18 | p1 | acerto | `randrange` | [1, 100] | 49 | 71 | `49 > 71` → F | aprovado: ACERTOU |
| 76 | 18 | p1 | crítico | `randrange` | [1, 100] | 12 | 35 | `12 <= 35` → V | aprovado: CRÍTICO |
| 77 | 18 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 3 | 2.0 | `3 > 2.0` → V | recusado: falhou na rolagem |
| 78 | 19 | p1 | acerto | `randrange` | [1, 100] | 9 | 71 | `9 > 71` → F | aprovado: ACERTOU |
| 79 | 19 | p1 | crítico | `randrange` | [1, 100] | 79 | 35 | `79 <= 35` → F | recusado: sem crítico |
| 80 | 19 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 88 | 2.0 | `88 > 2.0` → V | recusado: falhou na rolagem |
| 81 | 19 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 46 | 45.0 | `46 > 45.0` → V | recusado: falhou na rolagem |
| 82 | 20 | p2 | acerto | `randrange` | [1, 100] | 89 | 68 | `89 > 68` → V | recusado: ERROU |
| 83 | 20 | p1 | acerto | `randrange` | [1, 100] | 8 | 71 | `8 > 71` → F | aprovado: ACERTOU |
| 84 | 20 | p1 | crítico | `randrange` | [1, 100] | 54 | 35 | `54 <= 35` → F | recusado: sem crítico |
| 85 | 20 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 16 | 2.0 | `16 > 2.0` → V | recusado: falhou na rolagem |
| 86 | 21 | p2 | acerto | `randrange` | [1, 100] | 31 | 68 | `31 > 68` → F | aprovado: ACERTOU |
| 87 | 21 | p2 | crítico | `randrange` | [1, 100] | 43 | 30 | `43 <= 30` → F | recusado: sem crítico |
| 88 | 21 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 41 | 2.0 | `41 > 2.0` → V | recusado: falhou na rolagem |
| 89 | 21 | p1 | acerto | `randrange` | [1, 100] | 14 | 71 | `14 > 71` → F | aprovado: ACERTOU |
| 90 | 21 | p1 | crítico | `randrange` | [1, 100] | 60 | 35 | `60 <= 35` → F | recusado: sem crítico |
| 91 | 21 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 7 | 2.0 | `7 > 2.0` → V | recusado: falhou na rolagem |
| 92 | 22 | p2 | acerto | `randrange` | [1, 100] | 31 | 68 | `31 > 68` → F | aprovado: ACERTOU |
| 93 | 22 | p2 | crítico | `randrange` | [1, 100] | 37 | 30 | `37 <= 30` → F | recusado: sem crítico |
| 94 | 22 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 85 | 2.0 | `85 > 2.0` → V | recusado: falhou na rolagem |
| 95 | 22 | p1 | acerto | `randrange` | [1, 100] | 53 | 71 | `53 > 71` → F | aprovado: ACERTOU |
| 96 | 22 | p1 | crítico | `randrange` | [1, 100] | 20 | 35 | `20 <= 35` → V | aprovado: CRÍTICO |
| 97 | 22 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 74 | 2.0 | `74 > 2.0` → V | recusado: falhou na rolagem |
| 98 | 22 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 82 | 45.0 | `82 > 45.0` → V | recusado: falhou na rolagem |
| 99 | 23 | p2 | acerto | `randrange` | [1, 100] | 90 | 68 | `90 > 68` → V | recusado: ERROU |
| 100 | 23 | p1 | acerto | `randrange` | [1, 100] | 92 | 71 | `92 > 71` → V | recusado: ERROU |
| 101 | 24 | p2 | acerto | `randrange` | [1, 100] | 25 | 68 | `25 > 68` → F | aprovado: ACERTOU |
| 102 | 24 | p2 | crítico | `randrange` | [1, 100] | 70 | 30 | `70 <= 30` → F | recusado: sem crítico |
| 103 | 24 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 35 | 2.0 | `35 > 2.0` → V | recusado: falhou na rolagem |
| 104 | 24 | p1 | acerto | `randrange` | [1, 100] | 71 | 71 | `71 > 71` → F | aprovado: ACERTOU |
| 105 | 24 | p1 | crítico | `randrange` | [1, 100] | 44 | 35 | `44 <= 35` → F | recusado: sem crítico |
| 106 | 24 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 70 | 2.0 | `70 > 2.0` → V | recusado: falhou na rolagem |
| 107 | 25 | p2 | acerto | `randrange` | [1, 100] | 71 | 68 | `71 > 68` → V | recusado: ERROU |
| 108 | 25 | p1 | acerto | `randrange` | [1, 100] | 25 | 71 | `25 > 71` → F | aprovado: ACERTOU |
| 109 | 25 | p1 | crítico | `randrange` | [1, 100] | 3 | 35 | `3 <= 35` → V | aprovado: CRÍTICO |
| 110 | 25 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 48 | 2.0 | `48 > 2.0` → V | recusado: falhou na rolagem |
| 111 | 26 | p2 | acerto | `randrange` | [1, 100] | 67 | 68 | `67 > 68` → F | aprovado: ACERTOU |
| 112 | 26 | p2 | crítico | `randrange` | [1, 100] | 73 | 30 | `73 <= 30` → F | recusado: sem crítico |
| 113 | 26 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 89 | 2.0 | `89 > 2.0` → V | recusado: falhou na rolagem |
| 114 | 26 | p1 | acerto | `randrange` | [1, 100] | 25 | 71 | `25 > 71` → F | aprovado: ACERTOU |
| 115 | 26 | p1 | crítico | `randrange` | [1, 100] | 15 | 35 | `15 <= 35` → V | aprovado: CRÍTICO |
| 116 | 26 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 88 | 2.0 | `88 > 2.0` → V | recusado: falhou na rolagem |
| 117 | 26 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 64 | 45.0 | `64 > 45.0` → V | recusado: falhou na rolagem |
| 118 | 27 | p2 | acerto | `randrange` | [1, 100] | 6 | 68 | `6 > 68` → F | aprovado: ACERTOU |
| 119 | 27 | p2 | crítico | `randrange` | [1, 100] | 63 | 30 | `63 <= 30` → F | recusado: sem crítico |
| 120 | 27 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 91 | 2.0 | `91 > 2.0` → V | recusado: falhou na rolagem |
| 121 | 27 | p1 | acerto | `randrange` | [1, 100] | 67 | 71 | `67 > 71` → F | aprovado: ACERTOU |
| 122 | 27 | p1 | crítico | `randrange` | [1, 100] | 16 | 35 | `16 <= 35` → V | aprovado: CRÍTICO |
| 123 | 27 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 99 | 2.0 | `99 > 2.0` → V | recusado: falhou na rolagem |
| 124 | 28 | p2 | acerto | `randrange` | [1, 100] | 87 | 68 | `87 > 68` → V | recusado: ERROU |
| 125 | 28 | p1 | acerto | `randrange` | [1, 100] | 71 | 71 | `71 > 71` → F | aprovado: ACERTOU |
| 126 | 28 | p1 | crítico | `randrange` | [1, 100] | 7 | 35 | `7 <= 35` → V | aprovado: CRÍTICO |
| 127 | 28 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 81 | 2.0 | `81 > 2.0` → V | recusado: falhou na rolagem |
| 128 | 29 | p2 | acerto | `randrange` | [1, 100] | 2 | 68 | `2 > 68` → F | aprovado: ACERTOU |
| 129 | 29 | p2 | crítico | `randrange` | [1, 100] | 36 | 30 | `36 <= 30` → F | recusado: sem crítico |
| 130 | 29 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 77 | 2.0 | `77 > 2.0` → V | recusado: falhou na rolagem |
| 131 | 29 | p1 | acerto | `randrange` | [1, 100] | 32 | 71 | `32 > 71` → F | aprovado: ACERTOU |
| 132 | 29 | p1 | crítico | `randrange` | [1, 100] | 59 | 35 | `59 <= 35` → F | recusado: sem crítico |
| 133 | 29 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 85 | 2.0 | `85 > 2.0` → V | recusado: falhou na rolagem |
| 134 | 29 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 82 | 45.0 | `82 > 45.0` → V | recusado: falhou na rolagem |
| 135 | 30 | p2 | acerto | `randrange` | [1, 100] | 22 | 68 | `22 > 68` → F | aprovado: ACERTOU |
| 136 | 30 | p2 | crítico | `randrange` | [1, 100] | 86 | 30 | `86 <= 30` → F | recusado: sem crítico |
| 137 | 30 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 98 | 2.0 | `98 > 2.0` → V | recusado: falhou na rolagem |
| 138 | 30 | p1 | acerto | `randrange` | [1, 100] | 72 | 71 | `72 > 71` → V | recusado: ERROU |
| 139 | 31 | p2 | acerto | `randrange` | [1, 100] | 96 | 68 | `96 > 68` → V | recusado: ERROU |
| 140 | 31 | p1 | acerto | `randrange` | [1, 100] | 91 | 71 | `91 > 71` → V | recusado: ERROU |
| 141 | 32 | p2 | acerto | `randrange` | [1, 100] | 81 | 68 | `81 > 68` → V | recusado: ERROU |
| 142 | 32 | p1 | acerto | `randrange` | [1, 100] | 22 | 71 | `22 > 71` → F | aprovado: ACERTOU |
| 143 | 32 | p1 | crítico | `randrange` | [1, 100] | 45 | 35 | `45 <= 35` → F | recusado: sem crítico |
| 144 | 32 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 30 | 2.0 | `30 > 2.0` → V | recusado: falhou na rolagem |
| 145 | 33 | p2 | acerto | `randrange` | [1, 100] | 37 | 68 | `37 > 68` → F | aprovado: ACERTOU |
| 146 | 33 | p2 | crítico | `randrange` | [1, 100] | 61 | 30 | `61 <= 30` → F | recusado: sem crítico |
| 147 | 33 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 27 | 2.0 | `27 > 2.0` → V | recusado: falhou na rolagem |
| 148 | 33 | p1 | acerto | `randrange` | [1, 100] | 35 | 71 | `35 > 71` → F | aprovado: ACERTOU |
| 149 | 33 | p1 | crítico | `randrange` | [1, 100] | 35 | 35 | `35 <= 35` → V | aprovado: CRÍTICO |
| 150 | 33 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 3 | 2.0 | `3 > 2.0` → V | recusado: falhou na rolagem |
| 151 | 33 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 23 | 45.0 | `23 > 45.0` → F | aprovado: passou na rolagem |
| 152 | 34 | p2 | acerto | `randrange` | [1, 100] | 11 | 68 | `11 > 68` → F | aprovado: ACERTOU |
| 153 | 34 | p2 | crítico | `randrange` | [1, 100] | 85 | 30 | `85 <= 30` → F | recusado: sem crítico |
| 154 | 34 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 51 | 2.0 | `51 > 2.0` → V | recusado: falhou na rolagem |
| 155 | 34 | p1 | acerto | `randrange` | [1, 100] | 99 | 71 | `99 > 71` → V | recusado: ERROU |
| 156 | 35 | p2 | acerto | `randrange` | [1, 100] | 65 | 68 | `65 > 68` → F | aprovado: ACERTOU |
| 157 | 35 | p2 | crítico | `randrange` | [1, 100] | 75 | 30 | `75 <= 30` → F | recusado: sem crítico |
| 158 | 35 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 100 | 2.0 | `100 > 2.0` → V | recusado: falhou na rolagem |
| 159 | 35 | p1 | acerto | `randrange` | [1, 100] | 11 | 71 | `11 > 71` → F | aprovado: ACERTOU |
| 160 | 35 | p1 | crítico | `randrange` | [1, 100] | 91 | 35 | `91 <= 35` → F | recusado: sem crítico |
| 161 | 35 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 48 | 2.0 | `48 > 2.0` → V | recusado: falhou na rolagem |
| 162 | 36 | p2 | acerto | `randrange` | [1, 100] | 56 | 68 | `56 > 68` → F | aprovado: ACERTOU |
| 163 | 36 | p2 | crítico | `randrange` | [1, 100] | 45 | 30 | `45 <= 30` → F | recusado: sem crítico |
| 164 | 36 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 11 | 2.0 | `11 > 2.0` → V | recusado: falhou na rolagem |
| 165 | 36 | p1 | acerto | `randrange` | [1, 100] | 84 | 71 | `84 > 71` → V | recusado: ERROU |
| 166 | 37 | p2 | acerto | `randrange` | [1, 100] | 54 | 68 | `54 > 68` → F | aprovado: ACERTOU |
| 167 | 37 | p2 | crítico | `randrange` | [1, 100] | 14 | 30 | `14 <= 30` → V | aprovado: CRÍTICO |
| 168 | 37 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 79 | 2.0 | `79 > 2.0` → V | recusado: falhou na rolagem |

## Verificação de fidelidade

A final rodou duas vezes com `random.Random(6619800792897972838)`, os mesmos gladiadores (preparação nova a cada vez) e a mesma política: sem nenhuma instrumentação e auditada.

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

- **lubatv**: 33 golpes tentados com chance média de acerto 70.1%, 23 conectaram (69.7%); dano médio por golpe conectado 238.9. O fator de defesa médio que os golpes dele enfrentaram foi 0.1716 e a mitigação de entrada do alvo, 0.6552.
- **fer**: 33 golpes tentados com chance média de acerto 68.0%, 22 conectaram (66.7%); dano médio por golpe conectado 240.8. O fator de defesa médio que os golpes dele enfrentaram foi 0.1595 e a mitigação de entrada do alvo, 0.7100.
- Iniciativa: fer agiu primeiro em 25 de 37 rodadas; lubatv, em 12. Na rodada final, a ordem foi fer → lubatv (`score`).
- Score de iniciativa por rodada (p1 / p2 → quem agiu primeiro):
  - Rodada 1: 1.036408 / 1.064217 → fer
  - Rodada 2: 1.080726 / 1.064217 → lubatv **(a ordem virou)**; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847
  - Rodada 3: 1.080726 / 1.064217 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847
  - Rodada 4: 1.080726 / 1.064217 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847
  - Rodada 5: 1.080726 / 1.064217 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Postura Impecável de lubatv, Juramento da Muralha de fer
  - Rodada 6: 1.036408 / 1.064217 → fer **(a ordem virou)**
  - Rodada 7: 1.036408 / 1.042458 → fer; atributos efetivos diferentes da rodada 1 — fer: df 503→402
  - Rodada 8: 1.080726 / 1.042458 → lubatv **(a ordem virou)**; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402
  - Rodada 9: 1.080726 / 1.042458 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402
  - Rodada 10: 1.080726 / 1.042458 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402
  - Rodada 11: 1.080726 / 1.042458 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Postura Impecável de lubatv, Juramento da Muralha de fer
  - Rodada 12: 1.017149 / 1.064217 → fer **(a ordem virou)**; atributos efetivos diferentes da rodada 1 — lubatv: st 547→437
  - Rodada 13: 1.017149 / 1.064217 → fer; atributos efetivos diferentes da rodada 1 — lubatv: st 547→437
  - Rodada 14: 1.080726 / 1.064217 → lubatv **(a ordem virou)**; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847
  - Rodada 15: 1.080726 / 1.064217 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847
  - Rodada 16: 1.080726 / 1.042458 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402
  - Rodada 17: 1.080726 / 1.042458 → lubatv; atributos efetivos diferentes da rodada 1 — lubatv: st 547→847; fer: df 503→402; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Postura Impecável de lubatv, Juramento da Muralha de fer
  - Rodada 18: 1.036408 / 1.064217 → fer **(a ordem virou)**
  - Rodada 19: 1.036408 / 1.064217 → fer
  - Rodada 20: 1.036408 / 1.064217 → fer
  - Rodada 21: 1.036408 / 1.064217 → fer
  - Rodada 22: 1.036408 / 1.064217 → fer
  - Rodada 23: 1.036408 / 1.064217 → fer; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Juramento da Muralha de fer
  - Rodada 24: 1.036408 / 1.064217 → fer
  - Rodada 25: 1.036408 / 1.064217 → fer
  - Rodada 26: 1.036408 / 1.064217 → fer
  - Rodada 27: 1.036408 / 1.064217 → fer
  - Rodada 28: 1.036408 / 1.064217 → fer
  - Rodada 29: 1.036408 / 1.064217 → fer
  - Rodada 30: 1.036408 / 1.064217 → fer
  - Rodada 31: 1.036408 / 1.064217 → fer
  - Rodada 32: 1.036408 / 1.064217 → fer
  - Rodada 33: 1.036408 / 1.064217 → fer
  - Rodada 34: 1.036408 / 1.042458 → fer; atributos efetivos diferentes da rodada 1 — fer: df 503→402
  - Rodada 35: 1.036408 / 1.042458 → fer; atributos efetivos diferentes da rodada 1 — fer: df 503→402
  - Rodada 36: 1.036408 / 1.042458 → fer; atributos efetivos diferentes da rodada 1 — fer: df 503→402
  - Rodada 37: 1.036408 / 1.064217 → fer
  - Leitura: o vetor da iniciativa usa ST/MG/AG/DF efetivos e os TETOS de HP e MP, então um buff de atributo do próprio lado e um status do adversário que reduz atributo ou teto entram na ordem da rodada seguinte; quando expiram, saem dela.
- Na última rodada, lubatv havia travado Ataque básico (ataque básico); a ação ficou cancelada por morte, porque fer agiu antes e o golpe dele encerrou o duelo.
- Margem (estimativa, não registro): fer terminou com 1165 de HP; o dano médio por golpe conectado de lubatv foi 238.9, ou seja, ~4.9 golpe(s) conectado(s) de distância.
- Críticos de lubatv: 9, somando 3084 de 5494 de dano de golpe (56.1%).
- Sustentação de fer: cura 682 e Égide 0 contra 5494 de dano recebido.
- Críticos de fer: 5, somando 1961 de 5298 de dano de golpe (37.0%).
- Economia de ação: fer usou 27 skills e 10 ataques básicos; lubatv, 17 e 19.

