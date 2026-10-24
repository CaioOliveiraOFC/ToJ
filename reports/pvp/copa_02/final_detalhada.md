# Copa Arena 02 — Final detalhada: aspaszin × SkipNhO

Transcrição da final a partir do trace da auditoria (`tools/arena_auditoria.py`), na ordem em que o motor executou. Cada número abaixo foi capturado no momento da execução, pela chamada real da função canônica; os recálculos que explicam um número são feitos com as mesmas funções e constantes e conferidos contra o valor devolvido pelo motor — se divergissem, a auditoria pararia com erro.

## Convenções

- Gerador da partida: `random.Random(3846561752997802364)`, observado por um proxy que delega cada chamada e anota operação, limites, valor e chamador. O proxy não sorteia nada por conta própria.
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

### p1 — aspaszin (Mago, nível 23)

- HP 4477/4477, MP 1694/1694; ST 395, MG 666, AG 97, DF 412
- Arma: +36.0% de dano; Égide de Mana: 15%
- Equipamento: Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda
- Passivas: Lâmina Afiada (crit_chance 10), Lâmina Afiada (crit_chance 10), Oráculo Partido (magic 16), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3), Olho de Águia (crit_chance 5), Pulso Certeiro (crit_damage 15), Sangue de Vidente (magic 3)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 50.0, crit_damage 100.0, mana_regen 20.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Prisma de Devastação (`prisma_de_devastacao`) | damage | 0 | 131 | 4 | 5.096 × (1.0×mg) | -10 | 0 | vulnerable 70% por 3 | target_afflicted +45% | um cajado |
| Hora do Arauto (`n_hora_do_arauto`) | status | fear 85% por 4 | 140 | 5 | 0.0 × (—) | +0 | 0 | vulnerable 70% por 3 | — | — |
| Lente de Obsidiana (`lente_de_obsidiana`) | damage | 0 | 78 | 3 | 4.29 × (1.0×mg) | +15 | 0 | vulnerable 55% por 3 | target_healthy +25% | um cajado |
| Bola de Fogo (`bola_fogo`) | damage | 0 | 65 | 1 | 3.485 × (1.0×mg) | +0 | 0 | — | target_afflicted +45% | — |

### p2 — SkipNhO (Guerreiro, nível 22)

- HP 5004/5004, MP 648/648; ST 576, MG 324, AG 108, DF 505
- Arma: +33.0% de dano; Égide de Mana: 0%
- Equipamento: Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda
- Passivas: Escudo da Fé (damage_reduction 5), Escudo da Fé (damage_reduction 5), Alma Eterna (max_hp 100), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3), Sangue de Guerreiro (max_hp 25), Pele Grossa (defense 3), Postura Fechada (damage_reduction 3)
- Modificadores de combate (funil `fx.combat_modifier`): crit_damage 10.0, damage_reduction 43.0, life_steal 5.0, stun_chance 8.0, bleed_chance 10.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Fortaleza Viva (`fortaleza_viva`) | damage | 0 | 191 | 5 | 6.394 × (0.6×df + 0.4×st) | -15 | 0 | stun 40% por 1 | caster_wounded +60% | — |
| Golpe Poderoso (`golpe_poderoso`) | damage | 0 | 47 | 1 | 2.86 × (1.0×st) | +0 | 0 | — | target_healthy +8% | — |
| Juramento da Muralha (`juramento_da_muralha`) | damage_reduction | 45 por 4 | 136 | 5 | 0.0 × (—) | +0 | 0 | — | — | as duas mãos ocupadas |
| Guarda Cruzada (`n_guarda_cruzada`) | damage_reduction | 32 por 3 | 99 | 4 | 0.0 × (—) | +0 | 0 | — | — | as duas mãos ocupadas |

## Rodada 1

### 1.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 4477/4477 | 5004/5004 |
| MP | 1694/1694 | 648/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | — | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 1.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 1): eu HP 4477/4477, MP 1694/1694, efeitos —, buffs —; adversário SkipNhO HP 5004/5004, MP 648/648, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 0, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Hora do Arauto** — justificativa da política: Hora do Arauto aplica fear, que o adversário não carrega (efeitos visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 140

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 1): eu HP 5004/5004, MP 648/648, efeitos —, buffs —; adversário aspaszin HP 4477/4477, MP 1694/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 0, Guarda Cruzada 0
- Ações legais: Ataque básico, Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 136

- Lock: aspaszin (p1) reserva **140 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **136 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Hora do Arauto; SkipNhO (p2) = Juramento da Muralha

### 1.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1554 → min(1694, 1554 + 53) = 1607
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1554 → 1607
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 140, teto livre 1554 → MP 1607 → 1554
- Perde a oportunidade por controle: não

**Skill Hora do Arauto** (`n_hora_do_arauto`) de aspaszin (p1)

- Tipo `status`, valor fear ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 140 MP; reserva feita no lock 140; MP disponível na cobrança (livre + reserva liberada) 1694
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Status: chance base 85%, duração declarada 4

**Status `fear`** sobre SkipNhO (p2) (via `apply_skill`, fonte `n_hora_do_arauto`)

- Chance base 85%; resistência do alvo 0.0% → efetiva 85 × (1 − 0/100) = 85.0%
- sorteio nº 1 [aplicação de status (fear)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 85.0; teste `29 > 85.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 4 → após leis (nenhuma) 4; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `fear` no alvo antes: —; depois: [{'duration': 4, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `n_hora_do_arauto`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 2 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 70.0; teste `55 > 70.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]

- Resultado da skill: `status`; MP debitado 140; recarga depois 6; status fear pegou
- Mudanças em quem lançou: mp 1694 → 1554; recarga Hora do Arauto — → 6
- Mudanças no adversário: df 505 → 404; efeito fear entra (dur 4, stacks 1, int 20.0); efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Hora do Arauto; MP gasto 140, dano ao adversário 0.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 512 → min(648, 512 + 12) = 524
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 512 → 524; efeito fear: dur 4 → 3, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 136, teto livre 512 → MP 524 → 512
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de SkipNhO (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe SkipNhO (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 136 MP; reserva feita no lock 136; MP disponível na cobrança (livre + reserva liberada) 648
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 136; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 648 → 512; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): SkipNhO (p2) executou Juramento da Muralha; MP gasto 136, dano ao adversário 0.

### 1.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 4477/4477 | 5004/5004 |
| MP | 1554/1694 | 512/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 6 | Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Hora do Arauto — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- SkipNhO (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 2

### 2.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 4477/4477 | 5004/5004 |
| MP | 1554/1694 | 512/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 6 | Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

### 2.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 2): eu HP 4477/4477, MP 1554/1694, efeitos —, buffs —; adversário SkipNhO HP 5004/5004, MP 512/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 5, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Prisma de Devastação, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Prisma de Devastação** — justificativa da política: primeira skill de dano legal do deck: Prisma de Devastação
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 2): eu HP 5004/5004, MP 512/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha']; adversário aspaszin HP 4477/4477, MP 1554/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 5, Guarda Cruzada 0
- Ações legais: Ataque básico, Fortaleza Viva, Golpe Poderoso, Guarda Cruzada, Rendição
- Escolha: **Guarda Cruzada** — justificativa da política: Guarda Cruzada é legal e não está ativo (buffs visíveis: ['Juramento da Muralha'])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 99

- Lock: aspaszin (p1) reserva **131 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **99 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Prisma de Devastação; SkipNhO (p2) = Guarda Cruzada

### 2.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 404.0 | 299.0 | 1.351170568561873 | 1.1623986272195408 |

- Soma das seis raízes (`math.fsum`): 5.89838215396206
- ÷ 6 = build 0.98306369232701
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.98306369232701 × 0.995 = 0.9781483738653749**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9781483738653749 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 6 → 5
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1423 → min(1694, 1423 + 53) = 1476
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1423 → 1476; recarga Hora do Arauto 6 → 5
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 1563 → MP 1476 → 1476
- Perde a oportunidade por controle: não

**Skill Prisma de Devastação** (`prisma_de_devastacao`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 1607
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #1** — aspaszin (p1) → SkipNhO (p2), skill `prisma_de_devastacao`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 5.096 = 4615.75296; max(1, int(666.0 × (1 + 36/100) × 5.096)) = **4615**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação -10 − ocultação 0 = 73.39024390243902 → clamp [20, 95] e int → **73**
7. Rolagem de acerto: sorteio nº 3 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **47**; chance 73; teste `47 > 73` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 4 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **74**; chance 50; teste `74 <= 50` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 404
15. Fator de defesa: 100 / (100 + 404) = 0.1984126984126984
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 88.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 4615.0 × 1.45 × 1.0 × 0.1984126984126984 = 1327.7281746031745; max(1, int(bruto)) = 1327 → int(anterior × 1.0) = 1327 → int(anterior × 0.19999999999999996) = 265
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **265**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 265
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(265)`; HP do alvo 5004 → 4739 (retirado 265)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4739 → o alvo segue vivo

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `prisma_de_devastacao`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 5 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 70.0; teste `9 > 70.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]

- Resultado da skill: `damage`; MP debitado 131; recarga depois 5
- Mudanças em quem lançou: mp 1607 → 1476; recarga Prisma de Devastação — → 5
- Mudanças no adversário: hp 5004 → 4739; df 404 → 303; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Prisma de Devastação; MP gasto 131, dano ao adversário 265.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 413 → min(648, 413 + 12) = 425
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 413 → 425; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3; efeito fear: dur 3 → 2, stacks 1 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 99, teto livre 549 → MP 425 → 425
- Perde a oportunidade por controle: não

**Skill Guarda Cruzada** (`n_guarda_cruzada`) de SkipNhO (p2)

- Tipo `damage_reduction`, valor 32 ; alvo declarado `self` → recebe SkipNhO (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 99 MP; reserva feita no lock 99; MP disponível na cobrança (livre + reserva liberada) 524
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 99; recarga depois 5; buff gravado {'stat': 'damage_reduction', 'value': 32, 'duration': 3}
- Mudanças em quem lançou: mp 524 → 425; recarga Guarda Cruzada — → 5; buff Guarda Cruzada entra (damage_reduction 32, dur 3)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): SkipNhO (p2) executou Guarda Cruzada; MP gasto 99, dano ao adversário 0.

### 2.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 4477/4477 | 4739/5004 |
| MP | 1476/1694 | 425/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | Juramento da Muralha 5, Guarda Cruzada 5 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3); Guarda Cruzada (damage_reduction 32, dur 3) |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Prisma de Devastação — executada; dano causado na rodada 265 (golpes e DoT), recebido 0; cura 0
- SkipNhO (p2): Guarda Cruzada — executada; dano causado na rodada 0 (golpes e DoT), recebido 265; cura 0


## Rodada 3

### 3.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 4477/4477 | 4739/5004 |
| MP | 1476/1694 | 425/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | Juramento da Muralha 5, Guarda Cruzada 5 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3); Guarda Cruzada (damage_reduction 32, dur 3) |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

### 3.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 3): eu HP 4477/4477, MP 1476/1694, efeitos —, buffs —; adversário SkipNhO HP 4739/5004, MP 425/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 4, Hora do Arauto 4, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Lente de Obsidiana** — justificativa da política: primeira skill de dano legal do deck: Lente de Obsidiana
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 78

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 3): eu HP 4739/5004, MP 425/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha']; adversário aspaszin HP 4477/4477, MP 1476/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 4, Guarda Cruzada 4
- Ações legais: Ataque básico, Fortaleza Viva, Golpe Poderoso, Rendição
- Escolha: **Fortaleza Viva** — justificativa da política: primeira skill de dano legal do deck: Fortaleza Viva
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 191

- Lock: aspaszin (p1) reserva **78 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **191 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Lente de Obsidiana; SkipNhO (p2) = Fortaleza Viva

### 3.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 303.0 | 299.0 | 1.0133779264214047 | 1.00666674049628 |

- Soma das seis raízes (`math.fsum`): 5.742650267238799
- ÷ 6 = build 0.9571083778731332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.9571083778731332 × 0.995 = 0.9523228359837675**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9523228359837675 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 5 → 4; Prisma de Devastação 5 → 4
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1398 → min(1694, 1398 + 53) = 1451
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1398 → 1451; recarga Hora do Arauto 5 → 4; recarga Prisma de Devastação 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 78, teto livre 1616 → MP 1451 → 1451
- Perde a oportunidade por controle: não

**Skill Lente de Obsidiana** (`lente_de_obsidiana`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 78 MP; reserva feita no lock 78; MP disponível na cobrança (livre + reserva liberada) 1529
- Recarga antes do uso: 0; declarada 3 (o motor grava declarada + 1)

**Golpe #2** — aspaszin (p1) → SkipNhO (p2), skill `lente_de_obsidiana`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 4.29 = 3885.7103999999995; max(1, int(666.0 × (1 + 36/100) × 4.29)) = **3885**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 15 − ocultação 0 = 98.39024390243902 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 6 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **51**; chance 95; teste `51 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 7 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 50; teste `91 <= 50` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.25 → 1 + Σ = 1.25
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 303
15. Fator de defesa: 100 / (100 + 303) = 0.24813895781637718
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 120.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3885.0 × 1.25 × 1.0 × 0.24813895781637718 = 1205.0248138957818; max(1, int(bruto)) = 1205 → int(anterior × 1.0) = 1205 → int(anterior × 0.19999999999999996) = 240
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **240**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 240
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(240)`; HP do alvo 4739 → 4499 (retirado 240)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 4499 → o alvo segue vivo

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `lente_de_obsidiana`)

- Chance base 55%; resistência do alvo 0.0% → efetiva 55 × (1 − 0/100) = 55.0%
- sorteio nº 8 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **4**; chance 55.0; teste `4 > 55.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]; depois: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}, {'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'lente_de_obsidiana'}]

- Resultado da skill: `damage`; MP debitado 78; recarga depois 4
- Mudanças em quem lançou: mp 1529 → 1451; recarga Lente de Obsidiana — → 4
- Mudanças no adversário: hp 4739 → 4499; df 303 → 202; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Lente de Obsidiana; MP gasto 78, dano ao adversário 240.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 5 → 4; Guarda Cruzada 5 → 4
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 234 → min(648, 234 + 12) = 246
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 234 → 246; df 202 → 303; recarga Juramento da Muralha 5 → 4; recarga Guarda Cruzada 5 → 4; buff Guarda Cruzada dur 3 → 2; buff Juramento da Muralha dur 3 → 2; efeito fear: dur 2 → 1, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1; efeito vulnerable sai; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 191, teto livre 457 → MP 246 → 246
- Perde a oportunidade por controle: não

**Skill Fortaleza Viva** (`fortaleza_viva`) de SkipNhO (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe aspaszin (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 191 MP; reserva feita no lock 191; MP disponível na cobrança (livre + reserva liberada) 437
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

**Golpe #3** — SkipNhO (p2) → aspaszin (p1), skill `fortaleza_viva`

1. Atributos ofensivos efetivos: df 303.0, st 576.0
2. Pesos (da carta): df 0.6, st 0.4
3. Poder básico da ação: Σ = 412.2; × arma = 548.226; × power 6.394 = 3505.357044; max(1, int(412.2 × (1 + 33/100) × 6.394)) = **3505**
4. Bônus de arma: +33.0% → fator 1.33
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários -20 + precisão 0.0 + modificador da ação -15 − ocultação 0 = 51.609756097560975 → clamp [20, 95] e int → **51**
7. Rolagem de acerto: sorteio nº 9 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **10**; chance 51; teste `10 > 51` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 10 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 0; teste `60 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3505.0 × 1.0 × 1.0 × 0.1953125 = 684.5703125; max(1, int(bruto)) = 684 → int(anterior × 1.0) = 684 → int(anterior × 1.0) = 684
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **684**
20. Égide de Mana: desejado int(684 × 15 / 100) = 102; possível min(102, int(1451 × 2.0)) = 102; passa max(1, 684 − 102) = 582
21. MP da Égide: max(1, int(102 / 2.0)) = 51
22. Dano aplicado ao HP: `take_damage(582)`; HP do alvo 4477 → 3895 (retirado 582)
23. Roubo de vida: 5.0% → max(1, int(582 × 5 / 100)) = 29; HP do atacante +29 (teto do HP máximo)
24. Morte e death_ignore: HP final 3895 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 11 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 8.0; teste `16 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 12 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **37**; chance 10.0; teste `37 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_secundario`, fonte `fortaleza_viva`)

- Chance base 40%; resistência do alvo 0.0% → efetiva 40 × (1 − 0/100) = 40.0%
- sorteio nº 13 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 40.0; teste `98 > 40.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 191; recarga depois 6
- Mudanças em quem lançou: hp 4499 → 4528; mp 437 → 246; recarga Fortaleza Viva — → 6
- Mudanças no adversário: hp 4477 → 3895; mp 1451 → 1400

- Motor (`action_executed`): SkipNhO (p2) executou Fortaleza Viva; MP gasto 191, dano ao adversário 582.

### 3.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3895/4477 | 4528/5004 |
| MP | 1400/1694 | 246/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 4, Prisma de Devastação 4, Lente de Obsidiana 4 | Juramento da Muralha 4, Guarda Cruzada 4, Fortaleza Viva 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2); Guarda Cruzada (damage_reduction 32, dur 2) |
| Efeitos | — | fear (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte prisma_de_devastacao); vulnerable (dur 2, stacks 1, int 20.0, fonte lente_de_obsidiana) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Lente de Obsidiana — executada; dano causado na rodada 240 (golpes e DoT), recebido 582; cura 0
- SkipNhO (p2): Fortaleza Viva — executada; dano causado na rodada 582 (golpes e DoT), recebido 240; cura 29


## Rodada 4

### 4.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3895/4477 | 4528/5004 |
| MP | 1400/1694 | 246/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 4, Prisma de Devastação 4, Lente de Obsidiana 4 | Juramento da Muralha 4, Guarda Cruzada 4, Fortaleza Viva 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2); Guarda Cruzada (damage_reduction 32, dur 2) |
| Efeitos | — | fear (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte prisma_de_devastacao); vulnerable (dur 2, stacks 1, int 20.0, fonte lente_de_obsidiana) |
| death_ignore gasto / vivo | False / True | False / True |

### 4.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 4): eu HP 3895/4477, MP 1400/1694, efeitos —, buffs —; adversário SkipNhO HP 4528/5004, MP 246/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 3, Hora do Arauto 3, Lente de Obsidiana 3, Bola de Fogo 0
- Ações legais: Ataque básico, Bola de Fogo, Rendição
- Escolha: **Bola de Fogo** — justificativa da política: primeira skill de dano legal do deck: Bola de Fogo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 65

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 4): eu HP 4528/5004, MP 246/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha']; adversário aspaszin HP 3895/4477, MP 1400/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 5, Golpe Poderoso 0, Juramento da Muralha 3, Guarda Cruzada 3
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 47

- Lock: aspaszin (p1) reserva **65 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **47 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Bola de Fogo; SkipNhO (p2) = Golpe Poderoso

### 4.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 303.0 | 299.0 | 1.0133779264214047 | 1.00666674049628 |

- Soma das seis raízes (`math.fsum`): 5.742650267238799
- ÷ 6 = build 0.9571083778731332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.9571083778731332 × 0.995 = 0.9523228359837675**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9523228359837675 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 4 → 3; Prisma de Devastação 4 → 3; Lente de Obsidiana 4 → 3
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1335 → min(1694, 1335 + 53) = 1388
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1335 → 1388; recarga Lente de Obsidiana 4 → 3; recarga Hora do Arauto 4 → 3; recarga Prisma de Devastação 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 65, teto livre 1629 → MP 1388 → 1388
- Perde a oportunidade por controle: não

**Skill Bola de Fogo** (`bola_fogo`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 65 MP; reserva feita no lock 65; MP disponível na cobrança (livre + reserva liberada) 1453
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #4** — aspaszin (p1) → SkipNhO (p2), skill `bola_fogo`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 3.485 = 3156.5735999999993; max(1, int(666.0 × (1 + 36/100) × 3.485)) = **3156**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 14 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 83; teste `3 > 83` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 15 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 50; teste `34 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 303
15. Fator de defesa: 100 / (100 + 303) = 0.24813895781637718
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 120.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3156.0 × 1.45 × 2.5 × 0.24813895781637718 = 2838.833746898263; max(1, int(bruto)) = 2838 → int(anterior × 1.0) = 2838 → int(anterior × 0.19999999999999996) = 567
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **567**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 567
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(567)`; HP do alvo 4528 → 3961 (retirado 567)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3961 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 65; recarga depois 2
- Mudanças em quem lançou: mp 1453 → 1388; recarga Bola de Fogo — → 2
- Mudanças no adversário: hp 4528 → 3961

- Motor (`action_executed`): aspaszin (p1) executou Bola de Fogo; MP gasto 65, dano ao adversário 567.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Guarda Cruzada 4 → 3; Fortaleza Viva 6 → 5
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 199 → min(648, 199 + 12) = 211
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['fear', 'vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 199 → 211; df 303 → 404; recarga Fortaleza Viva 6 → 5; recarga Juramento da Muralha 4 → 3; recarga Guarda Cruzada 4 → 3; buff Guarda Cruzada dur 2 → 1; buff Juramento da Muralha dur 2 → 1; efeito fear sai; efeito vulnerable: dur 2 → 1, stacks 1 → 1; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 47, teto livre 601 → MP 211 → 211
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de SkipNhO (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe aspaszin (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 47 MP; reserva feita no lock 47; MP disponível na cobrança (livre + reserva liberada) 258
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #5** — SkipNhO (p2) → aspaszin (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 576.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 576.0; × arma = 766.08; × power 2.86 = 2190.9888; max(1, int(576.0 × (1 + 33/100) × 2.86)) = **2190**
4. Bônus de arma: +33.0% → fator 1.33
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 16 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **73**; chance 86; teste `73 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 17 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **1**; chance 0; teste `1 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.08 × 1.0 × 0.1953125 = 461.95312500000006; max(1, int(bruto)) = 461 → int(anterior × 1.0) = 461 → int(anterior × 1.0) = 461
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **461**
20. Égide de Mana: desejado int(461 × 15 / 100) = 69; possível min(69, int(1388 × 2.0)) = 69; passa max(1, 461 − 69) = 392
21. MP da Égide: max(1, int(69 / 2.0)) = 34
22. Dano aplicado ao HP: `take_damage(392)`; HP do alvo 3895 → 3503 (retirado 392)
23. Roubo de vida: 5.0% → max(1, int(392 × 5 / 100)) = 19; HP do atacante +19 (teto do HP máximo)
24. Morte e death_ignore: HP final 3503 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 18 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **26**; chance 8.0; teste `26 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 19 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 10.0; teste `63 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 47; recarga depois 2
- Mudanças em quem lançou: hp 3961 → 3980; mp 258 → 211; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3895 → 3503; mp 1388 → 1354

- Motor (`action_executed`): SkipNhO (p2) executou Golpe Poderoso; MP gasto 47, dano ao adversário 392.

### 4.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3503/4477 | 3980/5004 |
| MP | 1354/1694 | 211/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 3, Prisma de Devastação 3, Lente de Obsidiana 3, Bola de Fogo 2 | Juramento da Muralha 3, Guarda Cruzada 3, Fortaleza Viva 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1); Guarda Cruzada (damage_reduction 32, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte lente_de_obsidiana) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Bola de Fogo — executada; dano causado na rodada 567 (golpes e DoT), recebido 392; cura 0
- SkipNhO (p2): Golpe Poderoso — executada; dano causado na rodada 392 (golpes e DoT), recebido 567; cura 19


## Rodada 5

### 5.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3503/4477 | 3980/5004 |
| MP | 1354/1694 | 211/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 3, Prisma de Devastação 3, Lente de Obsidiana 3, Bola de Fogo 2 | Juramento da Muralha 3, Guarda Cruzada 3, Fortaleza Viva 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1); Guarda Cruzada (damage_reduction 32, dur 1) |
| Efeitos | — | vulnerable (dur 1, stacks 1, int 20.0, fonte lente_de_obsidiana) |
| death_ignore gasto / vivo | False / True | False / True |

### 5.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 5): eu HP 3503/4477, MP 1354/1694, efeitos —, buffs —; adversário SkipNhO HP 3980/5004, MP 211/648, efeitos ['vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 2, Hora do Arauto 2, Lente de Obsidiana 2, Bola de Fogo 1
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Prisma de Devastação', 'Hora do Arauto', 'Lente de Obsidiana', 'Bola de Fogo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 5): eu HP 3980/5004, MP 211/648, efeitos ['vulnerable'], buffs ['Guarda Cruzada', 'Juramento da Muralha']; adversário aspaszin HP 3503/4477, MP 1354/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 4, Golpe Poderoso 1, Juramento da Muralha 2, Guarda Cruzada 2
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: aspaszin (p1) = Ataque básico; SkipNhO (p2) = Ataque básico

### 5.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 404.0 | 299.0 | 1.351170568561873 | 1.1623986272195408 |

- Soma das seis raízes (`math.fsum`): 5.89838215396206
- ÷ 6 = build 0.98306369232701
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.98306369232701 × 0.995 = 0.9781483738653749**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9781483738653749 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 3 → 2; Prisma de Devastação 3 → 2; Lente de Obsidiana 3 → 2; Bola de Fogo 2 → 1
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1354 → min(1694, 1354 + 53) = 1407
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1354 → 1407; recarga Bola de Fogo 2 → 1; recarga Lente de Obsidiana 3 → 2; recarga Hora do Arauto 3 → 2; recarga Prisma de Devastação 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1694 → MP 1407 → 1407
- Perde a oportunidade por controle: não

**Golpe #6** — aspaszin (p1) → SkipNhO (p2), ataque básico

1. Atributos ofensivos efetivos: st 395.0, mg 666.0, ag 97.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 0.3, mg 1.9, ag 0.0
3. Poder básico da ação: Σ = 1383.8999999999999; dano médio max(1, int(1383.8999999999999 × (1 + 36/100))) = 1882; BASE do básico = max(1, int(1882 × 0.9)) = **1693** (multiplicador do básico 0.9)
4. Bônus de arma: +36.0% → fator 1.3599999999999999 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 20 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **75**; chance 83; teste `75 > 83` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 21 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **18**; chance 50; teste `18 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 404
15. Fator de defesa: 100 / (100 + 404) = 0.1984126984126984
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 120.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1693.0 × 1.0 × 2.5 × 0.1984126984126984 = 839.781746031746; max(1, int(bruto)) = 839 → int(anterior × 1.0) = 839 → int(anterior × 0.19999999999999996) = 167
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **167**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 167
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(167)`; HP do alvo 3980 → 3813 (retirado 167)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3813 → o alvo segue vivo

- Motor (`action_executed`): aspaszin (p1) executou Ataque básico; MP gasto 0, dano ao adversário 167.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2; Guarda Cruzada 3 → 2; Fortaleza Viva 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 211 → min(648, 211 + 12) = 223
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 211 → 223; df 404 → 505; recarga Fortaleza Viva 5 → 4; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 3 → 2; recarga Guarda Cruzada 3 → 2; buff Guarda Cruzada expira; buff Juramento da Muralha expira; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 223 → 223
- Perde a oportunidade por controle: não

**Golpe #7** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 22 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 86; teste `35 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 23 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 0; teste `64 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1258.0 × 1.0 × 1.0 × 0.1953125 = 245.703125; max(1, int(bruto)) = 245 → int(anterior × 1.0) = 245 → int(anterior × 1.0) = 245
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **245**
20. Égide de Mana: desejado int(245 × 15 / 100) = 36; possível min(36, int(1407 × 2.0)) = 36; passa max(1, 245 − 36) = 209
21. MP da Égide: max(1, int(36 / 2.0)) = 18
22. Dano aplicado ao HP: `take_damage(209)`; HP do alvo 3503 → 3294 (retirado 209)
23. Roubo de vida: 5.0% → max(1, int(209 × 5 / 100)) = 10; HP do atacante +10 (teto do HP máximo)
24. Morte e death_ignore: HP final 3294 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 24 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 8.0; teste `54 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 25 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **96**; chance 10.0; teste `96 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 209.

### 5.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3294/4477 | 3823/5004 |
| MP | 1389/1694 | 223/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 2, Prisma de Devastação 2, Lente de Obsidiana 2, Bola de Fogo 1 | Juramento da Muralha 2, Guarda Cruzada 2, Fortaleza Viva 4, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Ataque básico — executada; dano causado na rodada 167 (golpes e DoT), recebido 209; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 209 (golpes e DoT), recebido 167; cura 10


## Rodada 6

### 6.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 3294/4477 | 3823/5004 |
| MP | 1389/1694 | 223/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 2, Prisma de Devastação 2, Lente de Obsidiana 2, Bola de Fogo 1 | Juramento da Muralha 2, Guarda Cruzada 2, Fortaleza Viva 4, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 6.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 6): eu HP 3294/4477, MP 1389/1694, efeitos —, buffs —; adversário SkipNhO HP 3823/5004, MP 223/648, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 1, Hora do Arauto 1, Lente de Obsidiana 1, Bola de Fogo 0
- Ações legais: Ataque básico, Bola de Fogo, Rendição
- Escolha: **Bola de Fogo** — justificativa da política: primeira skill de dano legal do deck: Bola de Fogo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 65

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 6): eu HP 3823/5004, MP 223/648, efeitos —, buffs —; adversário aspaszin HP 3294/4477, MP 1389/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 3, Golpe Poderoso 0, Juramento da Muralha 1, Guarda Cruzada 1
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 47

- Lock: aspaszin (p1) reserva **65 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **47 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Bola de Fogo; SkipNhO (p2) = Golpe Poderoso

### 6.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 2 → 1; Prisma de Devastação 2 → 1; Lente de Obsidiana 2 → 1; Bola de Fogo 1 → livre
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1324 → min(1694, 1324 + 53) = 1377
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1324 → 1377; recarga Bola de Fogo 1 → livre; recarga Lente de Obsidiana 2 → 1; recarga Hora do Arauto 2 → 1; recarga Prisma de Devastação 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 65, teto livre 1629 → MP 1377 → 1377
- Perde a oportunidade por controle: não

**Skill Bola de Fogo** (`bola_fogo`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 65 MP; reserva feita no lock 65; MP disponível na cobrança (livre + reserva liberada) 1442
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #8** — aspaszin (p1) → SkipNhO (p2), skill `bola_fogo`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 3.485 = 3156.5735999999993; max(1, int(666.0 × (1 + 36/100) × 3.485)) = **3156**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 26 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **5**; chance 83; teste `5 > 83` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 27 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 50; teste `16 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 505
15. Fator de defesa: 100 / (100 + 505) = 0.1652892561983471
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.5700000000000001 (damage_reduction 43.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3156.0 × 1.0 × 2.5 × 0.1652892561983471 = 1304.1322314049587; max(1, int(bruto)) = 1304 → int(anterior × 1.0) = 1304 → int(anterior × 0.5700000000000001) = 743
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **743**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 743
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(743)`; HP do alvo 3823 → 3080 (retirado 743)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 3080 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 65; recarga depois 2
- Mudanças em quem lançou: mp 1442 → 1377; recarga Bola de Fogo — → 2
- Mudanças no adversário: hp 3823 → 3080

- Motor (`action_executed`): aspaszin (p1) executou Bola de Fogo; MP gasto 65, dano ao adversário 743.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Guarda Cruzada 2 → 1; Fortaleza Viva 4 → 3; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 176 → min(648, 176 + 12) = 188
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 176 → 188; recarga Fortaleza Viva 4 → 3; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 2 → 1; recarga Guarda Cruzada 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 47, teto livre 601 → MP 188 → 188
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de SkipNhO (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe aspaszin (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 47 MP; reserva feita no lock 47; MP disponível na cobrança (livre + reserva liberada) 235
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #9** — SkipNhO (p2) → aspaszin (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 576.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 576.0; × arma = 766.08; × power 2.86 = 2190.9888; max(1, int(576.0 × (1 + 33/100) × 2.86)) = **2190**
4. Bônus de arma: +33.0% → fator 1.33
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 28 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 86; teste `63 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 29 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **41**; chance 0; teste `41 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.1953125 = 427.734375; max(1, int(bruto)) = 427 → int(anterior × 1.0) = 427 → int(anterior × 1.0) = 427
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **427**
20. Égide de Mana: desejado int(427 × 15 / 100) = 64; possível min(64, int(1377 × 2.0)) = 64; passa max(1, 427 − 64) = 363
21. MP da Égide: max(1, int(64 / 2.0)) = 32
22. Dano aplicado ao HP: `take_damage(363)`; HP do alvo 3294 → 2931 (retirado 363)
23. Roubo de vida: 5.0% → max(1, int(363 × 5 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 2931 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 30 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 8.0; teste `14 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 31 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **18**; chance 10.0; teste `18 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 47; recarga depois 2
- Mudanças em quem lançou: hp 3080 → 3098; mp 235 → 188; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3294 → 2931; mp 1377 → 1345

- Motor (`action_executed`): SkipNhO (p2) executou Golpe Poderoso; MP gasto 47, dano ao adversário 363.

### 6.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2931/4477 | 3098/5004 |
| MP | 1345/1694 | 188/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 1, Prisma de Devastação 1, Lente de Obsidiana 1, Bola de Fogo 2 | Juramento da Muralha 1, Guarda Cruzada 1, Fortaleza Viva 3, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Bola de Fogo — executada; dano causado na rodada 743 (golpes e DoT), recebido 363; cura 0
- SkipNhO (p2): Golpe Poderoso — executada; dano causado na rodada 363 (golpes e DoT), recebido 743; cura 18


## Rodada 7

### 7.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2931/4477 | 3098/5004 |
| MP | 1345/1694 | 188/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 1, Prisma de Devastação 1, Lente de Obsidiana 1, Bola de Fogo 2 | Juramento da Muralha 1, Guarda Cruzada 1, Fortaleza Viva 3, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 7.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 7): eu HP 2931/4477, MP 1345/1694, efeitos —, buffs —; adversário SkipNhO HP 3098/5004, MP 188/648, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 0, Lente de Obsidiana 0, Bola de Fogo 1
- Ações legais: Ataque básico, Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Rendição
- Escolha: **Hora do Arauto** — justificativa da política: Hora do Arauto aplica fear, que o adversário não carrega (efeitos visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 140

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 7): eu HP 3098/5004, MP 188/648, efeitos —, buffs —; adversário aspaszin HP 2931/4477, MP 1345/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 2, Golpe Poderoso 1, Juramento da Muralha 0, Guarda Cruzada 0
- Ações legais: Ataque básico, Juramento da Muralha, Guarda Cruzada, Rendição
- Escolha: **Juramento da Muralha** — justificativa da política: Juramento da Muralha é legal e não está ativo (buffs visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 136

- Lock: aspaszin (p1) reserva **140 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **136 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Hora do Arauto; SkipNhO (p2) = Juramento da Muralha

### 7.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 1 → livre; Prisma de Devastação 1 → livre; Lente de Obsidiana 1 → livre; Bola de Fogo 2 → 1
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1205 → min(1694, 1205 + 53) = 1258
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1205 → 1258; recarga Bola de Fogo 2 → 1; recarga Lente de Obsidiana 1 → livre; recarga Hora do Arauto 1 → livre; recarga Prisma de Devastação 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 140, teto livre 1554 → MP 1258 → 1258
- Perde a oportunidade por controle: não

**Skill Hora do Arauto** (`n_hora_do_arauto`) de aspaszin (p1)

- Tipo `status`, valor fear ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 140 MP; reserva feita no lock 140; MP disponível na cobrança (livre + reserva liberada) 1398
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Status: chance base 85%, duração declarada 4

**Status `fear`** sobre SkipNhO (p2) (via `apply_skill`, fonte `n_hora_do_arauto`)

- Chance base 85%; resistência do alvo 0.0% → efetiva 85 × (1 − 0/100) = 85.0%
- sorteio nº 32 [aplicação de status (fear)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **22**; chance 85.0; teste `22 > 85.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 4 → após leis (nenhuma) 4; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `fear` no alvo antes: —; depois: [{'duration': 4, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `n_hora_do_arauto`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 33 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 70.0; teste `91 > 70.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `status`; MP debitado 140; recarga depois 6; status fear pegou
- Mudanças em quem lançou: mp 1398 → 1258; recarga Hora do Arauto — → 6
- Mudanças no adversário: efeito fear entra (dur 4, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Hora do Arauto; MP gasto 140, dano ao adversário 0.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Guarda Cruzada 1 → livre; Fortaleza Viva 3 → 2; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 52 → min(648, 52 + 12) = 64
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 52 → 64; recarga Fortaleza Viva 3 → 2; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 1 → livre; recarga Guarda Cruzada 1 → livre; efeito fear: dur 4 → 3, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 136, teto livre 512 → MP 64 → 64
- Perde a oportunidade por controle: não

**Skill Juramento da Muralha** (`juramento_da_muralha`) de SkipNhO (p2)

- Tipo `damage_reduction`, valor 45 ; alvo declarado `self` → recebe SkipNhO (p2)
- Requisito de equipamento: as duas mãos ocupadas → atendido: True
- Custo 136 MP; reserva feita no lock 136; MP disponível na cobrança (livre + reserva liberada) 200
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)

- Resultado da skill: `buff`; MP debitado 136; recarga depois 6; buff gravado {'stat': 'damage_reduction', 'value': 45, 'duration': 4}
- Mudanças em quem lançou: mp 200 → 64; recarga Juramento da Muralha — → 6; buff Juramento da Muralha entra (damage_reduction 45, dur 4)
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): SkipNhO (p2) executou Juramento da Muralha; MP gasto 136, dano ao adversário 0.

### 7.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2931/4477 | 3098/5004 |
| MP | 1258/1694 | 64/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Bola de Fogo 1, Hora do Arauto 6 | Fortaleza Viva 2, Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Hora do Arauto — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- SkipNhO (p2): Juramento da Muralha — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 8

### 8.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2931/4477 | 3098/5004 |
| MP | 1258/1694 | 64/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Bola de Fogo 1, Hora do Arauto 6 | Fortaleza Viva 2, Golpe Poderoso 1, Juramento da Muralha 6 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 4) |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

### 8.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 8): eu HP 2931/4477, MP 1258/1694, efeitos —, buffs —; adversário SkipNhO HP 3098/5004, MP 64/648, efeitos ['fear'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 5, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Prisma de Devastação, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Prisma de Devastação** — justificativa da política: primeira skill de dano legal do deck: Prisma de Devastação
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 8): eu HP 3098/5004, MP 64/648, efeitos ['fear'], buffs ['Juramento da Muralha']; adversário aspaszin HP 2931/4477, MP 1258/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 1, Golpe Poderoso 0, Juramento da Muralha 5, Guarda Cruzada 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 47

- Lock: aspaszin (p1) reserva **131 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **47 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Prisma de Devastação; SkipNhO (p2) = Golpe Poderoso

### 8.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Bola de Fogo 1 → livre; Hora do Arauto 6 → 5
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1127 → min(1694, 1127 + 53) = 1180
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1127 → 1180; recarga Bola de Fogo 1 → livre; recarga Hora do Arauto 6 → 5
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 1563 → MP 1180 → 1180
- Perde a oportunidade por controle: não

**Skill Prisma de Devastação** (`prisma_de_devastacao`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 1311
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #10** — aspaszin (p1) → SkipNhO (p2), skill `prisma_de_devastacao`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 5.096 = 4615.75296; max(1, int(666.0 × (1 + 36/100) × 5.096)) = **4615**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação -10 − ocultação 0 = 73.39024390243902 → clamp [20, 95] e int → **73**
7. Rolagem de acerto: sorteio nº 34 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 73; teste `31 > 73` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 35 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 50; teste `98 <= 50` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 505
15. Fator de defesa: 100 / (100 + 505) = 0.1652892561983471
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 88.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 4615.0 × 1.45 × 1.0 × 0.1652892561983471 = 1106.0743801652893; max(1, int(bruto)) = 1106 → int(anterior × 1.0) = 1106 → int(anterior × 0.19999999999999996) = 221
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **221**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 221
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(221)`; HP do alvo 3098 → 2877 (retirado 221)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2877 → o alvo segue vivo

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `prisma_de_devastacao`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 36 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 70.0; teste `9 > 70.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]

- Resultado da skill: `damage`; MP debitado 131; recarga depois 5
- Mudanças em quem lançou: mp 1311 → 1180; recarga Prisma de Devastação — → 5
- Mudanças no adversário: hp 3098 → 2877; df 505 → 404; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Prisma de Devastação; MP gasto 131, dano ao adversário 221.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Fortaleza Viva 2 → 1; Golpe Poderoso 1 → livre; Juramento da Muralha 6 → 5
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 17 → min(648, 17 + 12) = 29
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 17 → 29; recarga Fortaleza Viva 2 → 1; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 6 → 5; buff Juramento da Muralha dur 4 → 3; efeito fear: dur 3 → 2, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 47, teto livre 601 → MP 29 → 29
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de SkipNhO (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe aspaszin (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 47 MP; reserva feita no lock 47; MP disponível na cobrança (livre + reserva liberada) 76
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #11** — SkipNhO (p2) → aspaszin (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 576.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 576.0; × arma = 766.08; × power 2.86 = 2190.9888; max(1, int(576.0 × (1 + 33/100) × 2.86)) = **2190**
4. Bônus de arma: +33.0% → fator 1.33
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários -20 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 66.60975609756098 → clamp [20, 95] e int → **66**
7. Rolagem de acerto: sorteio nº 37 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 66; teste `11 > 66` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 38 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 0; teste `63 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.1953125 = 427.734375; max(1, int(bruto)) = 427 → int(anterior × 1.0) = 427 → int(anterior × 1.0) = 427
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **427**
20. Égide de Mana: desejado int(427 × 15 / 100) = 64; possível min(64, int(1180 × 2.0)) = 64; passa max(1, 427 − 64) = 363
21. MP da Égide: max(1, int(64 / 2.0)) = 32
22. Dano aplicado ao HP: `take_damage(363)`; HP do alvo 2931 → 2568 (retirado 363)
23. Roubo de vida: 5.0% → max(1, int(363 × 5 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 2568 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 39 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 8.0; teste `30 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 40 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **43**; chance 10.0; teste `43 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 47; recarga depois 2
- Mudanças em quem lançou: hp 2877 → 2895; mp 76 → 29; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2931 → 2568; mp 1180 → 1148

- Motor (`action_executed`): SkipNhO (p2) executou Golpe Poderoso; MP gasto 47, dano ao adversário 363.

### 8.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2568/4477 | 2895/5004 |
| MP | 1148/1694 | 29/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | Fortaleza Viva 1, Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Prisma de Devastação — executada; dano causado na rodada 221 (golpes e DoT), recebido 363; cura 0
- SkipNhO (p2): Golpe Poderoso — executada; dano causado na rodada 363 (golpes e DoT), recebido 221; cura 18


## Rodada 9

### 9.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2568/4477 | 2895/5004 |
| MP | 1148/1694 | 29/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | Fortaleza Viva 1, Juramento da Muralha 5, Golpe Poderoso 2 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 3) |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

### 9.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 9): eu HP 2568/4477, MP 1148/1694, efeitos —, buffs —; adversário SkipNhO HP 2895/5004, MP 29/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 4, Hora do Arauto 4, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Lente de Obsidiana** — justificativa da política: primeira skill de dano legal do deck: Lente de Obsidiana
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 78

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 9): eu HP 2895/5004, MP 29/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha']; adversário aspaszin HP 2568/4477, MP 1148/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 1, Juramento da Muralha 4, Guarda Cruzada 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: aspaszin (p1) reserva **78 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Lente de Obsidiana; SkipNhO (p2) = Ataque básico

### 9.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 404.0 | 299.0 | 1.351170568561873 | 1.1623986272195408 |

- Soma das seis raízes (`math.fsum`): 5.89838215396206
- ÷ 6 = build 0.98306369232701
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.98306369232701 × 0.995 = 0.9781483738653749**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9781483738653749 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 5 → 4; Prisma de Devastação 5 → 4
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1070 → min(1694, 1070 + 53) = 1123
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1070 → 1123; recarga Hora do Arauto 5 → 4; recarga Prisma de Devastação 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 78, teto livre 1616 → MP 1123 → 1123
- Perde a oportunidade por controle: não

**Skill Lente de Obsidiana** (`lente_de_obsidiana`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 78 MP; reserva feita no lock 78; MP disponível na cobrança (livre + reserva liberada) 1201
- Recarga antes do uso: 0; declarada 3 (o motor grava declarada + 1)

**Golpe #12** — aspaszin (p1) → SkipNhO (p2), skill `lente_de_obsidiana`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 4.29 = 3885.7103999999995; max(1, int(666.0 × (1 + 36/100) × 4.29)) = **3885**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 15 − ocultação 0 = 98.39024390243902 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 41 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 95; teste `14 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 42 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 50; teste `31 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 404
15. Fator de defesa: 100 / (100 + 404) = 0.1984126984126984
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 88.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3885.0 × 1.0 × 2.5 × 0.1984126984126984 = 1927.0833333333333; max(1, int(bruto)) = 1927 → int(anterior × 1.0) = 1927 → int(anterior × 0.19999999999999996) = 385
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **385**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 385
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(385)`; HP do alvo 2895 → 2510 (retirado 385)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2510 → o alvo segue vivo

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `lente_de_obsidiana`)

- Chance base 55%; resistência do alvo 0.0% → efetiva 55 × (1 − 0/100) = 55.0%
- sorteio nº 43 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 55.0; teste `88 > 55.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]

- Resultado da skill: `damage`; MP debitado 78; recarga depois 4
- Mudanças em quem lançou: mp 1201 → 1123; recarga Lente de Obsidiana — → 4
- Mudanças no adversário: hp 2895 → 2510

- Motor (`action_executed`): aspaszin (p1) executou Lente de Obsidiana; MP gasto 78, dano ao adversário 385.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Fortaleza Viva 1 → livre; Juramento da Muralha 5 → 4; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 29 → min(648, 29 + 12) = 41
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 29 → 41; recarga Fortaleza Viva 1 → livre; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 5 → 4; buff Juramento da Muralha dur 3 → 2; efeito fear: dur 2 → 1, stacks 1 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 41 → 41
- Perde a oportunidade por controle: não

**Golpe #13** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários -20 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 66.60975609756098 → clamp [20, 95] e int → **66**
7. Rolagem de acerto: sorteio nº 44 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 66; teste `56 > 66` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 45 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **49**; chance 0; teste `49 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1258.0 × 1.0 × 1.0 × 0.1953125 = 245.703125; max(1, int(bruto)) = 245 → int(anterior × 1.0) = 245 → int(anterior × 1.0) = 245
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **245**
20. Égide de Mana: desejado int(245 × 15 / 100) = 36; possível min(36, int(1123 × 2.0)) = 36; passa max(1, 245 − 36) = 209
21. MP da Égide: max(1, int(36 / 2.0)) = 18
22. Dano aplicado ao HP: `take_damage(209)`; HP do alvo 2568 → 2359 (retirado 209)
23. Roubo de vida: 5.0% → max(1, int(209 × 5 / 100)) = 10; HP do atacante +10 (teto do HP máximo)
24. Morte e death_ignore: HP final 2359 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 46 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **49**; chance 8.0; teste `49 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 47 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 10.0; teste `97 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 209.

### 9.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2359/4477 | 2520/5004 |
| MP | 1105/1694 | 41/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 4, Prisma de Devastação 4, Lente de Obsidiana 4 | Juramento da Muralha 4, Golpe Poderoso 1 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | fear (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Lente de Obsidiana — executada; dano causado na rodada 385 (golpes e DoT), recebido 209; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 209 (golpes e DoT), recebido 385; cura 10


## Rodada 10

### 10.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2359/4477 | 2520/5004 |
| MP | 1105/1694 | 41/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Hora do Arauto 4, Prisma de Devastação 4, Lente de Obsidiana 4 | Juramento da Muralha 4, Golpe Poderoso 1 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 2) |
| Efeitos | — | fear (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

### 10.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 10): eu HP 2359/4477, MP 1105/1694, efeitos —, buffs —; adversário SkipNhO HP 2520/5004, MP 41/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 3, Hora do Arauto 3, Lente de Obsidiana 3, Bola de Fogo 0
- Ações legais: Ataque básico, Bola de Fogo, Rendição
- Escolha: **Bola de Fogo** — justificativa da política: primeira skill de dano legal do deck: Bola de Fogo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 65

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 10): eu HP 2520/5004, MP 41/648, efeitos ['fear', 'vulnerable'], buffs ['Juramento da Muralha']; adversário aspaszin HP 2359/4477, MP 1105/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 3, Guarda Cruzada 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: aspaszin (p1) reserva **65 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Bola de Fogo; SkipNhO (p2) = Ataque básico

### 10.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 404.0 | 299.0 | 1.351170568561873 | 1.1623986272195408 |

- Soma das seis raízes (`math.fsum`): 5.89838215396206
- ÷ 6 = build 0.98306369232701
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.98306369232701 × 0.995 = 0.9781483738653749**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9781483738653749 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 4 → 3; Prisma de Devastação 4 → 3; Lente de Obsidiana 4 → 3
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1040 → min(1694, 1040 + 53) = 1093
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1040 → 1093; recarga Lente de Obsidiana 4 → 3; recarga Hora do Arauto 4 → 3; recarga Prisma de Devastação 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 65, teto livre 1629 → MP 1093 → 1093
- Perde a oportunidade por controle: não

**Skill Bola de Fogo** (`bola_fogo`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 65 MP; reserva feita no lock 65; MP disponível na cobrança (livre + reserva liberada) 1158
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #14** — aspaszin (p1) → SkipNhO (p2), skill `bola_fogo`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 3.485 = 3156.5735999999993; max(1, int(666.0 × (1 + 36/100) × 3.485)) = **3156**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 48 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **75**; chance 83; teste `75 > 83` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 49 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 50; teste `34 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 404
15. Fator de defesa: 100 / (100 + 404) = 0.1984126984126984
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.19999999999999996 (damage_reduction 88.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3156.0 × 1.45 × 2.5 × 0.1984126984126984 = 2269.940476190476; max(1, int(bruto)) = 2269 → int(anterior × 1.0) = 2269 → int(anterior × 0.19999999999999996) = 453
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **453**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 453
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(453)`; HP do alvo 2520 → 2067 (retirado 453)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 2067 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 65; recarga depois 2
- Mudanças em quem lançou: mp 1158 → 1093; recarga Bola de Fogo — → 2
- Mudanças no adversário: hp 2520 → 2067

- Motor (`action_executed`): aspaszin (p1) executou Bola de Fogo; MP gasto 65, dano ao adversário 453.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 4 → 3; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 41 → min(648, 41 + 12) = 53
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['fear', 'vulnerable'], leis —, pula a vez: False
- Mudanças de estado no início: mp 41 → 53; df 404 → 505; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 4 → 3; buff Juramento da Muralha dur 2 → 1; efeito fear sai; efeito vulnerable sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 53 → 53
- Perde a oportunidade por controle: não

**Golpe #15** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 50 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 86; teste `55 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 51 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **93**; chance 0; teste `93 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1258.0 × 1.0 × 1.0 × 0.1953125 = 245.703125; max(1, int(bruto)) = 245 → int(anterior × 1.0) = 245 → int(anterior × 1.0) = 245
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **245**
20. Égide de Mana: desejado int(245 × 15 / 100) = 36; possível min(36, int(1093 × 2.0)) = 36; passa max(1, 245 − 36) = 209
21. MP da Égide: max(1, int(36 / 2.0)) = 18
22. Dano aplicado ao HP: `take_damage(209)`; HP do alvo 2359 → 2150 (retirado 209)
23. Roubo de vida: 5.0% → max(1, int(209 × 5 / 100)) = 10; HP do atacante +10 (teto do HP máximo)
24. Morte e death_ignore: HP final 2150 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 52 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 8.0; teste `81 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 53 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **62**; chance 10.0; teste `62 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 209.

### 10.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2150/4477 | 2077/5004 |
| MP | 1075/1694 | 53/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 3, Prisma de Devastação 3, Lente de Obsidiana 3, Bola de Fogo 2 | Juramento da Muralha 3 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Bola de Fogo — executada; dano causado na rodada 453 (golpes e DoT), recebido 209; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 209 (golpes e DoT), recebido 453; cura 10


## Rodada 11

### 11.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 2150/4477 | 2077/5004 |
| MP | 1075/1694 | 53/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 3, Prisma de Devastação 3, Lente de Obsidiana 3, Bola de Fogo 2 | Juramento da Muralha 3 |
| Buffs | — | Juramento da Muralha (damage_reduction 45, dur 1) |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 11.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 11): eu HP 2150/4477, MP 1075/1694, efeitos —, buffs —; adversário SkipNhO HP 2077/5004, MP 53/648, efeitos —, buffs ['Juramento da Muralha'].
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 2, Hora do Arauto 2, Lente de Obsidiana 2, Bola de Fogo 1
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Prisma de Devastação', 'Hora do Arauto', 'Lente de Obsidiana', 'Bola de Fogo']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 11): eu HP 2077/5004, MP 53/648, efeitos —, buffs ['Juramento da Muralha']; adversário aspaszin HP 2150/4477, MP 1075/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 2, Guarda Cruzada 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 47

- Lock: SkipNhO (p2) reserva **47 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Ataque básico; SkipNhO (p2) = Golpe Poderoso

### 11.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 3 → 2; Prisma de Devastação 3 → 2; Lente de Obsidiana 3 → 2; Bola de Fogo 2 → 1
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1075 → min(1694, 1075 + 53) = 1128
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1075 → 1128; recarga Bola de Fogo 2 → 1; recarga Lente de Obsidiana 3 → 2; recarga Hora do Arauto 3 → 2; recarga Prisma de Devastação 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1694 → MP 1128 → 1128
- Perde a oportunidade por controle: não

**Golpe #16** — aspaszin (p1) → SkipNhO (p2), ataque básico

1. Atributos ofensivos efetivos: st 395.0, mg 666.0, ag 97.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 0.3, mg 1.9, ag 0.0
3. Poder básico da ação: Σ = 1383.8999999999999; dano médio max(1, int(1383.8999999999999 × (1 + 36/100))) = 1882; BASE do básico = max(1, int(1882 × 0.9)) = **1693** (multiplicador do básico 0.9)
4. Bônus de arma: +36.0% → fator 1.3599999999999999 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 54 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 83; teste `94 > 83` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 2077 → 2077)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): aspaszin (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 3 → 2
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 6 → min(648, 6 + 12) = 18
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 6 → 18; recarga Juramento da Muralha 3 → 2; buff Juramento da Muralha expira
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 47, teto livre 601 → MP 18 → 18
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de SkipNhO (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe aspaszin (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 47 MP; reserva feita no lock 47; MP disponível na cobrança (livre + reserva liberada) 65
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #17** — SkipNhO (p2) → aspaszin (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 576.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 576.0; × arma = 766.08; × power 2.86 = 2190.9888; max(1, int(576.0 × (1 + 33/100) × 2.86)) = **2190**
4. Bônus de arma: +33.0% → fator 1.33
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 55 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **69**; chance 86; teste `69 > 86` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 56 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 0; teste `94 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.1953125 = 427.734375; max(1, int(bruto)) = 427 → int(anterior × 1.0) = 427 → int(anterior × 1.0) = 427
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **427**
20. Égide de Mana: desejado int(427 × 15 / 100) = 64; possível min(64, int(1128 × 2.0)) = 64; passa max(1, 427 − 64) = 363
21. MP da Égide: max(1, int(64 / 2.0)) = 32
22. Dano aplicado ao HP: `take_damage(363)`; HP do alvo 2150 → 1787 (retirado 363)
23. Roubo de vida: 5.0% → max(1, int(363 × 5 / 100)) = 18; HP do atacante +18 (teto do HP máximo)
24. Morte e death_ignore: HP final 1787 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 57 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **66**; chance 8.0; teste `66 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 58 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 10.0; teste `71 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 47; recarga depois 2
- Mudanças em quem lançou: hp 2077 → 2095; mp 65 → 18; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2150 → 1787; mp 1128 → 1096

- Motor (`action_executed`): SkipNhO (p2) executou Golpe Poderoso; MP gasto 47, dano ao adversário 363.

### 11.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1787/4477 | 2095/5004 |
| MP | 1096/1694 | 18/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 2, Prisma de Devastação 2, Lente de Obsidiana 2, Bola de Fogo 1 | Juramento da Muralha 2, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 363; cura 0
- SkipNhO (p2): Golpe Poderoso — executada; dano causado na rodada 363 (golpes e DoT), recebido 0; cura 18


## Rodada 12

### 12.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1787/4477 | 2095/5004 |
| MP | 1096/1694 | 18/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 2, Prisma de Devastação 2, Lente de Obsidiana 2, Bola de Fogo 1 | Juramento da Muralha 2, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 12.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 12): eu HP 1787/4477, MP 1096/1694, efeitos —, buffs —; adversário SkipNhO HP 2095/5004, MP 18/648, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 1, Hora do Arauto 1, Lente de Obsidiana 1, Bola de Fogo 0
- Ações legais: Ataque básico, Bola de Fogo, Rendição
- Escolha: **Bola de Fogo** — justificativa da política: primeira skill de dano legal do deck: Bola de Fogo
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 65

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 12): eu HP 2095/5004, MP 18/648, efeitos —, buffs —; adversário aspaszin HP 1787/4477, MP 1096/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 1, Juramento da Muralha 1, Guarda Cruzada 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: aspaszin (p1) reserva **65 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Bola de Fogo; SkipNhO (p2) = Ataque básico

### 12.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 2 → 1; Prisma de Devastação 2 → 1; Lente de Obsidiana 2 → 1; Bola de Fogo 1 → livre
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 1031 → min(1694, 1031 + 53) = 1084
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1031 → 1084; recarga Bola de Fogo 1 → livre; recarga Lente de Obsidiana 2 → 1; recarga Hora do Arauto 2 → 1; recarga Prisma de Devastação 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 65, teto livre 1629 → MP 1084 → 1084
- Perde a oportunidade por controle: não

**Skill Bola de Fogo** (`bola_fogo`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 65 MP; reserva feita no lock 65; MP disponível na cobrança (livre + reserva liberada) 1149
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #18** — aspaszin (p1) → SkipNhO (p2), skill `bola_fogo`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 3.485 = 3156.5735999999993; max(1, int(666.0 × (1 + 36/100) × 3.485)) = **3156**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 83.39024390243902 → clamp [20, 95] e int → **83**
7. Rolagem de acerto: sorteio nº 59 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 83; teste `60 > 83` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 60 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **17**; chance 50; teste `17 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 505
15. Fator de defesa: 100 / (100 + 505) = 0.1652892561983471
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.5700000000000001 (damage_reduction 43.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3156.0 × 1.0 × 2.5 × 0.1652892561983471 = 1304.1322314049587; max(1, int(bruto)) = 1304 → int(anterior × 1.0) = 1304 → int(anterior × 0.5700000000000001) = 743
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **743**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 743
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(743)`; HP do alvo 2095 → 1352 (retirado 743)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 1352 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 65; recarga depois 2
- Mudanças em quem lançou: mp 1149 → 1084; recarga Bola de Fogo — → 2
- Mudanças no adversário: hp 2095 → 1352

- Motor (`action_executed`): aspaszin (p1) executou Bola de Fogo; MP gasto 65, dano ao adversário 743.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 2 → 1; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 18 → min(648, 18 + 12) = 30
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 18 → 30; recarga Golpe Poderoso 2 → 1; recarga Juramento da Muralha 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 30 → 30
- Perde a oportunidade por controle: não

**Golpe #19** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 86.60975609756098 → clamp [20, 95] e int → **86**
7. Rolagem de acerto: sorteio nº 61 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 86; teste `87 > 86` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 1787 → 1787)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 12.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1787/4477 | 1352/5004 |
| MP | 1084/1694 | 30/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 1, Prisma de Devastação 1, Lente de Obsidiana 1, Bola de Fogo 2 | Juramento da Muralha 1, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Bola de Fogo — executada; dano causado na rodada 743 (golpes e DoT), recebido 0; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 743; cura 0


## Rodada 13

### 13.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1787/4477 | 1352/5004 |
| MP | 1084/1694 | 30/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 505 |
| Recargas (contador interno) | Hora do Arauto 1, Prisma de Devastação 1, Lente de Obsidiana 1, Bola de Fogo 2 | Juramento da Muralha 1, Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 13.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 13): eu HP 1787/4477, MP 1084/1694, efeitos —, buffs —; adversário SkipNhO HP 1352/5004, MP 30/648, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 0, Lente de Obsidiana 0, Bola de Fogo 1
- Ações legais: Ataque básico, Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Rendição
- Escolha: **Hora do Arauto** — justificativa da política: Hora do Arauto aplica fear, que o adversário não carrega (efeitos visíveis: [])
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 140

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 13): eu HP 1352/5004, MP 30/648, efeitos —, buffs —; adversário aspaszin HP 1787/4477, MP 1084/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 0, Guarda Cruzada 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: aspaszin (p1) reserva **140 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Hora do Arauto; SkipNhO (p2) = Ataque básico

### 13.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 505.0 | 299.0 | 1.6889632107023411 | 1.2996011737076651 |

- Soma das seis raízes (`math.fsum`): 6.035584700450184
- ÷ 6 = build 1.005930783408364
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 1.005930783408364 × 0.995 = 1.0009011294913222**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 1.0009011294913222 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 1 → livre; Prisma de Devastação 1 → livre; Lente de Obsidiana 1 → livre; Bola de Fogo 2 → 1
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 944 → min(1694, 944 + 53) = 997
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 944 → 997; recarga Bola de Fogo 2 → 1; recarga Lente de Obsidiana 1 → livre; recarga Hora do Arauto 1 → livre; recarga Prisma de Devastação 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 140, teto livre 1554 → MP 997 → 997
- Perde a oportunidade por controle: não

**Skill Hora do Arauto** (`n_hora_do_arauto`) de aspaszin (p1)

- Tipo `status`, valor fear ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 140 MP; reserva feita no lock 140; MP disponível na cobrança (livre + reserva liberada) 1137
- Recarga antes do uso: 0; declarada 5 (o motor grava declarada + 1)
- Status: chance base 85%, duração declarada 4

**Status `fear`** sobre SkipNhO (p2) (via `apply_skill`, fonte `n_hora_do_arauto`)

- Chance base 85%; resistência do alvo 0.0% → efetiva 85 × (1 − 0/100) = 85.0%
- sorteio nº 62 [aplicação de status (fear)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 85.0; teste `79 > 85.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 4 → após leis (nenhuma) 4; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `fear` no alvo antes: —; depois: [{'duration': 4, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `n_hora_do_arauto`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 63 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 70.0; teste `56 > 70.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: —; depois: [{'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]

- Resultado da skill: `status`; MP debitado 140; recarga depois 6; status fear pegou
- Mudanças em quem lançou: mp 1137 → 997; recarga Hora do Arauto — → 6
- Mudanças no adversário: df 505 → 404; efeito fear entra (dur 4, stacks 1, int 20.0); efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Hora do Arauto; MP gasto 140, dano ao adversário 0.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Juramento da Muralha 1 → livre; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 30 → min(648, 30 + 12) = 42
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 30 → 42; recarga Golpe Poderoso 1 → livre; recarga Juramento da Muralha 1 → livre; efeito fear: dur 4 → 3, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 42 → 42
- Perde a oportunidade por controle: não

**Golpe #20** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários -20 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 66.60975609756098 → clamp [20, 95] e int → **66**
7. Rolagem de acerto: sorteio nº 64 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **6**; chance 66; teste `6 > 66` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 65 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **13**; chance 0; teste `13 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1258.0 × 1.0 × 1.0 × 0.1953125 = 245.703125; max(1, int(bruto)) = 245 → int(anterior × 1.0) = 245 → int(anterior × 1.0) = 245
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **245**
20. Égide de Mana: desejado int(245 × 15 / 100) = 36; possível min(36, int(997 × 2.0)) = 36; passa max(1, 245 − 36) = 209
21. MP da Égide: max(1, int(36 / 2.0)) = 18
22. Dano aplicado ao HP: `take_damage(209)`; HP do alvo 1787 → 1578 (retirado 209)
23. Roubo de vida: 5.0% → max(1, int(209 × 5 / 100)) = 10; HP do atacante +10 (teto do HP máximo)
24. Morte e death_ignore: HP final 1578 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 66 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 8.0; teste `14 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 67 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 10.0; teste `97 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 209.

### 13.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1578/4477 | 1362/5004 |
| MP | 979/1694 | 42/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Bola de Fogo 1, Hora do Arauto 6 | — |
| Buffs | — | — |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Hora do Arauto — executada; dano causado na rodada 0 (golpes e DoT), recebido 209; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 209 (golpes e DoT), recebido 0; cura 10


## Rodada 14

### 14.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1578/4477 | 1362/5004 |
| MP | 979/1694 | 42/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 404 |
| Recargas (contador interno) | Bola de Fogo 1, Hora do Arauto 6 | — |
| Buffs | — | — |
| Efeitos | — | fear (dur 3, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto) |
| death_ignore gasto / vivo | False / True | False / True |

### 14.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 14): eu HP 1578/4477, MP 979/1694, efeitos —, buffs —; adversário SkipNhO HP 1362/5004, MP 42/648, efeitos ['fear', 'vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 0, Hora do Arauto 5, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Prisma de Devastação, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Prisma de Devastação** — justificativa da política: primeira skill de dano legal do deck: Prisma de Devastação
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 131

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 14): eu HP 1362/5004, MP 42/648, efeitos ['fear', 'vulnerable'], buffs —; adversário aspaszin HP 1578/4477, MP 979/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 0, Guarda Cruzada 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: nenhuma skill útil e legal (fora: ['Fortaleza Viva', 'Golpe Poderoso', 'Juramento da Muralha', 'Guarda Cruzada']); ataque básico
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: aspaszin (p1) reserva **131 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Prisma de Devastação; SkipNhO (p2) = Ataque básico

### 14.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 404.0 | 299.0 | 1.351170568561873 | 1.1623986272195408 |

- Soma das seis raízes (`math.fsum`): 5.89838215396206
- ÷ 6 = build 0.98306369232701
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.98306369232701 × 0.995 = 0.9781483738653749**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9781483738653749 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Bola de Fogo 1 → livre; Hora do Arauto 6 → 5
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 848 → min(1694, 848 + 53) = 901
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 848 → 901; recarga Bola de Fogo 1 → livre; recarga Hora do Arauto 6 → 5
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 131, teto livre 1563 → MP 901 → 901
- Perde a oportunidade por controle: não

**Skill Prisma de Devastação** (`prisma_de_devastacao`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 131 MP; reserva feita no lock 131; MP disponível na cobrança (livre + reserva liberada) 1032
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)

**Golpe #21** — aspaszin (p1) → SkipNhO (p2), skill `prisma_de_devastacao`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 5.096 = 4615.75296; max(1, int(666.0 × (1 + 36/100) × 5.096)) = **4615**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_afflicted` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação -10 − ocultação 0 = 73.39024390243902 → clamp [20, 95] e int → **73**
7. Rolagem de acerto: sorteio nº 68 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **24**; chance 73; teste `24 > 73` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 69 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **57**; chance 50; teste `57 <= 50` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_afflicted) 0.45 → 1 + Σ = 1.45
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 404
15. Fator de defesa: 100 / (100 + 404) = 0.1984126984126984
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.5700000000000001 (damage_reduction 43.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 4615.0 × 1.45 × 1.0 × 0.1984126984126984 = 1327.7281746031745; max(1, int(bruto)) = 1327 → int(anterior × 1.0) = 1327 → int(anterior × 0.5700000000000001) = 756
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **756**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 756
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(756)`; HP do alvo 1362 → 606 (retirado 756)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final 606 → o alvo segue vivo

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `prisma_de_devastacao`)

- Chance base 70%; resistência do alvo 0.0% → efetiva 70 × (1 − 0/100) = 70.0%
- sorteio nº 70 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 70.0; teste `54 > 70.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 3 → após leis (nenhuma) 3; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `vulnerable` no alvo antes: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}]; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 3, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]

- Resultado da skill: `damage`; MP debitado 131; recarga depois 5
- Mudanças em quem lançou: mp 1032 → 901; recarga Prisma de Devastação — → 5
- Mudanças no adversário: hp 1362 → 606; df 404 → 303; efeito vulnerable entra (dur 3, stacks 1, int 20.0)

- Motor (`action_executed`): aspaszin (p1) executou Prisma de Devastação; MP gasto 131, dano ao adversário 756.

### Oportunidade de SkipNhO (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 648 × 2 / 100) = 12.96; + mana_regen 0.0 → int(0 + 12.96) = **12**; MP livre 42 → min(648, 42 + 12) = 54
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 42 → 54; efeito fear: dur 3 → 2, stacks 1 → 1; efeito vulnerable: dur 2 → 1, stacks 1 → 1; efeito vulnerable: dur 3 → 2, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 648 → MP 54 → 54
- Perde a oportunidade por controle: não

**Golpe #22** — SkipNhO (p2) → aspaszin (p1), ataque básico

1. Atributos ofensivos efetivos: st 576.0, mg 324.0, ag 108.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1051.2; dano médio max(1, int(1051.2 × (1 + 33/100))) = 1398; BASE do básico = max(1, int(1398 × 0.9)) = **1258** (multiplicador do básico 0.9)
4. Bônus de arma: +33.0% → fator 1.33 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 1.6097560975609757 (30 × (108 − 97) / 205) − evasão 0.0 + medo/precisão temporários -20 + precisão 0.0 + modificador da ação 0 − ocultação 0 = 66.60975609756098 → clamp [20, 95] e int → **66**
7. Rolagem de acerto: sorteio nº 71 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **13**; chance 66; teste `13 > 66` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 0 = 0, teto 75 → **0**
9. Rolagem de crítico: sorteio nº 72 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 0; teste `50 <= 0` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 412
15. Fator de defesa: 100 / (100 + 412) = 0.1953125
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 1.0 (damage_reduction 0.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1258.0 × 1.0 × 1.0 × 0.1953125 = 245.703125; max(1, int(bruto)) = 245 → int(anterior × 1.0) = 245 → int(anterior × 1.0) = 245
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **245**
20. Égide de Mana: desejado int(245 × 15 / 100) = 36; possível min(36, int(901 × 2.0)) = 36; passa max(1, 245 − 36) = 209
21. MP da Égide: max(1, int(36 / 2.0)) = 18
22. Dano aplicado ao HP: `take_damage(209)`; HP do alvo 1578 → 1369 (retirado 209)
23. Roubo de vida: 5.0% → max(1, int(209 × 5 / 100)) = 10; HP do atacante +10 (teto do HP máximo)
24. Morte e death_ignore: HP final 1369 → o alvo segue vivo

**Status `stun`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 8%; resistência do alvo 0.0% → efetiva 8 × (1 − 0/100) = 8.0%
- sorteio nº 73 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 8.0; teste `30 > 8.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `bleed`** sobre aspaszin (p1) (via `_aplicar_procs_on_hit`, fonte `SkipNhO`)

- Chance base 10%; resistência do alvo 0.0% → efetiva 10 × (1 − 0/100) = 10.0%
- sorteio nº 74 [aplicação de status (bleed)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **33**; chance 10.0; teste `33 > 10.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `bleed` no alvo antes: —; depois: —

- Motor (`action_executed`): SkipNhO (p2) executou Ataque básico; MP gasto 0, dano ao adversário 209.

### 14.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1369/4477 | 616/5004 |
| MP | 883/1694 | 54/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | — |
| Buffs | — | — |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Prisma de Devastação — executada; dano causado na rodada 756 (golpes e DoT), recebido 209; cura 0
- SkipNhO (p2): Ataque básico — executada; dano causado na rodada 209 (golpes e DoT), recebido 756; cura 10


## Rodada 15

### 15.0 Estado no início da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1369/4477 | 616/5004 |
| MP | 883/1694 | 54/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 5, Prisma de Devastação 5 | — |
| Buffs | — | — |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / True |

### 15.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**aspaszin (p1)**

- Estado recebido (`DuelView`, rodada 15): eu HP 1369/4477, MP 883/1694, efeitos —, buffs —; adversário SkipNhO HP 616/5004, MP 54/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Prisma de Devastação 4, Hora do Arauto 4, Lente de Obsidiana 0, Bola de Fogo 0
- Ações legais: Ataque básico, Lente de Obsidiana, Bola de Fogo, Rendição
- Escolha: **Lente de Obsidiana** — justificativa da política: primeira skill de dano legal do deck: Lente de Obsidiana
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 78

**SkipNhO (p2)**

- Estado recebido (`DuelView`, rodada 15): eu HP 616/5004, MP 54/648, efeitos ['fear', 'vulnerable', 'vulnerable'], buffs —; adversário aspaszin HP 1369/4477, MP 883/1694, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Fortaleza Viva 0, Golpe Poderoso 0, Juramento da Muralha 0, Guarda Cruzada 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: primeira skill de dano legal do deck: Golpe Poderoso
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 47

- Lock: aspaszin (p1) reserva **78 MP** (sai do caixa livre agora).
- Lock: SkipNhO (p2) reserva **47 MP** (sai do caixa livre agora).
- Ações travadas: aspaszin (p1) = Lente de Obsidiana; SkipNhO (p2) = Golpe Poderoso

### 15.2 Initiative Score

**aspaszin (p1)** — nível próprio 23, adversário 22; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 4477.0 | 4533.333333333333 | 0.9875735294117648 | 0.9937673416910846 |
| mp | 1694.0 | 1169.6666666666667 | 1.4482758620689655 | 1.203443335628631 |
| st | 395.0 | 512.3333333333334 | 0.770982433311646 | 0.8780560536273558 |
| mg | 666.0 | 459.6666666666667 | 1.4488759970993472 | 1.2036926505962173 |
| ag | 97.0 | 177.66666666666666 | 0.5459662288930582 | 0.7388952759986074 |
| df | 412.0 | 335.0 | 1.2298507462686568 | 1.1089863598208305 |

- Soma das seis raízes (`math.fsum`): 6.126841017362727
- ÷ 6 = build 1.0211401695604545
- Δnível = 1; Δ × 0.005 = 0.005, limitado a ±0.1 → modificador 1.005
- **Score = 1.0211401695604545 × 1.005 = 1.0262458704082567**
- AG relativa (desempate): 97.0 / 177.66666666666666 = 0.5459662288930582

**SkipNhO (p2)** — nível próprio 22, adversário 23; referências globais `foundation_reference(22)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5004.0 | 4047.6666666666665 | 1.2362678086140164 | 1.1118758062904401 |
| mp | 648.0 | 1044.3333333333333 | 0.6204915416533674 | 0.7877128548229789 |
| st | 576.0 | 457.3333333333333 | 1.2594752186588922 | 1.1222634354993895 |
| mg | 324.0 | 410.6666666666667 | 0.788961038961039 | 0.8882347881956881 |
| ag | 108.0 | 158.33333333333334 | 0.6821052631578947 | 0.8258966419340223 |
| df | 303.0 | 299.0 | 1.0133779264214047 | 1.00666674049628 |

- Soma das seis raízes (`math.fsum`): 5.742650267238799
- ÷ 6 = build 0.9571083778731332
- Δnível = -1; Δ × 0.005 = -0.005, limitado a ±0.1 → modificador 0.995
- **Score = 0.9571083778731332 × 0.995 = 0.9523228359837675**
- AG relativa (desempate): 108.0 / 158.33333333333334 = 0.6821052631578947

- Comparação: score p1 1.0262458704082567 > score p2 0.9523228359837675 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: aspaszin (p1) → SkipNhO (p2) (`score`).

- **Ordem travada**: aspaszin (p1) → SkipNhO (p2) (critério `score`).

### Oportunidade de aspaszin (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Hora do Arauto 5 → 4; Prisma de Devastação 5 → 4
- Regeneração de MP: max(1, 1694 × 2 / 100) = 33.88; + mana_regen 20.0 → int(20 + 33.88) = **53**; MP livre 805 → min(1694, 805 + 53) = 858
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 805 → 858; recarga Hora do Arauto 5 → 4; recarga Prisma de Devastação 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 78, teto livre 1616 → MP 858 → 858
- Perde a oportunidade por controle: não

**Skill Lente de Obsidiana** (`lente_de_obsidiana`) de aspaszin (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe SkipNhO (p2)
- Requisito de equipamento: um cajado → atendido: True
- Custo 78 MP; reserva feita no lock 78; MP disponível na cobrança (livre + reserva liberada) 936
- Recarga antes do uso: 0; declarada 3 (o motor grava declarada + 1)

**Golpe #23** — aspaszin (p1) → SkipNhO (p2), skill `lente_de_obsidiana`

1. Atributos ofensivos efetivos: mg 666.0
2. Pesos (da carta): mg 1.0
3. Poder básico da ação: Σ = 666.0; × arma = 905.7599999999999; × power 4.29 = 3885.7103999999995; max(1, int(666.0 × (1 + 36/100) × 4.29)) = **3885**
4. Bônus de arma: +36.0% → fator 1.3599999999999999
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -1.6097560975609757 (30 × (97 − 108) / 205) − evasão 0.0 + medo/precisão temporários 0 + precisão 0.0 + modificador da ação 15 − ocultação 0 = 98.39024390243902 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 75 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 95; teste `94 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 50 = 50, teto 75 → **50**
9. Rolagem de crítico: sorteio nº 76 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **21**; chance 50; teste `21 <= 50` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 100/100 = 2.5
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×2.5
13. Produto ×MULT bruto 2.5; `XMULT_CAP` 5.0 → aplicado 2.5
14. Defesa efetiva do alvo: 303
15. Fator de defesa: 100 / (100 + 303) = 0.24813895781637718
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.5700000000000001 (damage_reduction 43.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 3885.0 × 1.0 × 2.5 × 0.24813895781637718 = 2410.0496277915636; max(1, int(bruto)) = 2410 → int(anterior × 1.0) = 2410 → int(anterior × 0.5700000000000001) = 1373
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **1373**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 1373
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(1373)`; HP do alvo 616 → -757 (retirado 1373)
23. Roubo de vida: 0% no atacante — inaplicável
24. Morte e death_ignore: HP final -757 → o alvo morreu

**Status `vulnerable`** sobre SkipNhO (p2) (via `_aplicar_secundario`, fonte `lente_de_obsidiana`)

- Chance base 55%; resistência do alvo 0.0% → efetiva 55 × (1 − 0/100) = 55.0%
- sorteio nº 77 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **96**; chance 55.0; teste `96 > 55.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]; depois: [{'duration': 1, 'stacks': 1, 'intensity': 20.0, 'source_id': 'n_hora_do_arauto'}, {'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'prisma_de_devastacao'}]

- Resultado da skill: `damage`; MP debitado 78; recarga depois 4
- Mudanças em quem lançou: mp 936 → 858; recarga Lente de Obsidiana — → 4
- Mudanças no adversário: hp 616 → -757; morreu

- Motor (`action_executed`): aspaszin (p1) executou Lente de Obsidiana; MP gasto 78, dano ao adversário 1373.

- **Fim do duelo**: vence aspaszin (p1), motivo `ko`.

- Devolução: SkipNhO (p2) recebe de volta 47 MP reservados.
- Ação de SkipNhO (p2) **cancelada por morte**.
### 15.9 Estado ao final da rodada

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| HP | 1369/4477 | -757/5004 |
| MP | 858/1694 | 54/648 |
| ST / MG / AG / DF | 395 / 666 / 97 / 412 | 576 / 324 / 108 / 303 |
| Recargas (contador interno) | Hora do Arauto 4, Prisma de Devastação 4, Lente de Obsidiana 4 | — |
| Buffs | — | — |
| Efeitos | — | fear (dur 2, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 1, stacks 1, int 20.0, fonte n_hora_do_arauto); vulnerable (dur 2, stacks 1, int 20.0, fonte prisma_de_devastacao) |
| death_ignore gasto / vivo | False / True | False / False |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- aspaszin (p1): Lente de Obsidiana — executada; dano causado na rodada 1373 (golpes e DoT), recebido 0; cura 0
- SkipNhO (p2): Golpe Poderoso — cancelada por morte; dano causado na rodada 0 (golpes e DoT), recebido 1373; cura 0


## Conclusão da final (fatos registrados)

- Campeão: **aspaszin** (p1); vice: **SkipNhO** (p2).
- Rodadas: 15. Motivo exato: `ko` — o HP de SkipNhO chegou a 0 durante a rodada 15.

| | aspaszin (p1) | SkipNhO (p2) |
|---|---|---|
| Dano causado (golpes + DoT) | 5913 (5913 + 0) | 3108 (3108 + 0) |
| HP retirado do adversário | 5913 | 3108 |
| Cura (skill + roubo) | 0 (0 + 0) | 152 (0 + 152) |
| MP consumido em ações | 1307 | 750 |
| MP consumido pela Égide | 271 | 0 |
| Skills usadas | 13: Hora do Arauto ×3, Prisma de Devastação ×3, Lente de Obsidiana ×3, Bola de Fogo ×4 | 8: Juramento da Muralha ×2, Guarda Cruzada ×1, Fortaleza Viva ×1, Golpe Poderoso ×4 |
| Ataques básicos | 2 | 6 |
| Acertos / erros | 11 / 1 | 10 / 1 |
| Críticos (dano) | 7 (4431) | 0 (0) |
| Status aplicados | fear (rodada 1), vulnerable (rodada 1), vulnerable (rodada 2), vulnerable (rodada 3), fear (rodada 7), vulnerable (rodada 8), fear (rodada 13), vulnerable (rodada 13), vulnerable (rodada 14) | — |
| Status que falharam na rolagem | vulnerable (rodada 7), vulnerable (rodada 9), vulnerable (rodada 15) | stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14) |
| Status anulados por resistência / recusados | — | — |
| Ações perdidas por controle | 0 | 0 |
| Rodadas agindo primeiro | 15 | 0 |
| HP / MP restantes | 1369/4477 · 858/1694 | -757/5004 · 54/648 |

HP negativo é o valor cru do motor: `take_damage` não corta em zero, e a sobra mostra quanto o último golpe passou do necessário.

## Todas as chamadas ao gerador

77 chamadas, igual ao contador do proxy (77).

| Nº | Rodada | Ator | Mecânica | Operação | Limites | Valor | Chance | Teste | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | p1 | aplicação de status (fear) | `randrange` | [1, 100] | 29 | 85.0 | `29 > 85.0` → F | aprovado: passou na rolagem |
| 2 | 1 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 55 | 70.0 | `55 > 70.0` → F | aprovado: passou na rolagem |
| 3 | 2 | p1 | acerto | `randrange` | [1, 100] | 47 | 73 | `47 > 73` → F | aprovado: ACERTOU |
| 4 | 2 | p1 | crítico | `randrange` | [1, 100] | 74 | 50 | `74 <= 50` → F | recusado: sem crítico |
| 5 | 2 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 9 | 70.0 | `9 > 70.0` → F | aprovado: passou na rolagem |
| 6 | 3 | p1 | acerto | `randrange` | [1, 100] | 51 | 95 | `51 > 95` → F | aprovado: ACERTOU |
| 7 | 3 | p1 | crítico | `randrange` | [1, 100] | 91 | 50 | `91 <= 50` → F | recusado: sem crítico |
| 8 | 3 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 4 | 55.0 | `4 > 55.0` → F | aprovado: passou na rolagem |
| 9 | 3 | p2 | acerto | `randrange` | [1, 100] | 10 | 51 | `10 > 51` → F | aprovado: ACERTOU |
| 10 | 3 | p2 | crítico | `randrange` | [1, 100] | 60 | 0 | `60 <= 0` → F | recusado: sem crítico |
| 11 | 3 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 16 | 8.0 | `16 > 8.0` → V | recusado: falhou na rolagem |
| 12 | 3 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 37 | 10.0 | `37 > 10.0` → V | recusado: falhou na rolagem |
| 13 | 3 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 98 | 40.0 | `98 > 40.0` → V | recusado: falhou na rolagem |
| 14 | 4 | p1 | acerto | `randrange` | [1, 100] | 3 | 83 | `3 > 83` → F | aprovado: ACERTOU |
| 15 | 4 | p1 | crítico | `randrange` | [1, 100] | 34 | 50 | `34 <= 50` → V | aprovado: CRÍTICO |
| 16 | 4 | p2 | acerto | `randrange` | [1, 100] | 73 | 86 | `73 > 86` → F | aprovado: ACERTOU |
| 17 | 4 | p2 | crítico | `randrange` | [1, 100] | 1 | 0 | `1 <= 0` → F | recusado: sem crítico |
| 18 | 4 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 26 | 8.0 | `26 > 8.0` → V | recusado: falhou na rolagem |
| 19 | 4 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 63 | 10.0 | `63 > 10.0` → V | recusado: falhou na rolagem |
| 20 | 5 | p1 | acerto | `randrange` | [1, 100] | 75 | 83 | `75 > 83` → F | aprovado: ACERTOU |
| 21 | 5 | p1 | crítico | `randrange` | [1, 100] | 18 | 50 | `18 <= 50` → V | aprovado: CRÍTICO |
| 22 | 5 | p2 | acerto | `randrange` | [1, 100] | 35 | 86 | `35 > 86` → F | aprovado: ACERTOU |
| 23 | 5 | p2 | crítico | `randrange` | [1, 100] | 64 | 0 | `64 <= 0` → F | recusado: sem crítico |
| 24 | 5 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 54 | 8.0 | `54 > 8.0` → V | recusado: falhou na rolagem |
| 25 | 5 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 96 | 10.0 | `96 > 10.0` → V | recusado: falhou na rolagem |
| 26 | 6 | p1 | acerto | `randrange` | [1, 100] | 5 | 83 | `5 > 83` → F | aprovado: ACERTOU |
| 27 | 6 | p1 | crítico | `randrange` | [1, 100] | 16 | 50 | `16 <= 50` → V | aprovado: CRÍTICO |
| 28 | 6 | p2 | acerto | `randrange` | [1, 100] | 63 | 86 | `63 > 86` → F | aprovado: ACERTOU |
| 29 | 6 | p2 | crítico | `randrange` | [1, 100] | 41 | 0 | `41 <= 0` → F | recusado: sem crítico |
| 30 | 6 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 14 | 8.0 | `14 > 8.0` → V | recusado: falhou na rolagem |
| 31 | 6 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 18 | 10.0 | `18 > 10.0` → V | recusado: falhou na rolagem |
| 32 | 7 | p1 | aplicação de status (fear) | `randrange` | [1, 100] | 22 | 85.0 | `22 > 85.0` → F | aprovado: passou na rolagem |
| 33 | 7 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 91 | 70.0 | `91 > 70.0` → V | recusado: falhou na rolagem |
| 34 | 8 | p1 | acerto | `randrange` | [1, 100] | 31 | 73 | `31 > 73` → F | aprovado: ACERTOU |
| 35 | 8 | p1 | crítico | `randrange` | [1, 100] | 98 | 50 | `98 <= 50` → F | recusado: sem crítico |
| 36 | 8 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 9 | 70.0 | `9 > 70.0` → F | aprovado: passou na rolagem |
| 37 | 8 | p2 | acerto | `randrange` | [1, 100] | 11 | 66 | `11 > 66` → F | aprovado: ACERTOU |
| 38 | 8 | p2 | crítico | `randrange` | [1, 100] | 63 | 0 | `63 <= 0` → F | recusado: sem crítico |
| 39 | 8 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 30 | 8.0 | `30 > 8.0` → V | recusado: falhou na rolagem |
| 40 | 8 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 43 | 10.0 | `43 > 10.0` → V | recusado: falhou na rolagem |
| 41 | 9 | p1 | acerto | `randrange` | [1, 100] | 14 | 95 | `14 > 95` → F | aprovado: ACERTOU |
| 42 | 9 | p1 | crítico | `randrange` | [1, 100] | 31 | 50 | `31 <= 50` → V | aprovado: CRÍTICO |
| 43 | 9 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 88 | 55.0 | `88 > 55.0` → V | recusado: falhou na rolagem |
| 44 | 9 | p2 | acerto | `randrange` | [1, 100] | 56 | 66 | `56 > 66` → F | aprovado: ACERTOU |
| 45 | 9 | p2 | crítico | `randrange` | [1, 100] | 49 | 0 | `49 <= 0` → F | recusado: sem crítico |
| 46 | 9 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 49 | 8.0 | `49 > 8.0` → V | recusado: falhou na rolagem |
| 47 | 9 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 97 | 10.0 | `97 > 10.0` → V | recusado: falhou na rolagem |
| 48 | 10 | p1 | acerto | `randrange` | [1, 100] | 75 | 83 | `75 > 83` → F | aprovado: ACERTOU |
| 49 | 10 | p1 | crítico | `randrange` | [1, 100] | 34 | 50 | `34 <= 50` → V | aprovado: CRÍTICO |
| 50 | 10 | p2 | acerto | `randrange` | [1, 100] | 55 | 86 | `55 > 86` → F | aprovado: ACERTOU |
| 51 | 10 | p2 | crítico | `randrange` | [1, 100] | 93 | 0 | `93 <= 0` → F | recusado: sem crítico |
| 52 | 10 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 81 | 8.0 | `81 > 8.0` → V | recusado: falhou na rolagem |
| 53 | 10 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 62 | 10.0 | `62 > 10.0` → V | recusado: falhou na rolagem |
| 54 | 11 | p1 | acerto | `randrange` | [1, 100] | 94 | 83 | `94 > 83` → V | recusado: ERROU |
| 55 | 11 | p2 | acerto | `randrange` | [1, 100] | 69 | 86 | `69 > 86` → F | aprovado: ACERTOU |
| 56 | 11 | p2 | crítico | `randrange` | [1, 100] | 94 | 0 | `94 <= 0` → F | recusado: sem crítico |
| 57 | 11 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 66 | 8.0 | `66 > 8.0` → V | recusado: falhou na rolagem |
| 58 | 11 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 71 | 10.0 | `71 > 10.0` → V | recusado: falhou na rolagem |
| 59 | 12 | p1 | acerto | `randrange` | [1, 100] | 60 | 83 | `60 > 83` → F | aprovado: ACERTOU |
| 60 | 12 | p1 | crítico | `randrange` | [1, 100] | 17 | 50 | `17 <= 50` → V | aprovado: CRÍTICO |
| 61 | 12 | p2 | acerto | `randrange` | [1, 100] | 87 | 86 | `87 > 86` → V | recusado: ERROU |
| 62 | 13 | p1 | aplicação de status (fear) | `randrange` | [1, 100] | 79 | 85.0 | `79 > 85.0` → F | aprovado: passou na rolagem |
| 63 | 13 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 56 | 70.0 | `56 > 70.0` → F | aprovado: passou na rolagem |
| 64 | 13 | p2 | acerto | `randrange` | [1, 100] | 6 | 66 | `6 > 66` → F | aprovado: ACERTOU |
| 65 | 13 | p2 | crítico | `randrange` | [1, 100] | 13 | 0 | `13 <= 0` → F | recusado: sem crítico |
| 66 | 13 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 14 | 8.0 | `14 > 8.0` → V | recusado: falhou na rolagem |
| 67 | 13 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 97 | 10.0 | `97 > 10.0` → V | recusado: falhou na rolagem |
| 68 | 14 | p1 | acerto | `randrange` | [1, 100] | 24 | 73 | `24 > 73` → F | aprovado: ACERTOU |
| 69 | 14 | p1 | crítico | `randrange` | [1, 100] | 57 | 50 | `57 <= 50` → F | recusado: sem crítico |
| 70 | 14 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 54 | 70.0 | `54 > 70.0` → F | aprovado: passou na rolagem |
| 71 | 14 | p2 | acerto | `randrange` | [1, 100] | 13 | 66 | `13 > 66` → F | aprovado: ACERTOU |
| 72 | 14 | p2 | crítico | `randrange` | [1, 100] | 50 | 0 | `50 <= 0` → F | recusado: sem crítico |
| 73 | 14 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 30 | 8.0 | `30 > 8.0` → V | recusado: falhou na rolagem |
| 74 | 14 | p2 | aplicação de status (bleed) | `randrange` | [1, 100] | 33 | 10.0 | `33 > 10.0` → V | recusado: falhou na rolagem |
| 75 | 15 | p1 | acerto | `randrange` | [1, 100] | 94 | 95 | `94 > 95` → F | aprovado: ACERTOU |
| 76 | 15 | p1 | crítico | `randrange` | [1, 100] | 21 | 50 | `21 <= 50` → V | aprovado: CRÍTICO |
| 77 | 15 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 96 | 55.0 | `96 > 55.0` → V | recusado: falhou na rolagem |

## Verificação de fidelidade

A final rodou duas vezes com `random.Random(3846561752997802364)`, os mesmos gladiadores (preparação nova a cada vez) e a mesma política: sem nenhuma instrumentação e auditada.

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

- **aspaszin**: 12 golpes tentados com chance média de acerto 83.5%, 11 conectaram (91.7%); dano médio por golpe conectado 537.5. O fator de defesa médio que os golpes dele enfrentaram foi 0.2029 e a mitigação de entrada do alvo, 0.3345.
- **SkipNhO**: 11 golpes tentados com chance média de acerto 75.5%, 10 conectaram (90.9%); dano médio por golpe conectado 310.8. O fator de defesa médio que os golpes dele enfrentaram foi 0.1953 e a mitigação de entrada do alvo, 1.0000.
- Iniciativa: aspaszin agiu primeiro em 15 de 15 rodadas; SkipNhO, em 0. Na rodada final, a ordem foi aspaszin → SkipNhO (`score`).
- Score de iniciativa por rodada (p1 / p2 → quem agiu primeiro):
  - Rodada 1: 1.026246 / 1.000901 → aspaszin
  - Rodada 2: 1.026246 / 0.978148 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→404
  - Rodada 3: 1.026246 / 0.952323 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→303
  - Rodada 4: 1.026246 / 0.952323 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→303
  - Rodada 5: 1.026246 / 0.978148 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→404; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Juramento da Muralha de SkipNhO, Guarda Cruzada de SkipNhO
  - Rodada 6: 1.026246 / 1.000901 → aspaszin
  - Rodada 7: 1.026246 / 1.000901 → aspaszin
  - Rodada 8: 1.026246 / 1.000901 → aspaszin
  - Rodada 9: 1.026246 / 0.978148 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→404
  - Rodada 10: 1.026246 / 0.978148 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→404
  - Rodada 11: 1.026246 / 1.000901 → aspaszin; com duração 1 no lock (conta nesta leitura e expira no início da oportunidade do dono, antes da ação): Juramento da Muralha de SkipNhO
  - Rodada 12: 1.026246 / 1.000901 → aspaszin
  - Rodada 13: 1.026246 / 1.000901 → aspaszin
  - Rodada 14: 1.026246 / 0.978148 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→404
  - Rodada 15: 1.026246 / 0.952323 → aspaszin; atributos efetivos diferentes da rodada 1 — SkipNhO: df 505→303
  - Leitura: o vetor da iniciativa usa ST/MG/AG/DF efetivos e os TETOS de HP e MP, então um buff de atributo do próprio lado e um status do adversário que reduz atributo ou teto entram na ordem da rodada seguinte; quando expiram, saem dela.
- Na última rodada, SkipNhO havia travado Golpe Poderoso (skill de tipo `damage`); a ação ficou cancelada por morte, porque aspaszin agiu antes e o golpe dele encerrou o duelo.
- Margem (estimativa, não registro): aspaszin terminou com 1369 de HP; o dano médio por golpe conectado de SkipNhO foi 310.8, ou seja, ~4.4 golpe(s) conectado(s) de distância.
- Sustentação de aspaszin: cura 0 e Égide 543 contra 3108 de dano recebido.
- Críticos de aspaszin: 7, somando 4431 de 5913 de dano de golpe (74.9%).
- Sustentação de SkipNhO: cura 152 e Égide 0 contra 5913 de dano recebido.
- Economia de ação: aspaszin usou 13 skills e 2 ataques básicos; SkipNhO, 8 e 6.

