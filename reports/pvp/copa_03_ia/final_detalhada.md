# Copa Arena 03 v2 — Inteligência Estratégica — Final detalhada: Tenz × fer

Transcrição da final a partir do trace da auditoria (`tools/arena_auditoria.py`), na ordem em que o motor executou. Cada número abaixo foi capturado no momento da execução, pela chamada real da função canônica; os recálculos que explicam um número são feitos com as mesmas funções e constantes e conferidos contra o valor devolvido pelo motor — se divergissem, a auditoria pararia com erro.

## Convenções

- Gerador da partida: `random.Random(6619800792897972838)`, observado por um proxy que delega cada chamada e anota operação, limites, valor e chamador. O proxy não sorteia nada por conta própria.
- Rolagens percentuais do motor: `randrange(1, 101)`, inteiro uniforme em [1, 100]. Não é D20. O desempate de iniciativa usa `random() < 0.5`.
- Acerto: o golpe ERRA quando `rolagem > chance`. Crítico: CRITA quando `rolagem <= chance`. Status: NÃO pega quando `rolagem > chance efetiva`.
- Floats aparecem com `repr`: a precisão total que o motor usou. Nada é arredondado antes de uma comparação.
- Referências de iniciativa: `foundation_reference(nível)` — a média das três classes pelo crescimento canônico. Níveis desta final: [23].
- Golpes de skill são resolvidos por `apply_skill` com `publish=None`; a auditoria os vê porque intercepta a função no módulo, não o EventBus.
- Limite técnico do laço: 500 rodadas (não atingido).

## Referências globais usadas

| Nível | REF_hp | REF_mp | REF_st | REF_mg | REF_ag | REF_df |
|---|---|---|---|---|---|---|
| 23 | 4533.333333333333 | 1169.6666666666667 | 512.3333333333334 | 459.6666666666667 | 177.66666666666666 | 335.0 |

## Fichas completas antes do duelo

### p1 — Tenz (Guerreiro, nível 23)

- HP 5519/5519, MP 1050/1050; ST 601, MG 406, AG 121, DF 509
- Arma: +21.0% de dano; Égide de Mana: 0%
- Equipamento: Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Cajado de Cristal; Weapon2: Espada da Vingança +1; Body: Peitoral de Cota; Legs: Perneiras de Aço; Hands: Luvas de Couro; Shoes: Sapatos de Couro; Ring1: Anel da Esmeralda +1; Ring2: Anel de Bronze +1
- Passivas: Reserva Arcana (max_mp 20), Sede Silenciosa (life_steal 8), Sangue de Guerreiro (max_hp 25), Boca de Sangue (life_steal 4), Mente Serena (max_mp 10), Sangue de Guerreiro (max_hp 25), Imortalidade Momentânea (death_ignore 1), Olho de Caçador (precision 5), Fúria Berserker (strength 8), Olho de Águia (crit_chance 5), Poço Fundo (max_mp 40), Olho de Águia (crit_chance 5), Sangue de Guerreiro (max_hp 25), Pele de Sal (status_resistance 8), Sangue de Guerreiro (max_hp 25), Bênção Divina (max_hp 70), Olho de Águia (crit_chance 5), Boca de Sangue (life_steal 4), Sangue de Guerreiro (max_hp 25), Pele de Sal (status_resistance 8), Postura Fechada (damage_reduction 3), Pele de Adamântio (damage_reduction 15)
- Modificadores de combate (funil `fx.combat_modifier`): crit_chance 15.0, crit_damage 10.0, damage_reduction 21.0, precision 5.0, life_steal 21.0, status_resistance 16.0, death_ignore 1.0

| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta | Secundário | Bônus | Requisito |
|---|---|---|---|---|---|---|---|---|---|---|
| Golpe Poderoso (`golpe_poderoso`) | damage | 0 | 52 | 1 | 2.86 × (1.0×st) | +0 | 0 | — | target_healthy +8% | — |
| Soco de Placa (`soco_de_placa`) | damage | 0 | 61 | 1 | 3.012 × (1.0×st) | +0 | 0 | weakened 35% por 2 | caster_wounded +20% | — |
| Gancho e Corda (`n_gancho_e_corda`) | status | stun 50% por 1 | 117 | 4 | 0.0 × (—) | +0 | 0 | vulnerable 60% por 3 | — | — |
| Tomar Fôlego (`tomar_folego`) | heal | 12 | 93 | 4 | 0.0 × (—) | +0 | 0 | — | — | — |

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

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5519/5519 | 5977/5977 |
| MP | 1050/1050 | 1103/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 1.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 1): eu HP 5519/5519, MP 1050/1050, efeitos —, buffs —; adversário fer HP 5977/5977, MP 1103/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.404±0.002 com Golpe Poderoso; contra Soco de Placa 0.404, ataque básico 0.403, Gancho e Corda 0.403; dano esperado 278; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 1): eu HP 5977/5977, MP 1103/1103, efeitos —, buffs —; adversário Tenz HP 5519/5519, MP 1050/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.481±0.002 com Golpe Poderoso; contra Soco de Placa 0.480, ataque básico 0.479, Juramento da Muralha 0.477; dano esperado 326; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 1.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 1051 → min(1103, 1051 + 22) = 1073
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 1051 → 1073
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 1073 → 1051
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 1103
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #1** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 1 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 95; teste `9 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 2 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 30; teste `14 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.6 × 0.16420361247947454 = 599.5507389162561; max(1, int(bruto)) = 599 → int(anterior × 1.0) = 599 → int(anterior × 0.79) = 473
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **473**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 473
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(473)`; HP do alvo 5519 → 5046 (retirado 473)
23. Roubo de vida: 13.0% → max(1, int(473 × 13 / 100)) = 61; HP do atacante +0 (teto do HP máximo)
24. Morte e death_ignore: HP final 5046 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 3 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 1.68; teste `81 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 1103 → 1051; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5519 → 5046

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 473.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 998 → min(1050, 998 + 21) = 1019
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 998 → 1019
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 1019 → 998
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 1050
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #2** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 4 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **86**; chance 72; teste `86 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 5977 → 5977)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 1050 → 998; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### 1.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5046/5519 | 5977/5977 |
| MP | 998/1050 | 1051/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 473 (golpes e DoT), recebido 0; cura 0
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 473; cura 0


## Rodada 2

### 2.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5046/5519 | 5977/5977 |
| MP | 998/1050 | 1051/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 2.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 2): eu HP 5046/5519, MP 998/1050, efeitos —, buffs —; adversário fer HP 5977/5977, MP 1051/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.292±0.002 com Tomar Fôlego; contra Soco de Placa 0.290, Gancho e Corda 0.290, ataque básico 0.288; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 2): eu HP 5977/5977, MP 1051/1103, efeitos —, buffs —; adversário Tenz HP 5046/5519, MP 998/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.559±0.008 com Soco de Placa; contra ataque básico 0.553, Juramento da Muralha 0.540, Respirar Fundo 0.528; dano esperado 360; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Soco de Placa

### 2.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 990 → min(1103, 990 + 22) = 1012
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 990 → 1012; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 1012 → 1012
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 1073
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #3** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 5 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 95; teste `30 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 6 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 30; teste `98 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 5046 → 4758 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +0 (teto do HP máximo)
24. Morte e death_ignore: HP final 4758 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 7 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 1.68; teste `44 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 8 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 29.4; teste `70 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 1073 → 1012; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 5046 → 4758

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 905 → min(1050, 905 + 21) = 926
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 905 → 926; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 926 → 926
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 1019
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 4758 → 5420; mp 1019 → 926; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 2.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5420/5519 | 5977/5977 |
| MP | 926/1050 | 1012/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 0
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 662


## Rodada 3

### 3.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5420/5519 | 5977/5977 |
| MP | 926/1050 | 1012/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 3.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 3): eu HP 5420/5519, MP 926/1050, efeitos —, buffs —; adversário fer HP 5977/5977, MP 1012/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.248±0.003 com ataque básico; contra Golpe Poderoso 0.248, Soco de Placa 0.248, Gancho e Corda 0.247; dano esperado 112
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 3): eu HP 5977/5977, MP 1012/1103, efeitos —, buffs —; adversário Tenz HP 5420/5519, MP 926/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.565±0.008 com Golpe Poderoso; contra ataque básico 0.562, Juramento da Muralha 0.537, Respirar Fundo 0.526; dano esperado 368; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 3.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 960 → min(1103, 960 + 22) = 982
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 960 → 982; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 982 → 982
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 1034
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #4** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 9 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 95; teste `71 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 10 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 30; teste `88 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.16420361247947454 = 374.7192118226601; max(1, int(bruto)) = 374 → int(anterior × 1.0) = 374 → int(anterior × 0.79) = 295
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **295**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 295
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(295)`; HP do alvo 5420 → 5125 (retirado 295)
23. Roubo de vida: 13.0% → max(1, int(295 × 13 / 100)) = 38; HP do atacante +0 (teto do HP máximo)
24. Morte e death_ignore: HP final 5125 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 11 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 1.68; teste `94 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 1034 → 982; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5420 → 5125

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 295.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 926 → min(1050, 926 + 21) = 947
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 926 → 947; recarga Golpe Poderoso 1 → livre; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 947 → 947
- Perde a oportunidade por controle: não

**Golpe #5** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 12 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 72; teste `79 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 5977 → 5977)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 3.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5125/5519 | 5977/5977 |
| MP | 947/1050 | 982/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 295 (golpes e DoT), recebido 0; cura 0
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 295; cura 0


## Rodada 4

### 4.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5125/5519 | 5977/5977 |
| MP | 947/1050 | 982/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 4.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 4): eu HP 5125/5519, MP 947/1050, efeitos —, buffs —; adversário fer HP 5977/5977, MP 982/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.202±0.002 com Golpe Poderoso; contra Soco de Placa 0.202, ataque básico 0.201, Gancho e Corda 0.201; dano esperado 180; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 4): eu HP 5977/5977, MP 982/1103, efeitos —, buffs —; adversário Tenz HP 5125/5519, MP 947/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.519±0.012 com ataque básico; contra Soco de Placa 0.518, Juramento da Muralha 0.506, Respirar Fundo 0.483; dano esperado 194
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Ataque básico

### 4.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 982 → min(1103, 982 + 22) = 1004
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 982 → 1004; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 1004 → 1004
- Perde a oportunidade por controle: não

**Golpe #6** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 13 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **17**; chance 95; teste `17 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 14 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **92**; chance 30; teste `92 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 5125 → 4964 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +0 (teto do HP máximo)
24. Morte e death_ignore: HP final 4964 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 15 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **47**; chance 1.68; teste `47 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 895 → min(1050, 895 + 21) = 916
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 895 → 916; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 916 → 916
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 968
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #7** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 16 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 72; teste `11 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 17 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 15; teste `94 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.08 × 1.0 × 0.16583747927031509 = 372.3582089552239; max(1, int(bruto)) = 372 → int(anterior × 1.0) = 372 → int(anterior × 0.89) = 331
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **331**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 331
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(331)`; HP do alvo 5977 → 5646 (retirado 331)
23. Roubo de vida: 21.0% → max(1, int(331 × 21 / 100)) = 69; HP do atacante +69 (teto do HP máximo)
24. Morte e death_ignore: HP final 5646 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4964 → 5033; mp 968 → 916; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5977 → 5646

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 331.

### 4.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5033/5519 | 5646/5977 |
| MP | 916/1050 | 1004/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 2 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 331; cura 0
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 331 (golpes e DoT), recebido 161; cura 69


## Rodada 5

### 5.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 5033/5519 | 5646/5977 |
| MP | 916/1050 | 1004/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 2 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 5.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 5): eu HP 5033/5519, MP 916/1050, efeitos —, buffs —; adversário fer HP 5646/5977, MP 1004/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.201±0.003 com Soco de Placa; contra ataque básico 0.201, Gancho e Corda 0.197; dano esperado 198; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 5): eu HP 5646/5977, MP 1004/1103, efeitos —, buffs —; adversário Tenz HP 5033/5519, MP 916/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.480±0.010 com Soco de Placa; contra Golpe Poderoso 0.479, ataque básico 0.479, Juramento da Muralha 0.469; dano esperado 324; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Soco de Placa

### 5.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 943 → min(1103, 943 + 22) = 965
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 943 → 965; recarga Golpe Poderoso 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 965 → 965
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 1026
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #8** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 18 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **72**; chance 95; teste `72 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 19 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 30; teste `20 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.6 × 0.16420361247947454 = 584.5648604269294; max(1, int(bruto)) = 584 → int(anterior × 1.0) = 584 → int(anterior × 0.79) = 461
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **461**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 461
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(461)`; HP do alvo 5033 → 4572 (retirado 461)
23. Roubo de vida: 13.0% → max(1, int(461 × 13 / 100)) = 59; HP do atacante +59 (teto do HP máximo)
24. Morte e death_ignore: HP final 4572 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 20 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **93**; chance 1.68; teste `93 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 21 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 29.4; teste `60 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 5646 → 5705; mp 1026 → 965; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 5033 → 4572

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 461.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 855 → min(1050, 855 + 21) = 876
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 855 → 876; recarga Golpe Poderoso 2 → 1; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 876 → 876
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 937
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #9** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 22 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **84**; chance 72; teste `84 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 5705 → 5705)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 937 → 876; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 5.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4572/5519 | 5705/5977 |
| MP | 876/1050 | 965/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 1, Soco de Placa 2 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 461 (golpes e DoT), recebido 0; cura 59
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 461; cura 0


## Rodada 6

### 6.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4572/5519 | 5705/5977 |
| MP | 876/1050 | 965/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 1, Soco de Placa 2 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 6.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 6): eu HP 4572/5519, MP 876/1050, efeitos —, buffs —; adversário fer HP 5705/5977, MP 965/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.173±0.003 com Golpe Poderoso; contra ataque básico 0.173, Gancho e Corda 0.170; dano esperado 203; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 6): eu HP 5705/5977, MP 965/1103, efeitos —, buffs —; adversário Tenz HP 4572/5519, MP 876/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.589±0.014 com Golpe Poderoso; contra ataque básico 0.577, Juramento da Muralha 0.549, Respirar Fundo 0.536; dano esperado 360; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 6.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 913 → min(1103, 913 + 22) = 935
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 913 → 935; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 935 → 935
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 987
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #10** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 23 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 95; teste `9 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 24 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 30; teste `50 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.16420361247947454 = 374.7192118226601; max(1, int(bruto)) = 374 → int(anterior × 1.0) = 374 → int(anterior × 0.79) = 295
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **295**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 295
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(295)`; HP do alvo 4572 → 4277 (retirado 295)
23. Roubo de vida: 13.0% → max(1, int(295 × 13 / 100)) = 38; HP do atacante +38 (teto do HP máximo)
24. Morte e death_ignore: HP final 4277 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 25 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 1.68; teste `12 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5705 → 5743; mp 987 → 935; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4572 → 4277

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 295.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 824 → min(1050, 824 + 21) = 845
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 824 → 845; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 845 → 845
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 897
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #11** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 26 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 72; teste `50 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 27 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 15; teste `89 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.08 × 1.0 × 0.16583747927031509 = 372.3582089552239; max(1, int(bruto)) = 372 → int(anterior × 1.0) = 372 → int(anterior × 0.89) = 331
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **331**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 331
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(331)`; HP do alvo 5743 → 5412 (retirado 331)
23. Roubo de vida: 21.0% → max(1, int(331 × 21 / 100)) = 69; HP do atacante +69 (teto do HP máximo)
24. Morte e death_ignore: HP final 5412 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4277 → 4346; mp 897 → 845; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5743 → 5412

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 331.

### 6.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4346/5519 | 5412/5977 |
| MP | 845/1050 | 935/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 1, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 295 (golpes e DoT), recebido 331; cura 38
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 331 (golpes e DoT), recebido 295; cura 69


## Rodada 7

### 7.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4346/5519 | 5412/5977 |
| MP | 845/1050 | 935/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 1, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 7.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 7): eu HP 4346/5519, MP 845/1050, efeitos —, buffs —; adversário fer HP 5412/5977, MP 935/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.173±0.003 com Tomar Fôlego; contra Soco de Placa 0.170, ataque básico 0.169, Gancho e Corda 0.167; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 7): eu HP 5412/5977, MP 935/1103, efeitos —, buffs —; adversário Tenz HP 4346/5519, MP 845/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.547±0.022 com Soco de Placa; contra ataque básico 0.543, Respirar Fundo 0.523, Juramento da Muralha 0.519; dano esperado 331; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Soco de Placa

### 7.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 874 → min(1103, 874 + 22) = 896
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 874 → 896; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 896 → 896
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 957
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #12** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 28 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 95; teste `71 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 29 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 30; teste `29 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.6 × 0.16420361247947454 = 584.5648604269294; max(1, int(bruto)) = 584 → int(anterior × 1.0) = 584 → int(anterior × 0.79) = 461
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **461**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 461
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(461)`; HP do alvo 4346 → 3885 (retirado 461)
23. Roubo de vida: 13.0% → max(1, int(461 × 13 / 100)) = 59; HP do atacante +59 (teto do HP máximo)
24. Morte e death_ignore: HP final 3885 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 30 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 1.68; teste `85 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 31 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 29.4; teste `64 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 5412 → 5471; mp 957 → 896; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 4346 → 3885

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 461.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 752 → min(1050, 752 + 21) = 773
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 752 → 773; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 773 → 773
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 866
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 3885 → 4547; mp 866 → 773; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 7.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4547/5519 | 5471/5977 |
| MP | 773/1050 | 896/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 461 (golpes e DoT), recebido 0; cura 59
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 461; cura 662


## Rodada 8

### 8.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4547/5519 | 5471/5977 |
| MP | 773/1050 | 896/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 8.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 8): eu HP 4547/5519, MP 773/1050, efeitos —, buffs —; adversário fer HP 5471/5977, MP 896/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.159±0.003 com Golpe Poderoso; contra Soco de Placa 0.157, ataque básico 0.157, Gancho e Corda 0.154; dano esperado 215; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 8): eu HP 5471/5977, MP 896/1103, efeitos —, buffs —; adversário Tenz HP 4547/5519, MP 773/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.537±0.012 com Golpe Poderoso; contra ataque básico 0.536, Respirar Fundo 0.516, Juramento da Muralha 0.516; dano esperado 338; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 8.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 844 → min(1103, 844 + 22) = 866
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 844 → 866; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 866 → 866
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 918
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #13** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 32 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 95; teste `25 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 33 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 30; teste `55 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.08 × 1.0 × 0.16420361247947454 = 374.7192118226601; max(1, int(bruto)) = 374 → int(anterior × 1.0) = 374 → int(anterior × 0.79) = 295
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **295**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 295
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(295)`; HP do alvo 4547 → 4252 (retirado 295)
23. Roubo de vida: 13.0% → max(1, int(295 × 13 / 100)) = 38; HP do atacante +38 (teto do HP máximo)
24. Morte e death_ignore: HP final 4252 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 34 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 1.68; teste `48 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5471 → 5509; mp 918 → 866; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4547 → 4252

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 295.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 721 → min(1050, 721 + 21) = 742
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 721 → 742; recarga Golpe Poderoso 1 → livre; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 742 → 742
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 794
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #14** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 35 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **13**; chance 72; teste `13 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 36 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **93**; chance 15; teste `93 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.08 × 1.0 × 0.16583747927031509 = 372.3582089552239; max(1, int(bruto)) = 372 → int(anterior × 1.0) = 372 → int(anterior × 0.89) = 331
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **331**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 331
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(331)`; HP do alvo 5509 → 5178 (retirado 331)
23. Roubo de vida: 21.0% → max(1, int(331 × 21 / 100)) = 69; HP do atacante +69 (teto do HP máximo)
24. Morte e death_ignore: HP final 5178 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 4252 → 4321; mp 794 → 742; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5509 → 5178

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 331.

### 8.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4321/5519 | 5178/5977 |
| MP | 742/1050 | 866/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 295 (golpes e DoT), recebido 331; cura 38
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 331 (golpes e DoT), recebido 295; cura 69


## Rodada 9

### 9.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4321/5519 | 5178/5977 |
| MP | 742/1050 | 866/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 9.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 9): eu HP 4321/5519, MP 742/1050, efeitos —, buffs —; adversário fer HP 5178/5977, MP 866/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.158±0.004 com ataque básico; contra Soco de Placa 0.157, Gancho e Corda 0.155; dano esperado 121
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 9): eu HP 5178/5977, MP 866/1103, efeitos —, buffs —; adversário Tenz HP 4321/5519, MP 742/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.509±0.013 com Soco de Placa; contra ataque básico 0.505, Respirar Fundo 0.491, Juramento da Muralha 0.482; dano esperado 314; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 9.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 805 → min(1103, 805 + 22) = 827
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 805 → 827; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 827 → 827
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 888
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #15** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 37 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 95; teste `9 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 38 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **73**; chance 30; teste `73 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 4321 → 4033 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 4033 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 39 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 1.68; teste `85 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 40 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 29.4; teste `53 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 5178 → 5215; mp 888 → 827; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 4321 → 4033

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 742 → min(1050, 742 + 21) = 763
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 742 → 763; recarga Golpe Poderoso 2 → 1; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 763 → 763
- Perde a oportunidade por controle: não

**Golpe #16** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 41 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 72; teste `34 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 42 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **36**; chance 15; teste `36 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 5215 → 5036 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 5036 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 9.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4070/5519 | 5036/5977 |
| MP | 763/1050 | 827/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 179; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 288; cura 37


## Rodada 10

### 10.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 4070/5519 | 5036/5977 |
| MP | 763/1050 | 827/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 10.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 10): eu HP 4070/5519, MP 763/1050, efeitos —, buffs —; adversário fer HP 5036/5977, MP 827/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.155±0.005 com Golpe Poderoso; contra Soco de Placa 0.155, ataque básico 0.153, Gancho e Corda 0.152; dano esperado 226; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 10): eu HP 5036/5977, MP 827/1103, efeitos —, buffs —; adversário Tenz HP 4070/5519, MP 763/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.463±0.014 com Golpe Poderoso; contra ataque básico 0.460, Respirar Fundo 0.446, Juramento da Muralha 0.442; dano esperado 290; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 10.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 775 → min(1103, 775 + 22) = 797
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 775 → 797; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 797 → 797
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 849
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #17** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 43 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 95; teste `44 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 44 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 30; teste `48 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 4070 → 3797 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 3797 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 45 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 1.68; teste `63 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 5036 → 5071; mp 849 → 797; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4070 → 3797

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 711 → min(1050, 711 + 21) = 732
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 711 → 732; recarga Golpe Poderoso 1 → livre; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 732 → 732
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 784
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #18** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 46 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **24**; chance 72; teste `24 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 47 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **5**; chance 15; teste `5 <= 15` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: condição da carta (target_healthy) 0.08 → 1 + Σ = 1.08
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.08 × 1.6 × 0.16583747927031509 = 595.7731343283583; max(1, int(bruto)) = 595 → int(anterior × 1.0) = 595 → int(anterior × 0.89) = 529
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **529**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 529
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(529)`; HP do alvo 5071 → 4542 (retirado 529)
23. Roubo de vida: 21.0% → max(1, int(529 × 21 / 100)) = 111; HP do atacante +111 (teto do HP máximo)
24. Morte e death_ignore: HP final 4542 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3797 → 3908; mp 784 → 732; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 5071 → 4542

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 529.

### 10.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3908/5519 | 4542/5977 |
| MP | 732/1050 | 797/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 529; cura 35
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 529 (golpes e DoT), recebido 273; cura 111


## Rodada 11

### 11.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3908/5519 | 4542/5977 |
| MP | 732/1050 | 797/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 11.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 11): eu HP 3908/5519, MP 732/1050, efeitos —, buffs —; adversário fer HP 4542/5977, MP 797/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.190±0.006 com Soco de Placa; contra ataque básico 0.189, Gancho e Corda 0.177; dano esperado 252; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 11): eu HP 4542/5977, MP 797/1103, efeitos —, buffs —; adversário Tenz HP 3908/5519, MP 732/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.402±0.016 com ataque básico; contra Soco de Placa 0.401, Respirar Fundo 0.395, Juramento da Muralha 0.395; dano esperado 163
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Ataque básico

### 11.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 797 → min(1103, 797 + 22) = 819
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 797 → 819; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 819 → 819
- Perde a oportunidade por controle: não

**Golpe #19** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 48 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 95; teste `35 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 49 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 30; teste `14 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.6 × 0.16420361247947454 = 327.0935960591133; max(1, int(bruto)) = 327 → int(anterior × 1.0) = 327 → int(anterior × 0.79) = 258
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **258**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 258
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(258)`; HP do alvo 3908 → 3650 (retirado 258)
23. Roubo de vida: 13.0% → max(1, int(258 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final 3650 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 50 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 1.68; teste `3 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 258.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 671 → min(1050, 671 + 21) = 692
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 671 → 692; recarga Golpe Poderoso 2 → 1; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 692 → 692
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 753
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #20** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 51 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 72; teste `2 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 52 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 15; teste `20 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.16583747927031509 = 363.18407960199005; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.89) = 323
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **323**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 323
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(323)`; HP do alvo 4575 → 4252 (retirado 323)
23. Roubo de vida: 21.0% → max(1, int(323 × 21 / 100)) = 67; HP do atacante +67 (teto do HP máximo)
24. Morte e death_ignore: HP final 4252 → o alvo segue vivo

**Status `weakened`** sobre fer (p2) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 53 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **76**; chance 35.0; teste `76 > 35.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3650 → 3717; mp 753 → 692; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 4575 → 4252

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 323.

### 11.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3717/5519 | 4252/5977 |
| MP | 692/1050 | 819/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Golpe Poderoso 1, Soco de Placa 2 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 258 (golpes e DoT), recebido 323; cura 33
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 323 (golpes e DoT), recebido 258; cura 67


## Rodada 12

### 12.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3717/5519 | 4252/5977 |
| MP | 692/1050 | 819/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Golpe Poderoso 1, Soco de Placa 2 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 12.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 12): eu HP 3717/5519, MP 692/1050, efeitos —, buffs —; adversário fer HP 4252/5977, MP 819/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.198±0.006 com Golpe Poderoso; contra Tomar Fôlego 0.197, ataque básico 0.196, Gancho e Corda 0.190; dano esperado 243; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 12): eu HP 4252/5977, MP 819/1103, efeitos —, buffs —; adversário Tenz HP 3717/5519, MP 692/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.430±0.025 com Soco de Placa; contra Golpe Poderoso 0.427, ataque básico 0.417, Respirar Fundo 0.414; dano esperado 293; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Soco de Placa

### 12.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 758 → min(1103, 758 + 22) = 780
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 758 → 780; recarga Golpe Poderoso 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 780 → 780
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 841
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #21** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 54 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **65**; chance 95; teste `65 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 55 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 30; teste `56 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 3717 → 3429 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3429 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 56 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 1.68; teste `29 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 57 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **68**; chance 29.4; teste `68 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 4252 → 4289; mp 841 → 780; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3717 → 3429

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 640 → min(1050, 640 + 21) = 661
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 640 → 661; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 661 → 661
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 713
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #22** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 58 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 72; teste `64 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 59 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **76**; chance 15; teste `76 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.0 × 1.0 × 0.16583747927031509 = 344.77611940298505; max(1, int(bruto)) = 344 → int(anterior × 1.0) = 344 → int(anterior × 0.89) = 306
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **306**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 306
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(306)`; HP do alvo 4289 → 3983 (retirado 306)
23. Roubo de vida: 21.0% → max(1, int(306 × 21 / 100)) = 64; HP do atacante +64 (teto do HP máximo)
24. Morte e death_ignore: HP final 3983 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3429 → 3493; mp 713 → 661; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 4289 → 3983

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 306.

### 12.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3493/5519 | 3983/5977 |
| MP | 661/1050 | 780/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Golpe Poderoso 2 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 306; cura 37
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 306 (golpes e DoT), recebido 288; cura 64


## Rodada 13

### 13.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3493/5519 | 3983/5977 |
| MP | 661/1050 | 780/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Golpe Poderoso 2 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 13.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 13): eu HP 3493/5519, MP 661/1050, efeitos —, buffs —; adversário fer HP 3983/5977, MP 780/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.181±0.008 com Tomar Fôlego; contra Soco de Placa 0.177, ataque básico 0.172, Gancho e Corda 0.166; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 13): eu HP 3983/5977, MP 780/1103, efeitos —, buffs —; adversário Tenz HP 3493/5519, MP 661/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.383±0.018 com Golpe Poderoso; contra Respirar Fundo 0.376, ataque básico 0.374, Juramento da Muralha 0.375; dano esperado 271; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Golpe Poderoso

### 13.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 728 → min(1103, 728 + 22) = 750
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 728 → 750; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 750 → 750
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 802
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #23** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 60 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **28**; chance 95; teste `28 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 61 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **6**; chance 30; teste `6 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 3493 → 3055 (retirado 438)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 3055 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 62 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 1.68; teste `88 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3983 → 4039; mp 802 → 750; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3493 → 3055

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 438.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 568 → min(1050, 568 + 21) = 589
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 568 → 589; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 589 → 589
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 682
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 3055 → 3717; mp 682 → 589; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 13.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3717/5519 | 4039/5977 |
| MP | 589/1050 | 750/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 0; cura 56
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 438; cura 662


## Rodada 14

### 14.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3717/5519 | 4039/5977 |
| MP | 589/1050 | 750/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Golpe Poderoso 1, Tomar Fôlego 5 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 14.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 14): eu HP 3717/5519, MP 589/1050, efeitos —, buffs —; adversário fer HP 4039/5977, MP 750/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.180±0.006 com ataque básico; contra Golpe Poderoso 0.179, Soco de Placa 0.179, Gancho e Corda 0.170; dano esperado 144
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 14): eu HP 4039/5977, MP 750/1103, efeitos —, buffs —; adversário Tenz HP 3717/5519, MP 589/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.361±0.019 com Soco de Placa; contra Juramento da Muralha 0.362, Respirar Fundo 0.361, ataque básico 0.355; dano esperado 286; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 14.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 689 → min(1103, 689 + 22) = 711
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 689 → 711; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 711 → 711
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 772
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #24** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 63 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 95; teste `85 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 64 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 30; teste `54 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 3717 → 3429 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3429 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 65 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **100**; chance 1.68; teste `100 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 66 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 29.4; teste `12 > 29.4` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 2 → após leis (nenhuma) 2; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `weakened` no alvo antes: —; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'soco_de_placa'}]

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 4039 → 4076; mp 772 → 711; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3717 → 3429; st 601 → 480; efeito weakened entra (dur 2, stacks 1, int 20.0)

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 589 → min(1050, 589 + 21) = 610
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 589 → 610; recarga Golpe Poderoso 1 → livre; recarga Tomar Fôlego 5 → 4; efeito weakened: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 610 → 610
- Perde a oportunidade por controle: não

**Golpe #25** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 480.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 930.4; dano médio max(1, int(930.4 × (1 + 21/100))) = 1125; BASE do básico = max(1, int(1125 × 0.9)) = **1012** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 67 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **18**; chance 72; teste `18 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 68 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 15; teste `97 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1012.0 × 1.0 × 1.0 × 0.16583747927031509 = 167.82752902155886; max(1, int(bruto)) = 167 → int(anterior × 1.0) = 167 → int(anterior × 0.89) = 148
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **148**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 148
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(148)`; HP do alvo 4076 → 3928 (retirado 148)
23. Roubo de vida: 21.0% → max(1, int(148 × 21 / 100)) = 31; HP do atacante +31 (teto do HP máximo)
24. Morte e death_ignore: HP final 3928 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 148.

### 14.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3460/5519 | 3928/5977 |
| MP | 610/1050 | 711/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 148; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 148 (golpes e DoT), recebido 288; cura 31


## Rodada 15

### 15.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3460/5519 | 3928/5977 |
| MP | 610/1050 | 711/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

### 15.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 15): eu HP 3460/5519, MP 610/1050, efeitos ['weakened'], buffs —; adversário fer HP 3928/5977, MP 711/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.173±0.008 com Golpe Poderoso; contra Soco de Placa 0.172, ataque básico 0.171, Gancho e Corda 0.163; dano esperado 193; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 15): eu HP 3928/5977, MP 711/1103, efeitos —, buffs —; adversário Tenz HP 3460/5519, MP 610/1050, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.374±0.016 com Golpe Poderoso; contra ataque básico 0.372, Respirar Fundo 0.370, Juramento da Muralha 0.370; dano esperado 267; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 15.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 480.0 | 512.3333333333334 | 0.936890045543266 | 0.9679308061753515 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.016478945448366
- ÷ 6 = build 1.002746490908061
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.002746490908061 × 1.0 = 1.002746490908061**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.002746490908061 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 659 → min(1103, 659 + 22) = 681
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 659 → 681; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 681 → 681
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 733
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #26** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 69 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **55**; chance 95; teste `55 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 70 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 30; teste `12 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 3460 → 3022 (retirado 438)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 3022 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 71 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 1.68; teste `87 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3928 → 3984; mp 733 → 681; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3460 → 3022

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 438.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 558 → min(1050, 558 + 21) = 579
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['weakened'], leis —, pula a vez: False
- Mudanças de estado no início: mp 558 → 579; st 480 → 601; recarga Tomar Fôlego 4 → 3; efeito weakened sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 579 → 579
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 631
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #27** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 72 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 72; teste `53 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 73 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **90**; chance 15; teste `90 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.0 × 1.0 × 0.16583747927031509 = 344.77611940298505; max(1, int(bruto)) = 344 → int(anterior × 1.0) = 344 → int(anterior × 0.89) = 306
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **306**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 306
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(306)`; HP do alvo 3984 → 3678 (retirado 306)
23. Roubo de vida: 21.0% → max(1, int(306 × 21 / 100)) = 64; HP do atacante +64 (teto do HP máximo)
24. Morte e death_ignore: HP final 3678 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3022 → 3086; mp 631 → 579; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3984 → 3678

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 306.

### 15.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3086/5519 | 3678/5977 |
| MP | 579/1050 | 681/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 306; cura 56
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 306 (golpes e DoT), recebido 438; cura 64


## Rodada 16

### 16.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3086/5519 | 3678/5977 |
| MP | 579/1050 | 681/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 16.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 16): eu HP 3086/5519, MP 579/1050, efeitos —, buffs —; adversário fer HP 3678/5977, MP 681/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Gancho e Corda** — justificativa da política: P(vitória) 0.153±0.004 com Gancho e Corda; contra Soco de Placa 0.149, ataque básico 0.145; custa 117 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 117

**fer (p2)**

- Estado recebido (`DuelView`, rodada 16): eu HP 3678/5977, MP 681/1103, efeitos —, buffs —; adversário Tenz HP 3086/5519, MP 579/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.467±0.017 com Soco de Placa; contra ataque básico 0.461, Respirar Fundo 0.448, Juramento da Muralha 0.438; dano esperado 291; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **117 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Gancho e Corda; fer (p2) = Soco de Placa

### 16.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 620 → min(1103, 620 + 22) = 642
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 620 → 642; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 642 → 642
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 703
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #28** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 74 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 95; teste `91 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 75 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **49**; chance 30; teste `49 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 3086 → 2798 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2798 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 76 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 1.68; teste `12 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 77 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 29.4; teste `3 > 29.4` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 2 → após leis (nenhuma) 2; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `weakened` no alvo antes: —; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'soco_de_placa'}]

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3678 → 3715; mp 703 → 642; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3086 → 2798; st 601 → 480; efeito weakened entra (dur 2, stacks 1, int 20.0)

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 462 → min(1050, 462 + 21) = 483
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 462 → 483; recarga Golpe Poderoso 2 → 1; recarga Tomar Fôlego 3 → 2; efeito weakened: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 117, teto livre 933 → MP 483 → 483
- Perde a oportunidade por controle: não

**Skill Gancho e Corda** (`n_gancho_e_corda`) de Tenz (p1)

- Tipo `status`, valor stun ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 117 MP; reserva feita no lock 117; MP disponível na cobrança (livre + reserva liberada) 600
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Status: chance base 50%, duração declarada 1

**Status `stun`** sobre fer (p2) (via `apply_skill`, fonte `n_gancho_e_corda`)

- Chance base 50%; resistência do alvo 0.0% → efetiva 50 × (1 − 0/100) = 50.0%
- sorteio nº 78 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **9**; chance 50.0; teste `9 > 50.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 1 → após leis (nenhuma) 1; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `stun` no alvo antes: —; depois: [{'duration': 1, 'stacks': 1, 'intensity': 0.0, 'source_id': 'n_gancho_e_corda'}]

**Status `vulnerable`** sobre fer (p2) (via `_aplicar_secundario`, fonte `n_gancho_e_corda`)

- Chance base 60%; resistência do alvo 0.0% → efetiva 60 × (1 − 0/100) = 60.0%
- sorteio nº 79 [aplicação de status (vulnerable)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 60.0; teste `79 > 60.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `vulnerable` no alvo antes: —; depois: —

- Resultado da skill: `status`; MP debitado 117; recarga depois 5; status stun pegou
- Mudanças em quem lançou: mp 600 → 483; recarga Gancho e Corda — → 5
- Mudanças no adversário: efeito stun entra (dur 1, stacks 1, int 0.0)

- Motor (`action_executed`): Tenz (p1) executou Gancho e Corda; MP gasto 117, dano ao adversário 0.

### 16.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2798/5519 | 3715/5977 |
| MP | 483/1050 | 642/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 1, Gancho e Corda 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | stun (dur 1, stacks 1, int 0.0, fonte n_gancho_e_corda) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 37
- Tenz (p1): Gancho e Corda — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 0


## Rodada 17

### 17.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2798/5519 | 3715/5977 |
| MP | 483/1050 | 642/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Golpe Poderoso 1, Gancho e Corda 5 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | stun (dur 1, stacks 1, int 0.0, fonte n_gancho_e_corda) |
| death_ignore gasto / vivo | False / True | False / True |

### 17.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 17): eu HP 2798/5519, MP 483/1050, efeitos ['weakened'], buffs —; adversário fer HP 3715/5977, MP 642/1103, efeitos ['stun'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 4, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.169±0.006 com Golpe Poderoso; contra Soco de Placa 0.169, ataque básico 0.166; dano esperado 197; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 17): eu HP 3715/5977, MP 642/1103, efeitos ['stun'], buffs —; adversário Tenz HP 2798/5519, MP 483/1050, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.426±0.036 com ataque básico; contra Golpe Poderoso 0.426, Juramento da Muralha 0.426, Respirar Fundo 0.426; dano esperado 162
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Ataque básico

### 17.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 480.0 | 512.3333333333334 | 0.936890045543266 | 0.9679308061753515 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.016478945448366
- ÷ 6 = build 1.002746490908061
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.002746490908061 × 1.0 = 1.002746490908061**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.002746490908061 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 642 → min(1103, 642 + 22) = 664
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['stun'], leis —, pula a vez: True
- Mudanças de estado no início: mp 642 → 664; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1; efeito stun sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 664 → 664
- Perde a oportunidade por controle: **sim**

- Ação de fer (p2) **cancelada por controle**.
### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Golpe Poderoso 1 → livre; Gancho e Corda 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 431 → min(1050, 431 + 21) = 452
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['weakened'], leis —, pula a vez: False
- Mudanças de estado no início: mp 431 → 452; st 480 → 601; recarga Golpe Poderoso 1 → livre; recarga Gancho e Corda 5 → 4; recarga Tomar Fôlego 2 → 1; efeito weakened sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 452 → 452
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 504
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #29** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 80 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 72; teste `88 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 3715 → 3715)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: mp 504 → 452; recarga Golpe Poderoso — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 0.

### 17.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2798/5519 | 3715/5977 |
| MP | 452/1050 | 664/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Gancho e Corda 4, Golpe Poderoso 2 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — cancelada por controle; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 0 (golpes e DoT), recebido 0; cura 0


## Rodada 18

### 18.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2798/5519 | 3715/5977 |
| MP | 452/1050 | 664/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Gancho e Corda 4, Golpe Poderoso 2 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 18.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 18): eu HP 2798/5519, MP 452/1050, efeitos —, buffs —; adversário fer HP 3715/5977, MP 664/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 3, Tomar Fôlego 0
- Ações legais: Ataque básico, Soco de Placa, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.127±0.007 com Tomar Fôlego; contra Soco de Placa 0.121, ataque básico 0.120; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 18): eu HP 3715/5977, MP 664/1103, efeitos —, buffs —; adversário Tenz HP 2798/5519, MP 452/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.563±0.021 com ataque básico; contra Golpe Poderoso 0.544, Soco de Placa 0.537, Respirar Fundo 0.519; dano esperado 163
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Ataque básico

### 18.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 664 → min(1103, 664 + 22) = 686
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 664 → 686; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 686 → 686
- Perde a oportunidade por controle: não

**Golpe #30** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 81 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **46**; chance 95; teste `46 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 82 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 30; teste `89 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 2798 → 2637 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +20 (teto do HP máximo)
24. Morte e death_ignore: HP final 2637 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 83 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **8**; chance 1.68; teste `8 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Gancho e Corda 4 → 3; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 359 → min(1050, 359 + 21) = 380
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 359 → 380; recarga Golpe Poderoso 2 → 1; recarga Gancho e Corda 4 → 3; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 380 → 380
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 473
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 2637 → 3299; mp 473 → 380; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 18.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3299/5519 | 3735/5977 |
| MP | 380/1050 | 686/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 3, Golpe Poderoso 1, Tomar Fôlego 5 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 0; cura 20
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 161; cura 662


## Rodada 19

### 19.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 3299/5519 | 3735/5977 |
| MP | 380/1050 | 686/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 3, Golpe Poderoso 1, Tomar Fôlego 5 | — |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 19.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 19): eu HP 3299/5519, MP 380/1050, efeitos —, buffs —; adversário fer HP 3735/5977, MP 686/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 2, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.137±0.007 com ataque básico; contra Soco de Placa 0.137, Golpe Poderoso 0.136; dano esperado 135
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 19): eu HP 3735/5977, MP 686/1103, efeitos —, buffs —; adversário Tenz HP 3299/5519, MP 380/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.485±0.025 com Soco de Placa; contra Golpe Poderoso 0.482, ataque básico 0.478, Respirar Fundo 0.466; dano esperado 290; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 19.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 625 → min(1103, 625 + 22) = 647
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 625 → 647
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 647 → 647
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 708
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #31** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 84 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 95; teste `54 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 85 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 30; teste `16 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.6 × 0.16420361247947454 = 584.5648604269294; max(1, int(bruto)) = 584 → int(anterior × 1.0) = 584 → int(anterior × 0.79) = 461
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **461**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 461
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(461)`; HP do alvo 3299 → 2838 (retirado 461)
23. Roubo de vida: 13.0% → max(1, int(461 × 13 / 100)) = 59; HP do atacante +59 (teto do HP máximo)
24. Morte e death_ignore: HP final 2838 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 86 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 1.68; teste `31 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 87 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **43**; chance 29.4; teste `43 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3735 → 3794; mp 708 → 647; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3299 → 2838

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 461.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Gancho e Corda 3 → 2; Golpe Poderoso 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 380 → min(1050, 380 + 21) = 401
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 380 → 401; recarga Golpe Poderoso 1 → livre; recarga Gancho e Corda 3 → 2; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 401 → 401
- Perde a oportunidade por controle: não

**Golpe #32** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 88 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **41**; chance 72; teste `41 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 89 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 15; teste `14 <= 15` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.6 × 0.16583747927031509 = 324.7761194029851; max(1, int(bruto)) = 324 → int(anterior × 1.0) = 324 → int(anterior × 0.89) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 3794 → 3506 (retirado 288)
23. Roubo de vida: 21.0% → max(1, int(288 × 21 / 100)) = 60; HP do atacante +60 (teto do HP máximo)
24. Morte e death_ignore: HP final 3506 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 288.

### 19.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2898/5519 | 3506/5977 |
| MP | 401/1050 | 647/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 2, Tomar Fôlego 4 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 461 (golpes e DoT), recebido 288; cura 59
- Tenz (p1): Ataque básico — executada; dano causado na rodada 288 (golpes e DoT), recebido 461; cura 60


## Rodada 20

### 20.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2898/5519 | 3506/5977 |
| MP | 401/1050 | 647/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 2, Tomar Fôlego 4 | Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 20.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 20): eu HP 2898/5519, MP 401/1050, efeitos —, buffs —; adversário fer HP 3506/5977, MP 647/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 1, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.147±0.007 com Soco de Placa; contra Golpe Poderoso 0.147, ataque básico 0.145; dano esperado 250; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 20): eu HP 3506/5977, MP 647/1103, efeitos —, buffs —; adversário Tenz HP 2898/5519, MP 401/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.552±0.024 com Golpe Poderoso; contra ataque básico 0.543, Respirar Fundo 0.510, Juramento da Muralha 0.500; dano esperado 283; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Golpe Poderoso

### 20.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 595 → min(1103, 595 + 22) = 617
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 595 → 617; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 617 → 617
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 669
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #33** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 90 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **60**; chance 95; teste `60 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 91 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **7**; chance 30; teste `7 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 2898 → 2460 (retirado 438)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 2460 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 92 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **31**; chance 1.68; teste `31 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3506 → 3562; mp 669 → 617; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2898 → 2460

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 438.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Gancho e Corda 2 → 1; Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 340 → min(1050, 340 + 21) = 361
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 340 → 361; recarga Gancho e Corda 2 → 1; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 361 → 361
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 422
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #34** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 93 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **37**; chance 72; teste `37 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 94 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 15; teste `85 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.16583747927031509 = 363.18407960199005; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.89) = 323
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **323**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 323
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(323)`; HP do alvo 3562 → 3239 (retirado 323)
23. Roubo de vida: 21.0% → max(1, int(323 × 21 / 100)) = 67; HP do atacante +67 (teto do HP máximo)
24. Morte e death_ignore: HP final 3239 → o alvo segue vivo

**Status `weakened`** sobre fer (p2) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 95 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 35.0; teste `53 > 35.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2460 → 2527; mp 422 → 361; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3562 → 3239

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 323.

### 20.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2527/5519 | 3239/5977 |
| MP | 361/1050 | 617/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 1, Tomar Fôlego 3, Soco de Placa 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 323; cura 56
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 323 (golpes e DoT), recebido 438; cura 67


## Rodada 21

### 21.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2527/5519 | 3239/5977 |
| MP | 361/1050 | 617/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Gancho e Corda 1, Tomar Fôlego 3, Soco de Placa 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 21.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 21): eu HP 2527/5519, MP 361/1050, efeitos —, buffs —; adversário fer HP 3239/5977, MP 617/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.135±0.006 com ataque básico; contra Golpe Poderoso 0.134, Gancho e Corda 0.129; dano esperado 140
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 21): eu HP 3239/5977, MP 617/1103, efeitos —, buffs —; adversário Tenz HP 2527/5519, MP 361/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Respirar Fundo** — justificativa da política: P(vitória) 0.577±0.025 com Respirar Fundo; contra ataque básico 0.574, Soco de Placa 0.571, Juramento da Muralha 0.543; custa 82 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 82

- Lock: fer (p2) reserva **82 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Respirar Fundo

### 21.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 535 → min(1103, 535 + 22) = 557
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 535 → 557; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 82, teto livre 1021 → MP 557 → 557
- Perde a oportunidade por controle: não

**Skill Respirar Fundo** (`n_respirar_fundo`) de fer (p2)

- Tipo `heal`, valor 10 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 82 MP; reserva feita no lock 82; MP disponível na cobrança (livre + reserva liberada) 639
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5977 × 10 / 100)) = 597; potion_heal_bonus 0.0% → total 597

- Resultado da skill: `heal`; MP debitado 82; recarga depois 5; cura 597
- Mudanças em quem lançou: hp 3239 → 3836; mp 639 → 557; recarga Respirar Fundo — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Respirar Fundo; MP gasto 82, dano ao adversário 0.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Gancho e Corda 1 → livre; Tomar Fôlego 3 → 2; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 361 → min(1050, 361 + 21) = 382
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 361 → 382; recarga Gancho e Corda 1 → livre; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 382 → 382
- Perde a oportunidade por controle: não

**Golpe #35** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 96 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **20**; chance 72; teste `20 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 97 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **74**; chance 15; teste `74 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 3836 → 3657 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3657 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 21.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2564/5519 | 3657/5977 |
| MP | 382/1050 | 557/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1 | Golpe Poderoso 1, Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Respirar Fundo — executada; dano causado na rodada 0 (golpes e DoT), recebido 179; cura 597
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 0; cura 37


## Rodada 22

### 22.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2564/5519 | 3657/5977 |
| MP | 382/1050 | 557/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1 | Golpe Poderoso 1, Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 22.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 22): eu HP 2564/5519, MP 382/1050, efeitos —, buffs —; adversário fer HP 3657/5977, MP 557/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.117±0.004 com Soco de Placa; contra Golpe Poderoso 0.116, ataque básico 0.115, Gancho e Corda 0.113; dano esperado 251; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 22): eu HP 3657/5977, MP 557/1103, efeitos —, buffs —; adversário Tenz HP 2564/5519, MP 382/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 4
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.617±0.024 com ataque básico; contra Golpe Poderoso 0.613, Soco de Placa 0.611, Juramento da Muralha 0.550; dano esperado 169
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Ataque básico

### 22.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Respirar Fundo 5 → 4
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 557 → min(1103, 557 + 22) = 579
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 557 → 579; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 579 → 579
- Perde a oportunidade por controle: não

**Golpe #36** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 98 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **82**; chance 95; teste `82 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 99 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **90**; chance 30; teste `90 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 2564 → 2403 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +20 (teto do HP máximo)
24. Morte e death_ignore: HP final 2403 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 100 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **92**; chance 1.68; teste `92 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 321 → min(1050, 321 + 21) = 342
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 321 → 342; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 342 → 342
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 403
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #37** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 101 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 72; teste `25 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 102 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 15; teste `70 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.16583747927031509 = 363.18407960199005; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.89) = 323
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **323**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 323
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(323)`; HP do alvo 3677 → 3354 (retirado 323)
23. Roubo de vida: 21.0% → max(1, int(323 × 21 / 100)) = 67; HP do atacante +67 (teto do HP máximo)
24. Morte e death_ignore: HP final 3354 → o alvo segue vivo

**Status `weakened`** sobre fer (p2) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 103 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 35.0; teste `35 > 35.0` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 2 → após leis (nenhuma) 2; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `weakened` no alvo antes: —; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'soco_de_placa'}]

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2403 → 2470; mp 403 → 342; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3677 → 3354; st 654 → 523; efeito weakened entra (dur 2, stacks 1, int 20.0)

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 323.

### 22.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2470/5519 | 3354/5977 |
| MP | 342/1050 | 579/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 523 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 2 | Respirar Fundo 4 |
| Buffs | — | — |
| Efeitos | — | weakened (dur 2, stacks 1, int 20.0, fonte soco_de_placa) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 323; cura 20
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 323 (golpes e DoT), recebido 161; cura 67


## Rodada 23

### 23.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2470/5519 | 3354/5977 |
| MP | 342/1050 | 579/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 523 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 2 | Respirar Fundo 4 |
| Buffs | — | — |
| Efeitos | — | weakened (dur 2, stacks 1, int 20.0, fonte soco_de_placa) |
| death_ignore gasto / vivo | False / True | False / True |

### 23.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 23): eu HP 2470/5519, MP 342/1050, efeitos —, buffs —; adversário fer HP 3354/5977, MP 579/1103, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.125±0.004 com Tomar Fôlego; contra ataque básico 0.119, Golpe Poderoso 0.119, Gancho e Corda 0.120; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 23): eu HP 3354/5977, MP 579/1103, efeitos ['weakened'], buffs —; adversário Tenz HP 2470/5519, MP 342/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 3
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.579±0.012 com ataque básico; contra Golpe Poderoso 0.577, Soco de Placa 0.571, Juramento da Muralha 0.513; dano esperado 138
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Ataque básico

### 23.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 523.0 | 512.3333333333334 | 1.0208197787898503 | 1.0103562633001542 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.234063981496311
- ÷ 6 = build 1.0390106635827185
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0390106635827185 × 1.0 = 1.0390106635827185**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0390106635827185 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 4 → 3
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 579 → min(1103, 579 + 22) = 601
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 579 → 601; recarga Respirar Fundo 4 → 3; efeito weakened: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 601 → 601
- Perde a oportunidade por controle: não

**Golpe #38** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 523.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1015.2; dano médio max(1, int(1015.2 × (1 + 13/100))) = 1147; BASE do básico = max(1, int(1147 × 0.9)) = **1032** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 104 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 95; teste `71 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 105 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 30; teste `44 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1032.0 × 1.0 × 1.0 × 0.16420361247947454 = 169.45812807881774; max(1, int(bruto)) = 169 → int(anterior × 1.0) = 169 → int(anterior × 0.79) = 133
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **133**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 133
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(133)`; HP do alvo 2470 → 2337 (retirado 133)
23. Roubo de vida: 13.0% → max(1, int(133 × 13 / 100)) = 17; HP do atacante +17 (teto do HP máximo)
24. Morte e death_ignore: HP final 2337 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 106 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **70**; chance 1.68; teste `70 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 133.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 249 → min(1050, 249 + 21) = 270
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 249 → 270; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 270 → 270
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 363
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 2337 → 2999; mp 363 → 270; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 23.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2999/5519 | 3371/5977 |
| MP | 270/1050 | 601/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 523 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Tomar Fôlego 5 | Respirar Fundo 3 |
| Buffs | — | — |
| Efeitos | — | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 133 (golpes e DoT), recebido 0; cura 17
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 133; cura 662


## Rodada 24

### 24.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2999/5519 | 3371/5977 |
| MP | 270/1050 | 601/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 523 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Tomar Fôlego 5 | Respirar Fundo 3 |
| Buffs | — | — |
| Efeitos | — | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) |
| death_ignore gasto / vivo | False / True | False / True |

### 24.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 24): eu HP 2999/5519, MP 270/1050, efeitos —, buffs —; adversário fer HP 3371/5977, MP 601/1103, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.146±0.008 com ataque básico; contra Golpe Poderoso 0.146, Soco de Placa 0.146, Gancho e Corda 0.126; dano esperado 142
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 24): eu HP 3371/5977, MP 601/1103, efeitos ['weakened'], buffs —; adversário Tenz HP 2999/5519, MP 270/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 2
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.478±0.027 com ataque básico; contra Golpe Poderoso 0.476, Soco de Placa 0.465, Juramento da Muralha 0.453; dano esperado 138
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Ataque básico

### 24.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5977.0 | 4533.333333333333 | 1.3184558823529413 | 1.1482403417198601 |
| mp | 1103.0 | 1169.6666666666667 | 0.9430037047591906 | 0.971083778445089 |
| st | 523.0 | 512.3333333333334 | 1.0208197787898503 | 1.0103562633001542 |
| mg | 446.0 | 459.6666666666667 | 0.9702683103698332 | 0.9850219847139622 |
| ag | 142.0 | 177.66666666666666 | 0.799249530956848 | 0.8940075676172143 |
| df | 503.0 | 335.0 | 1.501492537313433 | 1.2253540457000307 |

- Soma das seis raízes (`math.fsum`): 6.234063981496311
- ÷ 6 = build 1.0390106635827185
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0390106635827185 × 1.0 = 1.0390106635827185**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0390106635827185 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 3 → 2
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 601 → min(1103, 601 + 22) = 623
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['weakened'], leis —, pula a vez: False
- Mudanças de estado no início: mp 601 → 623; st 523 → 654; recarga Respirar Fundo 3 → 2; efeito weakened sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 623 → 623
- Perde a oportunidade por controle: não

**Golpe #39** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 107 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 95; teste `71 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 108 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 30; teste `25 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.6 × 0.16420361247947454 = 327.0935960591133; max(1, int(bruto)) = 327 → int(anterior × 1.0) = 327 → int(anterior × 0.79) = 258
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **258**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 258
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(258)`; HP do alvo 2999 → 2741 (retirado 258)
23. Roubo de vida: 13.0% → max(1, int(258 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final 2741 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 109 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 1.68; teste `3 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 258.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 270 → min(1050, 270 + 21) = 291
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 270 → 291; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 291 → 291
- Perde a oportunidade por controle: não

**Golpe #40** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 110 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 72; teste `48 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 111 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 15; teste `67 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 3404 → 3225 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3225 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 24.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2778/5519 | 3225/5977 |
| MP | 291/1050 | 623/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Respirar Fundo 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 258 (golpes e DoT), recebido 179; cura 33
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 258; cura 37


## Rodada 25

### 25.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2778/5519 | 3225/5977 |
| MP | 291/1050 | 623/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Respirar Fundo 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 25.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 25): eu HP 2778/5519, MP 291/1050, efeitos —, buffs —; adversário fer HP 3225/5977, MP 623/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.141±0.004 com Soco de Placa; contra ataque básico 0.140, Golpe Poderoso 0.139, Gancho e Corda 0.130; dano esperado 255; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 25): eu HP 3225/5977, MP 623/1103, efeitos —, buffs —; adversário Tenz HP 2778/5519, MP 291/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 1
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.560±0.021 com ataque básico; contra Golpe Poderoso 0.557, Soco de Placa 0.557, Juramento da Muralha 0.510; dano esperado 170
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Ataque básico

### 25.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 623 → min(1103, 623 + 22) = 645
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 623 → 645; recarga Respirar Fundo 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 645 → 645
- Perde a oportunidade por controle: não

**Golpe #41** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 112 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **73**; chance 95; teste `73 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 113 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **89**; chance 30; teste `89 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 2778 → 2617 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +20 (teto do HP máximo)
24. Morte e death_ignore: HP final 2617 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 114 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 1.68; teste `25 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 230 → min(1050, 230 + 21) = 251
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 230 → 251; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 251 → 251
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 312
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #42** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 115 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **15**; chance 72; teste `15 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 116 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 15; teste `88 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.0 × 1.0 × 0.16583747927031509 = 363.18407960199005; max(1, int(bruto)) = 363 → int(anterior × 1.0) = 363 → int(anterior × 0.89) = 323
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **323**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 323
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(323)`; HP do alvo 3245 → 2922 (retirado 323)
23. Roubo de vida: 21.0% → max(1, int(323 × 21 / 100)) = 67; HP do atacante +67 (teto do HP máximo)
24. Morte e death_ignore: HP final 2922 → o alvo segue vivo

**Status `weakened`** sobre fer (p2) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 117 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **64**; chance 35.0; teste `64 > 35.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2617 → 2684; mp 312 → 251; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3245 → 2922

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 323.

### 25.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2684/5519 | 2922/5977 |
| MP | 251/1050 | 645/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Soco de Placa 2 | Respirar Fundo 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 323; cura 20
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 323 (golpes e DoT), recebido 161; cura 67


## Rodada 26

### 26.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2684/5519 | 2922/5977 |
| MP | 251/1050 | 645/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Soco de Placa 2 | Respirar Fundo 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 26.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 26): eu HP 2684/5519, MP 251/1050, efeitos —, buffs —; adversário fer HP 2922/5977, MP 645/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.127±0.003 com Golpe Poderoso; contra ataque básico 0.127, Gancho e Corda 0.123; dano esperado 245; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 26): eu HP 2922/5977, MP 645/1103, efeitos —, buffs —; adversário Tenz HP 2684/5519, MP 251/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Respirar Fundo** — justificativa da política: P(vitória) 0.578±0.011 com Respirar Fundo; contra Soco de Placa 0.572, Golpe Poderoso 0.568, ataque básico 0.536; custa 82 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 82

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **82 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Respirar Fundo

### 26.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 563 → min(1103, 563 + 22) = 585
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 563 → 585; recarga Respirar Fundo 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 82, teto livre 1021 → MP 585 → 585
- Perde a oportunidade por controle: não

**Skill Respirar Fundo** (`n_respirar_fundo`) de fer (p2)

- Tipo `heal`, valor 10 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 82 MP; reserva feita no lock 82; MP disponível na cobrança (livre + reserva liberada) 667
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5977 × 10 / 100)) = 597; potion_heal_bonus 0.0% → total 597

- Resultado da skill: `heal`; MP debitado 82; recarga depois 5; cura 597
- Mudanças em quem lançou: hp 2922 → 3519; mp 667 → 585; recarga Respirar Fundo — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Respirar Fundo; MP gasto 82, dano ao adversário 0.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 199 → min(1050, 199 + 21) = 220
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 199 → 220; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 220 → 220
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 272
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #43** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 118 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **6**; chance 72; teste `6 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 119 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **63**; chance 15; teste `63 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.0 × 1.0 × 0.16583747927031509 = 344.77611940298505; max(1, int(bruto)) = 344 → int(anterior × 1.0) = 344 → int(anterior × 0.89) = 306
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **306**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 306
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(306)`; HP do alvo 3519 → 3213 (retirado 306)
23. Roubo de vida: 21.0% → max(1, int(306 × 21 / 100)) = 64; HP do atacante +64 (teto do HP máximo)
24. Morte e death_ignore: HP final 3213 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2684 → 2748; mp 272 → 220; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3519 → 3213

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 306.

### 26.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2748/5519 | 3213/5977 |
| MP | 220/1050 | 585/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1, Golpe Poderoso 2 | Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Respirar Fundo — executada; dano causado na rodada 0 (golpes e DoT), recebido 306; cura 597
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 306 (golpes e DoT), recebido 0; cura 64


## Rodada 27

### 27.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2748/5519 | 3213/5977 |
| MP | 220/1050 | 585/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1, Golpe Poderoso 2 | Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 27.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 27): eu HP 2748/5519, MP 220/1050, efeitos —, buffs —; adversário fer HP 3213/5977, MP 585/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.133±0.008 com Soco de Placa; contra ataque básico 0.132, Gancho e Corda 0.126; dano esperado 258; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 27): eu HP 3213/5977, MP 585/1103, efeitos —, buffs —; adversário Tenz HP 2748/5519, MP 220/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 4
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.573±0.035 com Golpe Poderoso; contra ataque básico 0.558, Soco de Placa 0.558, Juramento da Muralha 0.519; dano esperado 284; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Golpe Poderoso

### 27.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 5 → 4
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 533 → min(1103, 533 + 22) = 555
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 533 → 555; recarga Respirar Fundo 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 555 → 555
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 607
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #44** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 120 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 95; teste `91 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 121 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 30; teste `67 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 2748 → 2475 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 2475 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 122 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **16**; chance 1.68; teste `16 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3213 → 3248; mp 607 → 555; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2748 → 2475

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 159 → min(1050, 159 + 21) = 180
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 159 → 180; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 180 → 180
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 241
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #45** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 123 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **99**; chance 72; teste `99 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 3248 → 3248)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 241 → 180; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 27.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2475/5519 | 3248/5977 |
| MP | 180/1050 | 555/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Golpe Poderoso 1, Soco de Placa 2 | Respirar Fundo 4, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 0; cura 35
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 273; cura 0


## Rodada 28

### 28.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2475/5519 | 3248/5977 |
| MP | 180/1050 | 555/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Golpe Poderoso 1, Soco de Placa 2 | Respirar Fundo 4, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 28.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 28): eu HP 2475/5519, MP 180/1050, efeitos —, buffs —; adversário fer HP 3248/5977, MP 555/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.112±0.003 com Tomar Fôlego; contra ataque básico 0.107, Golpe Poderoso 0.106, Gancho e Corda 0.097; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 28): eu HP 3248/5977, MP 555/1103, efeitos —, buffs —; adversário Tenz HP 2475/5519, MP 180/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 3
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.631±0.017 com Soco de Placa; contra ataque básico 0.618, Juramento da Muralha 0.553; dano esperado 297; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Soco de Placa

### 28.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 4 → 3; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 494 → min(1103, 494 + 22) = 516
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 494 → 516; recarga Golpe Poderoso 2 → 1; recarga Respirar Fundo 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 516 → 516
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 577
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #46** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 124 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **87**; chance 95; teste `87 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 125 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **71**; chance 30; teste `71 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 2475 → 2187 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2187 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 126 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **7**; chance 1.68; teste `7 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 127 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 29.4; teste `81 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3248 → 3285; mp 577 → 516; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 2475 → 2187

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 87 → min(1050, 87 + 21) = 108
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 87 → 108; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 108 → 108
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 201
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 2187 → 2849; mp 201 → 108; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 28.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2849/5519 | 3285/5977 |
| MP | 108/1050 | 516/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Tomar Fôlego 5 | Respirar Fundo 3, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 37
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 662


## Rodada 29

### 29.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2849/5519 | 3285/5977 |
| MP | 108/1050 | 516/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1, Tomar Fôlego 5 | Respirar Fundo 3, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 29.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 29): eu HP 2849/5519, MP 108/1050, efeitos —, buffs —; adversário fer HP 3285/5977, MP 516/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.116±0.004 com ataque básico; contra Golpe Poderoso 0.115, Soco de Placa 0.114; dano esperado 144
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 29): eu HP 3285/5977, MP 516/1103, efeitos —, buffs —; adversário Tenz HP 2849/5519, MP 108/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 2
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.537±0.023 com Golpe Poderoso; contra ataque básico 0.535, Juramento da Muralha 0.506; dano esperado 283; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 29.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 3 → 2; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 464 → min(1103, 464 + 22) = 486
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 464 → 486; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 3 → 2; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 486 → 486
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 538
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #47** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 128 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 95; teste `2 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 129 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **36**; chance 30; teste `36 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 2849 → 2576 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 2576 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 130 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **77**; chance 1.68; teste `77 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3285 → 3320; mp 538 → 486; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2849 → 2576

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 108 → min(1050, 108 + 21) = 129
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 108 → 129; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 129 → 129
- Perde a oportunidade por controle: não

**Golpe #48** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 131 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **32**; chance 72; teste `32 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 132 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **59**; chance 15; teste `59 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 3320 → 3141 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3141 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 29.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2613/5519 | 3141/5977 |
| MP | 129/1050 | 486/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Respirar Fundo 2, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 179; cura 35
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 273; cura 37


## Rodada 30

### 30.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2613/5519 | 3141/5977 |
| MP | 129/1050 | 486/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Respirar Fundo 2, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 30.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 30): eu HP 2613/5519, MP 129/1050, efeitos —, buffs —; adversário fer HP 3141/5977, MP 486/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.115±0.006 com Soco de Placa; contra ataque básico 0.112, Golpe Poderoso 0.112, Gancho e Corda 0.100; dano esperado 257; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 30): eu HP 3141/5977, MP 486/1103, efeitos —, buffs —; adversário Tenz HP 2613/5519, MP 129/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 1
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.548±0.020 com Soco de Placa; contra ataque básico 0.547, Juramento da Muralha 0.510; dano esperado 295; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Soco de Placa

### 30.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 2 → 1; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 425 → min(1103, 425 + 22) = 447
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 425 → 447; recarga Golpe Poderoso 2 → 1; recarga Respirar Fundo 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 447 → 447
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 508
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #49** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 133 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 95; teste `85 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 134 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **82**; chance 30; teste `82 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 2613 → 2325 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2325 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 135 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **22**; chance 1.68; teste `22 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 136 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **86**; chance 29.4; teste `86 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3141 → 3178; mp 508 → 447; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 2613 → 2325

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 68 → min(1050, 68 + 21) = 89
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 68 → 89; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 89 → 89
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 150
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #50** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 137 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **98**; chance 72; teste `98 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 3178 → 3178)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: mp 150 → 89; recarga Soco de Placa — → 2
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 0.

### 30.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2325/5519 | 3178/5977 |
| MP | 89/1050 | 447/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Soco de Placa 2 | Respirar Fundo 1, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 37
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 0


## Rodada 31

### 31.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2325/5519 | 3178/5977 |
| MP | 89/1050 | 447/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Soco de Placa 2 | Respirar Fundo 1, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 31.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 31): eu HP 2325/5519, MP 89/1050, efeitos —, buffs —; adversário fer HP 3178/5977, MP 447/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.092±0.008 com ataque básico; contra Golpe Poderoso 0.091; dano esperado 144
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 31): eu HP 3178/5977, MP 447/1103, efeitos —, buffs —; adversário Tenz HP 2325/5519, MP 89/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.618±0.016 com Golpe Poderoso; contra ataque básico 0.617, Respirar Fundo 0.573, Juramento da Muralha 0.534; dano esperado 279; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 31.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 1 → livre; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 395 → min(1103, 395 + 22) = 417
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 395 → 417; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 417 → 417
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 469
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #51** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 138 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **72**; chance 95; teste `72 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 139 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **96**; chance 30; teste `96 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 2325 → 2052 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 2052 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 140 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 1.68; teste `91 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3178 → 3213; mp 469 → 417; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2325 → 2052

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 89 → min(1050, 89 + 21) = 110
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 89 → 110; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 110 → 110
- Perde a oportunidade por controle: não

**Golpe #52** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 141 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **81**; chance 72; teste `81 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 3213 → 3213)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 31.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2052/5519 | 3213/5977 |
| MP | 110/1050 | 417/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 0; cura 35
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 273; cura 0


## Rodada 32

### 32.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2052/5519 | 3213/5977 |
| MP | 110/1050 | 417/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2, Soco de Placa 1 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 32.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 32): eu HP 2052/5519, MP 110/1050, efeitos —, buffs —; adversário fer HP 3213/5977, MP 417/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.086±0.003 com ataque básico; contra Soco de Placa 0.084, Golpe Poderoso 0.084; dano esperado 144
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 32): eu HP 3213/5977, MP 417/1103, efeitos —, buffs —; adversário Tenz HP 2052/5519, MP 110/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.670±0.022 com Soco de Placa; contra ataque básico 0.666, Respirar Fundo 0.624, Juramento da Muralha 0.578; dano esperado 293; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 32.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 356 → min(1103, 356 + 22) = 378
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 356 → 378; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 378 → 378
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 439
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #53** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 142 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **22**; chance 95; teste `22 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 143 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 30; teste `45 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 2052 → 1764 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 1764 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 144 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **30**; chance 1.68; teste `30 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 145 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **37**; chance 29.4; teste `37 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 3213 → 3250; mp 439 → 378; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 2052 → 1764

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1; Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 110 → min(1050, 110 + 21) = 131
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 110 → 131; recarga Soco de Placa 1 → livre; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 131 → 131
- Perde a oportunidade por controle: não

**Golpe #54** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 146 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **61**; chance 72; teste `61 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 147 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **27**; chance 15; teste `27 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 3250 → 3071 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 3071 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 32.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1801/5519 | 3071/5977 |
| MP | 131/1050 | 378/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 179; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 288; cura 37


## Rodada 33

### 33.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1801/5519 | 3071/5977 |
| MP | 131/1050 | 378/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 33.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 33): eu HP 1801/5519, MP 131/1050, efeitos —, buffs —; adversário fer HP 3071/5977, MP 378/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.088±0.007 com Tomar Fôlego; contra Golpe Poderoso 0.087, Soco de Placa 0.085, ataque básico 0.084; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 33): eu HP 3071/5977, MP 378/1103, efeitos —, buffs —; adversário Tenz HP 1801/5519, MP 131/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.679±0.029 com ataque básico; contra Golpe Poderoso 0.672, Respirar Fundo 0.634, Juramento da Muralha 0.578; dano esperado 163
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Ataque básico

### 33.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 378 → min(1103, 378 + 22) = 400
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 378 → 400; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 400 → 400
- Perde a oportunidade por controle: não

**Golpe #55** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 148 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 95; teste `35 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 149 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 30; teste `35 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 1801 → 1640 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +20 (teto do HP máximo)
24. Morte e death_ignore: HP final 1640 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 150 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **3**; chance 1.68; teste `3 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 38 → min(1050, 38 + 21) = 59
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 38 → 59; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 59 → 59
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 152
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 1640 → 2302; mp 152 → 59; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 33.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2302/5519 | 3091/5977 |
| MP | 59/1050 | 400/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 5 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 0; cura 20
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 161; cura 662


## Rodada 34

### 34.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 2302/5519 | 3091/5977 |
| MP | 59/1050 | 400/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 5 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 34.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 34): eu HP 2302/5519, MP 59/1050, efeitos —, buffs —; adversário fer HP 3091/5977, MP 400/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.099±0.006 com Golpe Poderoso; contra ataque básico 0.096; dano esperado 245; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

**fer (p2)**

- Estado recebido (`DuelView`, rodada 34): eu HP 3091/5977, MP 400/1103, efeitos —, buffs —; adversário Tenz HP 2302/5519, MP 59/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.621±0.022 com Golpe Poderoso; contra Soco de Placa 0.619, ataque básico 0.616, Respirar Fundo 0.598; dano esperado 276; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **52 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Golpe Poderoso; fer (p2) = Golpe Poderoso

### 34.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 348 → min(1103, 348 + 22) = 370
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 348 → 370; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 370 → 370
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 422
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #56** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 151 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **23**; chance 95; teste `23 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 152 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 30; teste `11 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 2302 → 1864 (retirado 438)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 1864 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 153 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **85**; chance 1.68; teste `85 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 3091 → 3147; mp 422 → 370; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 2302 → 1864

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 438.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 7 → min(1050, 7 + 21) = 28
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 7 → 28; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 998 → MP 28 → 28
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 80
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #57** — Tenz (p1) → fer (p2), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 2.86 = 2079.8205999999996; max(1, int(601.0 × (1 + 21/100) × 2.86)) = **2079**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 154 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **51**; chance 72; teste `51 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 155 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **99**; chance 15; teste `99 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2079.0 × 1.0 × 1.0 × 0.16583747927031509 = 344.77611940298505; max(1, int(bruto)) = 344 → int(anterior × 1.0) = 344 → int(anterior × 0.89) = 306
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **306**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 306
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(306)`; HP do alvo 3147 → 2841 (retirado 306)
23. Roubo de vida: 21.0% → max(1, int(306 × 21 / 100)) = 64; HP do atacante +64 (teto do HP máximo)
24. Morte e death_ignore: HP final 2841 → o alvo segue vivo

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 1864 → 1928; mp 80 → 28; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 3147 → 2841

- Motor (`action_executed`): Tenz (p1) executou Golpe Poderoso; MP gasto 52, dano ao adversário 306.

### 34.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1928/5519 | 2841/5977 |
| MP | 28/1050 | 370/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4, Golpe Poderoso 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 306; cura 56
- Tenz (p1): Golpe Poderoso — executada; dano causado na rodada 306 (golpes e DoT), recebido 438; cura 64


## Rodada 35

### 35.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1928/5519 | 2841/5977 |
| MP | 28/1050 | 370/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4, Golpe Poderoso 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 35.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 35): eu HP 1928/5519, MP 28/1050, efeitos —, buffs —; adversário fer HP 2841/5977, MP 370/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: recarga, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 35): eu HP 2841/5977, MP 370/1103, efeitos —, buffs —; adversário Tenz HP 1928/5519, MP 28/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.690±0.032 com Soco de Placa; contra ataque básico 0.678, Respirar Fundo 0.665, Juramento da Muralha 0.591; dano esperado 296; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 35.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 309 → min(1103, 309 + 22) = 331
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 309 → 331; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 331 → 331
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 392
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #58** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 156 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **65**; chance 95; teste `65 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 157 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **75**; chance 30; teste `75 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 1928 → 1640 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 1640 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 158 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **100**; chance 1.68; teste `100 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 159 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 29.4; teste `11 > 29.4` (operador `>`) é falso ⇒ **passou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Duração pedida 2 → após leis (nenhuma) 2; o núcleo decide empilhar/renovar: aplicou
- Instâncias de `weakened` no alvo antes: —; depois: [{'duration': 2, 'stacks': 1, 'intensity': 20.0, 'source_id': 'soco_de_placa'}]

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2841 → 2878; mp 392 → 331; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 1928 → 1640; st 601 → 480; efeito weakened entra (dur 2, stacks 1, int 20.0)

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 28 → min(1050, 28 + 21) = 49
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 28 → 49; recarga Golpe Poderoso 2 → 1; recarga Tomar Fôlego 4 → 3; efeito weakened: dur 2 → 1, stacks 1 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 49 → 49
- Perde a oportunidade por controle: não

**Golpe #59** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 480.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 930.4; dano médio max(1, int(930.4 × (1 + 21/100))) = 1125; BASE do básico = max(1, int(1125 × 0.9)) = **1012** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 160 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **91**; chance 72; teste `91 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 2878 → 2878)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 35.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1640/5519 | 2878/5977 |
| MP | 49/1050 | 331/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 0


## Rodada 36

### 36.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1640/5519 | 2878/5977 |
| MP | 49/1050 | 331/1103 |
| ST / MG / AG / DF | 480 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3, Golpe Poderoso 1 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | weakened (dur 1, stacks 1, int 20.0, fonte soco_de_placa) | — |
| death_ignore gasto / vivo | False / True | False / True |

### 36.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 36): eu HP 1640/5519, MP 49/1050, efeitos ['weakened'], buffs —; adversário fer HP 2878/5977, MP 331/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 36): eu HP 2878/5977, MP 331/1103, efeitos —, buffs —; adversário Tenz HP 1640/5519, MP 49/1050, efeitos ['weakened'], buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.728±0.026 com Golpe Poderoso; contra ataque básico 0.712, Respirar Fundo 0.704, Juramento da Muralha 0.612; dano esperado 280; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 36.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 480.0 | 512.3333333333334 | 0.936890045543266 | 0.9679308061753515 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.016478945448366
- ÷ 6 = build 1.002746490908061
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.002746490908061 × 1.0 = 1.002746490908061**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.002746490908061 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 279 → min(1103, 279 + 22) = 301
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 279 → 301; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 301 → 301
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 353
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #60** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 161 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **48**; chance 95; teste `48 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 162 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 30; teste `56 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 1640 → 1367 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 1367 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 163 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 1.68; teste `45 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2878 → 2913; mp 353 → 301; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 1640 → 1367

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2; Golpe Poderoso 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 49 → min(1050, 49 + 21) = 70
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados ['weakened'], leis —, pula a vez: False
- Mudanças de estado no início: mp 49 → 70; st 480 → 601; recarga Golpe Poderoso 1 → livre; recarga Tomar Fôlego 3 → 2; efeito weakened sai
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 70 → 70
- Perde a oportunidade por controle: não

**Golpe #61** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 164 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 72; teste `11 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 165 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **84**; chance 15; teste `84 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 2913 → 2734 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2734 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 36.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1404/5519 | 2734/5977 |
| MP | 70/1050 | 301/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 179; cura 35
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 273; cura 37


## Rodada 37

### 37.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1404/5519 | 2734/5977 |
| MP | 70/1050 | 301/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 37.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 37): eu HP 1404/5519, MP 70/1050, efeitos —, buffs —; adversário fer HP 2734/5977, MP 301/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.072±0.005 com Soco de Placa; contra ataque básico 0.071, Golpe Poderoso 0.070; dano esperado 312; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

**fer (p2)**

- Estado recebido (`DuelView`, rodada 37): eu HP 2734/5977, MP 301/1103, efeitos —, buffs —; adversário Tenz HP 1404/5519, MP 70/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Respirar Fundo, Rendição
- Escolha: **Respirar Fundo** — justificativa da política: P(vitória) 0.774±0.023 com Respirar Fundo; contra Soco de Placa 0.747, ataque básico 0.744, Juramento da Muralha 0.652; custa 82 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 82

- Lock: Tenz (p1) reserva **61 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **82 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Soco de Placa; fer (p2) = Respirar Fundo

### 37.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 219 → min(1103, 219 + 22) = 241
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 219 → 241; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 82, teto livre 1021 → MP 241 → 241
- Perde a oportunidade por controle: não

**Skill Respirar Fundo** (`n_respirar_fundo`) de fer (p2)

- Tipo `heal`, valor 10 ; alvo declarado `self` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 82 MP; reserva feita no lock 82; MP disponível na cobrança (livre + reserva liberada) 323
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5977 × 10 / 100)) = 597; potion_heal_bonus 0.0% → total 597

- Resultado da skill: `heal`; MP debitado 82; recarga depois 5; cura 597
- Mudanças em quem lançou: hp 2734 → 3331; mp 323 → 241; recarga Respirar Fundo — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): fer (p2) executou Respirar Fundo; MP gasto 82, dano ao adversário 0.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 9 → min(1050, 9 + 21) = 30
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 9 → 30; recarga Tomar Fôlego 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 989 → MP 30 → 30
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de Tenz (p1)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe fer (p2)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 91
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #62** — Tenz (p1) → fer (p2), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 601.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 601.0; × arma = 727.2099999999999; × power 3.012 = 2190.35652; max(1, int(601.0 × (1 + 21/100) × 3.012)) = **2190**
4. Bônus de arma: +21.0% → fator 1.21
5. Modificadores condicionais: condição `caster_wounded` satisfeita contra este alvo
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 166 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **54**; chance 72; teste `54 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 167 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **14**; chance 15; teste `14 <= 15` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: condição da carta (caster_wounded) 0.2 → 1 + Σ = 1.2
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2190.0 × 1.2 × 1.6 × 0.16583747927031509 = 697.3134328358209; max(1, int(bruto)) = 697 → int(anterior × 1.0) = 697 → int(anterior × 0.89) = 620
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **620**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 620
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(620)`; HP do alvo 3331 → 2711 (retirado 620)
23. Roubo de vida: 21.0% → max(1, int(620 × 21 / 100)) = 130; HP do atacante +130 (teto do HP máximo)
24. Morte e death_ignore: HP final 2711 → o alvo segue vivo

**Status `weakened`** sobre fer (p2) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 0.0% → efetiva 35 × (1 − 0/100) = 35.0%
- sorteio nº 168 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **79**; chance 35.0; teste `79 > 35.0` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 1404 → 1534; mp 91 → 30; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 3331 → 2711

- Motor (`action_executed`): Tenz (p1) executou Soco de Placa; MP gasto 61, dano ao adversário 620.

### 37.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1534/5519 | 2711/5977 |
| MP | 30/1050 | 241/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 2 | Golpe Poderoso 1, Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Respirar Fundo — executada; dano causado na rodada 0 (golpes e DoT), recebido 620; cura 597
- Tenz (p1): Soco de Placa — executada; dano causado na rodada 620 (golpes e DoT), recebido 0; cura 130


## Rodada 38

### 38.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1534/5519 | 2711/5977 |
| MP | 30/1050 | 241/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 1, Soco de Placa 2 | Golpe Poderoso 1, Respirar Fundo 5 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 38.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 38): eu HP 1534/5519, MP 30/1050, efeitos —, buffs —; adversário fer HP 2711/5977, MP 241/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 1, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: recarga, Tomar Fôlego: mp)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 38): eu HP 2711/5977, MP 241/1103, efeitos —, buffs —; adversário Tenz HP 1534/5519, MP 30/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 4
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.803±0.023 com Golpe Poderoso; contra Soco de Placa 0.800, ataque básico 0.794, Juramento da Muralha 0.657; dano esperado 278; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 38.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Respirar Fundo 5 → 4
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 189 → min(1103, 189 + 22) = 211
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 189 → 211; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 211 → 211
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 263
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #63** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 169 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 95; teste `45 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 170 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 30; teste `2 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 1534 → 1096 (retirado 438)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 1096 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 171 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **26**; chance 1.68; teste `26 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2711 → 2767; mp 263 → 211; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 1534 → 1096

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 438.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 30 → min(1050, 30 + 21) = 51
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 30 → 51; recarga Soco de Placa 2 → 1; recarga Tomar Fôlego 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 51 → 51
- Perde a oportunidade por controle: não

**Golpe #64** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 172 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **95**; chance 72; teste `95 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 2767 → 2767)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 38.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1096/5519 | 2767/5977 |
| MP | 51/1050 | 211/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1 | Respirar Fundo 4, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 0; cura 56
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 438; cura 0


## Rodada 39

### 39.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 1096/5519 | 2767/5977 |
| MP | 51/1050 | 211/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Soco de Placa 1 | Respirar Fundo 4, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 39.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 39): eu HP 1096/5519, MP 51/1050, efeitos —, buffs —; adversário fer HP 2767/5977, MP 211/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: mp)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 39): eu HP 2767/5977, MP 211/1103, efeitos —, buffs —; adversário Tenz HP 1096/5519, MP 51/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 3
- Ações legais: Ataque básico, Juramento da Muralha, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.892±0.028 com Soco de Placa; contra ataque básico 0.877, Juramento da Muralha 0.771; dano esperado 300; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 39.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 4 → 3; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 150 → min(1103, 150 + 22) = 172
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 150 → 172; recarga Golpe Poderoso 2 → 1; recarga Respirar Fundo 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 172 → 172
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 233
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #65** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 173 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **4**; chance 95; teste `4 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 174 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **88**; chance 30; teste `88 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 1096 → 808 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 808 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 175 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **96**; chance 1.68; teste `96 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 176 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 29.4; teste `67 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2767 → 2804; mp 233 → 172; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 1096 → 808

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 51 → min(1050, 51 + 21) = 72
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 51 → 72; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 72 → 72
- Perde a oportunidade por controle: não

**Golpe #66** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 177 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 72; teste `97 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 2804 → 2804)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 39.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 808/5519 | 2804/5977 |
| MP | 72/1050 | 172/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 3, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 0; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 288; cura 0


## Rodada 40

### 40.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 808/5519 | 2804/5977 |
| MP | 72/1050 | 172/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 3, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 40.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 40): eu HP 808/5519, MP 72/1050, efeitos —, buffs —; adversário fer HP 2804/5977, MP 172/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.040±0.008 com ataque básico; contra Golpe Poderoso 0.032, Soco de Placa 0.032; dano esperado 136
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 40): eu HP 2804/5977, MP 172/1103, efeitos —, buffs —; adversário Tenz HP 808/5519, MP 72/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 2
- Ações legais: Ataque básico, Golpe Poderoso, Juramento da Muralha, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.901±0.011 com Golpe Poderoso; contra ataque básico 0.893, Juramento da Muralha 0.847; dano esperado 284; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 40.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 3 → 2; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 120 → min(1103, 120 + 22) = 142
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 120 → 142; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 3 → 2; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 142 → 142
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 194
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #67** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 178 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **32**; chance 95; teste `32 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 179 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **80**; chance 30; teste `80 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 808 → 535 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 535 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 180 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **46**; chance 1.68; teste `46 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2804 → 2839; mp 194 → 142; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 808 → 535

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 72 → min(1050, 72 + 21) = 93
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 72 → 93
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 93 → 93
- Perde a oportunidade por controle: não

**Golpe #68** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: não calculados — o golpe errou antes do funil.
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 181 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **97**; chance 72; teste `97 > 72` (operador `>`) é verdadeiro ⇒ **ERROU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
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
22. Dano aplicado ao HP: 0 (HP do alvo 2839 → 2839)
23. Roubo de vida: inaplicável (sem dano).
24. Morte / death_ignore: não verificado — sem dano.

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 0.

### 40.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 535/5519 | 2839/5977 |
| MP | 93/1050 | 142/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 2, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 0; cura 35
- Tenz (p1): Ataque básico — executada; dano causado na rodada 0 (golpes e DoT), recebido 273; cura 0


## Rodada 41

### 41.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 535/5519 | 2839/5977 |
| MP | 93/1050 | 142/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 2, Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 41.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 41): eu HP 535/5519, MP 93/1050, efeitos —, buffs —; adversário fer HP 2839/5977, MP 142/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Tomar Fôlego, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.034±0.009 com ataque básico; contra Golpe Poderoso 0.032, Soco de Placa 0.032, Tomar Fôlego 0.031; dano esperado 136
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 41): eu HP 2839/5977, MP 142/1103, efeitos —, buffs —; adversário Tenz HP 535/5519, MP 93/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 1
- Ações legais: Ataque básico, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.919±0.014 com Soco de Placa; contra ataque básico 0.893; dano esperado 299; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 41.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 2 → 1; Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 81 → min(1103, 81 + 22) = 103
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 81 → 103; recarga Golpe Poderoso 2 → 1; recarga Respirar Fundo 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 103 → 103
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 164
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #69** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 182 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **67**; chance 95; teste `67 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 183 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **74**; chance 30; teste `74 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 535 → 247 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 247 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 184 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **83**; chance 1.68; teste `83 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 185 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **44**; chance 29.4; teste `44 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2839 → 2876; mp 164 → 103; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 535 → 247

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 93 → min(1050, 93 + 21) = 114
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 93 → 114
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 114 → 114
- Perde a oportunidade por controle: não

**Golpe #70** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 186 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **23**; chance 72; teste `23 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 187 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **12**; chance 15; teste `12 <= 15` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.6 × 0.16583747927031509 = 324.7761194029851; max(1, int(bruto)) = 324 → int(anterior × 1.0) = 324 → int(anterior × 0.89) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 2876 → 2588 (retirado 288)
23. Roubo de vida: 21.0% → max(1, int(288 × 21 / 100)) = 60; HP do atacante +60 (teto do HP máximo)
24. Morte e death_ignore: HP final 2588 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 288.

### 41.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 307/5519 | 2588/5977 |
| MP | 114/1050 | 103/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 1, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 288; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 288 (golpes e DoT), recebido 288; cura 60


## Rodada 42

### 42.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 307/5519 | 2588/5977 |
| MP | 114/1050 | 103/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | — | Respirar Fundo 1, Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | False / True | False / True |

### 42.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 42): eu HP 307/5519, MP 114/1050, efeitos —, buffs —; adversário fer HP 2588/5977, MP 103/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 0
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Tomar Fôlego, Rendição
- Escolha: **Tomar Fôlego** — justificativa da política: P(vitória) 0.047±0.002 com Tomar Fôlego; contra ataque básico 0.042, Golpe Poderoso 0.028, Soco de Placa 0.028; custa 93 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 93

**fer (p2)**

- Estado recebido (`DuelView`, rodada 42): eu HP 2588/5977, MP 103/1103, efeitos —, buffs —; adversário Tenz HP 307/5519, MP 114/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Respirar Fundo, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.979±0.006 com Golpe Poderoso; contra Respirar Fundo 0.919, ataque básico 0.919; dano esperado 280; chance de derrubar já 28%; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: Tenz (p1) reserva **93 MP** (sai do caixa livre agora).
- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Tomar Fôlego; fer (p2) = Golpe Poderoso

### 42.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Respirar Fundo 1 → livre; Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 51 → min(1103, 51 + 22) = 73
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 51 → 73; recarga Golpe Poderoso 1 → livre; recarga Respirar Fundo 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 73 → 73
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 125
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #71** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 188 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **46**; chance 95; teste `46 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 189 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **23**; chance 30; teste `23 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.6 × 0.16420361247947454 = 555.1395730706075; max(1, int(bruto)) = 555 → int(anterior × 1.0) = 555 → int(anterior × 0.79) = 438
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **438**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 438
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(438)`; HP do alvo 307 → 1 (retirado 306)
23. Roubo de vida: 13.0% → max(1, int(438 × 13 / 100)) = 56; HP do atacante +56 (teto do HP máximo)
24. Morte e death_ignore: HP final 1 → golpe letal anulado por `death_ignore`: HP fixado em 1, uma vez por combate

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 190 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **29**; chance 1.68; teste `29 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2588 → 2644; mp 125 → 73; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 307 → 1; death_ignore gasto

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 306.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): nenhuma
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 21 → min(1050, 21 + 21) = 42
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 21 → 42
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 93, teto livre 957 → MP 42 → 42
- Perde a oportunidade por controle: não

**Skill Tomar Fôlego** (`tomar_folego`) de Tenz (p1)

- Tipo `heal`, valor 12 ; alvo declarado `self` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 93 MP; reserva feita no lock 93; MP disponível na cobrança (livre + reserva liberada) 135
- Recarga antes do uso: 0; declarada 4 (o motor grava declarada + 1)
- Cura: max(1, int(5519 × 12 / 100)) = 662; potion_heal_bonus 0.0% → total 662

- Resultado da skill: `heal`; MP debitado 93; recarga depois 5; cura 662
- Mudanças em quem lançou: hp 1 → 663; mp 135 → 42; recarga Tomar Fôlego — → 5
- Mudanças no adversário: nenhuma

- Motor (`action_executed`): Tenz (p1) executou Tomar Fôlego; MP gasto 93, dano ao adversário 0.

### 42.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 663/5519 | 2644/5977 |
| MP | 42/1050 | 73/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 5 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 438 (golpes e DoT), recebido 0; cura 56
- Tenz (p1): Tomar Fôlego — executada; dano causado na rodada 0 (golpes e DoT), recebido 438; cura 662


## Rodada 43

### 43.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 663/5519 | 2644/5977 |
| MP | 42/1050 | 73/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 5 | Soco de Placa 1, Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

### 43.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 43): eu HP 663/5519, MP 42/1050, efeitos —, buffs —; adversário fer HP 2644/5977, MP 73/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 4
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 43): eu HP 2644/5977, MP 73/1103, efeitos —, buffs —; adversário Tenz HP 663/5519, MP 42/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Soco de Placa, Rendição
- Escolha: **Soco de Placa** — justificativa da política: P(vitória) 0.951±0.016 com Soco de Placa; contra ataque básico 0.857; dano esperado 295; custa 61 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 61

- Lock: fer (p2) reserva **61 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Soco de Placa

### 43.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre; Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 12 → min(1103, 12 + 22) = 34
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 12 → 34; recarga Golpe Poderoso 2 → 1; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 61, teto livre 1042 → MP 34 → 34
- Perde a oportunidade por controle: não

**Skill Soco de Placa** (`soco_de_placa`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 61 MP; reserva feita no lock 61; MP disponível na cobrança (livre + reserva liberada) 95
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #72** — fer (p2) → Tenz (p1), skill `soco_de_placa`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 3.012 = 2225.9282399999997; max(1, int(654.0 × (1 + 13/100) × 3.012)) = **2225**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `caster_wounded` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 191 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **47**; chance 95; teste `47 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 192 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **41**; chance 30; teste `41 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2225.0 × 1.0 × 1.0 × 0.16420361247947454 = 365.3530377668309; max(1, int(bruto)) = 365 → int(anterior × 1.0) = 365 → int(anterior × 0.79) = 288
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **288**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 288
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(288)`; HP do alvo 663 → 375 (retirado 288)
23. Roubo de vida: 13.0% → max(1, int(288 × 13 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 375 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 193 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **11**; chance 1.68; teste `11 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

**Status `weakened`** sobre Tenz (p1) (via `_aplicar_secundario`, fonte `soco_de_placa`)

- Chance base 35%; resistência do alvo 16.0% → efetiva 35 × (1 − 16/100) = 29.4%
- sorteio nº 194 [aplicação de status (weakened)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **59**; chance 29.4; teste `59 > 29.4` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `weakened` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 61; recarga depois 2
- Mudanças em quem lançou: hp 2644 → 2681; mp 95 → 34; recarga Soco de Placa — → 2
- Mudanças no adversário: hp 663 → 375

- Motor (`action_executed`): fer (p2) executou Soco de Placa; MP gasto 61, dano ao adversário 288.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 5 → 4
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 42 → min(1050, 42 + 21) = 63
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 42 → 63; recarga Tomar Fôlego 5 → 4
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 63 → 63
- Perde a oportunidade por controle: não

**Golpe #73** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 195 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **39**; chance 72; teste `39 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 196 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **82**; chance 15; teste `82 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 2681 → 2502 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2502 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 43.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 412/5519 | 2502/5977 |
| MP | 63/1050 | 34/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Soco de Placa — executada; dano causado na rodada 288 (golpes e DoT), recebido 179; cura 37
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 288; cura 37


## Rodada 44

### 44.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 412/5519 | 2502/5977 |
| MP | 63/1050 | 34/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 4 | Golpe Poderoso 1, Soco de Placa 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

### 44.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 44): eu HP 412/5519, MP 63/1050, efeitos —, buffs —; adversário fer HP 2502/5977, MP 34/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 3
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.005±0.006 com ataque básico; contra Soco de Placa 0.005, Golpe Poderoso 0.004; dano esperado 139
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 44): eu HP 2502/5977, MP 34/1103, efeitos —, buffs —; adversário Tenz HP 412/5519, MP 63/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 1, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: mp, Juramento da Muralha: mp, Respirar Fundo: mp, Soco de Placa: recarga)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Ataque básico

### 44.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 1 → livre; Soco de Placa 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 34 → min(1103, 34 + 22) = 56
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 34 → 56; recarga Golpe Poderoso 1 → livre; recarga Soco de Placa 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 56 → 56
- Perde a oportunidade por controle: não

**Golpe #74** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 197 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **10**; chance 95; teste `10 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 198 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **53**; chance 30; teste `53 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.0 × 0.16420361247947454 = 204.4334975369458; max(1, int(bruto)) = 204 → int(anterior × 1.0) = 204 → int(anterior × 0.79) = 161
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **161**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 161
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(161)`; HP do alvo 412 → 251 (retirado 161)
23. Roubo de vida: 13.0% → max(1, int(161 × 13 / 100)) = 20; HP do atacante +20 (teto do HP máximo)
24. Morte e death_ignore: HP final 251 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 199 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **25**; chance 1.68; teste `25 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 161.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 4 → 3
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 63 → min(1050, 63 + 21) = 84
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 63 → 84; recarga Tomar Fôlego 4 → 3
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 84 → 84
- Perde a oportunidade por controle: não

**Golpe #75** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 200 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **59**; chance 72; teste `59 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 201 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **92**; chance 15; teste `92 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 2522 → 2343 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2343 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 44.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 288/5519 | 2343/5977 |
| MP | 84/1050 | 56/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 161 (golpes e DoT), recebido 179; cura 20
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 161; cura 37


## Rodada 45

### 45.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 288/5519 | 2343/5977 |
| MP | 84/1050 | 56/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 3 | Soco de Placa 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

### 45.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 45): eu HP 288/5519, MP 84/1050, efeitos —, buffs —; adversário fer HP 2343/5977, MP 56/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 2
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.000±0.000 com ataque básico; contra Golpe Poderoso 0.000, Soco de Placa 0.000; dano esperado 140
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 45): eu HP 2343/5977, MP 56/1103, efeitos —, buffs —; adversário Tenz HP 288/5519, MP 84/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Golpe Poderoso, Rendição
- Escolha: **Golpe Poderoso** — justificativa da política: P(vitória) 0.958±0.008 com Golpe Poderoso; contra ataque básico 0.955; dano esperado 276; chance de derrubar já 28%; custa 52 MP
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 52

- Lock: fer (p2) reserva **52 MP** (sai do caixa livre agora).
- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Golpe Poderoso

### 45.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Soco de Placa 1 → livre
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 4 → min(1103, 4 + 22) = 26
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 4 → 26; recarga Soco de Placa 1 → livre
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 52, teto livre 1051 → MP 26 → 26
- Perde a oportunidade por controle: não

**Skill Golpe Poderoso** (`golpe_poderoso`) de fer (p2)

- Tipo `damage`, valor 0 ; alvo declarado `enemy` → recebe Tenz (p1)
- Requisito de equipamento: nenhum → atendido: True
- Custo 52 MP; reserva feita no lock 52; MP disponível na cobrança (livre + reserva liberada) 78
- Recarga antes do uso: 0; declarada 1 (o motor grava declarada + 1)

**Golpe #76** — fer (p2) → Tenz (p1), skill `golpe_poderoso`

1. Atributos ofensivos efetivos: st 654.0
2. Pesos (da carta): st 1.0
3. Poder básico da ação: Σ = 654.0; × arma = 739.02; × power 2.86 = 2113.5971999999997; max(1, int(654.0 × (1 + 13/100) × 2.86)) = **2113**
4. Bônus de arma: +13.0% → fator 1.13
5. Modificadores condicionais: condição `target_healthy` não satisfeita contra este alvo
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 202 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **78**; chance 95; teste `78 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 203 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **94**; chance 30; teste `94 <= 30` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 2113.0 × 1.0 × 1.0 × 0.16420361247947454 = 346.9622331691297; max(1, int(bruto)) = 346 → int(anterior × 1.0) = 346 → int(anterior × 0.79) = 273
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **273**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 273
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(273)`; HP do alvo 288 → 15 (retirado 273)
23. Roubo de vida: 13.0% → max(1, int(273 × 13 / 100)) = 35; HP do atacante +35 (teto do HP máximo)
24. Morte e death_ignore: HP final 15 → o alvo segue vivo

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 204 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **34**; chance 1.68; teste `34 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Resultado da skill: `damage`; MP debitado 52; recarga depois 2
- Mudanças em quem lançou: hp 2343 → 2378; mp 78 → 26; recarga Golpe Poderoso — → 2
- Mudanças no adversário: hp 288 → 15

- Motor (`action_executed`): fer (p2) executou Golpe Poderoso; MP gasto 52, dano ao adversário 273.

### Oportunidade de Tenz (p1)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Tomar Fôlego 3 → 2
- Regeneração de MP: max(1, 1050 × 2 / 100) = 21.0; + mana_regen 0.0 → int(0 + 21.0) = **21**; MP livre 84 → min(1050, 84 + 21) = 105
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 84 → 105; recarga Tomar Fôlego 3 → 2
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1050 → MP 105 → 105
- Perde a oportunidade por controle: não

**Golpe #77** — Tenz (p1) → fer (p2), ataque básico

1. Atributos ofensivos efetivos: st 601.0, mg 406.0, ag 121.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1124.0; dano médio max(1, int(1124.0 × (1 + 21/100))) = 1360; BASE do básico = max(1, int(1360 × 0.9)) = **1224** (multiplicador do básico 0.9)
4. Bônus de arma: +21.0% → fator 1.21 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing -2.3954372623574143 (30 × (121 − 142) / 263) − evasão 15.0 + medo/precisão temporários 0 + precisão 5.0 + modificador da ação 0 − ocultação 0 = 72.60456273764258 → clamp [20, 95] e int → **72**
7. Rolagem de acerto: sorteio nº 205 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **50**; chance 72; teste `50 > 72` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 15 = 15, teto 75 → **15**
9. Rolagem de crítico: sorteio nº 206 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **45**; chance 15; teste `45 <= 15` (operador `<=`) é falso ⇒ **sem crítico** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: não aplicado (sem crítico)
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: nenhuma parcela (×1.0)
13. Produto ×MULT bruto 1.0; `XMULT_CAP` 5.0 → aplicado 1.0
14. Defesa efetiva do alvo: 503
15. Fator de defesa: 100 / (100 + 503) = 0.16583747927031509
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.89 (damage_reduction 11.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1224.0 × 1.0 × 1.0 × 0.16583747927031509 = 202.98507462686567; max(1, int(bruto)) = 202 → int(anterior × 1.0) = 202 → int(anterior × 0.89) = 179
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **179**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 179
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(179)`; HP do alvo 2378 → 2199 (retirado 179)
23. Roubo de vida: 21.0% → max(1, int(179 × 21 / 100)) = 37; HP do atacante +37 (teto do HP máximo)
24. Morte e death_ignore: HP final 2199 → o alvo segue vivo

- Motor (`action_executed`): Tenz (p1) executou Ataque básico; MP gasto 0, dano ao adversário 179.

### 45.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 52/5519 | 2199/5977 |
| MP | 105/1050 | 26/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Golpe Poderoso — executada; dano causado na rodada 273 (golpes e DoT), recebido 179; cura 35
- Tenz (p1): Ataque básico — executada; dano causado na rodada 179 (golpes e DoT), recebido 273; cura 37


## Rodada 46

### 46.0 Estado no início da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | 52/5519 | 2199/5977 |
| MP | 105/1050 | 26/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2 | Golpe Poderoso 2 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / True | False / True |

### 46.1 Escolha simultânea

As duas visões foram montadas antes da primeira escolha (`run_round`); nenhum controlador recebe a ação, o herói ou o controlador do outro.

**Tenz (p1)**

- Estado recebido (`DuelView`, rodada 46): eu HP 52/5519, MP 105/1050, efeitos —, buffs —; adversário fer HP 2199/5977, MP 26/1103, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 0, Soco de Placa 0, Gancho e Corda 0, Tomar Fôlego 1
- Ações legais: Ataque básico, Golpe Poderoso, Soco de Placa, Rendição
- Escolha: **Ataque básico** — justificativa da política: P(vitória) 0.000±0.000 com ataque básico; contra Golpe Poderoso 0.000, Soco de Placa 0.000; dano esperado 140
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

**fer (p2)**

- Estado recebido (`DuelView`, rodada 46): eu HP 2199/5977, MP 26/1103, efeitos —, buffs —; adversário Tenz HP 52/5519, MP 105/1050, efeitos —, buffs —.
- Recargas vistas no lock (oportunidades que ainda faltam): Golpe Poderoso 1, Juramento da Muralha 0, Soco de Placa 0, Respirar Fundo 0
- Ações legais: Ataque básico, Rendição
- Escolha: **Ataque básico** — justificativa da política: só o básico é legal (Golpe Poderoso: recarga, Juramento da Muralha: mp, Respirar Fundo: mp, Soco de Placa: mp)
- Validação: legal na lista da visão; aceita por `Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).
- Custo de MP: 0

- Ações travadas: Tenz (p1) = Ataque básico; fer (p2) = Ataque básico

### 46.2 Initiative Score

**Tenz (p1)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

| Atributo | Efetivo | REF | Efetivo / REF | √ |
|---|---|---|---|---|
| hp | 5519.0 | 4533.333333333333 | 1.2174264705882354 | 1.1033705046756668 |
| mp | 1050.0 | 1169.6666666666667 | 0.8976916500427472 | 0.9474659096995244 |
| st | 601.0 | 512.3333333333334 | 1.173064411190631 | 1.083080980901535 |
| mg | 406.0 | 459.6666666666667 | 0.883248730964467 | 0.9398131361948858 |
| ag | 121.0 | 177.66666666666666 | 0.6810506566604128 | 0.8252579334125864 |
| df | 509.0 | 335.0 | 1.519402985074627 | 1.2326406552903515 |

- Soma das seis raízes (`math.fsum`): 6.13162912017455
- ÷ 6 = build 1.0219381866957582
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0219381866957582 × 1.0 = 1.0219381866957582**
- AG relativa (desempate): 121.0 / 177.66666666666666 = 0.6810506566604128

**fer (p2)** — nível próprio 23, adversário 23; referências globais `foundation_reference(23)`.

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
- Δnível = 0; Δ × 0.005 = 0.0, limitado a ±0.1 → modificador 1.0
- **Score = 1.0589227212980339 × 1.0 = 1.0589227212980339**
- AG relativa (desempate): 142.0 / 177.66666666666666 = 0.799249530956848

- Comparação: score p1 1.0219381866957582 < score p2 1.0589227212980339 (floats crus, sem arredondamento).
- AG relativa: não consultada (o score decidiu).
- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.
- Ordem: fer (p2) → Tenz (p1) (`score`).

- **Ordem travada**: fer (p2) → Tenz (p1) (critério `score`).

### Oportunidade de fer (p2)

Início da oportunidade (`process_turn_start_effects`):

- Recargas (−1 cada, some ao chegar a 0): Golpe Poderoso 2 → 1
- Regeneração de MP: max(1, 1103 × 2 / 100) = 22.06; + mana_regen 0.0 → int(0 + 22.06) = **22**; MP livre 26 → min(1103, 26 + 22) = 48
- Efeitos do núcleo (`tick_effects`): DoT —, dreno —, expirados —, leis —, pula a vez: False
- Mudanças de estado no início: mp 26 → 48; recarga Golpe Poderoso 2 → 1
- Corte do MP livre (`Duel._clamp_free_mp`): reservado 0, teto livre 1103 → MP 48 → 48
- Perde a oportunidade por controle: não

**Golpe #78** — fer (p2) → Tenz (p1), ataque básico

1. Atributos ofensivos efetivos: st 654.0, mg 446.0, ag 142.0
2. Pesos (classe, `CLASS_WEIGHTS`): st 1.6, mg 0.4, ag 0.0
3. Poder básico da ação: Σ = 1224.8000000000002; dano médio max(1, int(1224.8000000000002 × (1 + 13/100))) = 1384; BASE do básico = max(1, int(1384 × 0.9)) = **1245** (multiplicador do básico 0.9)
4. Bônus de arma: +13.0% → fator 1.13 (dentro do dano médio)
5. Modificadores condicionais: inaplicável (a ação não declara condição)
6. Chance de acerto: 85 + swing 2.3954372623574143 (30 × (142 − 121) / 263) − evasão 0.0 + medo/precisão temporários 0 + precisão 10.0 + modificador da ação 0 − ocultação 0 = 97.39543726235742 → clamp [20, 95] e int → **95**
7. Rolagem de acerto: sorteio nº 207 [acerto]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **56**; chance 95; teste `56 > 95` (operador `>`) é falso ⇒ **ACERTOU** — chamado em `mechanics/combat.py:420 resolve_physical_attack`
8. Chance de crítico: padrão 0 + carta 0 + fontes do atacante 30 = 30, teto 75 → **30**
9. Rolagem de crítico: sorteio nº 208 [crítico]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **2**; chance 30; teste `2 <= 30` (operador `<=`) é verdadeiro ⇒ **CRÍTICO** — chamado em `mechanics/combat.py:447 resolve_physical_attack`
10. Multiplicador de crítico: 1.5 + 10/100 = 1.6
11. +MULT: nenhuma parcela → 1 + Σ = 1.0
12. ×MULT: crítico ×1.6
13. Produto ×MULT bruto 1.6; `XMULT_CAP` 5.0 → aplicado 1.6
14. Defesa efetiva do alvo: 509
15. Fator de defesa: 100 / (100 + 509) = 0.16420361247947454
16. Mitigação: saída do atacante (outgoing_damage_multiplier) = 1.0; entrada do defensor (incoming_damage_multiplier) = 0.79 (damage_reduction 21.0, max(0.1, 1 − min(80, damage_reduction) / 100))
17. Valores intermediários: bruto = 1245.0 × 1.0 × 1.6 × 0.16420361247947454 = 327.0935960591133; max(1, int(bruto)) = 327 → int(anterior × 1.0) = 327 → int(anterior × 0.79) = 258
18. Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × fator)` para cada um dos 2 fatores de mitigação; por fim `max(1, ·)`
19. Dano final do funil: **258**
20. Égide de Mana: inaplicável (o alvo não tem Égide); passa 258
21. MP da Égide: 0
22. Dano aplicado ao HP: `take_damage(258)`; HP do alvo 52 → -206 (retirado 258)
23. Roubo de vida: 13.0% → max(1, int(258 × 13 / 100)) = 33; HP do atacante +33 (teto do HP máximo)
24. Morte e death_ignore: HP final -206 → o alvo morreu

**Status `stun`** sobre Tenz (p1) (via `_aplicar_procs_on_hit`, fonte `fer`)

- Chance base 2%; resistência do alvo 16.0% → efetiva 2 × (1 − 16/100) = 1.68%
- sorteio nº 209 [aplicação de status (stun)]: `randrange(1, 101)` — inteiro uniforme em [1, 100] → **35**; chance 1.68; teste `35 > 1.68` (operador `>`) é verdadeiro ⇒ **falhou na rolagem** — chamado em `mechanics/combat.py:582 try_apply_status`
- Instâncias de `stun` no alvo antes: —; depois: —

- Motor (`action_executed`): fer (p2) executou Ataque básico; MP gasto 0, dano ao adversário 258.

- **Fim do duelo**: vence fer (p2), motivo `ko`.

- Ação de Tenz (p1) **cancelada por morte**.
### 46.9 Estado ao final da rodada

| | Tenz (p1) | fer (p2) |
|---|---|---|
| HP | -206/5519 | 2232/5977 |
| MP | 105/1050 | 48/1103 |
| ST / MG / AG / DF | 601 / 406 / 121 / 509 | 654 / 446 / 142 / 503 |
| Recargas (contador interno) | Tomar Fôlego 2 | Golpe Poderoso 1 |
| Buffs | — | — |
| Efeitos | — | — |
| death_ignore gasto / vivo | True / False | False / True |

MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou devolvida).

- fer (p2): Ataque básico — executada; dano causado na rodada 258 (golpes e DoT), recebido 0; cura 33
- Tenz (p1): Ataque básico — cancelada por morte; dano causado na rodada 0 (golpes e DoT), recebido 258; cura 0


## Conclusão da final (fatos registrados)

- Campeão: **fer** (p2); vice: **Tenz** (p1).
- Rodadas: 46. Motivo exato: `ko` — o HP de Tenz chegou a 0 durante a rodada 46.

| | Tenz (p1) | fer (p2) |
|---|---|---|
| Dano causado (golpes + DoT) | 6993 (6993 + 0) | 12609 (12609 + 0) |
| HP retirado do adversário | 6993 | 12477 |
| Cura (skill + roubo) | 6752 (5296 + 1456) | 3248 (1791 + 1457) |
| MP consumido em ações | 1869 | 2045 |
| MP consumido pela Égide | 0 | 0 |
| Skills usadas | 27: Golpe Poderoso ×10, Tomar Fôlego ×8, Soco de Placa ×8, Gancho e Corda ×1 | 35: Golpe Poderoso ×17, Soco de Placa ×15, Respirar Fundo ×3 |
| Ataques básicos | 18 | 10 |
| Acertos / erros | 25 / 11 | 42 / 0 |
| Críticos (dano) | 4 (1725) | 13 (5258) |
| Status aplicados | stun (rodada 16), weakened (rodada 22) | weakened (rodada 14), weakened (rodada 16), weakened (rodada 35) |
| Status que falharam na rolagem | weakened (rodada 11), vulnerable (rodada 16), weakened (rodada 20), weakened (rodada 25), weakened (rodada 37) | stun (rodada 1), stun (rodada 2), weakened (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), weakened (rodada 5), stun (rodada 6), stun (rodada 7), weakened (rodada 7), stun (rodada 8), stun (rodada 9), weakened (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), weakened (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 18), stun (rodada 19), weakened (rodada 19), stun (rodada 20), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 28), weakened (rodada 28), stun (rodada 29), stun (rodada 30), weakened (rodada 30), stun (rodada 31), stun (rodada 32), weakened (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 38), stun (rodada 39), weakened (rodada 39), stun (rodada 40), stun (rodada 41), weakened (rodada 41), stun (rodada 42), stun (rodada 43), weakened (rodada 43), stun (rodada 44), stun (rodada 45), stun (rodada 46) |
| Status anulados por resistência / recusados | — | — |
| Ações perdidas por controle | 0 | 1 |
| Rodadas agindo primeiro | 0 | 46 |
| HP / MP restantes | -206/5519 · 105/1050 | 2232/5977 · 48/1103 |

HP negativo é o valor cru do motor: `take_damage` não corta em zero, e a sobra mostra quanto o último golpe passou do necessário.

## Todas as chamadas ao gerador

209 chamadas, igual ao contador do proxy (209).

| Nº | Rodada | Ator | Mecânica | Operação | Limites | Valor | Chance | Teste | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | p2 | acerto | `randrange` | [1, 100] | 9 | 95 | `9 > 95` → F | aprovado: ACERTOU |
| 2 | 1 | p2 | crítico | `randrange` | [1, 100] | 14 | 30 | `14 <= 30` → V | aprovado: CRÍTICO |
| 3 | 1 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 81 | 1.68 | `81 > 1.68` → V | recusado: falhou na rolagem |
| 4 | 1 | p1 | acerto | `randrange` | [1, 100] | 86 | 72 | `86 > 72` → V | recusado: ERROU |
| 5 | 2 | p2 | acerto | `randrange` | [1, 100] | 30 | 95 | `30 > 95` → F | aprovado: ACERTOU |
| 6 | 2 | p2 | crítico | `randrange` | [1, 100] | 98 | 30 | `98 <= 30` → F | recusado: sem crítico |
| 7 | 2 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 44 | 1.68 | `44 > 1.68` → V | recusado: falhou na rolagem |
| 8 | 2 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 70 | 29.4 | `70 > 29.4` → V | recusado: falhou na rolagem |
| 9 | 3 | p2 | acerto | `randrange` | [1, 100] | 71 | 95 | `71 > 95` → F | aprovado: ACERTOU |
| 10 | 3 | p2 | crítico | `randrange` | [1, 100] | 88 | 30 | `88 <= 30` → F | recusado: sem crítico |
| 11 | 3 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 94 | 1.68 | `94 > 1.68` → V | recusado: falhou na rolagem |
| 12 | 3 | p1 | acerto | `randrange` | [1, 100] | 79 | 72 | `79 > 72` → V | recusado: ERROU |
| 13 | 4 | p2 | acerto | `randrange` | [1, 100] | 17 | 95 | `17 > 95` → F | aprovado: ACERTOU |
| 14 | 4 | p2 | crítico | `randrange` | [1, 100] | 92 | 30 | `92 <= 30` → F | recusado: sem crítico |
| 15 | 4 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 47 | 1.68 | `47 > 1.68` → V | recusado: falhou na rolagem |
| 16 | 4 | p1 | acerto | `randrange` | [1, 100] | 11 | 72 | `11 > 72` → F | aprovado: ACERTOU |
| 17 | 4 | p1 | crítico | `randrange` | [1, 100] | 94 | 15 | `94 <= 15` → F | recusado: sem crítico |
| 18 | 5 | p2 | acerto | `randrange` | [1, 100] | 72 | 95 | `72 > 95` → F | aprovado: ACERTOU |
| 19 | 5 | p2 | crítico | `randrange` | [1, 100] | 20 | 30 | `20 <= 30` → V | aprovado: CRÍTICO |
| 20 | 5 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 93 | 1.68 | `93 > 1.68` → V | recusado: falhou na rolagem |
| 21 | 5 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 60 | 29.4 | `60 > 29.4` → V | recusado: falhou na rolagem |
| 22 | 5 | p1 | acerto | `randrange` | [1, 100] | 84 | 72 | `84 > 72` → V | recusado: ERROU |
| 23 | 6 | p2 | acerto | `randrange` | [1, 100] | 9 | 95 | `9 > 95` → F | aprovado: ACERTOU |
| 24 | 6 | p2 | crítico | `randrange` | [1, 100] | 50 | 30 | `50 <= 30` → F | recusado: sem crítico |
| 25 | 6 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 12 | 1.68 | `12 > 1.68` → V | recusado: falhou na rolagem |
| 26 | 6 | p1 | acerto | `randrange` | [1, 100] | 50 | 72 | `50 > 72` → F | aprovado: ACERTOU |
| 27 | 6 | p1 | crítico | `randrange` | [1, 100] | 89 | 15 | `89 <= 15` → F | recusado: sem crítico |
| 28 | 7 | p2 | acerto | `randrange` | [1, 100] | 71 | 95 | `71 > 95` → F | aprovado: ACERTOU |
| 29 | 7 | p2 | crítico | `randrange` | [1, 100] | 29 | 30 | `29 <= 30` → V | aprovado: CRÍTICO |
| 30 | 7 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 85 | 1.68 | `85 > 1.68` → V | recusado: falhou na rolagem |
| 31 | 7 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 64 | 29.4 | `64 > 29.4` → V | recusado: falhou na rolagem |
| 32 | 8 | p2 | acerto | `randrange` | [1, 100] | 25 | 95 | `25 > 95` → F | aprovado: ACERTOU |
| 33 | 8 | p2 | crítico | `randrange` | [1, 100] | 55 | 30 | `55 <= 30` → F | recusado: sem crítico |
| 34 | 8 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 48 | 1.68 | `48 > 1.68` → V | recusado: falhou na rolagem |
| 35 | 8 | p1 | acerto | `randrange` | [1, 100] | 13 | 72 | `13 > 72` → F | aprovado: ACERTOU |
| 36 | 8 | p1 | crítico | `randrange` | [1, 100] | 93 | 15 | `93 <= 15` → F | recusado: sem crítico |
| 37 | 9 | p2 | acerto | `randrange` | [1, 100] | 9 | 95 | `9 > 95` → F | aprovado: ACERTOU |
| 38 | 9 | p2 | crítico | `randrange` | [1, 100] | 73 | 30 | `73 <= 30` → F | recusado: sem crítico |
| 39 | 9 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 85 | 1.68 | `85 > 1.68` → V | recusado: falhou na rolagem |
| 40 | 9 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 53 | 29.4 | `53 > 29.4` → V | recusado: falhou na rolagem |
| 41 | 9 | p1 | acerto | `randrange` | [1, 100] | 34 | 72 | `34 > 72` → F | aprovado: ACERTOU |
| 42 | 9 | p1 | crítico | `randrange` | [1, 100] | 36 | 15 | `36 <= 15` → F | recusado: sem crítico |
| 43 | 10 | p2 | acerto | `randrange` | [1, 100] | 44 | 95 | `44 > 95` → F | aprovado: ACERTOU |
| 44 | 10 | p2 | crítico | `randrange` | [1, 100] | 48 | 30 | `48 <= 30` → F | recusado: sem crítico |
| 45 | 10 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 63 | 1.68 | `63 > 1.68` → V | recusado: falhou na rolagem |
| 46 | 10 | p1 | acerto | `randrange` | [1, 100] | 24 | 72 | `24 > 72` → F | aprovado: ACERTOU |
| 47 | 10 | p1 | crítico | `randrange` | [1, 100] | 5 | 15 | `5 <= 15` → V | aprovado: CRÍTICO |
| 48 | 11 | p2 | acerto | `randrange` | [1, 100] | 35 | 95 | `35 > 95` → F | aprovado: ACERTOU |
| 49 | 11 | p2 | crítico | `randrange` | [1, 100] | 14 | 30 | `14 <= 30` → V | aprovado: CRÍTICO |
| 50 | 11 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 3 | 1.68 | `3 > 1.68` → V | recusado: falhou na rolagem |
| 51 | 11 | p1 | acerto | `randrange` | [1, 100] | 2 | 72 | `2 > 72` → F | aprovado: ACERTOU |
| 52 | 11 | p1 | crítico | `randrange` | [1, 100] | 20 | 15 | `20 <= 15` → F | recusado: sem crítico |
| 53 | 11 | p1 | aplicação de status (weakened) | `randrange` | [1, 100] | 76 | 35.0 | `76 > 35.0` → V | recusado: falhou na rolagem |
| 54 | 12 | p2 | acerto | `randrange` | [1, 100] | 65 | 95 | `65 > 95` → F | aprovado: ACERTOU |
| 55 | 12 | p2 | crítico | `randrange` | [1, 100] | 56 | 30 | `56 <= 30` → F | recusado: sem crítico |
| 56 | 12 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 29 | 1.68 | `29 > 1.68` → V | recusado: falhou na rolagem |
| 57 | 12 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 68 | 29.4 | `68 > 29.4` → V | recusado: falhou na rolagem |
| 58 | 12 | p1 | acerto | `randrange` | [1, 100] | 64 | 72 | `64 > 72` → F | aprovado: ACERTOU |
| 59 | 12 | p1 | crítico | `randrange` | [1, 100] | 76 | 15 | `76 <= 15` → F | recusado: sem crítico |
| 60 | 13 | p2 | acerto | `randrange` | [1, 100] | 28 | 95 | `28 > 95` → F | aprovado: ACERTOU |
| 61 | 13 | p2 | crítico | `randrange` | [1, 100] | 6 | 30 | `6 <= 30` → V | aprovado: CRÍTICO |
| 62 | 13 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 88 | 1.68 | `88 > 1.68` → V | recusado: falhou na rolagem |
| 63 | 14 | p2 | acerto | `randrange` | [1, 100] | 85 | 95 | `85 > 95` → F | aprovado: ACERTOU |
| 64 | 14 | p2 | crítico | `randrange` | [1, 100] | 54 | 30 | `54 <= 30` → F | recusado: sem crítico |
| 65 | 14 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 100 | 1.68 | `100 > 1.68` → V | recusado: falhou na rolagem |
| 66 | 14 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 12 | 29.4 | `12 > 29.4` → F | aprovado: passou na rolagem |
| 67 | 14 | p1 | acerto | `randrange` | [1, 100] | 18 | 72 | `18 > 72` → F | aprovado: ACERTOU |
| 68 | 14 | p1 | crítico | `randrange` | [1, 100] | 97 | 15 | `97 <= 15` → F | recusado: sem crítico |
| 69 | 15 | p2 | acerto | `randrange` | [1, 100] | 55 | 95 | `55 > 95` → F | aprovado: ACERTOU |
| 70 | 15 | p2 | crítico | `randrange` | [1, 100] | 12 | 30 | `12 <= 30` → V | aprovado: CRÍTICO |
| 71 | 15 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 87 | 1.68 | `87 > 1.68` → V | recusado: falhou na rolagem |
| 72 | 15 | p1 | acerto | `randrange` | [1, 100] | 53 | 72 | `53 > 72` → F | aprovado: ACERTOU |
| 73 | 15 | p1 | crítico | `randrange` | [1, 100] | 90 | 15 | `90 <= 15` → F | recusado: sem crítico |
| 74 | 16 | p2 | acerto | `randrange` | [1, 100] | 91 | 95 | `91 > 95` → F | aprovado: ACERTOU |
| 75 | 16 | p2 | crítico | `randrange` | [1, 100] | 49 | 30 | `49 <= 30` → F | recusado: sem crítico |
| 76 | 16 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 12 | 1.68 | `12 > 1.68` → V | recusado: falhou na rolagem |
| 77 | 16 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 3 | 29.4 | `3 > 29.4` → F | aprovado: passou na rolagem |
| 78 | 16 | p1 | aplicação de status (stun) | `randrange` | [1, 100] | 9 | 50.0 | `9 > 50.0` → F | aprovado: passou na rolagem |
| 79 | 16 | p1 | aplicação de status (vulnerable) | `randrange` | [1, 100] | 79 | 60.0 | `79 > 60.0` → V | recusado: falhou na rolagem |
| 80 | 17 | p1 | acerto | `randrange` | [1, 100] | 88 | 72 | `88 > 72` → V | recusado: ERROU |
| 81 | 18 | p2 | acerto | `randrange` | [1, 100] | 46 | 95 | `46 > 95` → F | aprovado: ACERTOU |
| 82 | 18 | p2 | crítico | `randrange` | [1, 100] | 89 | 30 | `89 <= 30` → F | recusado: sem crítico |
| 83 | 18 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 8 | 1.68 | `8 > 1.68` → V | recusado: falhou na rolagem |
| 84 | 19 | p2 | acerto | `randrange` | [1, 100] | 54 | 95 | `54 > 95` → F | aprovado: ACERTOU |
| 85 | 19 | p2 | crítico | `randrange` | [1, 100] | 16 | 30 | `16 <= 30` → V | aprovado: CRÍTICO |
| 86 | 19 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 31 | 1.68 | `31 > 1.68` → V | recusado: falhou na rolagem |
| 87 | 19 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 43 | 29.4 | `43 > 29.4` → V | recusado: falhou na rolagem |
| 88 | 19 | p1 | acerto | `randrange` | [1, 100] | 41 | 72 | `41 > 72` → F | aprovado: ACERTOU |
| 89 | 19 | p1 | crítico | `randrange` | [1, 100] | 14 | 15 | `14 <= 15` → V | aprovado: CRÍTICO |
| 90 | 20 | p2 | acerto | `randrange` | [1, 100] | 60 | 95 | `60 > 95` → F | aprovado: ACERTOU |
| 91 | 20 | p2 | crítico | `randrange` | [1, 100] | 7 | 30 | `7 <= 30` → V | aprovado: CRÍTICO |
| 92 | 20 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 31 | 1.68 | `31 > 1.68` → V | recusado: falhou na rolagem |
| 93 | 20 | p1 | acerto | `randrange` | [1, 100] | 37 | 72 | `37 > 72` → F | aprovado: ACERTOU |
| 94 | 20 | p1 | crítico | `randrange` | [1, 100] | 85 | 15 | `85 <= 15` → F | recusado: sem crítico |
| 95 | 20 | p1 | aplicação de status (weakened) | `randrange` | [1, 100] | 53 | 35.0 | `53 > 35.0` → V | recusado: falhou na rolagem |
| 96 | 21 | p1 | acerto | `randrange` | [1, 100] | 20 | 72 | `20 > 72` → F | aprovado: ACERTOU |
| 97 | 21 | p1 | crítico | `randrange` | [1, 100] | 74 | 15 | `74 <= 15` → F | recusado: sem crítico |
| 98 | 22 | p2 | acerto | `randrange` | [1, 100] | 82 | 95 | `82 > 95` → F | aprovado: ACERTOU |
| 99 | 22 | p2 | crítico | `randrange` | [1, 100] | 90 | 30 | `90 <= 30` → F | recusado: sem crítico |
| 100 | 22 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 92 | 1.68 | `92 > 1.68` → V | recusado: falhou na rolagem |
| 101 | 22 | p1 | acerto | `randrange` | [1, 100] | 25 | 72 | `25 > 72` → F | aprovado: ACERTOU |
| 102 | 22 | p1 | crítico | `randrange` | [1, 100] | 70 | 15 | `70 <= 15` → F | recusado: sem crítico |
| 103 | 22 | p1 | aplicação de status (weakened) | `randrange` | [1, 100] | 35 | 35.0 | `35 > 35.0` → F | aprovado: passou na rolagem |
| 104 | 23 | p2 | acerto | `randrange` | [1, 100] | 71 | 95 | `71 > 95` → F | aprovado: ACERTOU |
| 105 | 23 | p2 | crítico | `randrange` | [1, 100] | 44 | 30 | `44 <= 30` → F | recusado: sem crítico |
| 106 | 23 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 70 | 1.68 | `70 > 1.68` → V | recusado: falhou na rolagem |
| 107 | 24 | p2 | acerto | `randrange` | [1, 100] | 71 | 95 | `71 > 95` → F | aprovado: ACERTOU |
| 108 | 24 | p2 | crítico | `randrange` | [1, 100] | 25 | 30 | `25 <= 30` → V | aprovado: CRÍTICO |
| 109 | 24 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 3 | 1.68 | `3 > 1.68` → V | recusado: falhou na rolagem |
| 110 | 24 | p1 | acerto | `randrange` | [1, 100] | 48 | 72 | `48 > 72` → F | aprovado: ACERTOU |
| 111 | 24 | p1 | crítico | `randrange` | [1, 100] | 67 | 15 | `67 <= 15` → F | recusado: sem crítico |
| 112 | 25 | p2 | acerto | `randrange` | [1, 100] | 73 | 95 | `73 > 95` → F | aprovado: ACERTOU |
| 113 | 25 | p2 | crítico | `randrange` | [1, 100] | 89 | 30 | `89 <= 30` → F | recusado: sem crítico |
| 114 | 25 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 25 | 1.68 | `25 > 1.68` → V | recusado: falhou na rolagem |
| 115 | 25 | p1 | acerto | `randrange` | [1, 100] | 15 | 72 | `15 > 72` → F | aprovado: ACERTOU |
| 116 | 25 | p1 | crítico | `randrange` | [1, 100] | 88 | 15 | `88 <= 15` → F | recusado: sem crítico |
| 117 | 25 | p1 | aplicação de status (weakened) | `randrange` | [1, 100] | 64 | 35.0 | `64 > 35.0` → V | recusado: falhou na rolagem |
| 118 | 26 | p1 | acerto | `randrange` | [1, 100] | 6 | 72 | `6 > 72` → F | aprovado: ACERTOU |
| 119 | 26 | p1 | crítico | `randrange` | [1, 100] | 63 | 15 | `63 <= 15` → F | recusado: sem crítico |
| 120 | 27 | p2 | acerto | `randrange` | [1, 100] | 91 | 95 | `91 > 95` → F | aprovado: ACERTOU |
| 121 | 27 | p2 | crítico | `randrange` | [1, 100] | 67 | 30 | `67 <= 30` → F | recusado: sem crítico |
| 122 | 27 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 16 | 1.68 | `16 > 1.68` → V | recusado: falhou na rolagem |
| 123 | 27 | p1 | acerto | `randrange` | [1, 100] | 99 | 72 | `99 > 72` → V | recusado: ERROU |
| 124 | 28 | p2 | acerto | `randrange` | [1, 100] | 87 | 95 | `87 > 95` → F | aprovado: ACERTOU |
| 125 | 28 | p2 | crítico | `randrange` | [1, 100] | 71 | 30 | `71 <= 30` → F | recusado: sem crítico |
| 126 | 28 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 7 | 1.68 | `7 > 1.68` → V | recusado: falhou na rolagem |
| 127 | 28 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 81 | 29.4 | `81 > 29.4` → V | recusado: falhou na rolagem |
| 128 | 29 | p2 | acerto | `randrange` | [1, 100] | 2 | 95 | `2 > 95` → F | aprovado: ACERTOU |
| 129 | 29 | p2 | crítico | `randrange` | [1, 100] | 36 | 30 | `36 <= 30` → F | recusado: sem crítico |
| 130 | 29 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 77 | 1.68 | `77 > 1.68` → V | recusado: falhou na rolagem |
| 131 | 29 | p1 | acerto | `randrange` | [1, 100] | 32 | 72 | `32 > 72` → F | aprovado: ACERTOU |
| 132 | 29 | p1 | crítico | `randrange` | [1, 100] | 59 | 15 | `59 <= 15` → F | recusado: sem crítico |
| 133 | 30 | p2 | acerto | `randrange` | [1, 100] | 85 | 95 | `85 > 95` → F | aprovado: ACERTOU |
| 134 | 30 | p2 | crítico | `randrange` | [1, 100] | 82 | 30 | `82 <= 30` → F | recusado: sem crítico |
| 135 | 30 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 22 | 1.68 | `22 > 1.68` → V | recusado: falhou na rolagem |
| 136 | 30 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 86 | 29.4 | `86 > 29.4` → V | recusado: falhou na rolagem |
| 137 | 30 | p1 | acerto | `randrange` | [1, 100] | 98 | 72 | `98 > 72` → V | recusado: ERROU |
| 138 | 31 | p2 | acerto | `randrange` | [1, 100] | 72 | 95 | `72 > 95` → F | aprovado: ACERTOU |
| 139 | 31 | p2 | crítico | `randrange` | [1, 100] | 96 | 30 | `96 <= 30` → F | recusado: sem crítico |
| 140 | 31 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 91 | 1.68 | `91 > 1.68` → V | recusado: falhou na rolagem |
| 141 | 31 | p1 | acerto | `randrange` | [1, 100] | 81 | 72 | `81 > 72` → V | recusado: ERROU |
| 142 | 32 | p2 | acerto | `randrange` | [1, 100] | 22 | 95 | `22 > 95` → F | aprovado: ACERTOU |
| 143 | 32 | p2 | crítico | `randrange` | [1, 100] | 45 | 30 | `45 <= 30` → F | recusado: sem crítico |
| 144 | 32 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 30 | 1.68 | `30 > 1.68` → V | recusado: falhou na rolagem |
| 145 | 32 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 37 | 29.4 | `37 > 29.4` → V | recusado: falhou na rolagem |
| 146 | 32 | p1 | acerto | `randrange` | [1, 100] | 61 | 72 | `61 > 72` → F | aprovado: ACERTOU |
| 147 | 32 | p1 | crítico | `randrange` | [1, 100] | 27 | 15 | `27 <= 15` → F | recusado: sem crítico |
| 148 | 33 | p2 | acerto | `randrange` | [1, 100] | 35 | 95 | `35 > 95` → F | aprovado: ACERTOU |
| 149 | 33 | p2 | crítico | `randrange` | [1, 100] | 35 | 30 | `35 <= 30` → F | recusado: sem crítico |
| 150 | 33 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 3 | 1.68 | `3 > 1.68` → V | recusado: falhou na rolagem |
| 151 | 34 | p2 | acerto | `randrange` | [1, 100] | 23 | 95 | `23 > 95` → F | aprovado: ACERTOU |
| 152 | 34 | p2 | crítico | `randrange` | [1, 100] | 11 | 30 | `11 <= 30` → V | aprovado: CRÍTICO |
| 153 | 34 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 85 | 1.68 | `85 > 1.68` → V | recusado: falhou na rolagem |
| 154 | 34 | p1 | acerto | `randrange` | [1, 100] | 51 | 72 | `51 > 72` → F | aprovado: ACERTOU |
| 155 | 34 | p1 | crítico | `randrange` | [1, 100] | 99 | 15 | `99 <= 15` → F | recusado: sem crítico |
| 156 | 35 | p2 | acerto | `randrange` | [1, 100] | 65 | 95 | `65 > 95` → F | aprovado: ACERTOU |
| 157 | 35 | p2 | crítico | `randrange` | [1, 100] | 75 | 30 | `75 <= 30` → F | recusado: sem crítico |
| 158 | 35 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 100 | 1.68 | `100 > 1.68` → V | recusado: falhou na rolagem |
| 159 | 35 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 11 | 29.4 | `11 > 29.4` → F | aprovado: passou na rolagem |
| 160 | 35 | p1 | acerto | `randrange` | [1, 100] | 91 | 72 | `91 > 72` → V | recusado: ERROU |
| 161 | 36 | p2 | acerto | `randrange` | [1, 100] | 48 | 95 | `48 > 95` → F | aprovado: ACERTOU |
| 162 | 36 | p2 | crítico | `randrange` | [1, 100] | 56 | 30 | `56 <= 30` → F | recusado: sem crítico |
| 163 | 36 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 45 | 1.68 | `45 > 1.68` → V | recusado: falhou na rolagem |
| 164 | 36 | p1 | acerto | `randrange` | [1, 100] | 11 | 72 | `11 > 72` → F | aprovado: ACERTOU |
| 165 | 36 | p1 | crítico | `randrange` | [1, 100] | 84 | 15 | `84 <= 15` → F | recusado: sem crítico |
| 166 | 37 | p1 | acerto | `randrange` | [1, 100] | 54 | 72 | `54 > 72` → F | aprovado: ACERTOU |
| 167 | 37 | p1 | crítico | `randrange` | [1, 100] | 14 | 15 | `14 <= 15` → V | aprovado: CRÍTICO |
| 168 | 37 | p1 | aplicação de status (weakened) | `randrange` | [1, 100] | 79 | 35.0 | `79 > 35.0` → V | recusado: falhou na rolagem |
| 169 | 38 | p2 | acerto | `randrange` | [1, 100] | 45 | 95 | `45 > 95` → F | aprovado: ACERTOU |
| 170 | 38 | p2 | crítico | `randrange` | [1, 100] | 2 | 30 | `2 <= 30` → V | aprovado: CRÍTICO |
| 171 | 38 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 26 | 1.68 | `26 > 1.68` → V | recusado: falhou na rolagem |
| 172 | 38 | p1 | acerto | `randrange` | [1, 100] | 95 | 72 | `95 > 72` → V | recusado: ERROU |
| 173 | 39 | p2 | acerto | `randrange` | [1, 100] | 4 | 95 | `4 > 95` → F | aprovado: ACERTOU |
| 174 | 39 | p2 | crítico | `randrange` | [1, 100] | 88 | 30 | `88 <= 30` → F | recusado: sem crítico |
| 175 | 39 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 96 | 1.68 | `96 > 1.68` → V | recusado: falhou na rolagem |
| 176 | 39 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 67 | 29.4 | `67 > 29.4` → V | recusado: falhou na rolagem |
| 177 | 39 | p1 | acerto | `randrange` | [1, 100] | 97 | 72 | `97 > 72` → V | recusado: ERROU |
| 178 | 40 | p2 | acerto | `randrange` | [1, 100] | 32 | 95 | `32 > 95` → F | aprovado: ACERTOU |
| 179 | 40 | p2 | crítico | `randrange` | [1, 100] | 80 | 30 | `80 <= 30` → F | recusado: sem crítico |
| 180 | 40 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 46 | 1.68 | `46 > 1.68` → V | recusado: falhou na rolagem |
| 181 | 40 | p1 | acerto | `randrange` | [1, 100] | 97 | 72 | `97 > 72` → V | recusado: ERROU |
| 182 | 41 | p2 | acerto | `randrange` | [1, 100] | 67 | 95 | `67 > 95` → F | aprovado: ACERTOU |
| 183 | 41 | p2 | crítico | `randrange` | [1, 100] | 74 | 30 | `74 <= 30` → F | recusado: sem crítico |
| 184 | 41 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 83 | 1.68 | `83 > 1.68` → V | recusado: falhou na rolagem |
| 185 | 41 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 44 | 29.4 | `44 > 29.4` → V | recusado: falhou na rolagem |
| 186 | 41 | p1 | acerto | `randrange` | [1, 100] | 23 | 72 | `23 > 72` → F | aprovado: ACERTOU |
| 187 | 41 | p1 | crítico | `randrange` | [1, 100] | 12 | 15 | `12 <= 15` → V | aprovado: CRÍTICO |
| 188 | 42 | p2 | acerto | `randrange` | [1, 100] | 46 | 95 | `46 > 95` → F | aprovado: ACERTOU |
| 189 | 42 | p2 | crítico | `randrange` | [1, 100] | 23 | 30 | `23 <= 30` → V | aprovado: CRÍTICO |
| 190 | 42 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 29 | 1.68 | `29 > 1.68` → V | recusado: falhou na rolagem |
| 191 | 43 | p2 | acerto | `randrange` | [1, 100] | 47 | 95 | `47 > 95` → F | aprovado: ACERTOU |
| 192 | 43 | p2 | crítico | `randrange` | [1, 100] | 41 | 30 | `41 <= 30` → F | recusado: sem crítico |
| 193 | 43 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 11 | 1.68 | `11 > 1.68` → V | recusado: falhou na rolagem |
| 194 | 43 | p2 | aplicação de status (weakened) | `randrange` | [1, 100] | 59 | 29.4 | `59 > 29.4` → V | recusado: falhou na rolagem |
| 195 | 43 | p1 | acerto | `randrange` | [1, 100] | 39 | 72 | `39 > 72` → F | aprovado: ACERTOU |
| 196 | 43 | p1 | crítico | `randrange` | [1, 100] | 82 | 15 | `82 <= 15` → F | recusado: sem crítico |
| 197 | 44 | p2 | acerto | `randrange` | [1, 100] | 10 | 95 | `10 > 95` → F | aprovado: ACERTOU |
| 198 | 44 | p2 | crítico | `randrange` | [1, 100] | 53 | 30 | `53 <= 30` → F | recusado: sem crítico |
| 199 | 44 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 25 | 1.68 | `25 > 1.68` → V | recusado: falhou na rolagem |
| 200 | 44 | p1 | acerto | `randrange` | [1, 100] | 59 | 72 | `59 > 72` → F | aprovado: ACERTOU |
| 201 | 44 | p1 | crítico | `randrange` | [1, 100] | 92 | 15 | `92 <= 15` → F | recusado: sem crítico |
| 202 | 45 | p2 | acerto | `randrange` | [1, 100] | 78 | 95 | `78 > 95` → F | aprovado: ACERTOU |
| 203 | 45 | p2 | crítico | `randrange` | [1, 100] | 94 | 30 | `94 <= 30` → F | recusado: sem crítico |
| 204 | 45 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 34 | 1.68 | `34 > 1.68` → V | recusado: falhou na rolagem |
| 205 | 45 | p1 | acerto | `randrange` | [1, 100] | 50 | 72 | `50 > 72` → F | aprovado: ACERTOU |
| 206 | 45 | p1 | crítico | `randrange` | [1, 100] | 45 | 15 | `45 <= 15` → F | recusado: sem crítico |
| 207 | 46 | p2 | acerto | `randrange` | [1, 100] | 56 | 95 | `56 > 95` → F | aprovado: ACERTOU |
| 208 | 46 | p2 | crítico | `randrange` | [1, 100] | 2 | 30 | `2 <= 30` → V | aprovado: CRÍTICO |
| 209 | 46 | p2 | aplicação de status (stun) | `randrange` | [1, 100] | 35 | 1.68 | `35 > 1.68` → V | recusado: falhou na rolagem |

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

- **Tenz**: 36 golpes tentados com chance média de acerto 72.0%, 25 conectaram (69.4%); dano médio por golpe conectado 279.7. O fator de defesa médio que os golpes dele enfrentaram foi 0.1658 e a mitigação de entrada do alvo, 0.8900.
- **fer**: 42 golpes tentados com chance média de acerto 95.0%, 42 conectaram (100.0%); dano médio por golpe conectado 300.2. O fator de defesa médio que os golpes dele enfrentaram foi 0.1642 e a mitigação de entrada do alvo, 0.7900.
- Iniciativa: fer agiu primeiro em 46 de 46 rodadas; Tenz, em 0. Na rodada final, a ordem foi fer → Tenz (`score`).
- Score de iniciativa por rodada (p1 / p2 → quem agiu primeiro):
  - Rodada 1: 1.021938 / 1.058923 → fer
  - Rodada 2: 1.021938 / 1.058923 → fer
  - Rodada 3: 1.021938 / 1.058923 → fer
  - Rodada 4: 1.021938 / 1.058923 → fer
  - Rodada 5: 1.021938 / 1.058923 → fer
  - Rodada 6: 1.021938 / 1.058923 → fer
  - Rodada 7: 1.021938 / 1.058923 → fer
  - Rodada 8: 1.021938 / 1.058923 → fer
  - Rodada 9: 1.021938 / 1.058923 → fer
  - Rodada 10: 1.021938 / 1.058923 → fer
  - Rodada 11: 1.021938 / 1.058923 → fer
  - Rodada 12: 1.021938 / 1.058923 → fer
  - Rodada 13: 1.021938 / 1.058923 → fer
  - Rodada 14: 1.021938 / 1.058923 → fer
  - Rodada 15: 1.002746 / 1.058923 → fer; atributos efetivos diferentes da rodada 1 — Tenz: st 601→480
  - Rodada 16: 1.021938 / 1.058923 → fer
  - Rodada 17: 1.002746 / 1.058923 → fer; atributos efetivos diferentes da rodada 1 — Tenz: st 601→480
  - Rodada 18: 1.021938 / 1.058923 → fer
  - Rodada 19: 1.021938 / 1.058923 → fer
  - Rodada 20: 1.021938 / 1.058923 → fer
  - Rodada 21: 1.021938 / 1.058923 → fer
  - Rodada 22: 1.021938 / 1.058923 → fer
  - Rodada 23: 1.021938 / 1.039011 → fer; atributos efetivos diferentes da rodada 1 — fer: st 654→523
  - Rodada 24: 1.021938 / 1.039011 → fer; atributos efetivos diferentes da rodada 1 — fer: st 654→523
  - Rodada 25: 1.021938 / 1.058923 → fer
  - Rodada 26: 1.021938 / 1.058923 → fer
  - Rodada 27: 1.021938 / 1.058923 → fer
  - Rodada 28: 1.021938 / 1.058923 → fer
  - Rodada 29: 1.021938 / 1.058923 → fer
  - Rodada 30: 1.021938 / 1.058923 → fer
  - Rodada 31: 1.021938 / 1.058923 → fer
  - Rodada 32: 1.021938 / 1.058923 → fer
  - Rodada 33: 1.021938 / 1.058923 → fer
  - Rodada 34: 1.021938 / 1.058923 → fer
  - Rodada 35: 1.021938 / 1.058923 → fer
  - Rodada 36: 1.002746 / 1.058923 → fer; atributos efetivos diferentes da rodada 1 — Tenz: st 601→480
  - Rodada 37: 1.021938 / 1.058923 → fer
  - Rodada 38: 1.021938 / 1.058923 → fer
  - Rodada 39: 1.021938 / 1.058923 → fer
  - Rodada 40: 1.021938 / 1.058923 → fer
  - Rodada 41: 1.021938 / 1.058923 → fer
  - Rodada 42: 1.021938 / 1.058923 → fer
  - Rodada 43: 1.021938 / 1.058923 → fer
  - Rodada 44: 1.021938 / 1.058923 → fer
  - Rodada 45: 1.021938 / 1.058923 → fer
  - Rodada 46: 1.021938 / 1.058923 → fer
  - Leitura: o vetor da iniciativa usa ST/MG/AG/DF efetivos e os TETOS de HP e MP, então um buff de atributo do próprio lado e um status do adversário que reduz atributo ou teto entram na ordem da rodada seguinte; quando expiram, saem dela.
- Na última rodada, Tenz havia travado Ataque básico (ataque básico); a ação ficou cancelada por morte, porque fer agiu antes e o golpe dele encerrou o duelo.
- Margem (estimativa, não registro): fer terminou com 2232 de HP; o dano médio por golpe conectado de Tenz foi 279.7, ou seja, ~8.0 golpe(s) conectado(s) de distância.
- Sustentação de Tenz: cura 6752 e Égide 0 contra 12609 de dano recebido.
- Críticos de Tenz: 4, somando 1725 de 6993 de dano de golpe (24.7%).
- Sustentação de fer: cura 3248 e Égide 0 contra 6993 de dano recebido.
- Críticos de fer: 13, somando 5258 de 12609 de dano de golpe (41.7%).
- fer perdeu 1 ação(ões) por controle.
- Economia de ação: fer usou 35 skills e 10 ataques básicos; Tenz, 27 e 18.


## As decisões da IA na final, rodada a rodada

### Tenz (W08)

- R1: **Golpe Poderoso** — P(vitória) 0.404±0.002 com Golpe Poderoso; contra Soco de Placa 0.404, ataque básico 0.403, Gancho e Corda 0.403; dano esperado 278; custa 52 MP. Opções: Golpe Poderoso 0,404; Soco de Placa 0,404; ataque básico 0,403; Gancho e Corda 0,403; Tomar Fôlego 0,400. PoliticaCopa: Gancho e Corda.
- R2: **Tomar Fôlego** — P(vitória) 0.292±0.002 com Tomar Fôlego; contra Soco de Placa 0.290, Gancho e Corda 0.290, ataque básico 0.288; custa 93 MP. Opções: Tomar Fôlego 0,292; Soco de Placa 0,290; Gancho e Corda 0,290; ataque básico 0,288. PoliticaCopa: Gancho e Corda.
- R3: **ataque básico** — P(vitória) 0.248±0.003 com ataque básico; contra Golpe Poderoso 0.248, Soco de Placa 0.248, Gancho e Corda 0.247; dano esperado 112. Opções: ataque básico 0,248; Golpe Poderoso 0,248; Soco de Placa 0,248; Gancho e Corda 0,247. PoliticaCopa: Gancho e Corda.
- R4: **Golpe Poderoso** — P(vitória) 0.202±0.002 com Golpe Poderoso; contra Soco de Placa 0.202, ataque básico 0.201, Gancho e Corda 0.201; dano esperado 180; custa 52 MP. Opções: Golpe Poderoso 0,202; Soco de Placa 0,202; ataque básico 0,201; Gancho e Corda 0,201. PoliticaCopa: Gancho e Corda.
- R5: **Soco de Placa** — P(vitória) 0.201±0.003 com Soco de Placa; contra ataque básico 0.201, Gancho e Corda 0.197; dano esperado 198; custa 61 MP. Opções: Soco de Placa 0,201; ataque básico 0,201; Gancho e Corda 0,197. PoliticaCopa: Gancho e Corda.
- R6: **Golpe Poderoso** — P(vitória) 0.173±0.003 com Golpe Poderoso; contra ataque básico 0.173, Gancho e Corda 0.170; dano esperado 203; custa 52 MP. Opções: Golpe Poderoso 0,173; ataque básico 0,173; Gancho e Corda 0,170. PoliticaCopa: Gancho e Corda.
- R7: **Tomar Fôlego** — P(vitória) 0.173±0.003 com Tomar Fôlego; contra Soco de Placa 0.170, ataque básico 0.169, Gancho e Corda 0.167; custa 93 MP. Opções: Tomar Fôlego 0,173; Soco de Placa 0,170; ataque básico 0,169; Gancho e Corda 0,168. PoliticaCopa: Gancho e Corda.
- R8: **Golpe Poderoso** — P(vitória) 0.159±0.003 com Golpe Poderoso; contra Soco de Placa 0.157, ataque básico 0.157, Gancho e Corda 0.154; dano esperado 215; custa 52 MP. Opções: Golpe Poderoso 0,159; Soco de Placa 0,157; ataque básico 0,157; Gancho e Corda 0,154. PoliticaCopa: Gancho e Corda.
- R9: **ataque básico** — P(vitória) 0.158±0.004 com ataque básico; contra Soco de Placa 0.157, Gancho e Corda 0.155; dano esperado 121. Opções: ataque básico 0,158; Soco de Placa 0,157; Gancho e Corda 0,155. PoliticaCopa: Gancho e Corda.
- R10: **Golpe Poderoso** — P(vitória) 0.155±0.005 com Golpe Poderoso; contra Soco de Placa 0.155, ataque básico 0.153, Gancho e Corda 0.152; dano esperado 226; custa 52 MP. Opções: Golpe Poderoso 0,155; Soco de Placa 0,155; ataque básico 0,153; Gancho e Corda 0,152. PoliticaCopa: Gancho e Corda.
- R11: **Soco de Placa** — P(vitória) 0.190±0.006 com Soco de Placa; contra ataque básico 0.189, Gancho e Corda 0.177; dano esperado 252; custa 61 MP. Opções: Soco de Placa 0,190; ataque básico 0,189; Gancho e Corda 0,177. PoliticaCopa: Gancho e Corda.
- R12: **Golpe Poderoso** — P(vitória) 0.198±0.006 com Golpe Poderoso; contra Tomar Fôlego 0.197, ataque básico 0.196, Gancho e Corda 0.190; dano esperado 243; custa 52 MP. Opções: Golpe Poderoso 0,198; Tomar Fôlego 0,198; ataque básico 0,196; Gancho e Corda 0,190. PoliticaCopa: Gancho e Corda.
- R13: **Tomar Fôlego** — P(vitória) 0.181±0.008 com Tomar Fôlego; contra Soco de Placa 0.177, ataque básico 0.172, Gancho e Corda 0.166; custa 93 MP. Opções: Tomar Fôlego 0,181; Soco de Placa 0,176; ataque básico 0,172; Gancho e Corda 0,166. PoliticaCopa: Gancho e Corda.
- R14: **ataque básico** — P(vitória) 0.180±0.006 com ataque básico; contra Golpe Poderoso 0.179, Soco de Placa 0.179, Gancho e Corda 0.170; dano esperado 144. Opções: ataque básico 0,180; Golpe Poderoso 0,179; Soco de Placa 0,179; Gancho e Corda 0,170. PoliticaCopa: Gancho e Corda.
- R15: **Golpe Poderoso** — P(vitória) 0.173±0.008 com Golpe Poderoso; contra Soco de Placa 0.172, ataque básico 0.171, Gancho e Corda 0.163; dano esperado 193; custa 52 MP. Opções: Golpe Poderoso 0,173; Soco de Placa 0,172; ataque básico 0,171; Gancho e Corda 0,163. PoliticaCopa: Gancho e Corda.
- R16: **Gancho e Corda** — P(vitória) 0.153±0.004 com Gancho e Corda; contra Soco de Placa 0.149, ataque básico 0.145; custa 117 MP. Opções: Gancho e Corda 0,153; Soco de Placa 0,149; ataque básico 0,145. PoliticaCopa: Gancho e Corda.
- R17: **Golpe Poderoso** — P(vitória) 0.169±0.006 com Golpe Poderoso; contra Soco de Placa 0.169, ataque básico 0.166; dano esperado 197; custa 52 MP. Opções: Golpe Poderoso 0,169; Soco de Placa 0,169; ataque básico 0,166. PoliticaCopa: Golpe Poderoso.
- R18: **Tomar Fôlego** — P(vitória) 0.127±0.007 com Tomar Fôlego; contra Soco de Placa 0.121, ataque básico 0.120; custa 93 MP. Opções: Tomar Fôlego 0,127; Soco de Placa 0,121; ataque básico 0,120. PoliticaCopa: Soco de Placa.
- R19: **ataque básico** — P(vitória) 0.137±0.007 com ataque básico; contra Soco de Placa 0.137, Golpe Poderoso 0.136; dano esperado 135. Opções: ataque básico 0,137; Golpe Poderoso 0,137; Soco de Placa 0,137. PoliticaCopa: Golpe Poderoso.
- R20: **Soco de Placa** — P(vitória) 0.147±0.007 com Soco de Placa; contra Golpe Poderoso 0.147, ataque básico 0.145; dano esperado 250; custa 61 MP. Opções: Golpe Poderoso 0,146; Soco de Placa 0,147; ataque básico 0,145. PoliticaCopa: Golpe Poderoso.
- R21: **ataque básico** — P(vitória) 0.135±0.006 com ataque básico; contra Golpe Poderoso 0.134, Gancho e Corda 0.129; dano esperado 140. Opções: ataque básico 0,135; Golpe Poderoso 0,134; Gancho e Corda 0,129. PoliticaCopa: Gancho e Corda.
- R22: **Soco de Placa** — P(vitória) 0.117±0.004 com Soco de Placa; contra Golpe Poderoso 0.116, ataque básico 0.115, Gancho e Corda 0.113; dano esperado 251; custa 61 MP. Opções: Soco de Placa 0,117; Golpe Poderoso 0,117; ataque básico 0,115; Gancho e Corda 0,113. PoliticaCopa: Gancho e Corda.
- R23: **Tomar Fôlego** — P(vitória) 0.125±0.004 com Tomar Fôlego; contra ataque básico 0.119, Golpe Poderoso 0.119, Gancho e Corda 0.120; custa 93 MP. Opções: Tomar Fôlego 0,125; ataque básico 0,119; Golpe Poderoso 0,119; Gancho e Corda 0,120. PoliticaCopa: Tomar Fôlego.
- R24: **ataque básico** — P(vitória) 0.146±0.008 com ataque básico; contra Golpe Poderoso 0.146, Soco de Placa 0.146, Gancho e Corda 0.126; dano esperado 142. Opções: ataque básico 0,146; Golpe Poderoso 0,146; Soco de Placa 0,146; Gancho e Corda 0,126. PoliticaCopa: Gancho e Corda.
- R25: **Soco de Placa** — P(vitória) 0.141±0.004 com Soco de Placa; contra ataque básico 0.140, Golpe Poderoso 0.139, Gancho e Corda 0.130; dano esperado 255; custa 61 MP. Opções: Soco de Placa 0,141; ataque básico 0,140; Golpe Poderoso 0,139; Gancho e Corda 0,130. PoliticaCopa: Gancho e Corda.
- R26: **Golpe Poderoso** — P(vitória) 0.127±0.003 com Golpe Poderoso; contra ataque básico 0.127, Gancho e Corda 0.123; dano esperado 245; custa 52 MP. Opções: Golpe Poderoso 0,127; ataque básico 0,127; Gancho e Corda 0,123. PoliticaCopa: Gancho e Corda.
- R27: **Soco de Placa** — P(vitória) 0.133±0.008 com Soco de Placa; contra ataque básico 0.132, Gancho e Corda 0.126; dano esperado 258; custa 61 MP. Opções: Soco de Placa 0,133; ataque básico 0,132; Gancho e Corda 0,126. PoliticaCopa: Gancho e Corda.
- R28: **Tomar Fôlego** — P(vitória) 0.112±0.003 com Tomar Fôlego; contra ataque básico 0.107, Golpe Poderoso 0.106, Gancho e Corda 0.097; custa 93 MP. Opções: Tomar Fôlego 0,112; ataque básico 0,107; Golpe Poderoso 0,106; Gancho e Corda 0,097. PoliticaCopa: Tomar Fôlego.
- R29: **ataque básico** — P(vitória) 0.116±0.004 com ataque básico; contra Golpe Poderoso 0.115, Soco de Placa 0.114; dano esperado 144. Opções: ataque básico 0,116; Golpe Poderoso 0,115; Soco de Placa 0,114. PoliticaCopa: Golpe Poderoso.
- R30: **Soco de Placa** — P(vitória) 0.115±0.006 com Soco de Placa; contra ataque básico 0.112, Golpe Poderoso 0.112, Gancho e Corda 0.100; dano esperado 257; custa 61 MP. Opções: Soco de Placa 0,115; ataque básico 0,112; Golpe Poderoso 0,112; Gancho e Corda 0,100. PoliticaCopa: Gancho e Corda.
- R31: **ataque básico** — P(vitória) 0.092±0.008 com ataque básico; contra Golpe Poderoso 0.091; dano esperado 144. Opções: ataque básico 0,092; Golpe Poderoso 0,091. PoliticaCopa: Golpe Poderoso.
- R32: **ataque básico** — P(vitória) 0.086±0.003 com ataque básico; contra Soco de Placa 0.084, Golpe Poderoso 0.084; dano esperado 144. Opções: ataque básico 0,086; Soco de Placa 0,084; Golpe Poderoso 0,084. PoliticaCopa: Golpe Poderoso.
- R33: **Tomar Fôlego** — P(vitória) 0.088±0.007 com Tomar Fôlego; contra Golpe Poderoso 0.087, Soco de Placa 0.085, ataque básico 0.084; custa 93 MP. Opções: Tomar Fôlego 0,088; Golpe Poderoso 0,087; Soco de Placa 0,085; ataque básico 0,084; Gancho e Corda 0,080. PoliticaCopa: Tomar Fôlego.
- R34: **Golpe Poderoso** — P(vitória) 0.099±0.006 com Golpe Poderoso; contra ataque básico 0.096; dano esperado 245; custa 52 MP. Opções: Golpe Poderoso 0,099; ataque básico 0,096. PoliticaCopa: Golpe Poderoso.
- R35: **ataque básico** — só o básico é legal (Golpe Poderoso: recarga, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R36: **ataque básico** — só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R37: **Soco de Placa** — P(vitória) 0.072±0.005 com Soco de Placa; contra ataque básico 0.071, Golpe Poderoso 0.070; dano esperado 312; custa 61 MP. Opções: Soco de Placa 0,072; ataque básico 0,071; Golpe Poderoso 0,070. PoliticaCopa: Golpe Poderoso.
- R38: **ataque básico** — só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: recarga, Tomar Fôlego: mp). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R39: **ataque básico** — só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: mp). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R40: **ataque básico** — P(vitória) 0.040±0.008 com ataque básico; contra Golpe Poderoso 0.032, Soco de Placa 0.032; dano esperado 136. Opções: ataque básico 0,040; Golpe Poderoso 0,032; Soco de Placa 0,032. PoliticaCopa: Golpe Poderoso.
- R41: **ataque básico** — P(vitória) 0.034±0.009 com ataque básico; contra Golpe Poderoso 0.032, Soco de Placa 0.032, Tomar Fôlego 0.031; dano esperado 136. Opções: ataque básico 0,034; Golpe Poderoso 0,032; Soco de Placa 0,032; Tomar Fôlego 0,031. PoliticaCopa: Tomar Fôlego.
- R42: **Tomar Fôlego** — P(vitória) 0.047±0.002 com Tomar Fôlego; contra ataque básico 0.042, Golpe Poderoso 0.028, Soco de Placa 0.028; custa 93 MP. Opções: Tomar Fôlego 0,047; ataque básico 0,042; Golpe Poderoso 0,028; Soco de Placa 0,028. PoliticaCopa: Tomar Fôlego.
- R43: **ataque básico** — só o básico é legal (Golpe Poderoso: mp, Gancho e Corda: mp, Soco de Placa: mp, Tomar Fôlego: recarga). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R44: **ataque básico** — P(vitória) 0.005±0.006 com ataque básico; contra Soco de Placa 0.005, Golpe Poderoso 0.004; dano esperado 139. Opções: ataque básico 0,005; Soco de Placa 0,005; Golpe Poderoso 0,004. PoliticaCopa: Golpe Poderoso.
- R45: **ataque básico** — P(vitória) 0.000±0.000 com ataque básico; contra Golpe Poderoso 0.000, Soco de Placa 0.000; dano esperado 140. Opções: ataque básico 0,000; Golpe Poderoso 0,000; Soco de Placa 0,000. PoliticaCopa: Golpe Poderoso.
- R46: **ataque básico** — P(vitória) 0.000±0.000 com ataque básico; contra Golpe Poderoso 0.000, Soco de Placa 0.000; dano esperado 140. Opções: ataque básico 0,000; Golpe Poderoso 0,000; Soco de Placa 0,000. PoliticaCopa: Golpe Poderoso.

### fer (W64)

- R1: **Golpe Poderoso** — P(vitória) 0.481±0.002 com Golpe Poderoso; contra Soco de Placa 0.480, ataque básico 0.479, Juramento da Muralha 0.477; dano esperado 326; custa 52 MP. Opções: Golpe Poderoso 0,481; Soco de Placa 0,480; ataque básico 0,479; Juramento da Muralha 0,477; Respirar Fundo 0,466. PoliticaCopa: Juramento da Muralha.
- R2: **Soco de Placa** — P(vitória) 0.559±0.008 com Soco de Placa; contra ataque básico 0.553, Juramento da Muralha 0.540, Respirar Fundo 0.528; dano esperado 360; custa 61 MP. Opções: Soco de Placa 0,559; ataque básico 0,553; Juramento da Muralha 0,540; Respirar Fundo 0,528. PoliticaCopa: Juramento da Muralha.
- R3: **Golpe Poderoso** — P(vitória) 0.565±0.008 com Golpe Poderoso; contra ataque básico 0.562, Juramento da Muralha 0.537, Respirar Fundo 0.526; dano esperado 368; custa 52 MP. Opções: Golpe Poderoso 0,565; ataque básico 0,562; Juramento da Muralha 0,537; Respirar Fundo 0,525. PoliticaCopa: Juramento da Muralha.
- R4: **ataque básico** — P(vitória) 0.519±0.012 com ataque básico; contra Soco de Placa 0.518, Juramento da Muralha 0.506, Respirar Fundo 0.483; dano esperado 194. Opções: ataque básico 0,519; Soco de Placa 0,518; Juramento da Muralha 0,506; Respirar Fundo 0,483. PoliticaCopa: Juramento da Muralha.
- R5: **Soco de Placa** — P(vitória) 0.480±0.010 com Soco de Placa; contra Golpe Poderoso 0.479, ataque básico 0.479, Juramento da Muralha 0.469; dano esperado 324; custa 61 MP. Opções: Soco de Placa 0,480; Golpe Poderoso 0,479; ataque básico 0,479; Juramento da Muralha 0,469; Respirar Fundo 0,459. PoliticaCopa: Juramento da Muralha.
- R6: **Golpe Poderoso** — P(vitória) 0.589±0.014 com Golpe Poderoso; contra ataque básico 0.577, Juramento da Muralha 0.549, Respirar Fundo 0.536; dano esperado 360; custa 52 MP. Opções: Golpe Poderoso 0,589; ataque básico 0,577; Juramento da Muralha 0,549; Respirar Fundo 0,536. PoliticaCopa: Juramento da Muralha.
- R7: **Soco de Placa** — P(vitória) 0.547±0.022 com Soco de Placa; contra ataque básico 0.543, Respirar Fundo 0.523, Juramento da Muralha 0.519; dano esperado 331; custa 61 MP. Opções: Soco de Placa 0,547; ataque básico 0,543; Respirar Fundo 0,523; Juramento da Muralha 0,519. PoliticaCopa: Juramento da Muralha.
- R8: **Golpe Poderoso** — P(vitória) 0.537±0.012 com Golpe Poderoso; contra ataque básico 0.536, Respirar Fundo 0.516, Juramento da Muralha 0.516; dano esperado 338; custa 52 MP. Opções: Golpe Poderoso 0,537; ataque básico 0,536; Respirar Fundo 0,516; Juramento da Muralha 0,516. PoliticaCopa: Juramento da Muralha.
- R9: **Soco de Placa** — P(vitória) 0.509±0.013 com Soco de Placa; contra ataque básico 0.505, Respirar Fundo 0.491, Juramento da Muralha 0.482; dano esperado 314; custa 61 MP. Opções: Soco de Placa 0,509; ataque básico 0,505; Respirar Fundo 0,491; Juramento da Muralha 0,482. PoliticaCopa: Juramento da Muralha.
- R10: **Golpe Poderoso** — P(vitória) 0.463±0.014 com Golpe Poderoso; contra ataque básico 0.460, Respirar Fundo 0.446, Juramento da Muralha 0.442; dano esperado 290; custa 52 MP. Opções: Golpe Poderoso 0,463; ataque básico 0,460; Respirar Fundo 0,446; Juramento da Muralha 0,442. PoliticaCopa: Juramento da Muralha.
- R11: **ataque básico** — P(vitória) 0.402±0.016 com ataque básico; contra Soco de Placa 0.401, Respirar Fundo 0.395, Juramento da Muralha 0.395; dano esperado 163. Opções: ataque básico 0,402; Soco de Placa 0,401; Respirar Fundo 0,395; Juramento da Muralha 0,396. PoliticaCopa: Juramento da Muralha.
- R12: **Soco de Placa** — P(vitória) 0.430±0.025 com Soco de Placa; contra Golpe Poderoso 0.427, ataque básico 0.417, Respirar Fundo 0.414; dano esperado 293; custa 61 MP. Opções: Soco de Placa 0,430; Golpe Poderoso 0,427; ataque básico 0,417; Respirar Fundo 0,414; Juramento da Muralha 0,413. PoliticaCopa: Juramento da Muralha.
- R13: **Golpe Poderoso** — P(vitória) 0.383±0.018 com Golpe Poderoso; contra Respirar Fundo 0.376, ataque básico 0.374, Juramento da Muralha 0.375; dano esperado 271; custa 52 MP. Opções: Golpe Poderoso 0,383; Respirar Fundo 0,377; ataque básico 0,374; Juramento da Muralha 0,375. PoliticaCopa: Juramento da Muralha.
- R14: **Soco de Placa** — P(vitória) 0.361±0.019 com Soco de Placa; contra Juramento da Muralha 0.362, Respirar Fundo 0.361, ataque básico 0.355; dano esperado 286; custa 61 MP. Opções: Soco de Placa 0,361; Juramento da Muralha 0,362; Respirar Fundo 0,361; ataque básico 0,355. PoliticaCopa: Juramento da Muralha.
- R15: **Golpe Poderoso** — P(vitória) 0.374±0.016 com Golpe Poderoso; contra ataque básico 0.372, Respirar Fundo 0.370, Juramento da Muralha 0.370; dano esperado 267; custa 52 MP. Opções: Golpe Poderoso 0,374; ataque básico 0,372; Respirar Fundo 0,370; Juramento da Muralha 0,370. PoliticaCopa: Juramento da Muralha.
- R16: **Soco de Placa** — P(vitória) 0.467±0.017 com Soco de Placa; contra ataque básico 0.461, Respirar Fundo 0.448, Juramento da Muralha 0.438; dano esperado 291; custa 61 MP. Opções: Soco de Placa 0,467; ataque básico 0,461; Respirar Fundo 0,448; Juramento da Muralha 0,438. PoliticaCopa: Juramento da Muralha.
- R17: **ataque básico** — P(vitória) 0.426±0.036 com ataque básico; contra Golpe Poderoso 0.426, Juramento da Muralha 0.426, Respirar Fundo 0.426; dano esperado 162. Opções: ataque básico 0,426; Golpe Poderoso 0,426; Juramento da Muralha 0,426; Respirar Fundo 0,426. PoliticaCopa: Juramento da Muralha.
- R18: **ataque básico** — P(vitória) 0.563±0.021 com ataque básico; contra Golpe Poderoso 0.544, Soco de Placa 0.537, Respirar Fundo 0.519; dano esperado 163. Opções: ataque básico 0,563; Golpe Poderoso 0,543; Soco de Placa 0,537; Respirar Fundo 0,519; Juramento da Muralha 0,505. PoliticaCopa: Juramento da Muralha.
- R19: **Soco de Placa** — P(vitória) 0.485±0.025 com Soco de Placa; contra Golpe Poderoso 0.482, ataque básico 0.478, Respirar Fundo 0.466; dano esperado 290; custa 61 MP. Opções: Soco de Placa 0,485; Golpe Poderoso 0,482; ataque básico 0,477; Respirar Fundo 0,466; Juramento da Muralha 0,459. PoliticaCopa: Juramento da Muralha.
- R20: **Golpe Poderoso** — P(vitória) 0.552±0.024 com Golpe Poderoso; contra ataque básico 0.543, Respirar Fundo 0.510, Juramento da Muralha 0.500; dano esperado 283; custa 52 MP. Opções: Golpe Poderoso 0,552; ataque básico 0,543; Respirar Fundo 0,510; Juramento da Muralha 0,500. PoliticaCopa: Juramento da Muralha.
- R21: **Respirar Fundo** — P(vitória) 0.577±0.025 com Respirar Fundo; contra ataque básico 0.574, Soco de Placa 0.571, Juramento da Muralha 0.543; custa 82 MP. Opções: Respirar Fundo 0,577; ataque básico 0,574; Soco de Placa 0,571; Juramento da Muralha 0,543. PoliticaCopa: Juramento da Muralha.
- R22: **ataque básico** — P(vitória) 0.617±0.024 com ataque básico; contra Golpe Poderoso 0.613, Soco de Placa 0.611, Juramento da Muralha 0.550; dano esperado 169. Opções: ataque básico 0,617; Golpe Poderoso 0,613; Soco de Placa 0,611; Juramento da Muralha 0,550. PoliticaCopa: Juramento da Muralha.
- R23: **ataque básico** — P(vitória) 0.579±0.012 com ataque básico; contra Golpe Poderoso 0.577, Soco de Placa 0.571, Juramento da Muralha 0.513; dano esperado 138. Opções: ataque básico 0,579; Golpe Poderoso 0,577; Soco de Placa 0,571; Juramento da Muralha 0,513. PoliticaCopa: Juramento da Muralha.
- R24: **ataque básico** — P(vitória) 0.478±0.027 com ataque básico; contra Golpe Poderoso 0.476, Soco de Placa 0.465, Juramento da Muralha 0.453; dano esperado 138. Opções: ataque básico 0,478; Golpe Poderoso 0,476; Soco de Placa 0,465; Juramento da Muralha 0,453. PoliticaCopa: Juramento da Muralha.
- R25: **ataque básico** — P(vitória) 0.560±0.021 com ataque básico; contra Golpe Poderoso 0.557, Soco de Placa 0.557, Juramento da Muralha 0.510; dano esperado 170. Opções: ataque básico 0,560; Golpe Poderoso 0,557; Soco de Placa 0,557; Juramento da Muralha 0,510. PoliticaCopa: Juramento da Muralha.
- R26: **Respirar Fundo** — P(vitória) 0.578±0.011 com Respirar Fundo; contra Soco de Placa 0.572, Golpe Poderoso 0.568, ataque básico 0.536; custa 82 MP. Opções: Respirar Fundo 0,578; Soco de Placa 0,572; Golpe Poderoso 0,568; ataque básico 0,536; Juramento da Muralha 0,531. PoliticaCopa: Respirar Fundo.
- R27: **Golpe Poderoso** — P(vitória) 0.573±0.035 com Golpe Poderoso; contra ataque básico 0.558, Soco de Placa 0.558, Juramento da Muralha 0.519; dano esperado 284; custa 52 MP. Opções: Golpe Poderoso 0,573; ataque básico 0,558; Soco de Placa 0,558; Juramento da Muralha 0,518. PoliticaCopa: Juramento da Muralha.
- R28: **Soco de Placa** — P(vitória) 0.631±0.017 com Soco de Placa; contra ataque básico 0.618, Juramento da Muralha 0.553; dano esperado 297; custa 61 MP. Opções: Soco de Placa 0,630; ataque básico 0,618; Juramento da Muralha 0,552. PoliticaCopa: Juramento da Muralha.
- R29: **Golpe Poderoso** — P(vitória) 0.537±0.023 com Golpe Poderoso; contra ataque básico 0.535, Juramento da Muralha 0.506; dano esperado 283; custa 52 MP. Opções: Golpe Poderoso 0,537; ataque básico 0,535; Juramento da Muralha 0,506. PoliticaCopa: Juramento da Muralha.
- R30: **Soco de Placa** — P(vitória) 0.548±0.020 com Soco de Placa; contra ataque básico 0.547, Juramento da Muralha 0.510; dano esperado 295; custa 61 MP. Opções: Soco de Placa 0,548; ataque básico 0,547; Juramento da Muralha 0,510. PoliticaCopa: Juramento da Muralha.
- R31: **Golpe Poderoso** — P(vitória) 0.618±0.016 com Golpe Poderoso; contra ataque básico 0.617, Respirar Fundo 0.573, Juramento da Muralha 0.534; dano esperado 279; custa 52 MP. Opções: Golpe Poderoso 0,618; ataque básico 0,617; Respirar Fundo 0,573; Juramento da Muralha 0,534. PoliticaCopa: Juramento da Muralha.
- R32: **Soco de Placa** — P(vitória) 0.670±0.022 com Soco de Placa; contra ataque básico 0.666, Respirar Fundo 0.624, Juramento da Muralha 0.578; dano esperado 293; custa 61 MP. Opções: Soco de Placa 0,670; ataque básico 0,666; Respirar Fundo 0,624; Juramento da Muralha 0,579. PoliticaCopa: Juramento da Muralha.
- R33: **ataque básico** — P(vitória) 0.679±0.029 com ataque básico; contra Golpe Poderoso 0.672, Respirar Fundo 0.634, Juramento da Muralha 0.578; dano esperado 163. Opções: ataque básico 0,679; Golpe Poderoso 0,672; Respirar Fundo 0,634; Juramento da Muralha 0,578. PoliticaCopa: Juramento da Muralha.
- R34: **Golpe Poderoso** — P(vitória) 0.621±0.022 com Golpe Poderoso; contra Soco de Placa 0.619, ataque básico 0.616, Respirar Fundo 0.598; dano esperado 276; custa 52 MP. Opções: Golpe Poderoso 0,621; Soco de Placa 0,619; ataque básico 0,616; Respirar Fundo 0,598; Juramento da Muralha 0,562. PoliticaCopa: Juramento da Muralha.
- R35: **Soco de Placa** — P(vitória) 0.690±0.032 com Soco de Placa; contra ataque básico 0.678, Respirar Fundo 0.665, Juramento da Muralha 0.591; dano esperado 296; custa 61 MP. Opções: Soco de Placa 0,690; ataque básico 0,678; Respirar Fundo 0,665; Juramento da Muralha 0,591. PoliticaCopa: Respirar Fundo.
- R36: **Golpe Poderoso** — P(vitória) 0.728±0.026 com Golpe Poderoso; contra ataque básico 0.712, Respirar Fundo 0.704, Juramento da Muralha 0.612; dano esperado 280; custa 52 MP. Opções: Golpe Poderoso 0,728; ataque básico 0,712; Respirar Fundo 0,704; Juramento da Muralha 0,612. PoliticaCopa: Respirar Fundo.
- R37: **Respirar Fundo** — P(vitória) 0.774±0.023 com Respirar Fundo; contra Soco de Placa 0.747, ataque básico 0.744, Juramento da Muralha 0.652; custa 82 MP. Opções: Respirar Fundo 0,774; Soco de Placa 0,747; ataque básico 0,744; Juramento da Muralha 0,652. PoliticaCopa: Respirar Fundo.
- R38: **Golpe Poderoso** — P(vitória) 0.803±0.023 com Golpe Poderoso; contra Soco de Placa 0.800, ataque básico 0.794, Juramento da Muralha 0.657; dano esperado 278; custa 52 MP. Opções: Golpe Poderoso 0,803; Soco de Placa 0,800; ataque básico 0,794; Juramento da Muralha 0,657. PoliticaCopa: Juramento da Muralha.
- R39: **Soco de Placa** — P(vitória) 0.892±0.028 com Soco de Placa; contra ataque básico 0.877, Juramento da Muralha 0.771; dano esperado 300; custa 61 MP. Opções: Soco de Placa 0,892; ataque básico 0,877; Juramento da Muralha 0,771. PoliticaCopa: Juramento da Muralha.
- R40: **Golpe Poderoso** — P(vitória) 0.901±0.011 com Golpe Poderoso; contra ataque básico 0.893, Juramento da Muralha 0.847; dano esperado 284; custa 52 MP. Opções: Golpe Poderoso 0,901; ataque básico 0,893; Juramento da Muralha 0,847. PoliticaCopa: Juramento da Muralha.
- R41: **Soco de Placa** — P(vitória) 0.919±0.014 com Soco de Placa; contra ataque básico 0.893; dano esperado 299; custa 61 MP. Opções: Soco de Placa 0,919; ataque básico 0,893. PoliticaCopa: Soco de Placa.
- R42: **Golpe Poderoso** — P(vitória) 0.979±0.006 com Golpe Poderoso; contra Respirar Fundo 0.919, ataque básico 0.919; dano esperado 280; chance de derrubar já 28%; custa 52 MP. Opções: Golpe Poderoso 0,979; Respirar Fundo 0,919; ataque básico 0,919. PoliticaCopa: Respirar Fundo.
- R43: **Soco de Placa** — P(vitória) 0.951±0.016 com Soco de Placa; contra ataque básico 0.857; dano esperado 295; custa 61 MP. Opções: Soco de Placa 0,951; ataque básico 0,857. PoliticaCopa: Soco de Placa.
- R44: **ataque básico** — só o básico é legal (Golpe Poderoso: mp, Juramento da Muralha: mp, Respirar Fundo: mp, Soco de Placa: recarga). Opções: ataque básico —. PoliticaCopa: ataque básico.
- R45: **Golpe Poderoso** — P(vitória) 0.958±0.008 com Golpe Poderoso; contra ataque básico 0.955; dano esperado 276; chance de derrubar já 28%; custa 52 MP. Opções: Golpe Poderoso 0,958; ataque básico 0,955. PoliticaCopa: Golpe Poderoso.
- R46: **ataque básico** — só o básico é legal (Golpe Poderoso: recarga, Juramento da Muralha: mp, Respirar Fundo: mp, Soco de Placa: mp). Opções: ataque básico —. PoliticaCopa: ataque básico.

