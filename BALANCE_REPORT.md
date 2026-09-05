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

| Classe | Andar médio | Mediano | Chega ao andar 20 | Passivas ao fim | Bot que só ataca |
|---|---:|---:|---:|---:|---:|
| Guerreiro | 9,3 | 5 | 32,8% | 11,3 | andar médio 1,2 |
| Mago | 5,8 | 3 | 16,4% | 6,9 | andar médio 0,3 |
| Ladino | 8,2 | 4 | 26,0% | 9,9 | andar médio 1,2 |

- O bot que só ataca **não termina a masmorra** em nenhuma classe.
- Distância entre a melhor e a pior classe: **3,5 andares**, com o Mago
  consistentemente atrás nas cinco seeds medidas (5,3 a 5,8 contra 8,4 a 9,3 do
  Guerreiro). É o maior desequilíbrio aberto.
- Jogar bem vale de **5,4 a 8,1 andares** de profundidade.
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

### O que o scout encontra agora

250 runs por classe, ablação com 150, comparação de intenções com 150
(`reports/scout_20260905.json`):

| Sistema desligado | Delta |
|---|---:|
| Essência | −5,1 |
| Passivas | −3,5 |
| Loja | −2,8 |
| Loot | −1,5 |
| Eventos aleatórios | −0,6 |
| Escolha de skill | −0,0 |

Quatro problemas que a métrica de profundidade sozinha não mostrava:

1. **A Essência decide a run mais que qualquer escolha do jogador.** Um
   multiplicador sorteado, sobre o qual ninguém tem controle, pesa mais que as
   passivas (−5,1 contra −3,5) e multiplica o XP em 1,51x na média. Isso é sorte
   no lugar de decisão, e é o problema de design mais grave em aberto.
2. **Escolher skill nova não muda nada** (−0,0 andar ao desligar). O bot leva
   skills Raras e Épicas de dano que depois nunca usa, porque custam mais mana e
   perdem para o ataque básico — que sozinho responde por **38% do dano total**.
   Três skills aparecem como "escolhidas mas nunca usadas", e **Explosão Arcana**
   consegue ser as duas coisas: levada por toda intenção e nunca lançada.
3. **As passivas grandes de HP são resposta óbvia, não escolha.** Coração de Titã
   é levada em 100% das 54 ofertas, Alma Eterna em 99% de 283, Bênção Divina em
   98% de 242. O eixo `max_hp` tem seis cartas de +15 a +200 e domina todos os
   outros efeitos.
4. **84% do ouro nunca é gasto** (829 mil de 5,29 milhões). A economia não tem no
   que competir consigo mesma: falta preço alto o bastante ou item bom o
   bastante para o ouro ter destino.

### Escolher vale 1,1 andar — mas a calibração usou a pior intenção

Com 150 runs por política:

    economy 9,6  >  random 8,5  >  offense 7,9  >  survival 7,9

Escolher de propósito rende **+1,1 andar** sobre sortear a carta ao acaso, então
o menu de cartas faz pergunta. O que ele revela é outro problema: `survival` —
a política usada em **toda a calibração** — empata em último, 1,7 andar atrás de
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
