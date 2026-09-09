# Balanceamento — rebalanceamento estrutural

Substitui o relatório anterior (PROMPT 14), que ajustava constantes de classe
sobre um modelo que divergia por construção.

## O que estava errado

A auditoria mediu, com o motor de combate real rodando headless, uma taxa de
vitória de **99% a 100% contra o monstro comum em todos os níveis e nas três
classes**. Sete causas, nenhuma delas de "número baixo demais":

| # | Causa | Evidência |
|---|---|---|
| D1 | Herói crescia em percentual composto (`+20%` de HP por nível), monstro em soma fixa (`+20` de HP) | Poder do Mago x21,8 do nível 1 ao 20; HP do monstro x4,8 |
| D2 | `rest()` restaurava tudo depois de cada vitória, a cada nível, ao equipar, ao desequipar e ao fugir | Cinco pontos; atrito zero |
| D3 | Todo combate durava 1 ou 2 turnos | Sem espaço para decisão nem para punir decisão ruim |
| D4 | 32 efeitos declarados no JSON não tinham tratamento no motor | 16 de 41 skills, 10 de 29 passivas, 6 de 11 poções |
| D5 | Um único monstro com 121 nomes; combate sempre 1 contra 1 | `weight` e `min_level` das categorias nunca eram lidos |
| D6 | Ladino ficava com 0% de chance de ser acertado a partir do nível 13 | `85 + AG_atacante - AG_defensor`, sem piso |
| D7 | Skill, cura e equipamento eram somas fixas sobre um poder que crescia | Melhor arma = 3% do poder base no nível 20 |

Baseline completa em `reports/baseline_20260904.json`.

## O modelo

**Uma razão de crescimento só.** `GROWTH_RATE = 1.12` para herói e monstro. A
razão poder-do-herói / HP-do-monstro fica constante ao longo dos 20 níveis, e a
dificuldade passa a ser controlada de propósito.

**Orçamento distribuído.** As três classes têm poder de ataque comparável no
nível 1; a identidade está em como elas gastam o resto.

| Classe | Poder | HP efetivo | Identidade | Fraqueza |
|---|---:|---:|---|---|
| Guerreiro | 89 | 581 | Ganha por atrito | Tank, que também ganha por atrito |
| Mago | 119 | 466 | Vence rápido ou não vence | Controlador, que rouba turno e mana |
| Ladino | 100 | 463 + esquiva | Escolhe quando lutar | Skirmisher, que anula a esquiva |

**Nove arquétipos de monstro**, com orçamento, comportamento, ameaça e
counterplay declarados em `src/data/monsters.json`. Todo arquétipo precisa de
pelo menos uma classe que sofre contra ele.

**Escala relativa.** Dano de skill é percentual do poder base; cura, percentual
do HP máximo; bônus de equipamento, percentual do atributo; chance de acerto usa
a diferença relativa de agilidade, com piso de 20% e teto de 95%.

**Atrito.** Concluir um andar devolve 32% dos recursos. Nada mais cura de graça.

## O que a simulação roda

A run simulada percorre os mesmos sistemas do jogo, e não só o combate:

| Sistema | Onde |
|---|---|
| Escolha de passiva a cada nível | `sim/progression.py: on_level_up` |
| Escolha de skill em nível ímpar a partir do 5 | `sim/progression.py: pick_skill` |
| Drop de item por vitória, com troca se for melhor | `sim/progression.py: collect_loot` |
| Loja entre andares: repõe cura e melhora equipamento | `sim/progression.py: visit_shop` |
| Evento aleatório de andar (Fonte, Altar) | `sim/harness.py: _apply_random_event` |
| Multiplicador de Essência por andar | `sim/progression.py: floor_essence_multiplier` |
| Buff, elixir, poção de mana e controle em combate | `sim/policies.py: smart_policy` |

Isso importa mais do que parece. Uma calibração anterior media um herói que
atravessava vinte andares **com zero passivas** e o equipamento do andar 1,
porque `while level_up(show=False)` nunca iterava — o método devolve lista vazia
quando `show=False`, mesmo tendo subido de nível. Os números daquela calibração
não valiam para o jogo que existe. `test_a_run_entrega_a_progressao_do_jogo`
existe para que isso não volte em silêncio.

## Resultado

250 runs por classe, política competente, equipamento típico
(`reports/validation_20260905.json`):

| Classe | Andar médio | Mediano | Chega ao andar 20 | Bot que só ataca |
|---|---:|---:|---:|---:|
| Guerreiro | 10,4 | 7 | 34,0% | andar médio 0,9 |
| Mago | 7,4 | 4 | 19,2% | andar médio 0,2 |
| Ladino | 9,7 | 5 | 28,8% | andar médio 0,9 |

> **Números superados.** A revisão do PR apontou duas divergências entre a
> masmorra simulada e a de produção — o nível de cada monstro era fixado no
> andar em vez de sortear `+0/+1/+2` (peso 70/25/5), e fugir não encerrava o
> andar, encadeando o próximo combate no mesmo HP baixo que motivou a fuga.
> Corrigidas as duas, a mesma medição dá **Guerreiro 8,8 · Mago 5,2 ·
> Ladino 8,3**. A masmorra sempre foi mais dura que isto: quem estava errado
> era o medidor. Distância entre classes: 3,6 andares (limite 4,0).

- O bot que só ataca **não termina a masmorra** em nenhuma classe.
- Distância entre a melhor e a pior classe: **3,0 andares**. Nenhum número de
  classe foi alterado em nenhuma das rodadas: os 3,5 anteriores caíram para 2,4
  ao consertar o bot que curava com o inimigo a um golpe da morte, e voltaram a
  3,0 ao tirar peso da sorte — o Mago era quem mais dependia de um sorteio alto
  de Essência para sobreviver aos primeiros andares.
- Jogar bem vale de **7,2 a 9,5 andares** de profundidade.
- Duração de combate: trash 3,4 turnos, bruiser 8-12, elite 12-17, chefe 16-24.

**A distribuição é bimodal**, e isso é um achado, não um detalhe: a maioria das
runs termina nos primeiros andares, e quem passa do andar 5 com passivas
empilhadas tende a chegar ao 20. A run é decidida cedo. Fechar essa lacuna —
fazer os andares finais voltarem a ser uma pergunta — é o próximo trabalho de
balanceamento, e depende de as passivas deixarem de ser puro acúmulo.

## Scout de sistemas

Profundidade média responde "está balanceado?". Não responde "qual skill é forte
demais, qual passiva ninguém leva, quanto a Essência decide a run". Para isso o
scout usa dois métodos, porque nenhum dos dois sozinho basta:

**Atribuição** — telemetria coletada durante runs normais: dano por skill e por
mana, ofertas e escolhas de cada carta, origem do equipamento, destino do ouro,
efeito da Essência, o que cada evento fez. Custa segundos, aponta o suspeito.

**Ablação** — desliga um sistema e compara a profundidade média. Custa dezenas
de segundos, condena.

Os dois discordam com frequência, e a discordância é informação: uma skill pode
ter dano alto por ser sempre usada mas ablação baixa, porque outra a substitui;
uma passiva rara pode ter atribuição baixa e ablação alta.

**Comparação entre intenções de build** — o scout roda a run com quatro
políticas de escolha de carta (`survival`, `offense`, `economy` e `random`) e
compara. Com uma política só, "esta passiva é ignorada" mistura duas causas:
a carta é fraca, ou serve a uma build que aquele bot não joga. Com várias, o
padrão separa: recusada por toda intenção é carta fraca; levada por toda
intenção é a resposta certa disfarçada de escolha; levada por uma só é
identidade de build, que é o que se quer. A política `random` é o grupo de
controle e mede o **valor da escolha**.

```bash
python -m src.sim.runner scout --iterations 60                    # atribuição rápida, ~40s
python -m src.sim.runner scout --iterations 250 --policy-iterations 150   # confiável, ~3min
python -m src.sim.runner scout --iterations 250 --ablate --ablation-iterations 150  # ~5min
python -m src.sim.runner scout --ablate --per-skill --per-passive # carta a carta, minutos
python -m src.sim.runner run --pick-policy economy                # calibrar com outra intenção
```

### Correção: os números do primeiro scout mediam ruído

O primeiro scout rodou sobre uma simulação que **não era reproduzível**. O
harness semeava o `rng` que injeta no combate, mas a camada de conteúdo sorteia
pelo gerador global do módulo `random` — oferta de carta, nível do monstro,
spawn de elite, drop, estoque da loja, Essência — e esse nunca era semeado.
Duas execuções do mesmo comando davam 7,0 e 7,8 de andar médio. Em cinco seeds
a 60 runs o andar médio do Guerreiro variou de 6,9 a 10,5.

Essa oscilação era maior que quase todo delta que o scout reportava. Três
conclusões do relatório anterior não sobreviveram à correção, e ficam
registradas porque o erro é do medidor, não do jogo:

| Afirmação anterior | Medida real |
|---|---|
| "Escolher carta vale +0,0 andar — o menu não faz pergunta nenhuma" | **+1,1 andar** sobre sortear ao acaso |
| "Eventos aleatórios não mudam nada (+0,2)" | **−0,6 andar** ao desligar: pequeno, mas real |
| "Escolher skill nova piora a run (+0,3)" | **−0,0 andar**: neutro, não prejudicial |

Delta positivo ao desligar um sistema — a run ficar *melhor* sem ele — era o
sinal de que a medição estava quebrada, e ele sumiu junto com o defeito: todos
os seis sistemas agora perdem profundidade ao serem desligados. Ver
`TestReprodutibilidade` em `tests/balance/test_invariants.py`.

### Mais dois defeitos do medidor, encontrados na reauditoria

**A batalha que encerrava a run não era registrada.** `simulate_run` saía do
laço assim que o herói morria, antes de chamar `record_battle`: a telemetria via
100% das vitórias e 0% das derrotas — 562 combates de 30.759. A correção
acrescentou `defeats` à telemetria, então agora dá para perguntar o que o herói
fazia quando morreu. A duração média do combate praticamente não mudou (9,93
para 9,90 turnos): ao contrário do que eu esperava, a luta fatal é **mais
curta** que a média, porque o herói superado morre rápido.

**Carta sem amostra era lida como carta recusada.** O scout descarta a carta
oferecida menos de dez vezes, e depois tratava a ausência como taxa zero. Agora
ela entra num grupo próprio, "sem amostra suficiente", em vez de ser condenada.

### A sorte deixou de decidir a run

A Essência sorteada nos cinco primeiros andares explicava **38,7%** da variância
da profundidade final. Nesse trecho o herói ainda não tem passiva, equipamento
nem nível para compensar um sorteio ruim, então o número decide antes de existir
decisão. Os 25% mais azarados paravam no andar 3,8; os 25% mais sortudos, no
16,2. Uma distância de **12,4 andares** tirada na moeda, num jogo em que escolher
carta de propósito valia 1,5.

O desvio do sorteio caiu de 0,5 para 0,2. A média não mudou, então o ritmo do
jogo é o mesmo — o andar médio vai de 9,5 para 9,2. O que sai é o peso da sorte:

| | Antes | Depois |
|---|---:|---:|
| Variância da run explicada pelo sorteio | 38,7% | 12,8% |
| Distância entre o quartil azarado e o sortudo | 12,4 andares | 7,4 andares |
| Valor de escolher carta de propósito | +1,5 andar | +1,8 andar |

Também foi medido um desvio que cresce com o andar, para deixar a sorte só onde
ela não decide mais. Perdeu para o desvio fixo nos três eixos: 14,7% de
variância explicada contra 12,6%, mesma distância entre quartis, e andar médio
menor. A ideia era melhor que o resultado.

Os limites do sorteio passaram de 0,5–3,0 para 0,6–2,2. Com desvio 0,2, os
extremos antigos ficavam a mais de oito desvios da média: a tela de extração
prometia ao jogador uma faixa que o sorteio nunca entregaria.

**O efeito colateral é o ponto.** Com menos ruído, todo sistema de decisão
passou a pesar mais na ablação:

| Sistema | Antes | Depois |
|---|---:|---:|
| Passivas | −4,4 | −4,4 |
| Loja | −3,8 | −3,8 |
| Loot | −2,1 | −2,1 |
| Escolha de skill | −0,2 | −0,2 |

Nenhum desses sistemas mudou. Eles só pararam de ser medidos por cima de um
sorteio que respondia por 38% do resultado.

### Dois defeitos que passavam por achado de design

**O elite do andar 3 não existe no jogo.** `_default_floor_plan` mantinha tabela
própria e punha um elite em todo andar múltiplo de 3, começando no 3.
`generate_monsters_for_level` só gera elite a partir do andar 4 e, dali em
diante, com 12% de chance. Esse elite inventado era onde a run terminava: 36 das
48 mortes do Guerreiro no andar 3, 66 das 117 do Mago, 44 das 53 do Ladino. O
scout reportava uma "parede do andar 3" com o Mago perdendo 47% das runs num
andar só, e a leitura era de design. Era o medidor. Corrigido, a maior queda da
curva vai para o andar 5 — o mini-chefe, que o jogo realmente gera.

**Matar antes de curar.** O bot competente curava sempre que caía abaixo de 35%
de vida, mesmo com o inimigo a um golpe da morte. Contra alvo de dano alto isso
vira espiral: cura, toma dano, cura de novo. O Mago gastava 231 dos 840 turnos
de skill curando na luta contra o glass cannon do andar 3, levava 5,0 turnos
onde o Ladino levava 2,7, e vencia 44,8% contra 99,8%.

O Mago não era fraco: o bot jogava mal, e a calibração inteira foi feita em cima
disso. Com a checagem de golpe letal, a taxa de vitória dele naquele encontro vai
a 76,8%, a cura cai de 231 para 43 usos, e o andar médio sobe de 5,8 para 8,2 —
sem alterar um único número de balanceamento.

### O que o scout encontra agora

250 runs por classe, ablação com 150, comparação de intenções com 150
(`reports/scout_20260905.json`):

| Sistema desligado | Delta |
|---|---:|
| Essência | −5,4 |
| Passivas | −3,5 |
| Loja | −3,3 |
| Loot | −1,5 |
| Eventos aleatórios | −0,6 |
| Escolha de skill | +0,1 |

Quatro problemas que a métrica de profundidade sozinha não mostrava:

1. **A Essência decide a run mais que qualquer escolha do jogador.** Um
   multiplicador sorteado, sobre o qual ninguém tem controle, pesa mais que as
   passivas (−5,4 contra −4,4) e multiplica o XP em 1,47x na média. Isso é sorte
   no lugar de decisão, e é o problema de design mais grave em aberto.
2. **Escolher skill nova quase não muda nada** (−0,2 andar ao desligar). O bot leva
   skills Raras e Épicas de dano que depois nunca usa, porque custam mais mana e
   perdem para o ataque básico — que sozinho responde por **38% do dano total**.
   Três skills aparecem como "escolhidas mas nunca usadas", e **Explosão Arcana**
   consegue ser as duas coisas: levada por toda intenção e nunca lançada.
3. **As passivas grandes de HP são resposta óbvia, não escolha.** Coração de Titã
   é levada em 100% das 54 ofertas, Alma Eterna em 99% de 283, Bênção Divina em
   98% de 242. O eixo `max_hp` tem seis cartas de +15 a +200 e domina todos os
   outros efeitos.
4. **82% do ouro nunca é gasto** (1,05 milhão de 5,76 milhões). A economia não tem no
   que competir consigo mesma: falta preço alto o bastante ou item bom o
   bastante para o ouro ter destino.

### Escolher vale 1,1 andar — mas a calibração usou a pior intenção

Com 150 runs por política:

    economy 12,2  >  random 10,4  >  offense 10,0  >  survival 9,3

Escolher de propósito rende **+1,8 andar** sobre sortear a carta ao acaso, então
o menu de cartas faz pergunta. O que ele revela é outro problema: `survival` —
a política usada em **toda a calibração** — fica em último, 2,9 andares atrás de
`economy`. O jogo é mais fácil do que os números de calibração dizem para quem
constrói pensando em progressão, e a banda de dificuldade foi ajustada contra a
build mais fraca.

A comparação entre intenções também reclassifica cartas que uma política só
condenava por engano. Das 29 passivas, apenas **uma** é recusada por toda
intenção (Reflexos Rápidos); **20** são levadas por exatamente uma intenção, o
que é identidade saudável e não deve ser mexido. Nas skills, **10** são
recusadas por todas — essas são fracas de verdade — e **Assassinato** e
**Explosão Arcana** são levadas por todas, ou seja, não são opção: são a
resposta certa.

Outras **5** skills ficam explicitamente **sem julgamento** (Apocalipse,
Esmagar, Imortal, Morte Súbita, Ressurgir): pelo menos uma intenção não as
ofereceu dez vezes, e sem amostra não há taxa. O scout classificava essas
cartas como se a taxa fosse zero, e o viés não era aleatório — `survival` e
`offense` morrem mais raso e nunca chegam aos níveis em que as cartas de fim de
jogo aparecem, então eram sempre elas as condenadas. `Ressurgir` estava na lista
de fracas por esse motivo, e `Apocalipse` e `Morte Súbita` estavam na de
identidade. Para julgá-las, `--policy-iterations` maior.

### O relatório dizia as duas coisas ao mesmo tempo

A comparação acima entrou no scout, mas as análises antigas continuaram lá do
lado. `analyse_skills` e `analyse_passives` recebem a telemetria de `collect`,
que roda com **uma** política de escolha (`DEFAULT_PICK_POLICY = "survival"`), e
mesmo assim emitiam veredito sobre a carta: `ignorada` abaixo de 15% de escolha,
`SUSPEITA — é a escolha óbvia` acima de 90%.

O mesmo relatório saía, então, afirmando duas coisas incompatíveis sobre a mesma
carta. Sob `survival`, `max_hp` é a prioridade 1 e `gold_drop_bonus` é a 13 de
13: toda passiva de ouro aparecia como carta ignorada no bloco de passivas,
enquanto três parágrafos acima ela constava como identidade da build de
economia. O bloco single-policy não media a força da carta — media a lista de
prioridades daquele bot, e chamava isso de conteúdo morto.

Os dois vereditos de escolha saíram de `analyse_skills` e `analyse_passives`.
Quem classifica carta é `_analyse_cards`, com as quatro políticas. O que sobrou
nas duas funções é o que não depende de quem escolhe: dano por mana, fatia do
dano total, e se o sorteio chega a pôr a carta na mesa.

É o mesmo padrão dos outros defeitos do medidor: nada levantou exceção, a suíte
ficou verde, e o relatório saiu bonito com o número errado dentro.

## O combate voltou a ter escolha

O pedido era direto: *"precisamos nerfar o ataque básico, não faz sentido. (...)
o jogador nunca vai se adaptar ao que está acontecendo, ele só vai spamar uma
skill."* O diagnóstico estava certo e a causa era outra.

### O que a medição disse, e o que ela desmentiu

Com o ataque básico entregando o poder inteiro, de graça e sem recarga, **36%
do dano do herói saía dele** e o bot soltava **2,2 skills por combate de doze
turnos**. O Mago usava **uma** skill acima de 10% dos usos; Guerreiro, duas.

A hipótese óbvia — o ataque básico está forte demais — foi testada e **está
errada**. Mexer só nele não move o número:

| `BASIC_ATTACK_POWER_MULT` | Regen | Guerreiro | Mago | Ladino | Distância | Dano do básico | Skills/luta |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1,00 (antes) | 0 | 9,2 | 5,3 | 8,9 | 3,9 | 35,9% | 2,2 |
| 0,90 | 0 | 8,1 | 5,2 | 8,4 | 3,2 | **35,2%** | 2,2 |
| 1,00 | 2% | 10,2 | 5,8 | 10,5 | **4,7** | 19,3% | 2,9 |
| 1,00 | 3% | 11,3 | 6,0 | 11,7 | **5,6** | 17,6% | 3,1 |
| **0,90** | **2%** | **9,2** | **6,7** | **10,1** | **3,4** | **17,4%** | **3,1** |
| 0,80 | 3% | 9,6 | 7,6 | 11,7 | 4,0 | 13,4% | 3,3 |

250 runs por classe, seed 11, política competente, equipamento típico.

Baixar o ataque básico de 1,0 para 0,9 sem mais nada move a fatia do dano dele
de 35,9% para 35,2% — **nada** — e custa 1,1 andar ao Guerreiro. O herói não
spamava o básico porque o básico era forte. Spamava porque **ficava sem mana no
terceiro turno**: o Guerreiro entra no nível 1 com 60 de MP e a Investida custa
20. A única recarga do jogo era o descanso de fim de andar.

### A correção é um par, e nenhuma das duas metades funciona sozinha

**`MP_REGEN_PERCENT_PER_TURN = 2`.** A mana deixa de ser um estoque gasto uma
vez e vira ritmo: dá para bater agora e pagar a skill grande dali a três turnos.
Sozinha, ela derruba o básico de 36% para 19% — mas leva a distância entre
classes de 3,9 para **4,7 andares, acima do limite de 4,0**, porque Guerreiro e
Ladino aproveitam a mana nova e o Mago quase não muda.

**`BASIC_ATTACK_POWER_MULT = 0.90`.** É o nerf que paga a regeneração. Junto com
ela, a distância cai para 3,4 e o Guerreiro fica exatamente onde estava (9,2).

O par entrega o que foi pedido: básico de 36% para **17,4%** do dano, 2,2 para
**3,1 skills por combate**, e o Mago passa a usar **duas** skills em vez de uma.
Dificuldade preservada no Guerreiro, e o Mago — a classe mais fraca — sobe 1,4
andar sem que nenhum número de classe fosse tocado.

### Os monstros ganharam intenção

*"Parece que os monstros não seguem uma lógica baseada na armadura deles."* Não
seguiam mesmo, e por um defeito: `Monster.get_df()` devolvia a defesa crua e
ignorava `active_buffs`. **Nenhum buff de monstro tinha efeito** — a Bênção
Sombria do suporte gastava mana, turno e recarga para não mudar nada, e o
arquétipo tank inteiro dependia disso. Corrigido junto com os outros achados da
revisão do PR.

Com o buff funcionando, a IA passou de estática para reativa. Antes, fora a cura
de emergência, o monstro escolhia sempre a mesma skill do papel, e o uso passava
por uma moeda (`skill_use_chance`) que ignorava a situação: um tank buffava a
armadura no turno em que fosse sorteado, inclusive no último; um chefe com o
herói a um golpe da morte podia dar um tapa.

Agora existem quatro momentos, e três **furam a moeda**, porque jogada decisiva
não é sorteio:

| Momento | Quando | Quem |
|---|---|---|
| **Execução** | herói abaixo de 35% de vida | todo arquétipo com dano |
| **Sobrevivência** | o próprio monstro ferido, com cura na mão | suporte |
| **Desespero** | abaixo de 35% da própria vida | quem defende se fecha; quem não defende gasta o maior dano |
| **Abertura** | primeiro turno | tank, elite, chefe, suporte |

E a rotina do papel nunca relança um buff que já está no ar — outra forma de
gastar turno em nada.

**Catálogo de arquétipos:** todo papel exceto o trash passou a ter no mínimo
duas intenções (eram cinco papéis com uma skill só, dependendo da moeda cair na
hora certa). O trash continua sem skill de propósito: o arquétipo dele é
acúmulo, e a ameaça é o número, não a jogada. Novas: Fúria (bruiser), Muralha e
Impacto de Escudo (tank), Detonação Arcana (glass cannon), Esquiva Felina e
Ferida Aberta (skirmisher), Presságio (controlador), Maldição (suporte), Pele de
Ferro (elite), Ira Final (chefe).

Custo isolado da IA nova, medido com o ataque básico ainda em 1,0: Guerreiro
0,0, Mago +0,2, Ladino −1,0 andar. O Ladino é quem mais sente, e faz sentido —
a Esquiva Felina do skirmisher e a Muralha do tank atacam exatamente o que ele
faz.

### O que isto expôs: 13 pares de skills dominadas

Ao fixar o piso de "toda skill de dano tem de valer mais que bater", oito skills
reprovaram. A causa não é o piso: é que **a tabela de preços das skills não é
monótona**. Uma skill que custa mais mana e mais recarga entrega menos dano que
a que a classe já ganha no nível 1.

| Classe | Dominada | Domina |
|---|---|---|
| Guerreiro | `golpe_devastador` (nv 10, 50%, 30 MP, cd 3) | `golpe_poderoso` (nv 1, 60%, 15 MP, cd 1) |
| Guerreiro | `golpe_duplo` (nv 9, 45%, 35 MP, cd 3) | `investida` (nv 1, 70%, 20 MP, cd 1) |
| Guerreiro | `cutelada` (nv 5, 35%, 20 MP, cd 2) | `golpe_poderoso` |
| Mago | `relampago` (nv 5), `explosao_arcana` (nv 7), `tempestade` (nv 13) | `bola_fogo` e `missil_magico` (nv 1) |
| Ladino | `assassinato` (nv 9), `danca_laminas` (nv 13) | `ataque_furtivo` (nv 1) |

Eficiência em dano por mana: as skills de nível 1 entregam de 3,2 a 4,0; as
aprendidas depois, de 1,3 a 2,0. **O kit inicial é o kit final.**

É a explicação, com causa, do achado que estava aberto desde o primeiro scout —
"escolher skill vale −0,2 andar" e "10 skills recusadas por toda intenção". Não
era o bot escolhendo mal nem as skills serem fracas: metade delas é
matematicamente pior que o que o jogador já tem na mão.

### A tabela de preços passou a ter uma regra

As doze skills **aprendidas** (nível exigido acima de 1) foram reprecificadas
por uma curva; as **iniciais não foram tocadas**, porque resolver dominância
tirando poder do jogador seria a direção contrária à que já foi escolhida para
a paridade entre classes.

```
valor = teto_inicial_da_classe × (1 + 0,040·(nível−1)) × (1 + 0,10·(recarga−1))
mana  = valor / (2,4 + 0,30·(recarga−1))
```

O `teto_inicial_da_classe` é o dano da melhor skill de nível 1 da classe — é o
que garante que subir de nível entregue mais poder que o kit de partida. O
prêmio de recarga é o que dá razão de existir a uma skill lenta: ela troca
frequência por pico, e rende mais dano por mana em troca.

| Classe | Skill | Nível | Dano | Mana |
|---|---|---:|---|---|
| Guerreiro | `cutelada` | 5 | 35 → **90** | 20 → 35 |
| Guerreiro | `golpe_duplo` | 9 | 45 → **110** | 35 → 35 |
| Guerreiro | `golpe_devastador` | 10 | 50 → **115** | 30 → 40 |
| Guerreiro | `esmagar` | 15 | 80 → **140** | 50 → 40 |
| Mago | `relampago` | 5 | 45 → **100** | 30 → 35 |
| Mago | `explosao_arcana` | 7 | 60 → **120** | 40 → 40 |
| Mago | `tempestade` | 13 | 75 → **140** | 50 → 45 |
| Mago | `apocalipse` | 20 | 120 → **195** | 70 → 55 |
| Ladino | `golpe_sombras` | 5 | 30 → **100** | 15 → 35 |
| Ladino | `assassinato` | 9 | 60 → **125** | 40 → 40 |
| Ladino | `danca_laminas` | 13 | 70 → **140** | 45 → 45 |
| Ladino | `morte_subita` | 20 | 150 → **195** | 80 → 55 |

Pares dominados: **13 → 0**. A pior razão skill/ataque-básico do catálogo sobe
de 1,44 para 1,78.

**O efeito na profundidade é pequeno, e isso é o achado.** 150 runs por classe,
três seeds:

| Classe | Antes da tabela | Depois |
|---|---:|---:|
| Guerreiro | 9,2 | 9,4 |
| Mago | 6,7 | 7,2 |
| Ladino | 10,1 | 10,2 |

Quase nada, porque **a run mediana morre no andar 6** — antes de o herói chegar
aos níveis em que essas skills existem. Consertar a tabela não deixa o jogo mais
fácil; deixa a escolha de skill significar alguma coisa para quem chega lá. É
exatamente o tipo de mudança que a ablação não captura e que só aparece na
diversidade de uso:

| Classe | Uso das skills, antes | Depois |
|---|---|---|
| Guerreiro | 1 skill acima de 10% | `investida` 51%, `golpe_poderoso` 22%, `golpe_devastador` 8% |
| Mago | 1 skill acima de 10% | `bola_fogo` 59%, `explosao_arcana` 28%, `barreira_arcana` 11% |
| Ladino | 3 skills acima de 10% | `ataque_furtivo` 46%, `assassinato` 32%, `passo_felino` 16% |

Quatro regras novas em `tests/test_skills.py` fixam isso: nenhuma skill de dano
pode ser dominada, toda skill aprendida bate o teto do kit inicial, o dano cresce
com o nível exigido, e recarga longa é paga em eficiência. Dez delas falham nos
dados anteriores.


## Como reproduzir

Todo comando é determinístico: a mesma `--seed` devolve o mesmo resultado.

```bash
python -m pytest tests/balance -q                     # invariantes, ~60s
python -m pytest tests/balance -q -m balance_full     # runs completas
python -m src.sim.runner run --iterations 250 --loadout expected
python -m src.sim.runner matrix --iterations 500 --levels 1,10,20
python -m src.sim.runner compare --against reports/baseline_20260904.json
```

**Amostra mínima.** A profundidade da run é bimodal, então a média tem erro
amostral grande: a 60 runs o andar médio do Guerreiro variou 3,6 andares entre
seeds; a 250, 0,9. Abaixo de 250 runs por classe, qualquer delta menor que um
andar é ruído — o scout avisa quando o valor medido é pequeno perto do
espalhamento entre políticas.
