# Gameplay Contracts

Decisões de design que **não podem ser alteradas de passagem** por outra fase.
Quebrar uma delas muda o significado de um sistema. Isso pode até ser a decisão
certa, mas tem de ser tomada de propósito, registrada aqui e com o teste
correspondente atualizado no mesmo commit.

Este arquivo não lista constantes. O valor vigente de cada número está no código
(`src/shared/constants.py`, `src/data/*.json`). O design completo está em
[`GAME_DESIGN.md`](GAME_DESIGN.md), e o histórico de como se chegou aqui, em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md).

---

## Dungeon

- **A dungeon é infinita.** Não existe andar final nem condição de vitória.
- **Uma run bem-sucedida termina por extração.** O personagem extraído é
  preservado e não volta para a mesma dungeon.
- **Permadeath.** Na morte, o save é apagado e o troféu é gravado.
- **Combate é sempre 1x1**, um herói contra um monstro, chefe e elite incluídos.
  `run_battle` recusa mais de um monstro (`tests/test_combate_1x1.py`).
- **O combate no mapa pode ser evitado.** Contornar um monstro é jogada legal. O
  preço de não lutar vem da economia (taxa de saída, Essência), e não de uma regra
  que proíba evitar.
- **Serviços e eventos são casas do mapa, não recompensas automáticas de fim de
  andar.** Loja, Ferreiro, Evento e Extração só acontecem se o jogador andar até
  eles. Sozinha, no fim do andar, só roda a regra da saída: taxa, descanso parcial
  e juros.

## Classes e crescimento

- **Herói e monstro usam o mesmo crescimento geométrico** (`GROWTH_RATE`).
  Valor fixo por nível contra uma base que cresce foi o defeito estrutural que
  essa regra resolveu.
- **A assimetria entre as classes é intencional.**
  - Os atributos base e os pesos do ataque básico são diferentes por classe.
  - O vetor do herói gera magnitude: somas 2,0, 2,2 e 2,9. O do monstro só
    compõe: soma 1.
  - Calibrar não é igualar: a Etapa 8 mexeu na Força do Warrior e no HP do Rogue
    justamente para preservar a identidade de cada um.
- **Combat/Class Balance é medido sob condições controladas**, na régua
  `expected loadout` (ver [Duas réguas](#duas-réguas-de-balanceamento)).
- **Não se altera uma classe porque uma métrica de progressão real divergiu**
  sem isolar a causa. Na jornada real entram mapa, loot, economia, bot e sorte, e
  a classe é só uma das variáveis.

## Skills e deck

- **Herói e monstro usam a mesma `SkillCard`** e a mesma gramática: não existe
  `MonsterSkill` nem um segundo resolvedor. Todo conteúdo passa pelo mesmo
  validador estático.
- **A proteção da assinatura é do deck automático do monstro.** A primeira carta
  do kit, a assinatura do papel, nunca sai do deck dele.
- **O herói não tem essa proteção.** Ele começa com a assinatura da classe, a
  única skill do nível 1, e pode substituir qualquer uma das 4 skills ativas,
  inclusive essa inicial. Não existe contrato de permanência para a assinatura
  do herói.
- **O deck tem teto de 4 cartas ativas** (`MAX_ACTIVE_SKILLS`), dos dois lados.
- **Desbloqueio por nível.**
  - O herói recebe uma oferta de 3 cartas a cada 3 níveis e escolhe 1.
  - O monstro ganha a carta de `level_required` correspondente, na mesma
    cadência.
- **Com o deck cheio, o herói escolhe** qual das 4 cartas esquecer, ou recusa a
  nova. O motor nunca decide por ele.
- **Com o deck cheio, o monstro sorteia** qual das três cartas que não são a
  assinatura dá lugar à nova. Usa o gerador da run, então a mesma semente dá o
  mesmo deck.
- **O save preserva o deck.** Recarregar não sorteia de novo.

Verificado em `tests/test_structural_invariants.py` (`TestDeckDoMonstro`).

## Mana

- **A mana do monstro pertence ao papel.** O pool vem do multiplicador do
  arquétipo, não de uma constante comum aos nove.
- **O custo percentual mantém a quantidade relativa de casts.** Pool e custo
  crescem pela mesma curva, então quantas vezes um papel conjura com o pool cheio
  não muda com o nível.
- **O custo absoluto (`mana_cost`) continua na carta** por compatibilidade e
  proveniência. O motor só o lê quando o percentual é zero.
- O monstro cobra mana pelo mesmo caminho do herói (`skill_mana_cost`). Não
  existe uma segunda conta de custo.

Verificado em `tests/test_structural_invariants.py` (`TestManaDoMonstro`).

## Dano

Conceitos canônicos. A fórmula é código e vive em `src/mechanics/combat.py`.

- **BASE**: a identidade da ação. São os atributos resolvidos vezes os pesos
  (os da classe no ataque básico, os da carta numa skill), vezes a arma, vezes o
  `power`.
  - O `power` é **derivado** de um orçamento declarado (`bud`), não é número de
    autoria. Ele é rederivado quando a referência muda (`tools/orcamento_de_cartas.py`).
- **Multiplicadores**:
  - o `+MULT` é aditivo: `damage_percent` e o bônus condicional satisfeito somam
    entre si, e só a soma multiplica;
  - o `×MULT` é um produto com teto (`XMULT_CAP`).
  - Não existe balde `FLAT`.
- **Crítico**:
  - **sem fonte, sem crítico**. A chance vem só de fontes declaradas: carta,
    passiva, item, encantamento, buff, poção ou passiva inata do arquétipo;
  - o multiplicador do crítico entra no `×MULT` antes do teto;
  - existe um multiplicador-base único, cujo valor ainda está pendente.
- **Mitigação**: a defesa é a curva `k / (k + defesa)`, então o dano nunca chega a
  zero; depois vem o produto das mitigações.
- **Os consumidores usam os funis canônicos.** Motor, bot, validador, forge e
  ficha do confronto leem as mesmas funções, e ninguém copia a conta:
  - `skill_damage_base`;
  - `damage_modifiers` e `additive_multiplier`;
  - `crit_chance`, `crit_multiplier` e `expected_crit_factor`;
  - `fx.combat_modifier`, o funil único de buff, passiva e equipamento.
- Nada multiplica dano fora do funil, e isso inclui as leis de interação.

## Starter Kit

Contrato fechado. Vive em `src/content/starter_kit.py` e
`src/data/starter_kit.json`, e é verificado por `tests/test_starter_kit.py`.

- Toda nova jornada recebe **exatamente 1 item**, já equipado.
- O item é **Lv1**: Common com `shop_min_floor` 1, sem consumível e sem
  restrição de classe.
- **A pool é compartilhada** pelas três classes e separada do loot.
- O sorteio é feito primeiro pela **categoria, uniforme**, e depois pelo **item,
  uniforme dentro da categoria**.
  - `Weapon1` e `Weapon2` contam como a categoria `Weapon`.
  - `Ring1` e `Ring2` contam como a categoria `Ring`.
  - Sortear por posição daria peso dobrado à arma e ao anel.
- A peça nasce por **`instance()`**: sem socket aleatório nem bônus escondido.
- **`origin="starter"` fica só no exemplar** entregue. A definição do catálogo
  nunca vira starter.
- **Save e load preservam a origem.** Um save antigo, sem o campo, continua
  carregando.
- **O Starter Kit não entra na régua `expected loadout`.** Peças `starter_only`
  ficam fora do loadout de medição, do drop, da loja e da referência de preço.
- **`create_player_for_new_run` é o único caminho de nova jornada.** Usam esse
  caminho a tela do jogador e o BotPadrão.
- **`create_player_from_data` continua neutro**: é o herói puro de testes e
  benchmarks, e não é nova jornada.

## Duas réguas de balanceamento

Elas medem coisas diferentes, e cada uma tem seu próprio estado. O índice das
medições está em [`BASELINES.md`](BASELINES.md).

### Combat/Class Balance

- **Benchmark sintético.** `src/sim/harness.simulate_run` com
  **`loadout="expected"`**: o equipamento esperado para o nível, aplicado sem
  passar pela dungeon.
- As bandas estão em `tests/balance/` e rodam com `pytest -m balance`.
- **Estado: FECHADO** no checkpoint atual (`bc815fcd`).
- **Três bandas medem a dungeon, não as classes.** `MAX_SMART_REACH_20`,
  `MIN_TOTAL_ATTRITION` e `MAX_CLASS_MEAN_FLOOR` medem dificuldade global sob
  expected loadout.
  - Elas se movem quando a dungeon muda de propósito.
  - Toda remedição registra o valor antigo, o novo, o protocolo e o motivo em
    `tests/balance/thresholds.py`.
  - Foram remedidas duas vezes, por decisão do usuário: no bloco Dungeon / Run
    Progression e no primeiro level-up (`d3105edc`).
- **Todas as outras bandas continuam congeladas**: o spread entre classes (a
  paridade), o TTK, o skill gap, o peso da sorte, os arquétipos e os encontros.
  Uma falha nelas não se resolve mexendo no limite.

### Run/Progression Balance

- **A nova jornada real** com Starter Kit, mapa, loot, economia, serviços, fuga e
  extração, jogada pelo BotPadrão.
- A referência atual é a auditoria do primeiro level-up,
  [`baselines/progression/d3105edc/`](baselines/progression/d3105edc/README.md).
  As anteriores são a auditoria da dungeon,
  [`baselines/progression/4d0a9a0a/`](baselines/progression/4d0a9a0a/README.md),
  a auditoria do instrumento,
  [`baselines/progression/0ab837b9/`](baselines/progression/0ab837b9/README.md),
  e a primeira baseline real, medida com o instrumento antigo,
  [`baselines/progression/fb321d4e/`](baselines/progression/fb321d4e/README.md).
- **Estado: CALIBRADO.** Os problemas estruturais conhecidos foram tratados ou
  aceitos, e o `-m balance` completo passou no `82ff73ea` (118 passed).

> **Um resultado ruim de progressão não reabre automaticamente o balance de
> classe.**

Mudar uma classe exige mostrar a causa na régua de combate, e mantê-la verde.

## BotPadrão

- `tools/bot_padrao.py` é um **instrumento de regressão e medição**.
  - Toda REGRA vem do jogo: criação, andar, combate, pós-combate, loot, loja,
    saída, extração.
  - A DECISÃO mora em `src/sim/bot/` e `tools/bot_adapter.py`.
- **Ele não é a definição do "jogador ideal".** O que ele faz bem ou mal descreve
  a política dele, não o teto do jogo.
- **Um comportamento ruim do bot é uma categoria própria.** Todo achado é
  classificado em uma de cinco categorias antes de virar mudança:
  - bug/mecânica;
  - progressão/dificuldade;
  - comportamento do bot;
  - starter;
  - inconclusivo.
- **Mudar o bot é mudar o instrumento.** Medições de progressão de antes e de
  depois de uma mudança no bot não se comparam sem remedir a baseline.
- **O mapa não revela o monstro ao bot.** O bot sabe o que o jogador sabe.
  - Antes da colisão, um `&` é só casa, distância e caminho (`TargetView`). Não
    há nome, nível, HP, atributos nem dano.
  - Alvos visualmente iguais valem igual para a policy.
  - O estado exato do monstro (`CombatState`) só existe depois da colisão.
  - Protegido por `tests/test_bot_observation.py` e
    `tests/test_bot_decisao_mapa.py`. Esses testes não mudam para acomodar uma
    implementação.
  - Uma decisão melhor antes da luta vem do que o jogador sabe: o histórico
    observado e os recursos que de fato pode pagar.

## Arena

Fase 1 do PvP, na branch `phase/pvp-arena`, sobre a fundação congelada em
`v0.3-pve`. **O motor do duelo existe e é headless**: dois gladiadores, decisões
simultâneas, resolução sequencial. **A Arena ainda não é modo de jogo**: não há
entrada no menu, fila, MMR, UI nem rede, e carregar um personagem extraído
continua avisando que a Arena não está aberta.

Verificado em `tests/test_pvp_duel.py` e `tests/test_pvp_initiative.py`.

### Fronteira com o PvE

- **O PvP não muda o PvE.** `run_battle` continua herói contra monstro, com a
  ordem por AG e o teto `MAX_BATTLE_TURNS`, e não é tocado.
- **O duelo é uma orquestração própria** (`src/mechanics/pvp_duel.py`) sobre as
  MESMAS regras: `apply_skill`, `resolve_physical_attack` e
  `process_turn_start_effects`. Não existe segundo resolvedor de dano, efeito,
  recarga ou mana. Dano físico e mágico, crítico, evasão, defesa, mitigação,
  resistência, cura, roubo de vida, Égide, regeneração de 2% do MP, recargas,
  efeitos, leis de interação e bônus de equipamento valem no duelo porque são o
  mesmo código.
- **O que for descoberto no PvP não altera em silêncio a fundação PvE.** Uma
  mudança em classe, dano, skill ou progressão continua sujeita aos contratos
  acima e às duas réguas.
- `overall_power` (`src/sim/arena.py`) e `tools/arena_alvo.py` continuam sendo
  instrumentos de medição do PvE. Não são o modo de jogo, e `overall_power` não
  é iniciativa.

### Regras aprovadas e implementadas

- **Gladiador.**
  - Só entra um personagem cuja run terminou pela **Extração**.
  - Ele nasce do snapshot de save pelo caminho canônico de reconstrução
    (`src/engine/arena_setup.py`), e a preparação (`src/content/gladiator.py`)
    trabalha numa **cópia**: o snapshot e o personagem salvo não mudam.
  - Na entrada: HP e MP a 100%, buffs, efeitos e recargas da dungeon removidos,
    `death_ignore` rearmado, **todo consumível fora**.
  - **Sem risco de morte**, como diz o pilar da Arena em
    [`GAME_DESIGN.md`](GAME_DESIGN.md): perder o duelo derruba a instância do
    duelo, e não o personagem salvo.
  - Classe, nível, atributos, equipamento, deck e passivas são os do
    personagem. O duelo não tem ação de equipar nem de trocar skill, passiva ou
    atributo: reorganizar equipamento é coisa de antes da fila.
- **Ações:** ataque básico, skill do deck e rendição. Consumível e fuga não
  existem no duelo. **Rendição é derrota imediata**, resolvida no lock, antes de
  qualquer golpe, inclusive sob controle.
- **Rodada.** Os dois escolhem sem ver a escolha do outro → validação das duas
  → reserva de MP → lock → iniciativa → ordem travada → as oportunidades, na
  ordem. A ação ilegal é recusada sem mudar nada.
- **Iniciativa.**
  - `média(sqrt(atributo / REF_atributo(nível)))` sobre HP máx., MP máx., ST, MG,
    AG e DF **efetivos**, com peso igual, vezes o modificador de nível
    `1 + clamp(Δnível × 0,005, −0,10, +0,10)`.
  - Recalculada no início de cada resolução, sobre o estado atual. HP e MP
    atuais não entram. Nenhum arredondamento antes da comparação.
  - **Referência global (`REF`)**: uma por nível, comum às três classes, vinda
    da fundação e sem número próprio:

        REF_s(nível) = média, sobre Warrior, Mage e Rogue, de
                       geometric(CLASS_BASE[s], nível)

    É exatamente a média dos três heróis sem equipamento, passiva nem efeito
    naquele nível (`foundation_reference`, em
    `src/mechanics/pvp_initiative.py`). Ela é neutra (em cada atributo, a média
    das razões das três classes é 1) e não favorece nível: a build sem
    equipamento de cada classe lê o mesmo em todo nível, então quem leva o
    nível para a ordem é só o modificador. Não tem teto próprio. Equipamento,
    buff e passiva mudam o score do gladiador, nunca a referência.
  - **Desempate, definitivo:** maior score, depois maior AG relativa ao nível,
    depois o sorteio pela semente da partida (`SeededCoinTieBreak`). O sorteio só
    acontece quando score e AG relativa são exatamente iguais. Não há
    alternância nem prioridade fixa por lado.
  - É o padrão do duelo: `Duel(p1, p2, rng=random.Random(semente))` já usa as
    referências canônicas e o sorteio. Os dois continuam injetáveis para teste.
  - A ordem travada não muda dentro da rodada. A iniciativa não aparece na
    visão do controlador.
- **Ação comprometida.** Depois do lock ela resolve contra o estado ATUAL da
  batalha: o escudo lançado por quem age primeiro protege do golpe de quem age
  depois. Buff, debuff e mudança de MP não a invalidam. Só **morte do ator** ou
  **controle** a cancelam. Um efeito fora da família `control` só interrompe se
  o contrato o declarar explicitamente interruptivo, e hoje nenhum declara.
- **Interrupção não tem penalidade.** A ação cancelada por controle ou morte
  devolve o MP reservado e não aplica recarga à skill que não saiu.
- **MP reservado.** No lock o custo da skill sai do MP livre e fica reservado.
  Tudo que drena ou consome mana no meio da rodada (`mana_burn`, Égide) só
  alcança o MP livre. A skill paga **uma vez**, pelo caminho de sempre. A
  regeneração não enche o caixa acima de `teto − reserva`.
- **Controle.**
  - `stun`, `frozen` e `sleep` consomem oportunidades: duração N = exatamente N
    oportunidades perdidas.
  - Aplicado antes da ação pendente, ele a cancela e conta como a primeira.
    Aplicado depois que o alvo agiu, pega a próxima.
  - As durações contam as oportunidades do PORTADOR, como no PvE. A iniciativa
    não causa perda dupla nem prolonga efeito.
  - `fear`, `poison`, `bleed`, `mana_burn`, `slowed`, `weakened`, `hexed`,
    `vulnerable` e buffs defensivos não interrompem ação comprometida.
- **Fim.** MD1. Termina na primeira morte, sem ação póstuma e sem empate, na
  rendição, ou por timeout ou desconexão vindos de fora do motor (`forfeit`).
  **Não há teto de rodadas**: `MAX_BATTLE_TURNS` não se aplica, e o motor resolve
  uma rodada por vez, conduzido pela camada de cima. O resultado traz vencedor,
  perdedor, motivo e o histórico das rodadas.

### Pendência de decisão

- **Rendição simultânea.** Hoje perde quem está à frente da ordem travada, para o
  motor ser total. É provisório.

O desempate, as referências globais e as consequências da interrupção, que
apareciam aqui na Fase 1, estão fechados acima.

### Contratos futuros, ainda não implementados

A arquitetura não os impede, mas nenhum existe ainda.

- A fila prioriza humanos por 30 segundos e depois aceita bots. Partida contra
  bot conta normalmente no MMR.
- 45 segundos por decisão, e o primeiro timeout é derrota. A desconexão dá 60
  segundos para voltar e pausa o cronômetro. O motor não tem relógio: os dois
  chegam por `forfeit`.
- MMR individual por gladiador.
- As builds adversárias (equipamento, skills e passivas) ficam visíveis antes do
  duelo.
- A população artificial sai só de heróis extraídos de runs PvE reais.
