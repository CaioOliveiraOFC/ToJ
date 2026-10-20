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

### Run/Progression Balance

- **A nova jornada real** com Starter Kit, mapa, loot, economia, serviços, fuga e
  extração, jogada pelo BotPadrão.
- A referência atual é a auditoria do instrumento,
  [`baselines/progression/0ab837b9/`](baselines/progression/0ab837b9/README.md).
  A primeira baseline real, medida com o instrumento antigo, é
  [`baselines/progression/fb321d4e/`](baselines/progression/fb321d4e/README.md).
- **Estado: PENDENTE DE CALIBRAÇÃO.**

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

Só o contrato de fronteira. Nenhuma regra de Arena foi aprovada até aqui.

- **A Arena ainda não existe como sistema de gameplay.**
  - Não há modo nem entrada no menu.
  - Carregar um personagem extraído avisa que a Arena ainda não está aberta.
  - O nome aparece só em instrumentos de medição, e eles não são o modo de jogo:
    - `src/sim/arena.py` mede o poder geral;
    - `tools/arena_alvo.py` guarda o poder de referência;
    - a política de extração do bot compara a build contra esse alvo.
- **O PvP é uma fase posterior** à calibração da progressão PvE.
- **O que for descoberto no PvP não altera em silêncio a fundação PvE.** Uma
  mudança em classe, dano, skill ou progressão continua sujeita aos contratos
  acima e às duas réguas.
- Regras específicas de PvP podem existir quando a fase começar, e entram aqui
  quando forem aprovadas.
