# Etapa 1 — plano técnico das correções mecânicas do PvE

| | |
|---|---|
| **Estado** | **proposta, não implementada.** Nenhuma linha de gameplay muda antes da aprovação |
| **Base** | `phase/game-core` em `04f50ea`, B0 em [`baselines/progression/97965ae/`](../../baselines/progression/97965ae/README.md) |
| **Escopo** | KI-007 (Altar), KI-008 (buffs de HP/MP), KI-009 (Amuleto de Argila) e a divergência do Mercador entre jogo e simulação |
| **Fora do escopo** | a inteligência do bot (etapa própria), KI-010 (gemas na venda, etapa própria), KI-013 e KI-014 (pendências de design e conteúdo), a refatoração do RNG, a `phase/pvp-arena` e a Ranked |

---

## 0. Regras do ciclo

- **Pré-requisitos.** Antes da primeira correção, precisam estar integrados, com
  autorização:
  - o fechamento da Etapa 0 (PR #7);
  - a correção da sonda de status (KI-015). Sem ela, a matriz não enxerga o que
    as correções de status e de buff mudam.
- **Uma branch por correção** (`fix/ki009-…`, `fix/ki008-…`…), cada uma com PR
  próprio para a `phase/game-core`. A CI do PR precisa ficar verde, e nenhum
  merge acontece sem autorização.
- **A B0 é preservada.** Nenhuma correção reescreve `baselines/progression/97965ae/`.
  As medições novas vão para diretórios novos.
- **Nenhum threshold muda.** Se o `-m balance` reprovar depois de uma correção
  legítima, isso é um achado de balanceamento e volta para decisão. Pelo
  [`GAMEPLAY_CONTRACTS.md`](../../GAMEPLAY_CONTRACTS.md#combatclass-balance),
  só as três bandas globais podem ser remedidas, por decisão, com o registro em
  `tests/balance/thresholds.py`.
- **"Mudar o bot é mudar o instrumento"** ([contrato do BotPadrão](../../GAMEPLAY_CONTRACTS.md#botpadrão)).
  As correções de mecânica são medidas contra a B0 com o mesmo instrumento. A
  correção do Mercador muda o instrumento e abre uma baseline nova.

---

## 1. Ordem e dependências

| # | correção | por que nesta posição | depende de | decisão necessária |
|---|---|---|---|---|
| 1 | KI-009: `defense` do Amuleto | menor e isolada; testa o fluxo inteiro (PR, CI, medição) com risco mínimo | 0 | D3 |
| 2 | KI-008: buffs de HP/MP | mecânica de núcleo, afeta herói e monstro; maior impacto no balanceamento das quatro | 0 | D2 |
| 3 | KI-007: Bênção do Altar | só depois da decisão de design; a mecânica escolhida pode usar o canal de buff que a KI-008 define | 0, D1 e, conforme a opção, 2 | D1 |
| 4 | Mercador: paridade jogo × simulação | muda o instrumento e a régua do `-m balance`; por último, para não misturar a mudança do instrumento com as correções de mecânica | 0, 1–3 medidas | D4, D5 |

---

## 2. KI-009 — o efeito `defense` do Amuleto de Argila

**Causa raiz.**
- `Player.equipment_percent("df")` soma o `defense_bonus` da peça.
- O `elif` seguinte, que leria `effect_type in EQUIP_STAT_SOURCES["df"]`, nunca
  é alcançado para `df`.
- O `elif` entrou em `8fb2f0e` para que uma peça com as duas vias não rendesse
  "mais defesa do que declara", e deixou o efeito órfão.
- O único item afetado é o `amuleto_argila`: `defense_bonus` 1, `effect_type:
  defense` 3, Common, à venda desde o andar 1.
- A tela mostra "Defesa +1" e, abaixo, "Efeito: defense +3": o jogador lê +4.

**Decisão D3.** Quanto o amuleto deve valer, e qual é a regra para o futuro.

| opção | o que muda | prós | contras |
|---|---|---|---|
| **a. Uma via por atributo** (recomendada) | dado: o amuleto declara o total numa via só (ex.: `defense_bonus` 3 e sem `effect_type`, ou o contrário). Um teste de dados proíbe peça com `df` nas duas vias | sem mudança de código; a regra do `elif` vira contrato explícito; a tela passa a mostrar um número só | é preciso escolher o valor (1, 3 ou 4) |
| b. As duas vias somam | código: o `elif` vira `if` para `df` | a tela atual ("+1" e "+3") passa a ser verdade | desfaz a intenção de `8fb2f0e`; a regra fica implícita |
| c. O efeito prevalece | código: ler `effect_type` quando houver, e senão o `defense_bonus` | — | duas regras de leitura para o mesmo atributo |

**Testes.**
- `equipamento:defense` passa de `xfail` a aprovado. O `xfail` estrito obriga a
  tirar a marca.
- Um teste dirigido calcula o `equipment_percent("df")` exato do amuleto (com e
  sem `+N`).
- Na opção (a), um teste de integridade de dados em `tests/test_data_integrity.py`:
  nenhuma peça declara o mesmo atributo em `defense_bonus` e em `effect_type`.

**Impacto.** Desprezível no balanceamento: o amuleto termina equipado em 3 das
300 runs da B0. O valor está em fechar o caso e testar o fluxo.

---

## 3. KI-008 — buffs de vida e mana máxima

**Causa raiz.**
- Seis skills de herói declaram buff de `hp` ou `mp`:
  - `cura_menor`, `respiracao_de_forja` e `n_folego_de_marcha`;
  - `reserva_profunda`, `bolso_do_alfaiate` e `n_amuleto_rachado`.
- Duas de monstro declaram buff de `hp`: `mob_raizes_fundas` (`tank`) e
  `mob_folego_emprestado` (`support`).
- `apply_skill` grava `{"stat": "hp", "value": buff_value(...)}` em
  `active_buffs`. O valor já sai em pontos: `buff_value` converte o percentual
  sobre a base no momento do lançamento.
- Nenhum leitor do teto soma esse buff:
  - no herói, `Player._scaled` aplica só o `effect_core.resource_percent` dos
    efeitos de catálogo;
  - no monstro, `Monster.base_hp` e `Monster.base_mp` fazem o mesmo, e só
    `get_stat("hp")` soma o buff, mas o combate usa `base_hp`.

**Proposta técnica (recomendada).** Os tetos de HP e MP passam a somar
`sum_buffs(entidade, "hp"|"mp")`, no herói e no monstro, pela mesma função.
- O buff continua sendo buff: dura `duration` turnos de combate, vence em
  `process_turn_start_effects` e some no `recover()` do fim do andar, como todo
  buff.

**Alternativa não recomendada agora.** Migrar as oito skills para os efeitos de
catálogo `vitality` e `focused`, com intensidade por carta.
- A semântica já existe e é testada.
- Mas daria fonte a dois dos sete efeitos do PVE-02 e tornaria alcançáveis as
  leis `vitality_frailty` e `focused_clouded`. Isso contraria a decisão de
  manter o KI-014 como pendência sem ativar as leis agora.

**Decisão D2: o contrato do HP atual.** Hoje `get_hp()` devolve o `_hp` cru, sem
limitar ao teto. Por isso o contrato precisa dizer:

| momento | opções | recomendação |
|---|---|---|
| ao lançar | (i) só o teto sobe; (ii) teto e HP atual sobem o mesmo tanto ("toma emprestado do amanhã") | depende do texto da carta. "Toma emprestado o que precisa agora" sugere (ii) para `cura_menor`; as demais dizem só "+X% de vida máxima" |
| ao vencer | (i) o HP atual fica como está, mesmo acima do teto; (ii) o HP atual desce ao teto | (ii): sem isso, um buff vencido deixa vida acima do máximo, e o mesmo vale para MP |
| relançar | a chave do buff é o nome da carta, então relançar renova e não empilha | manter |

A mesma regra vale para herói e monstro, sem exceção por entidade.

**Testes.**
- Os três casos `xfail` passam a aprovados: `skill-heroi:buff:hp`,
  `skill-heroi:buff:mp` e `skill-monstro:buff:hp`.
- Testes dirigidos, com valores exatos pelo contrato de D2:
  - o teto sobe exatamente `buff_value` pontos no lançamento;
  - o HP atual segue o contrato;
  - o teto volta ao valor anterior no turno em que o buff vence;
  - o HP atual desce ao teto;
  - o MP segue as mesmas regras.
- No monstro, o mesmo teste com `mob_raizes_fundas`.
- Nenhuma mudança no `test_placebo`, que continua valendo.

**Impacto.**
- **No herói, pelo bot: pequeno.** As skills estão no deck final de 9 das 300
  runs, e o bot quase não lança buff (10 escolhas em 17.408 turnos disponíveis).
- **No jogador humano: real.** A carta passa a fazer o que diz.
- **No monstro: relevante.** Na B0, o `tank` lançou buff 2.004 vezes e o
  `support`, 186, contando todos os buffs desses papéis. O `tank` com +35% de
  vida nos turnos do buff alonga a luta. A banda
  `TestEncontros.test_duracao_dentro_da_banda[tank_solo]` é congelada e pode
  reprovar, e isso seria um achado de balanceamento, não um ajuste de limite.
- **Medição antes do PR.** TTK e dano recebido contra `tank_solo` e
  `support_solo`, em simulação de encontro pareada (seção 6).

---

## 4. KI-007 — a Bênção do Altar (precisa da decisão D1)

**Causa raiz.**
- `apply_altar_blessing` grava `{"value": 15, "duration": 5}` sem `stat`.
- `buff_stat` recorre a `LEGACY_BUFF_STATS`, que não conhece "Benção do Altar",
  então o buff não soma em lugar nenhum.
- O jogador paga 30% do HP máximo (`altar_hp_cost`), e a tela promete "+15 dano
  por 5 turnos".
- Jogo (`ui/random_event_flow.py`), BotPadrão e régua do `-m balance`
  (`sim/harness.py`) chamam a MESMA `apply_altar_blessing`. A correção chega aos
  três sem código duplicado.

**Restrição de contrato.** O
[contrato de dano](../../GAMEPLAY_CONTRACTS.md#dano) diz "Não existe balde
`FLAT`". Um "+15 de dano" literal não tem onde entrar sem mudar o contrato.

**Decisão D1: o que a bênção é.** Nenhuma opção é adotada sem decisão, e a
conversão automática de +15 em +15% está descartada.

| opção | mecânica | escala com o nível | respeita os contratos | observação |
|---|---|---|---|---|
| A | `damage_percent` +15 no `+MULT`, por buff com `stat: damage_percent` | sim | sim | é a leitura "+15%". Fica como opção, não como padrão |
| B | +15 pontos planos de Força/Magia (buff com `stat: st` ou `mg`, sem `buff_value`) | não: é ruído no fim do jogo, como o próprio `buff_value` documenta | sim | literal no "+15"; exige escolher o atributo por classe |
| C | +15% do atributo ofensivo da classe, por `buff_value` | sim | sim | o "dano" chega pelo atributo, como nas skills de buff |
| D | um balde `FLAT` novo no funil | não | **não**: exige mudar o contrato de dano | não recomendada |
| E | efeito de catálogo (`empowered` / `arcane_surge`) | sim | sim | dá fonte a efeitos do PVE-02 e ativa leis de par, o que contraria a decisão de manter o KI-014 parado |

**A duração também é decisão.** Hoje "5 turnos" significa 5 turnos de combate
do herói. O buff atravessa lutas dentro do andar e é limpo no `recover()` do fim
do andar. A alternativa é "o próximo combate inteiro". O texto da tela muda
junto e passa a ser montado a partir das constantes, para não divergir de novo.

**O que não muda nesta etapa.**
- O custo de 30% do HP.
- A política do bot. Hoje o avaliador do `?` (`_avaliar_evento`) só soma o
  risco do Altar, nunca o benefício. Depois da correção, o bot continua sem
  valorizar a bênção ao escolher ir ao evento.
- Valorizar a bênção é inteligência do bot e fica para a etapa do bot. Isso
  precisa ser lembrado ao ler a medição: o efeito da correção na régua do bot
  será um limite inferior.

**Testes.**
- `evento:altar` passa de `xfail` a aprovado.
- Um teste dirigido no funil confere o valor exato pela opção escolhida (por
  exemplo, o `+MULT` ou o atributo resolvido) durante a bênção, e a ausência
  dela depois da duração.
- Um teste de que o texto da tela sai das mesmas constantes que a mecânica.
- Um teste de que jogo, bot e régua passam pela mesma `apply_altar_blessing`.

**Impacto.** Na B0, o Altar foi aceito 69 vezes em 56 das 300 runs. A régua do
`-m balance` também aceita o Altar, então as bandas podem se mover, conforme a
opção escolhida.

---

## 5. Mercador: a mesma regra no jogo, no bot e na régua

**Causa raiz.** Três implementações para o mesmo evento:

| onde | o que faz hoje |
|---|---|
| jogo (`ui/random_event_flow.run_merchant_event`) | 1 a 3 ofertas de `get_merchant_offers`, ponderadas por raridade, a 90% do preço; compra opcional; nada de cura paga, poção avulsa ou reroll, a não ser que uma oferta seja consumível |
| BotPadrão (`tools/bot_padrao.py`) | `_comprar_com_orcamento("Evento Mercador")`: abre a Loja inteira, com cura paga, poções e reroll |
| régua do `-m balance` (`sim/harness.py`) | uma segunda `progression.visit_shop` completa |

O bot e a régua tratam o Mercador como uma segunda Loja, que o jogador não tem.

**Proposta técnica.**
1. **Uma função de conteúdo para a compra**, extraída de `run_merchant_event`:
   gasto com categoria no livro-caixa e item no inventário. A UI passa a chamá-la,
   e o comportamento do jogo fica idêntico.
2. **`progression.visit_merchant(hero, floor, rng, policy)`.** Gera as ofertas
   por `get_merchant_offers` e compra só entre elas, pela função do item 1. A
   régua e o bot a usam no lugar da Loja.
3. **Política de compra do bot (D4).** O avaliador de equipamento que o bot já
   usa na Loja, sobre as ofertas, com a mesma reserva da taxa de saída. Sem
   avaliador novo: a política "melhor" é da etapa do bot.
4. **RNG.**
   - O jogo sorteia as ofertas pelo `random` global, e o bot faz o mesmo, por
     paridade.
   - A régua passa o próprio `rng`, como já faz com a Loja.
   - O consumo de sorteio muda, então só as comparações agregadas valem
     (KI-012).

**Testes.**
- Teste de paridade: com o mesmo estado, a visita do bot e a da régua só compram
  itens que `get_merchant_offers` ofereceu, aos preços dele. Nenhuma cura paga,
  poção avulsa ou reroll.
- A UI e a simulação passam pela mesma função de compra.
- Categorias do livro-caixa iguais às do jogo.

**Impacto e medição.**
- **Instrumento.** É uma mudança de instrumento e de régua. Na B0, o Mercador
  foi visitado 66 vezes em 51 runs, e o bot comprava cura paga e poções nele.
  Tirar isso deve tornar as runs do bot mais difíceis, e isso é a medição sendo
  corrigida, não o jogo ficando mais difícil.
- **Baseline nova.** Logo depois do merge, uma baseline nova do instrumento, com
  o mesmo protocolo, vira o "antes" das etapas seguintes.
- **Régua do `-m balance`.** As bandas globais podem se mover, e remedi-las é
  decisão (D5). As demais são congeladas.

---

## 6. Como medir correções pequenas (KI-012)

Pela decisão de não refatorar o RNG agora, a evidência de cada correção vem em
camadas, da mais forte para a mais fraca:

1. **Testes dirigidos e exatos.** O valor esperado é calculado pelo contrato, e
   o `xfail` estrito vira aprovação. É o critério de aceite da correção.
2. **Cobertura funcional.**
   - `test_cobertura_de_efeitos` sem a pendência corrigida;
   - matriz da passada instrumentada, com a coluna "efeito" do sistema saindo
     de zero (Altar);
   - sonda de status corrigida.
3. **Simulação de mecanismo, pareada.** Milhares de batalhas ou encontros
   isolados com o mesmo `random.Random(seed)` por batalha, antes e depois.
   - Dentro de uma batalha o gerador é dedicado, então o pareamento é bom
     enquanto a mudança não reordena os sorteios.
   - Relata a diferença pareada com intervalo de confiança por bootstrap. Por
     exemplo: TTK contra `tank_solo` (KI-008), dano causado durante a bênção
     (KI-007).
4. **Run completa (protocolo da B0, 300 runs).** Métricas e testes declarados
   antes de rodar:
   - sobrevivência por andar (Kaplan–Meier e log-rank);
   - taxa de extração (Fisher);
   - distribuição do andar final (teste de permutação).

   O efeito mínimo detectável vai junto: ~1,8 andar no total e ~3 por classe,
   sem pareamento. Um resultado abaixo disso é "inconclusivo", nunca "sem
   efeito". Comparação run a run entre versões não é usada.
5. **`-m balance` na CI**, com os thresholds intactos, como gate de regressão.

---

## 7. Decisões pendentes

| | decisão | quem decide | bloqueia |
|---|---|---|---|
| D1 | o efeito da Bênção do Altar (A–E), a duração e o texto | design | KI-007 |
| D2 | o contrato do HP/MP atual ao lançar e ao vencer o buff de recurso | design | KI-008 |
| D3 | o valor total do Amuleto de Argila e a regra "uma via por atributo" | design | KI-009 |
| D4 | a política de compra do bot no Mercador, sobre as ofertas (proposta: o avaliador de equipamento existente) | técnica, com aprovação, porque muda o instrumento | Mercador |
| D5 | remedir ou não as bandas globais do `-m balance`, se a régua corrigida do Mercador ou do Altar as mover | decisão do usuário | merges que movam bandas |

---

## 8. Riscos

- **Bandas congeladas reprovando** depois do KI-008: duração do `tank_solo` ou
  `support_solo`. A resposta é medir e decidir, não mexer no limite.
- **Interação entre correções.** Se D1 escolher um buff de atributo e D2 mudar
  a leitura de buffs, a ordem 2 → 3 evita que a medição de uma contamine a da
  outra.
- **PvP.** As correções mudam `src/` da `phase/game-core`, e a
  `phase/pvp-arena` não é tocada. Uma integração futura entre as duas vai exigir
  remedir o benchmark da Arena e a calibração da Ranked, porque o combate dos
  gladiadores passa pelas mesmas funções.
- **A régua do bot subestima as correções** enquanto o bot não usar buffs nem
  valorizar o Altar. Isso só se resolve na etapa do bot, e precisa estar
  escrito em cada leitura de resultado.
