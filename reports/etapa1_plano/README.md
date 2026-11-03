# Etapa 1 — plano técnico das correções mecânicas do PvE

| | |
|---|---|
| **Estado** | **proposta, não implementada.** Nenhuma linha de gameplay muda antes da aprovação. Revisão 3: D3 aprovado; D2 comparado (seção 3); hipótese do D1 medida (seção 4); fidelidade da régua do `-m balance` (seção 5) |
| **Base** | `phase/game-core` em `04f50ea`, B0 em [`baselines/progression/97965ae/`](../../baselines/progression/97965ae/README.md) |
| **Escopo** | KI-007 (Altar), KI-008 (buffs de HP/MP), KI-009 (Amuleto de Argila) e a divergência do Mercador entre jogo e simulação |
| **Fora do escopo** | a inteligência do bot (etapa própria), KI-010 (gemas na venda, etapa própria), KI-013 e KI-014 (pendências de design e conteúdo), a refatoração do RNG, a `phase/pvp-arena` e a Ranked |

---

## 0. Regras do ciclo

- **Pré-requisitos.** Antes da primeira correção, precisam estar integrados, com
  autorização:
  - o fechamento da Etapa 0 (PR #7);
  - a correção da sonda de status (KI-015, PR #8, validada em 300 runs). Sem
    ela, a matriz não enxerga o que as correções de status e de buff mudam.
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
  O KI-009 é medido contra a B0, com o mesmo instrumento. A fidelidade das
  réguas (passo 2) muda os instrumentos e abre baselines novas; o KI-008 e o
  KI-007 são medidos contra elas.

---

## 1. Ordem e dependências

A revisão 3 põe a fidelidade das réguas antes das correções que dependem
delas. Corrigir um mecanismo enquanto a simulação joga uma jornada diferente
da do jogador mede a correção na jornada errada.

| # | passo | por que nesta posição | depende de | decisão necessária |
|---|---|---|---|---|
| 1 | KI-009: `defense` do Amuleto | isolado e pequeno; independe das réguas | 0 | D3 (aprovado) |
| 2 | Fidelidade das réguas: eventos e serviços no meio do andar no `-m balance` (seção 5) e Mercador por ofertas na régua e no BotPadrão (seção 6) | muda os dois instrumentos; abre baselines novas, contra as quais as correções seguintes são medidas | 0 | D4, D5, D6 |
| 3 | KI-008: buffs de HP/MP | mecânica de núcleo; o modelo depende de D2 | 0, 2 | D2 |
| 4 | KI-007: Bênção do Altar | o efeito depende de D1; só é medível no `-m balance` depois do passo 2 | 0, 2, D1 | D1 |

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

**Decisão D3: aprovada** (+4% de DF, as duas vias somam). As opções consideradas:

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

## 3. KI-008 — buffs de vida e mana máxima (decisão D2 em aberto)

**Causa raiz.**
- Seis skills de herói declaram buff de `hp` ou `mp`:
  - `cura_menor`, `respiracao_de_forja` e `n_folego_de_marcha`;
  - `reserva_profunda`, `bolso_do_alfaiate` e `n_amuleto_rachado`.
- Duas de monstro declaram buff de `hp`: `mob_raizes_fundas` (`tank`) e
  `mob_folego_emprestado` (`support`).
- O buff vai para `active_buffs` com o valor já em pontos (`buff_value`), e
  nenhum leitor do teto o soma:
  - no herói, `Player._scaled` lê só o `resource_percent` dos efeitos de
    catálogo;
  - no monstro, `Monster.base_hp` faz o mesmo.

**O que está em decisão.** Duas famílias de correção:
- **M1 — preservar a semântica.** Aumento temporário do máximo, com expiração
  correta. Entrega o que a carta já diz: "+X% de vida máxima".
- **M2 — mecânica nova.** Recurso temporário: pontos que absorvem dano (e, no
  MP, pagam habilidades) e somem no vencimento.

A regra da primeira versão do plano (subir teto e HP atual e só limitar no
vencimento) continua descartada: 20/100 → 60/140 → vence → 60/100 transforma
bônus temporário em cura permanente.

### M1 em detalhe

1. **Ao lançar.** O teto sobe `B` pontos, com `B` calculado sobre o teto sem
   buffs de recurso, para relançar não compor sobre si mesmo. O HP atual não
   muda.
2. **Durante o buff, todo leitor do máximo lê o teto elevado.** É o que "vida
   máxima" significa no motor:
   - cura percentual: poção, skill de cura, Fonte, descanso e o limite de
     `heal()`;
   - dano por turno: sangramento e veneno são percentuais do máximo de quem
     sofre;
   - custo do Altar: 30% do máximo;
   - razões de vida: a IA do monstro (`_hp_ratio`) e as condições
     `target_wounded` e `caster_wounded` (`_fracao_de_vida`).
3. **Qualquer queda de teto limita o atual.** Vencimento, `frailty`, troca de
   equipamento: `HP = min(HP, teto novo)`. Hoje só a troca de equipamento faz
   isso (`heroes.py:674`). O vencimento de `vitality` e a aplicação de
   `frailty` deixam HP acima do teto, um defeito latente que o M1 corrige junto.
4. **Relançar.** Renova o buff (a chave é o nome da carta). Cartas diferentes
   somam no teto.
5. **MP pela mesma regra.** O custo das skills percentuais usa a mana de
   referência do nível (`skill_mana_cost`), não o máximo de quem lança, e não
   muda. Regeneração e poção podem encher até o teto elevado, e o vencimento
   limita o MP atual.
6. **Monstro.** A mesma regra (`Monster.base_hp` e `base_mp` somam o buff).
7. **Save e load.** `active_buffs` já é salvo, e o load limita o HP ao teto já
   com o buff.

**Conservação em M1.** O buff nunca concede HP. Vida acima do teto real só
existe se veio de cura durante o buff, e ela se perde no vencimento.

| passo | sem cura | com cura de 100 durante o buff |
|---|---|---|
| início | 20/100 | 20/100 |
| buff de +40 | 20/140 | 20/140 |
| cura | — | 120/140 |
| vence | 20/100 | 100/100 (os 20 acima do teto real se perdem) |

### Comparação

| critério | M1: teto temporário | M2: recurso temporário |
|---|---|---|
| texto atual das cartas | cumprido literalmente | precisa mudar ("vida temporária") |
| profundidade | correção: os buffs alimentam o teto que já existe | mecânica nova: saldo separado, ordem de consumo, regras para custo e sacrifício |
| código tocado | o teto (`_scaled`, `Monster.base_hp` e `base_mp`) e o limite na queda de teto | perda de HP e MP (`reduce_hp`, `reduce_mp`), separação entre gasto e regeneração, custo do Altar, barra da tela |
| coerência com o motor | a mesma semântica dos efeitos de recurso do catálogo (`vitality`, `frailty`) | uma segunda semântica de "vida extra", ao lado da do catálogo |
| conservação | sim, com o limite na queda | sim, por construção |
| utilidade em combate | só com cura no mesmo intervalo; sem cura, o teto maior não protege | absorve dano direto |
| efeitos colaterais | cura percentual maior; dano por turno maior no portador; razão de vida menor (a IA e as condições o veem mais ferido); Altar mais caro se pago com o buff ativo | nenhum nos leitores de percentual; a ordem de consumo precisa ser especificada |
| por carta | herói, HP: vale com poção ou cura; herói, MP: quase nada, porque o MP raramente enche no combate; `tank` (sem cura no kit): quase inerte, e o dano por turno fica maior; `support` (tem `mob_regenerar`, 30%): sinergia real | todas absorvem: herói, `tank` e `support` |
| risco de balanceamento | baixo; maior no `support` | maior: o `tank` ganha absorção real e lançou buff 2.004 vezes na B0 |
| testes | dirigidos por regra, mais a propriedade "HP nunca acima do teto depois de uma queda" | dirigidos por regra, mais a propriedade de conservação por sequência |

### Leitura

- **M1 corrige o defeito; M2 redesenha a mecânica.** O M1 entrega o que a
  carta promete e usa a mecânica de teto que o motor já tem. O M2 entrega o
  que as cartas parecem querer (aguentar mais), mas muda texto, regras e o
  equilíbrio do `tank`.
- **O preço do M1 é a utilidade.** Sem cura no mesmo intervalo, várias cartas
  continuam fracas, o `tank` principalmente. Isso seria tratado depois como
  conteúdo (valores, textos ou kit), e não como motor.
- **Recomendação para a Etapa 1: M1**, com o limite na queda de teto valendo
  para todo efeito de recurso. O M2 fica registrado como evolução de design,
  se a medição mostrar que as cartas continuam sem papel.
- **Medição antes do PR, em qualquer modelo:** TTK e dano recebido contra
  `tank_solo` e `support_solo`, e o uso das cartas do herói com poção, em
  simulação pareada (seção 7).

### Testes (para M1)

- Os três `xfail` passam a aprovados. O teste A/B já detecta a mudança, porque
  `base_hp` e `base_mp` entram na assinatura.
- Testes dirigidos:
  - o teto sobe exatamente `B`, e o HP atual não muda no lançamento;
  - a cura enche até o teto elevado;
  - o vencimento limita o HP atual;
  - relançar não compõe;
  - `frailty` limita;
  - o MP segue as mesmas regras;
  - o monstro segue as mesmas regras.
- Propriedade: em qualquer sequência semeada de lançamento, dano, cura e
  vencimento, o HP fica abaixo do teto em todo passo em que o teto caiu.

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
- O custo de 30% do HP. Se o modelo escolhido no D2 tiver saldo temporário, o
  custo do Altar é sacrifício e se paga com HP real. No M1, o custo é 30% do
  teto vigente, como qualquer leitor do máximo.
- A política do bot. Hoje o avaliador do `?` (`_avaliar_evento`) só soma o
  risco do Altar, nunca o benefício. Valorizar a bênção é inteligência do bot e
  fica para a etapa do bot. Até lá, o efeito da correção na régua do bot é um
  limite inferior.

**Testes.**
- `evento:altar` passa de `xfail` a aprovado.
- Um teste dirigido no funil confere o valor exato pela opção escolhida (por
  exemplo, o `+MULT` ou o atributo resolvido) durante a bênção, e a ausência
  dela depois da duração.
- Um teste de que o texto da tela sai das mesmas constantes que a mecânica.
- Um teste de que jogo, bot e régua passam pela mesma `apply_altar_blessing`.

**Impacto.** Na B0, o Altar foi aceito 69 vezes em 56 das 300 runs. No `-m
balance`, a bênção nunca chega a um combate (seção 5). Corrigir o efeito não
aparece nessa régua antes da correção de fidelidade.

### Hipótese em avaliação: +15% de dano por 5 turnos

Medida por simulação pareada, sem tocar `src/`. A bênção é um buff
`damage_percent` de 15 no `+MULT`, por 5 turnos.
- O herói (equipamento esperado, nível igual ao andar) passa por duas lutas
  seguidas do plano do andar, que é o trecho que a bênção alcança.
- 300 seeds por classe e andar.
- Três braços:
  - **A:** sem Altar;
  - **B:** paga 30% do HP e recebe a bênção;
  - **C:** recebe sem pagar, para isolar o benefício.
- Valores em % do HP máximo ao fim das duas lutas (uma morte conta como 0),
  com o intervalo de 95% da diferença pareada.

**Benefício puro (C − A):**

| classe | andar 3 | andar 8 | andar 14 | andar 20 |
|---|---:|---:|---:|---:|
| Warrior | +1,6 (±1,9) | +0,9 (±2,1) | +1,8 (±0,8) | +1,0 (±0,4) |
| Mage | +2,1 (±1,4) | +0,3 (±1,4) | +3,3 (±1,3) | +2,5 (±0,9) |
| Rogue | +3,7 (±1,7) | -1,9 (±2,2) | +2,0 (±1,5) | +1,1 (±0,9) |

**A decisão real do jogador (B − A):**

| classe | andar 3 | andar 8 | andar 14 | andar 20 |
|---|---:|---:|---:|---:|
| Warrior | -7,9 (±3,2) | +8,8 (±3,5) | -18,1 (±2,4) | -25,6 (±0,5) |
| Mage | -6,4 (±3,4) | +5,7 (±3,5) | -14,2 (±2,5) | -21,0 (±2,1) |
| Rogue | -3,7 (±3,3) | +3,5 (±3,9) | -15,2 (±3,0) | -21,6 (±1,3) |

**Leitura.**
- **A bênção, sozinha, poupa no máximo 3,7% do HP máximo** nas duas lutas que
  alcança (de -1,9% a +3,7%, conforme classe e andar). O custo é 30%.
- **Um B − A positivo não é ganho.** Com menos HP, a política toma poção ou cura
  mais cedo e termina mais alto; o consumo não entra na conta.
- **Mortes (A/B/C, nos andares 3 e 8):** Warrior 3: 1/1/1; Warrior 8: 0/1/1; Mage 3: 1/1/1; Mage 8: 0/3/0; Rogue 3: 2/1/2; Rogue 8: 2/3/1.
- **Conclusão para o D1.** Com +15% de dano por 5 turnos, o Altar continua uma
  troca ruim, mesmo corrigido. A decisão de design precisa mexer na magnitude,
  na duração (por exemplo, até o fim do andar) ou no custo, e não só escolher o
  canal. Nada disso está decidido.
- **Reprodução.** `reports/etapa1_plano/altar_hipotese.py`, sobre o jogo deste
  commit.

---

## 5. Fidelidade da régua do `-m balance`: o evento acontece depois das lutas

**O achado, confirmado por execução.** Em cada andar, `simulate_run` faz, nesta
ordem:
1. todas as lutas;
2. `_apply_random_event`;
3. Loja e Ferreiro;
4. a saída;
5. `recover()`, que limpa `active_buffs`.

A execução real, com 3 classes × 250 runs (o tamanho do teste de bandas) e
contadores que só observam (`reports/etapa1_plano/altar_na_regua.py`), deu:

| medida | valor |
|---|---:|
| combates | 73.888 |
| bênçãos do Altar aplicadas | 792 |
| combates iniciados com a bênção ativa | **0** |
| visitas à Fonte (todas depois da última luta do andar) | 711, com 247.524 de HP curado |

**No jogo.**
- O evento é uma casa do mapa (`EventTile`), resolvida quando o jogador pisa
  nela (`engine/loop.py`).
- O fim do andar é só `FIM_DE_ANDAR = ("saida", "descanso", "juros")`.
- As lutas depois da casa herdam a bênção, e a cura da Fonte serve às lutas
  seguintes do andar.

**No BotPadrão, que joga o mapa:** 69 bênçãos aceitas na B0, e 36 combates
iniciados com a bênção ativa, em 27 runs.

**Por que a régua ficou assim.** O comentário do `simulate_run` cita a ordem
antiga do fim de andar (evento, descanso, loja). Quando eventos e serviços
viraram casas do mapa, o jogo mudou e a régua não.

**O mesmo vale para os serviços.**
- Loja e Ferreiro também são casas do mapa no jogo, e na régua rodam no fim do
  andar: a cura paga e o equipamento comprado não servem às lutas do andar em
  que foram encontrados.
- O Mercador ainda é uma segunda Loja (seção 6).

**Opções de correção (decisão D6; nenhuma implementada):**

| opção | como | fidelidade | custo | observação |
|---|---|---|---|---|
| F1. Posição sorteada | o evento (e os serviços, se D6 incluir) acontece antes da luta `k`, com `k` sorteado pelo `rng` da régua entre 0 e o número de lutas | boa no agregado | baixo | simples e reprodutível; a distribuição uniforme é uma hipótese |
| F2. Posição calibrada | como F1, mas `k` segue a distribuição medida no jogo: em que ponto do andar o jogador chega à casa, medido nos mapas reais por uma sonda do BotPadrão | melhor | médio | exige uma medição nova, só de observação, antes da mudança |
| F3. A régua joga o mapa | a régua passa a percorrer o mapa, como o BotPadrão | máxima | alto | desfaz a régua sintética e deixa o `-m balance` muito mais lento |

**Recomendação: F2.** É a F1 com a distribuição medida, aplicada ao evento e
aos serviços, numa mudança só de régua e com baseline própria do `-m balance`,
antes de qualquer correção que dependa dela (Altar, Fonte, Mercador).
- **A decisão de ir ao evento** também muda de lugar. `_bot_visita_evento`
  passa a olhar o HP do momento da casa, e não o do fim do andar.
- **Impacto esperado.** A Fonte e a cura paga passam a servir às lutas
  seguintes, o que torna a régua mais fácil. O Altar passa a ter custo e efeito
  dentro do andar.
  - As três bandas globais podem se mover (D5).
  - As congeladas precisam continuar verdes. Se não ficarem, é achado de
    balanceamento, não ajuste de limite.
- **É mudança de instrumento.** Não é implementada sem aprovação, e vem com
  baseline própria.

## 6. Mercador: a mesma regra no jogo, no bot e na régua

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

## 7. Como medir correções pequenas (KI-012)

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

## 8. Decisões pendentes

| | decisão | estado | quem decide | bloqueia |
|---|---|---|---|---|
| D1 | o efeito da Bênção do Altar: magnitude, duração, custo e texto. A hipótese de +15% por 5 turnos foi medida (seção 4) | em aberto | design | KI-007 |
| D2 | M1 (teto temporário com expiração correta, recomendado) ou M2 (recurso temporário), seção 3 | em aberto | design | KI-008 |
| D3 | +4% de DF no Amuleto de Argila, as duas vias somam | **aprovado** | — | — |
| D4 | a política de compra do bot no Mercador, sobre as ofertas (proposta: o avaliador de equipamento existente) | em aberto | técnica, com aprovação, porque muda o instrumento | fidelidade |
| D5 | remedir ou não as bandas globais do `-m balance`, se as réguas corrigidas as moverem | em aberto | usuário | fidelidade e merges que movam bandas |
| D6 | a correção da ordem do andar na régua (F1, F2 ou F3) e se os serviços entram junto com o evento | em aberto | técnica, com aprovação | fidelidade |

## 9. Riscos

- **Corrigir mecanismos numa jornada diferente da do jogador.** Enquanto a
  régua do `-m balance` resolver eventos e serviços depois das lutas, as
  correções do Altar, da Fonte e do Mercador não aparecem nela. Por isso a
  fidelidade (passo 2) vem antes do KI-008 e do KI-007.
- **Bandas congeladas reprovando** depois do KI-008: duração do `tank_solo` ou
  `support_solo`. A resposta é medir e decidir, não mexer no limite.
- **Interação entre correções.** Se D1 escolher um buff de atributo e D2 mudar
  a leitura de buffs, a ordem 3 → 4 evita que a medição de uma contamine a da
  outra.
- **PvP.** As correções mudam `src/` da `phase/game-core`, e a
  `phase/pvp-arena` não é tocada. Uma integração futura entre as duas vai exigir
  remedir o benchmark da Arena e a calibração da Ranked, porque o combate dos
  gladiadores passa pelas mesmas funções.
- **A régua do bot subestima as correções** enquanto o bot não usar buffs nem
  valorizar o Altar. Isso só se resolve na etapa do bot, e precisa estar
  escrito em cada leitura de resultado.
