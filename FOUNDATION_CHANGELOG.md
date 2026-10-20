# Foundation Changelog — de `v0.2-prebalance` ao checkpoint atual

O que mudou na fundação do jogo desde a tag `v0.2-prebalance` (`9fddf5e7`), e
por quê. **Não é o `git log` reescrito**: só as mudanças estruturais que explicam
a fundação de hoje.

As outras fontes ficam onde estão:

- os números medidos em cada etapa estão na mensagem do commit dela;
- o design vigente está em [`GAME_DESIGN.md`](GAME_DESIGN.md);
- as decisões que não podem mudar por acidente estão em
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md).

> **Sobre os commits das Etapas 1 a 7.** São reconstruções. Os commits
> originais se perderam junto com um container, antes de qualquer push. Cada um
> foi refeito a partir do plano e da transcrição registrados e conferido contra
> os números gravados na época; os fingerprints estão na mensagem de cada commit.
> O `dde62c22` é um alinhamento dessa reconstrução, não uma etapa.

| Etapa | Commit | Assunto |
|---|---|---|
| 1 | `270873b8` | Atributos ofensivos reais do monstro |
| 2 | `f4b3ca13`, `f587891c` | Deck do monstro por nível |
| 3 | `88bf5ee0` | MP do monstro por papel, custo percentual |
| 4 | `e6c88fad` | Funil de dano: bônus condicional no `+MULT`, fim do `FLAT` |
| 5 | `826d1967` | Crítico orientado por fonte |
| 6 | `c6b5f0b2` | Limpeza comportamentalmente neutra |
| 7 | `213c2957` | Recalibração: todo `power` rederivado do orçamento |
| 8 | `bc815fcd` | Combat/Class Balance |
| — | `fb321d4e` | Starter Kit |
| — | `24430155` | Primeira baseline real de progressão |
| — | `9ef74639`…`0ab837b9` | Bloco do instrumento: BotPadrão corrigido e auditado |

---

## Etapa 1 — atributos ofensivos dos monstros

**O defeito.** O monstro tinha um número de ataque, e os atributos eram
reconstruídos a partir dele: `st = mg = int(attack × 1,5)`. Todo monstro era
igualmente físico e mágico, a skill lia o atributo inflado, e o arquétipo não
tinha vetor de pesos. A Agilidade do skirmisher não contribuía com nada para o
ataque básico.

**O que entrou.**

- **ST, MG e AG reais por arquétipo**, declarados em `src/data/monsters.json`.
- **`offensive_weights`**: o vetor de pesos do ataque do monstro.
  - Usa só os eixos ST, MG e AG, e a soma é 1.
  - O carregador (`src/content/factories/archetypes.py`) recusa um vetor que
    não cumpra isso.
- O básico do monstro passou a ser a mesma `weighted_power` do herói.
- **Fim da reconstrução de atributo a partir de ataque.**
  - `MONSTER_BUDGET_ATTACK` virou `MONSTER_BUDGET_OFFENSE`.
  - `MONSTER_ATTACK_TO_STAT_RATIO` saiu.

## Etapa 2 — deck do monstro

**O defeito.** O monstro nascia com o kit inteiro do arquétipo, de 3 a 7 cartas,
já no nível 1. O herói nasce com uma.

**O que entrou.**

- **Desbloqueio por nível.** As 54 cartas de monstro declaram `level_required`
  pela posição no kit: 1, 3, 6, 9, 12, 15 e 18. É a cadência do herói.
- **Assinatura permanente no deck do monstro.** A primeira carta do kit é a
  assinatura do papel e nunca sai do deck. É uma proteção do deck automático do
  monstro; o herói escolhe livremente qual das 4 skills troca, inclusive a
  inicial.
- **Teto de 4** (`MAX_ACTIVE_SKILLS`, o mesmo do herói).
- **Troca das outras cartas** (`f587891c`). Com o deck cheio, a carta nova entra
  no lugar de uma das outras três, sorteada pelo gerador da run. Não existe
  regra de troca por carta.
- **Persistência.** O save grava as cartas ativas de cada monstro do mapa, e o
  load restaura exatamente esse deck. Um save antigo, ou com uma carta que não
  existe mais, refaz o deck pela regra.

Onde vive: `deck_for_level` e `spawn_by_role`, em
`src/content/factories/archetypes.py`.

## Etapa 3 — MP do monstro

**O defeito.** O pool de mana era o mesmo para os nove papéis, e o custo das
cartas era um inteiro fixo. O pool crescia com o nível e o custo não, então a
mana deixava de restringir: um chefe conjurava 2 vezes com o pool cheio no
nível 1 e 17 vezes no nível 20.

**O que entrou.**

- **Mana por papel.** O pool é `geometric(60 × m_mp, nível)`, com um
  multiplicador por arquétipo (de 0,5 no trash a 1,5 no controller, support e
  glass cannon). É calibração inicial, não derivação.
- **Custo percentual.** O custo da carta é um percentual sobre a mesma curva de
  referência do herói (`SKILL_COST_REFERENCE_MP`).
- **Invariância com o crescimento.** Pool e custo crescem pela mesma razão, então
  quantas vezes cada papel conjura com o pool cheio fica constante do nível 1 ao
  20.
- O `mana_cost` absoluto continua na carta, como fallback e registro de
  proveniência.

## Etapa 4 — funil de dano

**O defeito.** O bônus condicional da carta morava dentro do BASE e compunha de
forma multiplicativa com todo `+MULT`. Uma carta de +90% sob um encantamento de
+10% rendia 2,09 em vez de 2,00. Além disso, o funil tinha um quarto balde, o
`FLAT`, que nenhuma fonte do jogo preenchia.

**O que entrou.**

- O **BASE** guarda só a identidade da ação:
  `Σ(atributo × peso) × (1 + arma%) × power`.
- Os **multiplicadores** ficam em três baldes: `+MULT` aditivo (`damage_percent`
  mais o bônus condicional satisfeito), `×MULT` com teto, e mitigação.
- **O bônus flat morto saiu** do funil.

## Etapa 5 — crítico

**O defeito.** Todo atacante tinha 10% de crítico sem que nada dissesse de onde
vinham. O único crítico que tinha fonte, o do Ataque Furtivo, era um `if` pelo
nome da skill dentro do motor.

**O que entrou.**

- **Crítico orientado por fonte.** `CRIT_CHANCE_DEFAULT = 0`, e há uma única
  leitura, `combat.crit_chance`. Ela soma a chance da carta e as fontes do
  atacante (`fx.combat_modifier`) e aplica o teto.
- **Nenhuma chance implícita.**
- **A carta e a passiva são fontes reais.**
  - A carta declara a chance no JSON (`crit_chance`): o Ataque Furtivo declara
    25.
  - A passiva inata do arquétipo controller declara 10, em `monsters.json`; é
    ele quem congela.
- A ficha do confronto mostra a chance de crítico do monstro.
- `CRIT_DAMAGE_BASE = 1,5` ficou marcado como pendente: está decidido que existe
  um multiplicador-base único, mas não que ele vale 1,5.

## Etapa 6 — cleanup

Comportamentalmente neutra: suíte, amostra do BotPadrão, `-m balance` e poder de
referência da Arena ficaram idênticos aos da Etapa 5. O que importa para entender
a fundação:

- o `Monster` deixou de ter defaults de classe: atributos e vetor ofensivo
  passaram a ser obrigatórios, e o único construtor é `spawn_by_role`;
- saíram o parâmetro morto `skill_name` do ataque físico e constantes sem
  consumidor, como as duplicatas do catálogo de efeitos e o veneno V1;
- o smoke de monstro de `tools/audit_interactions.py` passou a ler a carta do
  kit e a semear o spawn, então a seção dirigida ficou determinística.

## Etapa 7 — recalibração

**O defeito.** O `power` de uma carta é derivado: ele resolve uma intenção (o
`bud`, em % do ataque básico da referência) contra um personagem de referência.
Quando o monstro ganhou atributos reais, as cartas de lote continuaram com o
`power` resolvido contra a referência inflada e passaram a entregar entre 2/3 e
1,8 vez o que declaravam. A referência do herói era uma tabela congelada à mão e
tinha derivado. E 24 cartas nunca tinham passado por orçamento nenhum.

**O que entrou.**

- **Ledger.** O `tools/orcamento_de_cartas.py` é o livro-razão do `bud` de toda
  carta de dano, com a origem de cada um: lote, lote+preparar ou legado.
  `tests/test_orcamento_de_cartas.py` falha se uma carta sair do orçamento.
- **Orçamento como fonte do `power`.** Todo `power` de dano é rederivado do `bud`
  declarado.
- **`SKILL_REFERENCE_STATS`** é remedido por um regenerador
  (`medir_referencia_do_heroi`), e um teste confere a tabela contra a medição.
- **Alinhamento entre forge, validador e combate.** O `+MULT` do funil virou a
  função `combat.additive_multiplier`, e o validador e o forge passaram a usá-la.
- O crítico que a carta declara entra no orçamento pelo valor esperado
  (`combat.crit_multiplier`, `combat.expected_crit_factor`).
- Primeira suíte padrão inteiramente verde da reforma.

## Etapa 8 — Class Balance

Fechada na **régua controlada `expected loadout`**: `simulate_run` com o
equipamento esperado para o nível, aplicado sinteticamente
(`src/sim/loadouts.py`). A régua não é a largada real da dungeon.

| Atributo | Antes | Depois |
|---|---:|---:|
| Warrior ST base (`WARRIOR_BASE_ST`) | 54 | **49** |
| Rogue HP base (`ROGUE_BASE_HP`) | 370 | **314** |
| Mage | — | **sem alteração final** |

- A referência foi remedida, 23 cartas foram rederivadas para preservar o `bud`,
  e o livro-razão ficou com 0 cartas fora do orçamento. O balance veio do
  atributo da classe, não de mudar o orçamento das skills.
- O poder de referência da Arena (`PODER_ESPERADO`, em `tools/arena_alvo.py`)
  foi remedido.
- O `-m balance` ficou verde por inteiro pela primeira vez na reforma.
- As bandas vivem em `tests/balance/thresholds.py` e são verificadas por
  `tests/balance/test_balance_bands.py`. Os números da escolha (variáveis
  isoladas e validação de 3.000 runs por classe) estão na mensagem do
  `bc815fcd`.

Essa etapa fechou **`Combat/Class Balance`**. Ela **não** fechou
**`Run/Progression Balance`**.

## Starter Kit — `fb321d4e`

- Toda nova jornada recebe **exatamente 1 item Lv1**, equipado.
- **Pool única** para as três classes, separada do loot
  (`src/data/starter_kit.json`, `src/content/starter_kit.py`).
- **Sorteio em duas etapas, uniforme nas duas: categoria → item.**
- A peça leva **`origin="starter"`** no exemplar, nunca na definição do catálogo.
  O save preserva a origem.
- **`create_player_for_new_run`** é o caminho de nova jornada. A tela do jogador
  e o BotPadrão usam esse caminho; o bot passa o gerador da run, então a mesma
  seed dá o mesmo starter.
- **`create_player_from_data` continua neutro**: o herói puro, sem starter, para
  testes e benchmarks.
- **A régua sintética fica isolada.** As peças `starter_only` ficam fora do drop,
  da loja, do `expected loadout` e da referência de preço. Por isso a Etapa 8 não
  se move.
- Item novo: o Talismã do Viajante (Accessory, Common), exclusivo de starter.

## Baseline real — `24430155`

A primeira baseline oficial de progressão real, com 300 runs do BotPadrão sobre
o `fb321d4e`, está em
[`baselines/progression/fb321d4e/`](baselines/progression/fb321d4e/README.md).
O protocolo, os números e a classificação dos achados vivem lá.

Resultado: nenhum bug mecânico encontrado, e **`Run/Progression Balance —
pendente de calibração`**. Os problemas abertos estão em
[`KNOWN_ISSUES.md`](KNOWN_ISSUES.md).

## Bloco do instrumento — BotPadrão corrigido e auditado

Quatro correções do BotPadrão, uma por commit, e uma auditoria única de 300 runs
depois delas. **Corrigiu-se o piloto, não a pista:** nenhuma regra do jogo mudou.
Classes, monstros, atributos, dano, HP, Starter Kit, loot, mapa, preços,
economia, Essência, saída, extração e expected loadout ficaram como estavam.

A fronteira de informação do mapa também ficou intacta:
- `TargetView` continua sem a identidade do monstro;
- `CombatState` só existe depois da colisão;
- alvos visualmente iguais continuam empatando;
- os testes dessa fronteira, em `tests/test_bot_observation.py` e
  `tests/test_bot_decisao_mapa.py`, não foram alterados.
  - O único teste alterado nesses arquivos é o da poção que cura mais que o HP
    faltante, em `test_bot_decisao_mapa.py`. Ele passou a provar a regra nova
    do `7c08bdec`.

| Commit | Correção |
|---|---|
| `9ef74639` | KI-001: a Loja só promete a cura de HP que o orçamento real paga |
| `7c08bdec` | KI-004, parte do bot: poção por necessidade observada |
| `7b9734c3` | KI-003, parte do bot: a descida sem pagar deixa de ser estratégia |
| `0ab837b9` | KI-006: intenção explícita para as 23 famílias de passiva (D3 encerrada) |

**`9ef74639` — a Loja deixa de prometer cura impagável.**
- O defeito: a policy prometia "HP a recuperar" sempre que `ouro > taxa_de_saida`,
  mas o driver entra na Loja com o orçamento real de `_orcamento()`, que guarda a
  reserva da saída. No Warrior seed 24 da `fb321d4e`, a visita não comprou nada e
  a Loja se perdeu.
- `ServiceView.cura_hp` é um fato da Loja: a fração do HP que o primeiro passo de
  recuperação de HP devolve com aquele orçamento, ou zero.
  - Vem de `progression.primeiro_reparo_de_hp`, uma leitura pura da primeira
    volta de `_repair` sobre `content.economy.recovery_offers`.
  - Não compra nada, não muda `_repair` e não replica preço.
- Com combate observado e `hp_frac − dano_por_luta < HP_DE_APOSTA`, uma cura que
  existe de verdade atende `RECUPERAR`. Abaixo do ponto de aposta continua
  `SOBREVIVER`. Sem combate observado, nenhum risco é inventado. Nenhuma
  constante nova.

**`7c08bdec` — recuperação com intenção.**
- A poção no mapa vale só com necessidade: `SOBREVIVER`, ou `RECUPERAR` pela mesma
  regra do commit anterior. Sem necessidade observada, ela fica na mochila. E
  nunca vale quando mais da metade da cura transbordaria.
- `ServiceView.pocao_pagavel` é outro fato da Loja: ela vende poção de cura neste
  andar por um preço (`price_of`) que cabe no orçamento depois do reparo.
  - Os desbloqueios são lidos dos campos do próprio item, sem montar vitrine,
    porque a Loja real consome RNG ao montar o estoque.
  - Um teste confere a paridade contra `Shop.get_available_items`.
- Preço, estoque, disponibilidade, `visit_shop` e `TARGET_HEALING_POTIONS` não
  mudaram.

**`7b9734c3` — a espiral de saídas não pagas deixa de ser estratégia.**
- O estado tem só fronteiras naturais: nível abaixo do andar, saída que não seria
  paga, luta no mapa e fôlego observado (`(HP + cura na mão) / dano_por_luta`)
  para pelo menos uma luta média.
- Nesse estado e abaixo do ponto de aposta:
  - a saída fica em `ENCERRAR`, com o custo real de `perda_de_essencia`, e
    continua sempre disponível;
  - a luta vale o fôlego que sobra por luta.
- Fora dele vale a regra de antes, e a sobrevivência continua acima.
- Nenhum contador de saídas e nenhuma constante nova. O Mage seed 59 é testado
  como caso histórico, sem seed no código.

**`0ab837b9` — as 23 famílias de passiva têm intenção.**
- `survival`, `offense` e `economy` ordenam as 23 famílias. As 13 originais
  mantêm a ordem relativa que tinham.
- `PASSIVE_SEM_PREFERENCIA` e o estado `NEUTRA` saíram. Sem família da intenção
  na oferta, o desempate é só raridade: nenhum `effect_value` se compara entre
  famílias.
- Essas políticas também são as do `simulate_run`, a régua do Combat/Class
  Balance. Por isso o `-m balance` rodou como portão: 118 passed.
- D3 foi encerrada em [`GAME_DESIGN.md`](GAME_DESIGN.md).

### KI-001 — como foi fechado

**O mapa não aprende a força do monstro escondido.** O que foi corrigido foi a
política de risco antes do engajamento:

> usando apenas histórico observado e recursos realmente disponíveis, o
> BotPadrão deixa de ignorar uma recuperação viável antes de entrar na próxima
> luta.

A incerteza sobre qual monstro existe num `&` permanece **por design**.

### A auditoria

Mesmo protocolo da `fb321d4e`, sobre o código do `0ab837b9`. O "antes" é o
próprio `fb321d4e`, remedido com o mesmo coletor; nos campos que a baseline já
tinha, ele reproduz as 300 runs registro a registro. Protocolo, números e
leitura estão em
[`baselines/progression/0ab837b9/`](baselines/progression/0ab837b9/README.md).

Resultado:
- KI-001 e KI-006 fechados;
- as partes do bot de KI-003 e KI-004 corrigidas;
- KI-002, KI-003, KI-004 e KI-005 abertos como problemas da dungeon e da
  economia ([`KNOWN_ISSUES.md`](KNOWN_ISSUES.md)).

**`Run/Progression Balance — pendente de calibração`.**
