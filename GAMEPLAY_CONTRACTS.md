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

Branch `phase/pvp-arena`, sobre a fundação congelada em `v0.3-pve`.

**O ToJ 1.0 é 100% offline, em Python.** A Arena do jogo é a **Arena offline**
(Fase 5): o gladiador extraído do jogador contra uma população fixa de
gladiadores extraídos de runs PvE reais, controlados pela IA estratégica, sem
rede, conta nem servidor.

- **O motor do duelo é headless** (Fases 1 e 1.1): dois gladiadores, decisões
  simultâneas, resolução sequencial.
- **O modo local** (Fase 2) virou a Arena offline (Fase 5).
- **O multiplayer humano × humano** (Fases 3 e 4) continua no repositório e no
  histórico, com os testes e o gate de compatibilidade, mas **fora do fluxo do
  jogo**: o menu não o abre e a Arena não importa `src/multiplayer/`. Os
  contratos dele estão na seção [Multiplayer](#multiplayer--compatibilidade-de-versão).
- **A Arena Ranqueada** (Fases 6 e 6.1, experimental) dá a cada gladiador um MMR
  dinâmico (Glicko-2), com matchmaking automático, 10 partidas de
  posicionamento, 45 divisões de 100 PR de Iron V a Obsidian I, a elite
  (Master, International Master, Distinguished Master) decidida em atualizações
  periódicas da leaderboard, empate técnico por impasse e um mundo NPC × NPC que
  continua jogando. Fila em rede, matchmaking público e relógio de decisão eram
  da ranked online e saem do escopo do 1.0.

Verificado em `tests/test_pvp_duel.py`, `tests/test_pvp_initiative.py`,
`tests/test_pvp_references.py`, `tests/test_arena_mode.py`,
`tests/test_arena_populacao.py`, `tests/test_arena_ia_offline.py` e
`tests/test_ranked_*.py`.

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
  motor ser total. É provisório. Na Arena offline ela não acontece: a IA nunca
  se rende.

O desempate, as referências globais e as consequências da interrupção, que
apareciam aqui na Fase 1, estão fechados acima.

### Arena offline

A opção 3 do menu principal abre o hub da Arena (`src/engine/ranked_mode.py`):
**Duelo Livre** (esta seção), **Arena Ranqueada** (a seção abaixo) e a
**Classificação**. O Duelo Livre é `src/engine/arena_mode.py`, desenhado por
`src/ui/arena_screens.py`.

- **Quem luta.** Do lado do jogador, só personagens salvos com extração
  registrada; um basta. Nenhum gladiador do jogador é gerado. Sem nenhum, a
  Arena explica que falta uma extração e volta ao menu.
- **Preparação.** Ficha do gladiador (atributos, equipamento, skills e
  passivas) e o inventário de sempre, com as regras de sempre: classe, posição e
  mãos.
  - Só equipar e desequipar, e só com a mochila do próprio gladiador. Não há
    loja nem transferência.
  - Consumível aparece e não se usa. Deck, passivas e atributos não mudam.
  - A configuração é confirmada antes do duelo. Gravá-la é escolha explícita, e
    regrava só `equipment` e `inventory` no save do próprio slot
    (`save_loadout`). O resto do save fica como estava.
- **Adversário.** Da [população offline](#população-offline), numa lista com
  filtro de classe e páginas, ordenada pela força de referência. Antes de
  confirmar, a ficha pública: nome, classe, nível, equipamento, skills,
  passivas, o andar da extração e o estilo da run que o formou.
- **Duelo.** O jogador decide pela visão do motor (`HumanDuelController`), e o
  adversário pela IA estratégica (`src/sim/ia_estrategica.py`), só pela visão
  dele. A cada rodada `run_round` monta as duas visões antes de qualquer escolha
  e chama `play_round`.
  - A tela mostra os dois gladiadores, HP, MP, efeitos ativos, skills com custo
    e recarga, e as três ações: ataque básico, skill e rendição.
  - Depois do lock, a rodada aparece na ordem em que o motor a resolveu, com a
    ação de cada lado e os cancelamentos por controle ou morte. O Initiative
    Score não aparece.
- **Fim.** Vitória, derrota ou rendição, o placar do gladiador na sessão, e a
  escolha: revanche, outro adversário ou voltar. O duelo roda sobre cópias:
  ninguém morre, o save não muda, o catálogo não muda e não há XP, ouro nem
  recompensa.

### A IA dos adversários

A mesma IA da Copa Arena 03 v2, trazida de `tools/` para `src/sim/` sem mudar
uma decisão (`test_a_mudanca_para_src_sim_nao_mudou_decisao`).

- **Só ação legal.** Ela escolhe entre as ações de `DuelView.legal_actions`, e
  nunca a rendição.
- **Só a própria visão.** Do adversário ela vê o que a tela mostra (classe,
  nível, HP, MP, efeitos e buffs) e modela o resto a partir do herói canônico da
  classe e do que observa rodada a rodada.
- **Simulação isolada.** As continuações rodam no motor de verdade, sobre
  cópias, com geradores próprios. Escolher não consome o gerador do duelo, não
  mexe nos heróis do duelo e não toca o `random` global.
- **Determinística.** A mesma visão dá a mesma ação; a mesma semente de duelo
  dá a mesma partida.
- **Custo.** No orçamento padrão, uma decisão leva décimos de segundo; o teste
  exige mediana abaixo de 1 s.

### População offline

O catálogo está em `src/data/arena_populacao/` (um snapshot por gladiador e o
`indice.json`), é lido por `src/engine/arena_populacao.py` e é gerado por
`tools/arena_offline_geracao.py`. O resumo de cada tentativa da geração está em
`reports/pvp/arena_offline/tentativas.jsonl`.

- **Só extração real.** Todo gladiador é o snapshot canônico do save de uma
  run PvE real, jogada pelo BotPadrão com a variante perfil × política da Copa
  Arena 03, desde a criação canônica da jornada até a Extração. Nada é inventado:
  atributo, item, passiva e carta são os que a run deixou.
- **As origens.** Os 64 Guerreiros da Copa 03 com os mesmos bytes; Guerreiros
  que a Copa 03 recusou só pelo OP, re-executados pela mesma seed e conferidos
  contra o log dela; e Mages e Rogues de runs novas. A população não tem limite
  de OP.
- **Elegibilidade.** Classe do índice, marca de extração no andar do snapshot,
  vivo, Chave gasta, e o snapshot volta idêntico pela ida e volta canônica.
- **Unicidade.** Id, apelido, bytes, seed e build não se repetem.
- **Tamanho.** Entre 128 e 256 gladiadores. O catálogo atual tem **186**: 96
  Guerreiros (64 da Copa 03 e 32 fora da faixa dela), 45 Mages e 45 Rogues, cinco
  por grupo perfil × política em cada classe nova. Níveis de 2 a 29, força de
  referência de 4,3 a 42,4. A geração custou 151 runs de Mage e 265 de Rogue; as
  32 re-execuções de Guerreiro saíram iguais ao log da Copa 03.
- **Integridade em jogo.** Antes de cada partida, o arquivo tem de bater com o
  sha256 do índice e passar de novo pela elegibilidade. Um adversário que não
  passa não luta; um índice ilegível, de outra versão ou com entrada repetida
  bloqueia a Arena inteira, com aviso. Nunca há gladiador montado pela metade.
- **Apelidos fictícios**, sorteados com semente fixa. O nome do jogador de
  origem não entra.
- **Força de referência.** O OP medido na geração (`overall_power`). É só o
  ponto de partida para comparar gladiadores; não é rating nem regra.

### Duelo Livre: o histórico da sessão

`src/engine/arena_historico.py`. No Duelo Livre o jogador escolhe o adversário,
e por isso ele **não mexe em rating**: cada partida vira um `ResultadoDaPartida`
no histórico da sessão (em memória) e passa pela `SemClassificacao`.

- **Identidade estável.** O gladiador do jogador é o slot mais o hash do save
  sem `equipment` e `inventory`: gravar equipamento não muda quem ele é, e uma
  run nova no mesmo slot é outro gladiador. A Ranked usa a mesma identidade.

### Arena Ranqueada (Fase 6, experimental)

A opção 2 do hub da Arena. Código em `src/ranked/` (rating, Ladder, ranks,
matchmaking: puro, só importa `shared/`), `src/engine/ranked_partidas.py` (o
confronto NPC × NPC), `src/engine/ranked_mundo.py` (estado local e mundo) e
`src/engine/ranked_mode.py` (as telas). Os experimentos que sustentam cada
número estão em `tools/ranked_experimentos.py` e `reports/ranked/relatorio.md`.

**Contrato competitivo aprovado:**

- MMR dinâmico para todos os gladiadores, NPCs e do jogador.
- Confronto NPC × NPC muda o rating dos dois.
- O jogador tem um MMR separado para cada gladiador extraído.
- O OP serve só como estimativa inicial fraca, com incerteza alta.
- Só o resultado conta — vitória, derrota ou, desde a Fase 6.1, empate técnico
  por impasse: nada de bônus por duração, HP restante ou dano.
- Equipamento pode ser reorganizado sem mudar a identidade.
- Matchmaking automático: o jogador não escolhe o adversário.
- Rank por percentil da população competitiva; os cinco primeiros são os
  **Definitive Masters**.
- 100% offline. O motor PvP, o PvE congelado e a IA estratégica não mudam para
  favorecer classificação.

**O confronto NPC × NPC** é o duelo canônico, com a IA estratégica nos dois lados
e o gerador semeado: a mesma dupla com a mesma seed dá o mesmo resultado. O lado
(p1/p2) sai da seed. Na Fase 6, a partida que passava de 500 rodadas terminava
**sem resultado**; na 6.1 ela virou **empate técnico por impasse** (abaixo), e o
"sem resultado" da Fase 6 é lido como partida anulada.

**O rating.** Glicko-2, escolhido na comparação com TrueSkill sobre confrontos
reais (`reports/ranked/relatorio.md`): com 1.631 partidas de treino e 150 duplas
inéditas no holdout, os dois empataram na previsão (log-loss 0,549 × 0,547,
Brier 0,190 × 0,190, dentro do ruído); o Glicko-2 convergiu mais rápido no
começo — o que pesa nas 10 partidas de posicionamento —, foi um pouco mais
estável, e a incerteza dele é em pontos de rating. Uma partida por período,
com os valores de antes da partida para os dois lados (`src/ranked/sistema.py`).
Com um período por partida a volatilidade não tem efeito (τ 0,3, 0,6 e 1,0
dão o mesmo resultado); fica registrado. O NPC começa na priori
fraca do OP: metade do logit que o OP prevê, medido em confrontos reais, presa a
±3, com a incerteza inicial cheia (RD 350). O gladiador do jogador começa no
centro (1500, RD 350), sem priori. A exibição é o rating ± 2 RD.

**Posicionamento.** As 10 primeiras partidas de cada gladiador do jogador:

| partidas | etapa | o adversário |
|---|---|---|
| 1–4 | Descoberta | sorteado numa faixa larga (±1 desvio da população) em volta da estimativa |
| 5–7 | Nivelamento | entre os 4 mais próximos da estimativa, em ±0,5 desvio |
| 8–10 | Validação | entre os 2 mais próximos, em ±0,25 desvio |
| 11+ | Ranqueada | entre os 5 mais próximos, em ±0,35 desvio |

- O rating muda desde a primeira partida; o rank aparece depois da 10ª.
- **A sequência pesa pelo nível dos derrotados.** Cada vitória seguida contra
  quem não estava mais de meio desvio abaixo empurra o alvo 0,15 desvio para
  cima (no máximo 3); a derrota contra quem não estava mais de meio desvio
  acima, para baixo. Vitórias sobre gladiadores muito mais fracos não endurecem
  o próximo adversário — e o próprio Glicko-2 já sobe pouco com elas.
- Na Fase 6, quem enfrentou o gladiador nas últimas 3 partidas ficava de fora
  enquanto houvesse alternativa; na 6.1 isso virou um custo progressivo de
  repetição (abaixo).
- O adversário sorteado fica **reservado** até a partida: sair da tela e voltar
  não troca o oponente.

**A Ladder e os ranks.** A classificação é pelo rating, entre os competitivos
(todos os NPCs e os gladiadores do jogador já posicionados). O percentil vai de
0 (o último) a 100 (o primeiro). Os 12 ranks são faixas de percentil
(`src/ranked/ranks.py`); os limites são uma **proposta** sobre os 186
calibrados, e a regra definitiva depende de validação com população maior:

| rank | percentil mínimo | com 186 |
|---|---|---|
| Iron | 0 | 19 |
| Bronze | 10 | 22 |
| Silver | 22 | 24 |
| Gold | 35 | 24 |
| Platinum | 48 | 22 |
| Emerald | 60 | 19 |
| Sapphire | 70 | 17 |
| Diamond | 79 | 13 |
| Obsidian | 86 | 11 |
| Master | 92 | 7 |
| International Master | 96 | 5 |
| Distinguished Master | 98,5 | 3 |

O critério: no meio da classificação uma incerteza (1 RD) cobre ~19 posições, e
cada faixa do meio tem ~1,2–1,4 RD de largura — o rank diz algo apesar do ruído
entre builds parecidas. No topo os ratings se separam bem (~1 posição por RD), e
as faixas podem ser estreitas. Os cinco primeiros, por cima do rank, são os
Definitive Masters.

**O mundo.** Depois de cada partida do jogador, 2 confrontos NPC × NPC entram na
fila. O `AgendadorDoMundo` joga a fila numa thread, só enquanto o jogador está
nos menus da Ranqueada, e para antes do duelo dele; a Ladder só muda na thread
principal. Ao voltar ao jogo, a incerteza de todos cresce com os dias fora (até
30) e entram na fila até 24 confrontos (4 por hora fora) — nunca as horas
inteiras. Duplas e seeds saem da semente e do relógio do mundo.

**Persistência e identidade.** Tudo em `saves/ranked.json`, gravado de forma
atômica; na primeira vez, ele nasce da calibração publicada
(`src/data/arena_ranked/ladder_inicial.json`). Arquivo ilegível ou de outra
versão bloqueia a Ranqueada com aviso e não é sobrescrito. Gladiador novo no
catálogo ganha registro com a priori; nenhum registro existente é apagado ou
reiniciado. Uma run nova no slot é outra identidade e não herda nada. O save do
personagem nunca é tocado: ninguém morre e não há XP nem ouro.

### Arena Ranqueada: progressão competitiva (Fase 6.1, experimental)

Código em `src/ranked/progressao.py` (divisões e PR), `src/ranked/leaderboard.py`
(atualizações periódicas, candidatura e elite), `src/ranked/impasse.py` (empate
técnico), `src/ranked/matchmaking.py` (custo de repetição) e
`src/engine/ranked_mundo.py` (persistência v2 e relógio). Os experimentos
estão em `tools/ranked_progressao.py` e `reports/ranked/fase61/`.

**Três conceitos, e só um deles é a verdade.**

| | o que é | para que serve |
|---|---|---|
| **MMR** | o rating do Glicko-2, com incerteza (RD) | a estimativa competitiva: escolhe adversário e ordena a classificação |
| **Percentil** | a posição na população competitiva, de 0 a 100 | a base dos limites dos ranks (`ranks.LIMITES`) |
| **PR** | a barra de 0 a 100 dentro da divisão | a progressão que o jogador vê; anda atrás do MMR e nunca é um segundo MMR |

**As 45 divisões.** Iron, Bronze, Silver, Gold, Platinum, Emerald, Sapphire,
Diamond e Obsidian têm as divisões V, IV, III, II e I, nessa ordem crescente,
cada uma com 100 PR. Master, International Master e Distinguished Master são a
elite, sem divisões: valem a posição na leaderboard e o MMR. Os cinco membros da
elite mais bem colocados levam a distinção **Definitive Masters**, sem 13º rank.
Nenhuma divisão precisa ter um número mínimo de gladiadores.

**O alvo.** O percentil vira uma coordenada contínua na régua das divisões: cada
rank vale 500, e dentro do rank a coordenada é linear no percentil. Iron V 0 PR é
0, Obsidian I 100 PR é 4.500, e a elite continua a régua (Master de 4.500 a
5.000, International Master até 5.500, Distinguished Master até 6.000). A
coordenada VISÍVEL do gladiador é `100 × divisão + PR`.

**A variação de PR** de uma partida:

    ΔPR = K · (S − E) · m        m = e^{+βg} no ganho, e^{−βg} na perda, em [1/M, M]

- `S` é o resultado (1, ½ ou 0) e `E` a chance que o Glicko-2 dava antes dela:
  vencer o favorito rende mais, perder para o azarão custa mais. Com a chance
  certa, a média de `S − E` é zero: jogar muito sem melhorar não sobe ninguém.
- `g = (alvo − visível)/100`, em divisões, com o alvo de ANTES da partida. Quem
  está abaixo do que o MMR diz ganha mais e perde menos; quem está acima, o
  contrário. No alvo, `m = 1`. Um gladiador visualmente em Platinum com MMR de
  Diamond sobe até 3× mais rápido.
- Vitória rende pelo menos 1 e derrota custa pelo menos 1; uma partida move no
  máximo 60 PR e no máximo uma divisão.

**Promoção, rebaixamento e escudo.**

- 100 PR promove para a divisão seguinte, e o excedente vai junto.
- Abaixo de 0 rebaixa: o que faltou sai de 100, mas a divisão de baixo começa no
  máximo em 75 PR. Voltar exige mais de uma vitória, e a fronteira não vira
  pisca-pisca.
- Depois de uma promoção (ou do posicionamento), as 3 partidas seguintes não
  rebaixam: o PR para em 0. O escudo só vale enquanto o alvo não estiver mais de
  uma divisão abaixo — ele segura a oscilação, não esconde um gladiador fora do
  lugar.
- Iron V não desce de 0. Nenhuma proteção é permanente.

**O posicionamento.** As 10 primeiras partidas não têm PR, mas o MMR já muda
desde a primeira. Empate conta como partida disputada; partida anulada, não. Na
10ª, a coordenada visível nasce no alvo (divisão e PR), com escudo, e no máximo
Obsidian I com 0 PR: a barra de Obsidian I sempre se conquista jogando.

**NPCs e jogadores seguem as mesmas regras.** Toda partida (do jogador ou do
mundo) mexe no PR dos dois lados. A divisão inicial dos NPCs vem da fundação
(abaixo); um NPC novo no catálogo recebe a divisão do alvo.

**Candidato a Master.** Obsidian I com 100/100 PR vira **Candidato a Master**.
O PR para em 100 (não acumula), o MMR continua andando, e o jogador continua
jogando normalmente. A candidatura vale enquanto ele estiver em Obsidian I; cair
para Obsidian II a encerra (o evento fica registrado). A promoção NÃO é
automática: só acontece numa atualização oficial da leaderboard.

**A leaderboard publicada.** O MMR muda a cada partida; a leaderboard publicada
é um retrato tirado no começo de cada ciclo. O ciclo é de **1 hora**
(configurável; 24 horas também é testado), alinhado ao relógio (UTC). Nada roda
com o jogo fechado: ao abrir, depois de cada partida e a cada volta ao painel, o
jogo confere se o ciclo virou. Depois de muitos ciclos com o jogo fechado, sai
**um** retrato, o do ciclo atual, com o estado gravado; os ciclos pulados ficam
registrados. Ao reabrir, o retrato pendente sai antes da inatividade e da fila
do mundo. O jogador vê quando saiu o último retrato e quando sai o próximo.

**O que um retrato decide, em ordem:**

1. **Integridade.** Ladder com rating inválido, contagem negativa, PR fora da
   régua, candidato fora de Obsidian I ou competitivo sem divisão adia o retrato.
   O ciclo continua pendente e o aviso aparece na tela.
2. **A elite que já existe.** Membro com percentil no mínimo de Master (92) fica.
   Abaixo dele, mas a menos de 3 pontos, entra **em risco**. Em risco e ainda
   abaixo no retrato seguinte, ou mais de 3 pontos abaixo de uma vez, sai da
   elite para a divisão do alvo, como num posicionamento (no máximo Obsidian I
   com 0 PR) — e tem de reconquistar a barra para ser candidato de novo.
   Ninguém precisa jogar entre retratos para continuar na elite.
3. **As candidaturas.** O candidato é promovido se, no retrato, (a) continua
   candidato e posicionado, (b) o percentil alcança 92 e (c) a classificação é
   confiável: RD até 150. Senão, a candidatura é **mantida** e reavaliada no
   próximo retrato, com o motivo registrado e mostrado.
4. **O nível na elite** é o rank que o percentil dá no retrato (no mínimo
   Master): quem é promovido com percentil de Distinguished Master entra direto
   nele. Os cinco membros da elite mais bem colocados são os **Definitive
   Masters**.
5. **A variação de posições** é contada entre um retrato e o anterior.

**Partida empatada, anulada e interrompida.**

| desfecho | quando | Glicko-2 | posicionamento | PR | histórico |
|---|---|---|---|---|---|
| vitória/derrota | KO ou rendição | 1 / 0 | conta | sim | `vitoria`/`derrota`, motivo `ko`/`surrender` |
| **empate técnico** | o árbitro de impasse encerrou | ½ para cada | conta | pela expectativa | `empate`, motivo `impasse` ou `teto` |
| **anulada** | erro técnico, interrupção | nada | não conta | nada | `anulada`, motivo `erro técnico: …`/`interrompida`/`limite` (Fase 6) |

O **árbitro de impasse** (`ranked/impasse.py`) vale para NPC × NPC e para
jogador × NPC, e não toca no motor nem no PvE:

- **Impasse:** por **150 rodadas** seguidas, nenhum dos dois chegou a um HP ou a
  um MP mais baixo do que já tinha chegado na partida, com folga de 1% do máximo.
- **Teto:** **1.000 rodadas**, como rede de segurança.

Nos dois casos, o empate não favorece quem tem mais HP, OP, nível ou MMR. O
critério saiu de 242 duelos reais refeitos rodada a rodada: nas partidas que
terminaram em KO com desgaste contínuo, a maior espera por um mínimo novo foi de
50 rodadas. Uma build de cura ou controle que está ganhando empurra o outro para
mínimos novos e nunca é encerrada. A interrupção do mundo
orgânico (o agendador parado) não é registrada: a partida é jogada de novo. A do
jogador pelo teclado fica no histórico como anulada, e o adversário continua
reservado. O erro técnico consome a vaga (no mundo) ou libera a reserva (do
jogador), porque a mesma seed falharia de novo.

**Repetição de adversário.** O matchmaking escolhe entre os candidatos de menor
custo:

    custo = (distância ao alvo / janela da etapa)² + Σ 8 · ½^((idade − 1)/5)

A soma corre sobre os confrontos com aquele adversário nas últimas 20 partidas do
gladiador (idade 1 = a última). Pesam a frequência (cada confronto soma), a
recência (meia-vida de 5 partidas) e a diferença de MMR (o primeiro termo). O
adversário da partida anterior fica de fora enquanto houver qualquer outro.
Nunca bloqueia: com poucas alternativas, o custo escolhe entre repetir e
enfrentar alguém mais distante. Com 5.000 gladiadores a mesma regra vale sem
mudança: a janela tem dezenas de candidatos e a repetição quase some
(`reports/ranked/fase61/repeticao.json`).

**Persistência (versão 2).** `saves/ranked.json` ganha, por gladiador, empates,
divisão, PR, escudo, candidatura, elite, risco, título e os eventos de promoção
e rebaixamento. Ganha também a leaderboard publicada: período, último ciclo,
último retrato, posições do anterior e eventos da elite. A escrita continua
atômica, e uma gravação que falha não estraga o arquivo.

O arquivo da Fase 6 (versão 1) é migrado na leitura. Nada se perde: as vitórias,
derrotas, ratings, históricos e reservas ficam, e o "sem resultado" vira partida
anulada. O original fica copiado em `saves/ranked.v1.json`, que nunca é
sobrescrito. A progressão nasce da **fundação**: o retrato inicial põe na elite
todo competitivo com percentil de Master e os outros na divisão do alvo. O estado
inicial publicado (`ladder_inicial.json`, a calibração da Fase 6) passa pela
mesma fundação.

**Parâmetros propostos, ainda não aprovados:**

| parâmetro | valor | onde |
|---|---|---|
| K (PR por unidade de surpresa) | 40 | `progressao.K` |
| β (força do puxão para o alvo, por divisão) | 0,20 | `progressao.BETA` |
| multiplicador máximo | 3 | `progressao.MULTIPLICADOR_MAXIMO` |
| variação máxima por partida | 60 PR | `progressao.VARIACAO_MAXIMA` |
| escudo depois de promoção ou posicionamento | 3 partidas | `progressao.ESCUDO` |
| PR depois de rebaixar | no máximo 75 | `progressao.PR_APOS_REBAIXAMENTO` |
| ciclo da leaderboard | 1 hora (24 h testado) | `leaderboard.PERIODO` |
| faixa de risco da elite | 3 pontos de percentil | `leaderboard.FAIXA_DE_RISCO` |
| RD máximo para promover | 150 | `leaderboard.RD_MAXIMO_PARA_PROMOVER` |
| janela e teto do impasse | 150 rodadas, folga de 1%, teto de 1.000 | `impasse.JANELA`, `MARGEM`, `TETO` |
| custo de repetição | peso 8, meia-vida 5, memória 20 | `matchmaking.PESO_DA_REPETICAO`, `MEIA_VIDA`, `MEMORIA` |
| limites percentuais dos ranks | os da Fase 6 | `ranks.LIMITES` |

### Ainda não validado

- **Os parâmetros da tabela acima**, com uma população maior e com jogo humano.
  Os números da Fase 6.1 vêm de 5 jogadores artificiais sobre os 186
  (`reports/ranked/fase61/relatorio.md`).
- **Empates em sequência no topo.** Duplas de sustain (R31 × M33) empatam sempre;
  o custo de repetição afasta a dupla, mas com 186 o topo tem poucos rivais.
- **Partida longa demais para um humano.** Um impasse real termina perto da
  rodada 300–420. Um humano leva 30–40 minutos para chegar lá, se não render
  antes.
- **Piso da incerteza.** Com uma partida por período, o RD para em ~62 (±123 na
  tela).
- Os limites percentuais e o ritmo do mundo orgânico com 5.000 gladiadores.
- Rendição na Ranqueada conta como derrota comum.

## Multiplayer — compatibilidade de versão

> **Fora do ToJ 1.0.** O 1.0 é offline. O multiplayer das Fases 3 e 4 está
> preservado no repositório, com testes e gate, e fora do fluxo do jogo: o menu
> não o abre e a Arena não o importa. Os contratos abaixo valem para quando ele
> voltar.

Requisito **obrigatório e bloqueante**: o multiplayer só está pronto com estes
controles implementados, testados e no pipeline de publicação. Princípio:
**incompatibilidade implica bloqueio seguro, nunca execução silenciosa com regras
divergentes.**

O código está em `src/multiplayer/`, o gate em `tools/multiplayer_manifesto.py`, e
o CI em `.github/workflows/ci.yml` (job `compatibilidade`) e
`.github/workflows/publicacao.yml`.

### Isolamento e estabilidade

- **O multiplayer usa o motor canônico.** O servidor resolve a rodada com
  `Duel.play_round` e não tem fórmula, dano, efeito, iniciativa, mana ou recarga
  próprios.
  - Uma partida pelo servidor é o mesmo duelo do motor direto, rodada a rodada,
    com iniciativa e eventos.
  - A final publicada da Copa Arena 03, rejogada pela rede, chega aos mesmos HP,
    MP e resultado nas 37 rodadas.
- **A rede é uma camada à parte.** O servidor recebe `(conexão, texto)` e devolve
  os envios; não conhece socket nem relógio. `rede.ServidorDeRede` é o transporte
  WebSocket e `transporte.RedeLocal` o transporte em processo; os dois só movem
  texto e não tocam em regra.
- **Nada entra sozinho numa versão publicada.** Mudança no PvE, nos catálogos, nas
  classes ou nas mecânicas compartilhadas muda o hash; hash novo exige manifesto
  novo, e manifesto publicado não muda. Toda mudança passa pelo gate, pela suíte
  e por uma publicação explícita.

### O manifesto da versão

Cada distribuição tem um manifesto imutável em
`src/multiplayer/manifestos/<versão>.json`, com:

- a versão exata do jogo;
- a versão do protocolo multiplayer;
- o identificador das regras de combate;
- a versão do esquema de persistência do gladiador;
- o sha256 de cada arquivo que decide uma partida, o hash de cada grupo e o do
  conjunto.

Os quatro identificadores são declarados em `src/multiplayer/versao.py`, que fica
fora dos hashes. Os grupos medidos:

| grupo | o que cobre | quem responde por ele |
|---|---|---|
| `regras` | `src/mechanics/`, `src/shared/`, `src/entities/` | `REGRAS_DE_COMBATE` |
| `catalogos` | `src/data/`, `src/content/`, `src/engine/game_logic.py` | a versão do jogo |
| `persistencia` | `src/storage/`, `src/engine/arena_setup.py` (e o `__init__` do pacote), `src/multiplayer/gladiadores.py` | `ESQUEMA_DO_GLADIADOR` |
| `protocolo` | `src/multiplayer/protocolo.py` | `VERSAO_DO_PROTOCOLO` |
| `servidor` | o resto de `src/multiplayer/` | a versão do jogo |

- **O escopo é testado, não suposto.** Um processo limpo sobe o servidor, joga uma
  partida pela rede e confere que todo módulo de `src/` que carregou está no
  manifesto. O teste já pegou uma lacuna: `src/engine/__init__.py`.
- **Fora do escopo:** `ui/`, `sim/` (bot de medição não é regra) e o resto de
  `engine/`. O servidor não os carrega, e o mesmo teste falha se passar a
  carregar.
- **Fim de linha é normalizado.** O mesmo arquivo em checkout Windows ou Linux é a
  mesma versão.
- **Um identificador nomeia um só conteúdo.** Dois manifestos com o mesmo
  identificador de regras, protocolo ou esquema e conteúdo diferente nesse grupo
  são recusados. Regra nova exige identificador de regras novo; catálogo novo
  exige só versão nova.
- **Manifesto publicado é imutável.** Publicar é criar a tag `v<versão>`. Depois
  dela:
  - `gerar` recusa reescrever aquela versão;
  - `verificar` acusa manifesto publicado alterado ou apagado, lendo o texto
    na tag.

Para publicar uma mudança de gameplay:

1. Mude o código.
2. Em `versao.py`, declare uma versão nova e o identificador novo do grupo
   afetado.
3. Se o esquema mudou, registre a migração em `gladiadores.MIGRACOES`, com teste.
4. Rode `python tools/multiplayer_manifesto.py gerar`.
5. Abra o PR; o job `compatibilidade` precisa ficar verde.
6. Crie a tag `v<versão>`.

O workflow `publicacao.yml` só empacota a distribuição depois do gate e da suíte.

### Versão obrigatória entre cliente e servidor

- **O servidor é a autoridade.** O cliente manda a identidade da versão no
  `login` e no `ola`, e o login é recusado por versão ANTES de olhar a senha. Só
  identidade **idêntica** conecta: os quatro identificadores, os hashes de
  todos os grupos e o hash do conteúdo. Não há compatibilidade com versão
  próxima, anterior ou posterior.
- **A recusa é explícita.** Mensagem `recusado`, com `atualizacao_obrigatoria:
  true`, a `versao_exigida` e um motivo estável:
  - `versao_do_jogo`, `protocolo`, `regras`, `esquema_gladiador`;
  - `conteudo`: o mesmo número de versão com outro hash;
  - `identidade_invalida`;
  - `servidor_em_atualizacao`.
- **A conferência se repete** na entrada da fila e da sala, na criação da
  partida (para os dois lados) e na reconexão. Reconexão recusada deixa a partida exatamente como
  estava.
- **A instalação se confere antes de jogar.** `manifesto_da_instalacao` compara o
  código que está rodando com o manifesto da versão que ele declara.
  `ServidorAutoritativo.da_instalacao` não sobe com código divergente
  (`InstalacaoDivergenteError`).

### Servidor autoritativo

- **O cliente só manda autenticação, ação e comando de sessão.** A ação é `kind`
  e `skill_id`; os comandos são `login`, `ola`, `entrar_na_fila`, `sair_da_fila`,
  `criar_sala`, `entrar_na_sala`, `cancelar_sala` e `reconectar`.
  - Mensagem com campo a mais, de tipo desconhecido ou com ação fora do
    vocabulário é recusada inteira, e nada muda.
  - Não existe campo para HP, dano, atributo, equipamento, recarga, resultado,
    MMR, conta ou dono.
- **O gladiador fica no servidor** (`RegistroDeGladiadores`). O cliente só nomeia
  o id; nunca envia ficha nem snapshot.
- **O servidor decide tudo.** Ele valida a ação contra `Duel.legal_actions`,
  recusa a ilegal sem mudar nada e roda o motor. O desfecho vai para o livro
  `Resultados`.
- **Cada lado vê o mesmo que um controlador local.** A observação é a `DuelView`
  do motor, e só ela. A rodada pública mostra ações, ordem, passos, HP e MP, mas
  não a iniciativa.
- **A identidade declarada pelo cliente não prova integridade.** Quem adultera o
  código adultera a identidade junto. Ela serve para recusar, com uma mensagem
  útil, quem está honestamente na versão errada. A segurança competitiva vem de o
  servidor validar e executar tudo.

### Atualização sem interrupção indevida

- **A partida fica presa à versão em que nasceu.** Ela guarda a impressão da
  versão (sha256 da identidade).
- **Publicar uma versão nova drena a antiga** (`Frota.publicar`). A versão antiga:
  - recusa sessão, fila e partida novas e avisa quem estava na fila;
  - deixa as partidas em andamento terminarem nela;
  - aceita reconexão só para terminar a partida.
- **Desligar uma instância** (`Frota.desligar`) passa cada partida em andamento
  para outra instância da **mesma** versão, por replay conferido.
  - O replay usa a semente e as ações registradas.
  - HP e MP de cada rodada têm de bater, e cada gladiador tem de ser o mesmo
    registro.
  - O resultado é o mesmo da partida sem interrupção.
- **Sem instância compatível, a partida é anulada:**
  - não há vencedor nem derrota;
  - ela fica fora de `Resultados.classificaveis()`, de onde um MMR futuro vai ler;
  - uma partida nunca muda de versão.
- **Replay de outra versão é recusado**, e não rejogado com outras regras.

### Gladiadores e persistência

- **O multiplayer nunca altera o snapshot.** Tudo trabalha em cópias, e o sha256
  dos 64 snapshots da Copa 03 é conferido depois das partidas.
- **A reconstrução é a canônica** (`arena_setup.character_from_snapshot`, sobre
  `player_from_save_data`), com uma conferência antes e outra depois.
  - **Antes:** os campos exatos do esquema e os tipos, a extração, e todo item,
    carta e passiva no catálogo desta versão.
  - **Depois:** o personagem, serializado de volta por `to_save_data`, devolve
    classe, nome, nível, equipamento, mochila, gemas, passivas e deck idênticos.
  - O carregador local é tolerante de propósito: um item que saiu do catálogo
    some e o save abre. O multiplayer não aceita essa tolerância. Um deck de 5
    cartas, que o carregador cortaria em silêncio, é recusado.
- **O registro tem esquema:** `{"esquema": N, "snapshot": {...}}`.
  - O esquema 1 são exatamente os campos de `to_save_data`. Um campo novo no save
    reprova `test_o_esquema_e_exatamente_o_formato_de_save` até existir esquema
    novo e migração.
  - Esquema mais novo que o da versão é recusado. Esquema mais velho só entra por
    um passo registrado em `gladiadores.MIGRACOES`.
- **O gladiador é revalidado a cada preparação.** Um registro que deixou de ser
  compatível é recusado na fila ou na criação da partida, nunca depois.

### Rede, autenticação e propriedade

A Fase 4 pôs dois humanos em computadores diferentes na mesma partida. Nada aqui
toca o motor: a rede só transporta texto, e quem decide é o mesmo servidor.

- **Transporte WebSocket** (`src/multiplayer/rede.py`, `websockets` 16.1.1).
  - Mensagens JSON estruturadas, só texto; quadro binário fecha a conexão.
  - Quadro acima de 64 KiB derruba a conexão; texto acima de 2048 caracteres num
    campo é recusado.
  - Até 64 conexões. Conexão que não abre sessão em 30 segundos é fechada; dez
    mensagens malformadas também.
  - Cada conexão tem uma fila de saída própria: as mensagens chegam na ordem em
    que o servidor as produziu, e um cliente que não lê é desconectado em vez de
    travar os outros.
- **TLS obrigatório fora do loopback.** O servidor não escuta fora de
  `127.0.0.1` sem certificado, e o cliente não usa `ws://` para fora, a menos que
  alguém peça explicitamente o modo inseguro de desenvolvimento. O cliente confere
  o certificado e o nome do servidor; um certificado próprio entra pela
  autoridade (`--autoridade`).
- **Contas e sessão autenticada** (`src/multiplayer/contas.py`).
  - O login troca usuário e senha por um token. A conta da sessão é a que o
    servidor extrai do token, nunca um nome que o cliente declara.
  - A senha é guardada como scrypt com sal. Usuário inexistente e senha errada
    custam o mesmo e dão a mesma resposta. Cada conexão tem cinco tentativas.
  - O token é assinado com HMAC-SHA256 e expira em 8 horas. A assinatura é
    conferida antes do conteúdo; token alterado, de outra chave, vencido ou
    malformado é recusado.
  - Um token que vence no meio da sessão não deixa entrar em fila nem em sala.
    A partida em andamento segue: não existe política de derrota por isso.
  - A chave dos tokens fica num arquivo 0600 na pasta de dados do servidor.
  - Contas são criadas só pelo administrador; não há cadastro pela rede.
  - `Autenticador` é a interface; um provedor externo entra por ela.
- **Credenciais fora dos logs.**
  - Os quadros do WebSocket carregam senha e token, e o logger entregue à
    biblioteca descarta o conteúdo deles.
  - Os objetos que carregam token ou sessão não os mostram no `repr`.
  - Um teste roda uma partida inteira com log em DEBUG e confere que nenhum
    segredo aparece.
- **Propriedade dos gladiadores** (`src/multiplayer/registro.py`).
  - O registro guarda, em arquivo, o snapshot validado, o dono e a origem.
  - Só entra por importação do administrador, de origem confiável: hoje, o
    snapshot publicado de uma Copa, conferido pelo sha256 do índice. Snapshot
    enviado por cliente nunca é aceito; o protocolo não tem como enviá-lo.
  - Não há transferência, troca de dono nem o mesmo personagem registrado duas
    vezes.
  - O arquivo guarda a impressão de cada registro: alterado por fora, o
    gladiador é recusado.
- **A posse é conferida** na entrada da fila, na criação e na entrada da sala, e
  de novo na criação da partida. Gladiador alheio e inexistente dão a mesma
  resposta, para ninguém descobrir o acervo dos outros perguntando.
- **Uma conta, um lado.**
  - A conta tem uma sessão ativa por vez: uma segunda conexão da mesma conta é
    recusada.
  - Não se entra na própria sala, e a criação da partida recusa a mesma conta
    nos dois lados, mesmo que as outras travas falhem.
- **Partida direta por sala.** Um jogador cria a sala e passa o código; o outro
  entra com o próprio gladiador. A fila simples continua existindo e só junta os
  dois primeiros que esperam. Não há matchmaking público.
- **Sigilo antes do lock.** Quem age recebe só `acao_recebida`. O adversário não
  recebe nada até a rodada resolver; aí os dois recebem a mesma rodada pública.
- **Queda de conexão.**
  - A partida espera, intacta: estado, rodada e histórico não mudam.
  - O jogador volta por `reconectar`, com a sessão e um token válido da MESMA
    conta. O token de outra conta não assume a sessão.
  - Prazo de reconexão e derrota por desconexão dependem do relógio competitivo,
    que ainda não existe.
- **O cliente de terminal** (`tools/toj_multiplayer.py`) faz o fluxo inteiro:
  login, escolha do gladiador próprio, sala, as fichas públicas dos dois lados,
  a ação escolhida sem ver a do outro, a rodada resolvida e o resultado. O passo
  a passo está em [`MULTIPLAYER.md`](MULTIPLAYER.md).

| garantia da Fase 4 | onde |
|---|---|
| dois clientes reais, partida inteira, resultado do servidor e replay canônico | `test_multiplayer_rede.py::test_dois_clientes_reais_jogam_uma_partida_inteira` |
| sessões independentes | `…::test_partidas_e_sessoes_independentes` |
| handshake válido e inválido pela rede | `…::test_handshake_valido_e_invalido_pela_rede` |
| autenticação válida, expirada e adulterada | `test_multiplayer_contas.py`, `test_multiplayer_propriedade.py`, `test_multiplayer_rede.py::test_autenticacao_*` e `::test_token_expirado_pela_rede` |
| gladiador de outra conta | `test_multiplayer_propriedade.py::test_gladiador_de_outra_conta_e_recusado` e os de sala e criação |
| uma conta nos dois lados | `test_multiplayer_propriedade.py::test_a_mesma_conta_*` e `::test_a_criacao_da_partida_recusa_a_mesma_conta_dos_dois_lados` |
| ação ilegal sem mudar o estado | `test_multiplayer_rede.py::test_acao_ilegal_pela_rede_nao_muda_o_estado` |
| decisões simultâneas e sigilo antes do lock | `…::test_decisoes_simultaneas_sem_revelar_a_escolha_antes_do_lock` |
| queda de conexão sem corromper o duelo | `…::test_queda_de_conexao_nao_corrompe_o_duelo` |
| limites, TLS e log sem segredo | `…::test_mensagem_acima_*`, `::test_quadro_binario_*`, `::test_abuso_*`, `::test_conexao_sem_autenticacao_*`, `::test_limite_de_conexoes`, `::test_wss_*`, `::test_sem_tls_*`, `::test_senha_e_token_nunca_vao_para_o_log` |
| compatibilidade após atualização, pela rede | `…::test_drenagem_pela_rede_*` e `::test_servidor_de_outra_versao_recusa_o_cliente_antigo` |
| o terminal humano × humano | `…::test_o_cliente_de_terminal_joga_humano_contra_humano` |

### Testes bloqueantes

Todos rodam na suíte padrão e no job `compatibilidade`.

| garantia | onde |
|---|---|
| cliente e servidor idênticos: conexão autorizada | `test_multiplayer_conexao.py::test_cliente_e_servidor_identicos_conexao_autorizada` |
| cliente desatualizado: recusado | `…::test_cliente_desatualizado_conexao_recusada` |
| cliente com versão superior: recusado | `…::test_cliente_com_versao_superior_conexao_recusada` |
| mesma versão, hash incompatível: recusado | `…::test_mesmo_numero_de_versao_com_hash_incompativel_conexao_recusada` (os cinco grupos) |
| regra ou catálogo mudou sem manifesto: publicação bloqueada | `test_multiplayer_manifesto.py::test_mudanca_em_regra_ou_catalogo_sem_atualizar_o_manifesto_bloqueia` e os testes de identificador e imutabilidade |
| atualização durante partida: continuidade ou encerramento seguro | `test_multiplayer_atualizacao.py` |
| reconexão com versão incompatível: recusada | `test_multiplayer_conexao.py::test_reconexao_com_versao_incompativel_e_recusada` |
| snapshots e resultados canônicos intactos | `test_multiplayer_servidor.py` (final da Copa 03, motor direto, sha256 dos snapshots) e `test_multiplayer_gladiadores.py` |
| replay determinístico na versão contratada | `test_multiplayer_servidor.py::test_replay_*` (inclusive em outro processo) |
| falha de compatibilidade bloqueia build e deploy | `test_multiplayer_manifesto.py::test_o_ci_tem_o_gate_*` e `::test_a_publicacao_so_empacota_depois_do_gate` |

### Ainda não implementado

Estes contratos não dependem de nada acima e ainda não existem:

- **registrar uma extração nova no servidor.** A run PvE roda no computador do
  jogador, e o servidor não tem como confiar num snapshot que chega de lá. Hoje
  só entram snapshots de origem confiável (as Copas publicadas). Fechar isso
  exige PvE autoritativo ou extração assinada;
- o relógio de decisão (45 segundos), o prazo de reconexão (60 segundos) e a
  derrota por desconexão (`Duel.forfeit` existe; falta o relógio);
- o MMR, o matchmaking público, a prioridade humana na fila e bots na fila;
- persistência dos resultados entre reinícios do servidor (o livro `Resultados`
  vive na memória, porque ninguém o lê enquanto o MMR não existe);
- provedor de identidade externo, troca de senha e revogação de token antes da
  expiração (trocar a chave invalida todos);
- limite de tentativas de login por conta e por endereço. Hoje é por conexão, e
  quem abre conexões novas continua tentando; cada tentativa custa um scrypt, que
  roda no laço do servidor de rede. Basta para uma rede de teste, não para um
  servidor exposto.
