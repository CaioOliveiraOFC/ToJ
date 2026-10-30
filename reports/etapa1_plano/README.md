# Etapa 1 — plano técnico das correções mecânicas do PvE

| | |
|---|---|
| **Estado** | **proposta, não implementada.** Nenhuma linha de gameplay muda antes da aprovação. Revisão 2: contrato de HP/MP temporário (seção 3) e valor do Amuleto (seção 2) |
| **Base** | `phase/game-core` em `04f50ea`, B0 em [`baselines/progression/97965ae/`](../../baselines/progression/97965ae/README.md) |
| **Escopo** | KI-007 (Altar), KI-008 (buffs de HP/MP), KI-009 (Amuleto de Argila) e a divergência do Mercador entre jogo e simulação |
| **Fora do escopo** | a inteligência do bot (etapa própria), KI-010 (gemas na venda, etapa própria), KI-013 e KI-014 (pendências de design e conteúdo), a refatoração do RNG, a `phase/pvp-arena` e a Ranked |

---

## 0. Regras do ciclo

- **Pré-requisitos.** Antes da primeira correção, precisam estar integrados, com
  autorização:
  - o fechamento da Etapa 0 (PR #7);
  - a correção da sonda de status (KI-015, PR #8, validada em 300 runs). Sem ela, a matriz não enxerga o que
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
| 2 | KI-008: buffs de HP/MP | mecânica de núcleo, afeta herói e monstro; maior impacto no balanceamento das quatro; o contrato de pontos temporários (seção 3) é fechado antes | 0 | D2, D2b |
| 3 | KI-007: Bênção do Altar | só depois da decisão de design; a mecânica escolhida pode usar o canal de buff que a KI-008 define | 0, D1 e, conforme a opção, 2 | D1 |
| 4 | Mercador: paridade jogo × simulação | muda o instrumento e a régua do `-m balance`; por último, para não misturar a mudança do instrumento com as correções de mecânica | 0, 1–3 medidas | D4, D5 |

---

## 2. KI-009 — o efeito `defense` do Amuleto de Argila

**Causa raiz.**
- `Player.equipment_percent("df")` soma o `defense_bonus` da peça.
- O `elif` seguinte, que leria `effect_type in EQUIP_STAT_SOURCES["df"]`, nunca
  é alcançado para `df`.
- O `elif` entrou em `8fb2f0e` com a justificativa de que a peça "rendia mais
  defesa do que declara".
- O único item afetado é o `amuleto_argila`: Common, preço 20, à venda desde o
  andar 1, com `defense_bonus` 1 e `effect_type: defense` 3.

**O que a tela mostra.** "Defesa +1" e, abaixo, "Efeito: defense +3". O motor
entrega só o `defense_bonus`: +1% de DF. Os dois números são percentuais sobre a
DF; a tela omite o "%", o que é uma questão de interface fora deste escopo.

**O valor pretendido: +4% de DF (1 da base + 3 da especialidade).** A
justificativa vem do próprio catálogo. Todo amuleto Common segue o mesmo molde:
uma base de defesa do slot e um efeito de especialidade.

| amuleto Common | preço | base (`defense_bonus`) | especialidade (`effect_type`) | o que o motor entrega hoje |
|---|---:|---:|---|---|
| Argila | 20 | 1 | defense 3 | **+1% DF** (a especialidade some) |
| Cordão | 25 | 1 | agility 3 | +1% DF e +3% AG |
| Ferro | 25 | 1 | strength 3 | +1% DF e +3% ST |
| Concha | 25 | 1 | max_mp 5 | +1% DF e +5% MP |
| Madeira | 30 | 1 | max_hp 10 | +1% DF e +10% HP |
| Pedra | 30 | 1 | max_mp 10 | +1% DF e +10% MP |

- **O Argila segue o molde.** A especialidade dele é defesa, como a do Ferro é
  força.
- **O `elif` engoliu a especialidade.** Ela coincide com o atributo da base, e
  isso deixou o Argila como o único Common dominado por todos os pares: só a
  base, sem especialidade.
- **A justificativa de `8fb2f0e` não se sustenta.** A peça declara 1 + 3.
  Somar as duas vias entrega exatamente o que ela declara, e não mais.
- **Com +4%, a tela atual passa a ser verdadeira** ("+1" e "+3"), sem mudar
  texto nem dado.
- **O Argila vira o amuleto de defesa pura**, o mais barato do andar 1. Isso é
  coerente com o papel de especialista, e o efeito no balanceamento é
  desprezível: ele termina equipado em 3 das 300 runs da B0.

**Opções, para a decisão D3:**

| opção | valor | como | leitura |
|---|---:|---|---|
| **b. As duas vias somam** (recomendada) | 4 | código: em `equipment_percent`, o `elif` volta a `if` para `df`; o dado não muda | restaura o molde; só o Argila é afetado (é o único item com `defense` nas duas vias) |
| a. Uma via só, no dado | 4 | dado: `defense_bonus` 4 e sem `effect_type` | o mesmo número, mas quebra o molde "base + especialidade" e muda a tela |
| c. Manter +1 | 1 | nenhuma | o item continua dominado e a tela continua mentindo; exigiria mudar o texto |
| d. Só a especialidade | 3 | código: o efeito prevalece | perde a base do slot; duas regras de leitura para o mesmo atributo |

**Contrato proposto.** Uma peça entrega a soma das vias que declara, inclusive
quando a base e a especialidade são o mesmo atributo. O `+N` aprimora as duas,
como já aprimora `defense_bonus` e `effect_value` hoje.

**Testes.**
- `equipamento:defense` passa de `xfail` a aprovado.
- Um teste dirigido: `equipment_percent("df")` do Argila é 4, e com `+N` é o
  valor aprimorado de cada via, somado.
- Um teste de dados: todo amuleto Common declara base 1 mais uma especialidade.
  Se o molde mudar, a mudança precisa ser deliberada.

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
  - no monstro, `Monster.base_hp` faz o mesmo, e só `get_stat("hp")` soma o
    buff, mas o combate usa `base_hp`.

### A regra descartada

A primeira versão deste plano propunha subir o teto e o HP atual juntos e, ao
vencer, só limitar o HP ao teto. **Isso transforma bônus temporário em cura
permanente:** 20/100 → buff de +40 → 60/140 → vence → **60/100**. Os 40 pontos
concedidos viram HP real. A regra está descartada.

### Modelos considerados

| modelo | o que o buff faz | conserva? | serve em combate? |
|---|---|---|---|
| M1. Teto temporário | só o teto sobe; o HP atual não muda; ao vencer, o HP atual desce ao teto real | sim: o buff nunca concede HP | pouco: sem cura durante o buff, o teto maior não protege de nada |
| **M2. Pontos temporários** (recomendado) | concede um saldo de pontos temporários, separado do HP real, que o dano consome primeiro e que some ao vencer | sim, por construção | sim: absorve dano, que é o que "aguentar mais" significa nas cartas |
| ~~M3. Teto e atual sobem, limite ao vencer~~ | a regra descartada acima | **não** | — |

O M2 também lê melhor os textos das cartas: "toma emprestado do amanhã o que
precisa agora", "uma segunda gaveta de mana", "uma última carga", "tira de si e
dá a quem ainda vai lutar".

### Contrato proposto (M2), caso a caso

Notação: `HP` é o HP real, `teto` é o máximo real (`base_hp`) e `T` é o saldo
temporário do buff.

1. **Concessão.** Ao lançar, `T = ⌊% da carta × teto no momento do lançamento⌋`.
   `HP` e `teto` não mudam.
2. **Dano.** Golpe, DoT (`tick_effects`) e qualquer outra perda por dano
   consomem `T` primeiro, depois `HP`. A morte só acontece com `HP ≤ 0`. O
   `death_ignore` continua olhando o `HP` real.
3. **Sacrifício e custo não são dano.** O Altar cobra `HP` real e nunca `T`.
   Sem isso, um buff lançado em combate pagaria o Altar de graça no mapa,
   porque o buff atravessa as lutas do andar. Hoje o Altar cobra por
   `take_damage`, o mesmo caminho do dano, então a correção separa "pagar com
   vida" de "levar dano".
4. **Cura.** Skill de cura, poção, Fonte, roubo de vida, regeneração e
   recuperação paga restauram só `HP`, até o `teto`. Nada recarrega `T`.
5. **Razões de vida usam o real.** `HP / teto` é o que decide:
   - execução e `target_wounded`;
   - `caster_wounded`;
   - a IA do monstro (`_hp_ratio`);
   - a cura percentual.

   `T` não conta. Um herói com 10/100 (+40) continua ferido.
6. **Vencimento.** O `T` restante some, e `HP` e `teto` não mudam. O buff vence
   no início do turno de combate, como todo buff. No fim do andar, `recover()`
   limpa `active_buffs`, e `T` vai junto.
7. **Relançar a mesma carta.** Não empilha: `T = max(T restante, novo T)`, e a
   duração renova. A chave do buff é o nome da carta, como hoje.
8. **Cartas diferentes.** Cada uma tem o próprio `T`, e os saldos somam. O dano
   consome primeiro o saldo que vence antes, para nenhum ponto vencer intacto
   enquanto outro é gasto.
9. **Save e load.** `T` mora no buff, e `active_buffs` já vai para o save. O
   load limita `HP` ao `teto` real, como já faz.
10. **MP, pela mesma regra.** `T_mp` é concedido do mesmo jeito.
    - Todo GASTO de MP consome `T_mp` primeiro: custo de skill, Égide de Mana e
      dreno de `mana_burn`.
    - Toda RESTAURAÇÃO vai só para o MP real, até o teto: regeneração por turno,
      poção e recuperação paga.
    - O custo percentual das skills é calculado sobre o teto real.
    - Hoje a regeneração passa por `reduce_mp(-regen)`, com sinal negativo, e a
      correção precisa separar "gastar" de "restaurar".
11. **Monstro.** A mesma regra, sem exceção por entidade: `mob_raizes_fundas`
    e `mob_folego_emprestado`.
12. **Tela e texto (decisão D2b).**
    - A barra passa a mostrar `HP/teto (+T)`.
    - O texto das cartas troca "+X% de vida máxima" por "+X% de vida temporária
      por N turnos", e o mesmo para mana.
    - O texto sai das mesmas constantes que a mecânica.

**O invariante de conservação.** Em qualquer sequência de eventos, o `HP` real
ao fim do buff é exatamente o que seria sem o buff, mais a vida que o `T`
poupou do dano. O buff nunca soma vida real; ele só absorve.

**O caso do exemplo, sob o M2.**

| passo | sem buff | com buff de +40 |
|---|---|---|
| início | 20/100 | 20/100 (+40) |
| leva 30 de dano | morre | 20/100 (+10) |
| cura de 50 | — | 70/100 (+10) |
| vence o buff | — | 70/100 |

Os 70 de vida vieram da cura, e não do buff. O buff só impediu a morte.

### Alternativa não recomendada agora

Migrar as oito skills para os efeitos de catálogo `vitality` e `focused`, com
intensidade por carta. Isso daria fonte a dois dos sete efeitos do PVE-02 e
tornaria alcançáveis as leis `vitality_frailty` e `focused_clouded`, o que
contraria a decisão de manter o KI-014 parado. Além disso, a semântica de
recurso do catálogo sobe o teto (como o M1) e hoje não limita o HP no
vencimento: `get_hp()` devolve o `_hp` cru. Esse ponto também precisa ser
revisto se um dia esses efeitos ganharem fonte.

### Testes (quando a regra for aprovada)

- Os três `xfail` passam a aprovados: `skill-heroi:buff:hp`,
  `skill-heroi:buff:mp` e `skill-monstro:buff:hp`.
- Um teste dirigido por regra, de 1 a 11, com valores exatos. Entre eles:
  - o dano consome `T` antes do `HP`;
  - o Altar não toca o `T`;
  - a cura não recarrega o `T`;
  - a razão de vida ignora o `T`;
  - o vencimento não muda o `HP`;
  - relançar faz `max`, não soma;
  - a regeneração de MP não vira `T_mp`.
- **Teste de propriedade do invariante.** Sequências aleatórias semeadas de
  dano, cura, custo, relançamento e vencimento, aplicadas com e sem o buff. O
  `HP` real final nunca é maior que o sem buff mais o dano absorvido. É exato
  por sequência, não agregado.
- O `test_placebo` continua valendo, sem mudança.

### Impacto

- **No herói, pelo bot: pequeno.** As skills estão no deck final de 9 das 300
  runs, e o bot quase não lança buff (10 escolhas em 17.408 turnos disponíveis).
- **No jogador humano: real.** A carta passa a absorver dano.
- **No monstro: relevante.** O `tank` lançou buff 2.004 vezes e o `support`
  186 na B0, contando todos os buffs desses papéis. Como pontos temporários, o
  efeito é absorção, e não cura.
  - A banda `TestEncontros.test_duracao_dentro_da_banda[tank_solo]` é
    congelada e pode reprovar. Isso seria um achado de balanceamento, não um
    ajuste de limite.
  - Antes do PR, mede-se TTK e dano recebido contra `tank_solo` e
    `support_solo`, em simulação pareada (seção 6).

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
- O custo de 30% do HP. Pela regra 3 do contrato de pontos temporários (seção 3),
  esse custo é sacrifício e é pago com HP real, nunca com pontos temporários.
  Se o KI-008 entrar antes, o Altar já chega com o caminho "pagar com vida"
  separado de "levar dano".
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
| D2 | o modelo do buff de recurso (recomendado: M2, pontos temporários) e as regras 1–11 da seção 3 | design | KI-008 |
| D2b | o texto das cartas e da barra ("+X% de vida temporária", `HP/teto (+T)`) | design | KI-008 |
| D3 | o valor do Amuleto de Argila (recomendado: +4% de DF, as duas vias somam) e o contrato "a peça entrega a soma das vias que declara" | design | KI-009 |
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
