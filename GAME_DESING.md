# GAME DESIGN — Tales of the Journey

> A bússola criativa. O resto é código, suor e tokens.

> **Como ler este documento.** Toda afirmação carrega um estado verificado contra
> o código em `master`:
>
> | Marca | Significado |
> |---|---|
> | **`[implementado]`** | Está no código e foi conferido |
> | **`[divergiu]`** | Existe, mas diferente do que este documento pedia. A diferença está escrita |
> | **`[não existe]`** | Especificado aqui e nunca construído |
> | **`[bug]`** | Deveria funcionar assim, não funciona |
>
> Antes desta revisão, o documento descrevia coisas que nunca foram construídas
> sem dizer isso — e três relatórios de balanceamento foram escritos sem que
> ninguém o lesse. Um documento de design que não distingue intenção de estado
> não é bússola, é ficção. As perguntas abertas ficam no fim, na seção
> **Decisões pendentes**.

---

## A Alma do Jogo

**Frase guia:** "Você não está farmando. Você está jogando xadrez com a morte."

O TOJ é um RPG de masmorra em terminal, hardcore, com combate tático por turnos e
progressão de personagem através de escolhas significativas. O jogador desce andares
numerados de uma masmorra infinita, enfrenta monstros e bosses, e decide a cada passo:
continuar ou garantir seu progresso saindo vivo. O objetivo final é forjar um gladiador
digno da **Arena (PvP)**.

**A Sagrada Trindade:** Velocidade, Inteligência, Caos.

**Referências de feel:**
- Pokémon Ruby (progressão de habilidades por escolha, encontros ao explorar)
- Auto Chess / TFT (recompensas como "cartas", builds diferenciadas)
- Hades (ritmo acelerado, "só mais uma run")
- Minecraft Hardcore (morte = perda total do personagem)

---

## Os Dois Pilares

| Modo | Propósito | Risco | Estado |
|---|---|---|---|
| **Forge Run** | Criar e fortalecer personagens na masmorra | Morte permanente. Perde tudo. | **`[implementado]`** |
| **Arena** | Provar o valor do personagem contra jogadores | Sem risco de morte. Ranking por Elo. | **`[não existe]`** |

**`[não existe]`** O menu principal deveria ter Forge Run e Arena, com a Arena em
branco. Hoje não há nenhuma menção à Arena no menu — nem como opção desabilitada.

> **A consequência disso é maior do que parece.** A Arena é a resposta do jogo à
> pergunta "por que o jogador recomeça depois de morrer". Sem ela, extrair um
> personagem vivo não leva a lugar nenhum: o gladiador salvo não tem onde provar
> valor. Metade do laço do jogo está especificada e não construída.

---

## Exploração

**`[implementado]`** A masmorra é **infinita**. Não existe andar final nem condição
de vitória: `dungeon_level += 1` para sempre. A única forma de uma run terminar bem
é **extrair**.

**`[implementado]`** O jogador caminha por um mapa em grade. Inimigos ocupam posições,
a saída ocupa outra — **combate é opcional**, dá para contornar um inimigo e ir para
a saída.

**`[implementado]`** Evento aleatório a 25% ao entrar no andar: Mercador Errante
(1-3 itens com 10% de desconto), Altar (sacrifica 30% do HP máximo por um buff) ou
Fonte (cura 50% do HP máximo).

**`[implementado]`** Boss a cada 5 andares. Elite a partir do andar 4, com 12% de
chance.

**`[divergiu]`** O documento dizia *"inimigos são encontros isolados (estilo Pokémon)"*.
Hoje há **grupos**: encontros de mais de um monstro a partir do andar 4, e grupos
grandes a partir do andar 10. Foi uma mudança deliberada do rebalanceamento — um
tank protegendo um glass cannon é um problema diferente de qualquer um dos dois
sozinho.

**`[implementado]`** Entre andares: loja, depois a decisão de **Extrair** ou **Continuar**.

---

## Progressão na Forge Run

### Essência (XP)

**`[implementado]`** Cada monstro derrotado fornece Essência, que escala com o andar.
O multiplicador é re-gerado a cada andar e exibido ao jogador.

**`[divergiu]`** O documento especificava **0.5x a 3.0x**, *"puro RNG"*, com a batida
emocional descrita no mapa da jornada (*"Andar 2 — Multiplicador 0.6x. A fartura
acabou."*).

Hoje a faixa é **0.6x a 2.2x**, com desvio menor. A mudança foi feita durante o
rebalanceamento porque a medição mostrou que a Essência dos primeiros andares
explicava **38,7% da variância** da profundidade final — e o objetivo era derrubar
isso para ~12,8%.

> A faixa foi estreitada sem que este documento fosse consultado, o que era um
> conflito com o pilar "Caos". **Resolvido: a faixa estreitada foi ratificada** —
> ver **Decisões pendentes, D1**, que registra a decisão e o porquê.

**`[implementado]`** Passivas influenciam o ganho de Essência: 4 cartas com
`essence_bonus` (+10% a +60%).

**`[não existe]`** A Essência multiplica o XP e **não** multiplica o ouro. O documento
não diz qual dos dois é o certo.

### Subida de Nível

**`[divergiu]`** O documento dizia *"stats base aumentam automaticamente com valores
fixos por classe (ex: Guerreiro +10 HP, +2 Força)"*.

Hoje os atributos são **derivados do nível por uma razão geométrica única**
(`GROWTH_RATE = 1.12`), a mesma que os monstros usam. Valor fixo contra uma base que
cresce foi o defeito estrutural que produziu 99-100% de vitória contra o monstro
comum — está documentado em `BALANCE_REPORT.md`. A mudança é deliberada e não deve
voltar.

**`[não existe]`** *"O jogador recebe pontos de atributo para distribuir livremente."*
Não há pontos de atributo no código. Os atributos são inteiramente derivados do nível
e da classe.

**`[não existe]`** *"A distribuição pode ser resetada pagando 100 de ouro."*
Não existe — e este é o **único ralo de ouro que o documento nomeia**. É a causa
direta de o ouro não ter destino no jogo: o sistema que ia consumi-lo nunca foi
construído. Ver **Decisões pendentes, D2**.

**`[implementado]`** Ao subir de nível, o jogador escolhe **1 entre 3 passivas**
exibidas como cartas.

---

## Passivas Permanentes (O Coração da Build)

**`[implementado]`** 29 passivas, permanentes para a run.

**`[implementado]`** Taxonomia, conforme o campo `category` em `passives.json`:

| Categoria | Quantas | Exemplo |
|---|---:|---|
| **Stats** | 13 | +200 de HP máximo |
| **Recursos** | 7 | +20% de ouro dropado, +60% de Essência |
| **Combate** | 9 | 10% de chance de atordoar, sobreviver a um golpe letal |

**`[implementado]`** Quatro raridades: Comum, Raro, Épico, Lendário.

**`[implementado]`** Acúmulo permitido, sem limite. O sorteio não filtra as passivas
já possuídas.

**`[divergiu]`** O documento dizia *"totalmente aleatório"*. O sorteio é **ponderado
por raridade**: 60 / 28 / 10 / 2. Uma Lendária vale 2 contra 60 de uma Comum.

**`[implementado]` — e é o sistema mais saudável do jogo.** Medido entre quatro
intenções de build (survival, offense, economy, aleatória): **zero cartas com escolha
automática** e **uma única carta fraca de verdade** (`Reflexos Rápidos`). Vinte e duas
são cartas de identidade — alta numa intenção, baixa noutra. É exatamente o que um
sistema de cartas deve produzir.

**`[implementado]`** Se o personagem for extraído vivo, as passivas vão com ele —
para a Arena, quando ela existir.

---

## Habilidades (Ativas em Combate)

**`[bug]`** *"Cada classe começa com 4 habilidades iniciais."* Um personagem recém-criado
tem **zero**. As 4 iniciais são adquiridas uma por nível, do 1 ao 4. Este bug já estava
no roadmap deste documento e continua aberto.

**`[divergiu]`** O documento dizia *"ao atingir certos níveis, aprende novas habilidades
automaticamente conforme a tabela da classe"*. Hoje, ao subir para um nível ímpar a
partir do 5, o jogador **escolhe 1 entre 3 cartas de skill** — o mesmo formato das
passivas.

**`[não existe]`** *"O personagem sempre carrega exatamente 4 habilidades equipadas."*
Não há limite. As skills acumulam sem teto.

**`[implementado]`** Skills consomem MP e têm recarga por skill, definida em
`skills.json`. Os cooldowns batem com a especificação:

| Raridade | Cooldown especificado | Cooldown no JSON |
|---|---|---|
| Common | 1-2 | 1-2 ✓ |
| Rare | 3 | 3 ✓ |
| Epic | 3 | 3 ✓ |
| Legendary | 4-5 | 4-5 ✓ |

**`[implementado]`** A tabela de preços das skills foi reescrita por curva: o dano
cresce com o nível exigido e a mana com o dano, com prêmio para recarga longa. Antes
havia **13 pares dominados** — skills que custavam mais mana e mais recarga para
entregar menos dano que a skill de nível 1 da classe. Hoje são zero.

---

## Combate Tático

**`[implementado]`** O pipeline de dano está especificado em `COMBAT_DESIGN.md` e o
código o segue exatamente. Uma fórmula única para todas as classes; a identidade vem
dos pesos.

**`[implementado]`** Cooldowns, `damage_reduction`, atordoamento (Esmagar a 30%).

**`[divergiu]`** *"Iniciativa dinâmica: a ordem dos turnos muda conforme ações."*
A ordem é calculada **uma vez**, antes do primeiro turno, por agilidade decrescente,
com o herói vencendo empates. Ela não muda durante o combate.

**`[implementado]`** O herói nem sempre começa: um monstro mais ágil age primeiro.

**`[implementado]`** Fuga: o jogador pode tentar escapar do combate. Fugir encerra
o andar.

**`[implementado] — não estava no documento.` Nove arquétipos de monstro**, cada um
com orçamento próprio de atributos, ameaça declarada e counterplay declarado, em
`monsters.json`:

`trash` · `bruiser` · `tank` · `glass_cannon` · `skirmisher` · `controller` ·
`support` · `elite` · `boss`

A regra que fecha o sistema: todo arquétipo precisa de pelo menos uma classe que
sofre contra ele.

**`[implementado] — não estava no documento.`** A IA de monstro tem quatro momentos,
e três deles ignoram a rolagem de chance de usar skill: **execução** (herói abaixo de
35% de vida), **sobrevivência** (monstro ferido com cura na mão), **desespero**
(monstro abaixo de 35% — quem defende se fecha, quem não defende gasta o maior dano)
e **abertura** (primeiro turno de tank, elite, chefe e suporte).

**`[divergiu]`** O documento pedia *"boss com duas fases: ao chegar a 50% de HP muda
seu padrão"*. O que existe é o **desespero a 35%, para todos os arquétipos** — não é
exclusivo do boss e não é a 50%.

**`[implementado] — não estava no documento.`** Regeneração de mana de 2% do máximo
por turno de combate, e o ataque básico entrega 90% do poder base em vez de 100%.
Os dois foram medidos como um par: sem a regeneração, o herói ficava sem mana no
terceiro turno e 36% do dano dele saía do ataque gratuito.

---

## Itens, Loja e Economia

**`[implementado]`** 159 itens, uso livre de consumíveis no turno de combate.

**`[implementado]`** Poções curam **percentual** do máximo (25% / 40% / 60%), não
valor fixo. Armas somam percentual sobre o poder base.

**`[bug]`** **A loja não vende nenhum equipamento a partir do andar 16.** 121 dos 135
itens vendáveis têm `shop_max_floor = 15`; os 14 que sobrevivem são todos consumíveis.
Numa masmorra infinita, isso significa que o comércio acaba e o jogo continua.

**`[bug]`** **O preço cresce linearmente e a renda cresce geometricamente.**
Preço: `base × (1 + andar × 0,05)` — dobra em 20 andares. Renda: razão 1,12 — cresce
8,6× nos mesmos 20 andares. No andar 1 a renda de um andar compra meio item; no
andar 20 compra 8,6.

**`[bug]`** **O loot é uniforme.** `random.choice` sobre os 159 itens: a raridade não
pesa em nada. Uma Lendária é tão provável quanto um Comum — 1,51% por abate, o que
dá 88% de sair pelo menos uma numa run de 20 andares.

**`[bug]`** As 8 Lendárias não são vendidas na loja, mas o campo `price` delas
continua valendo para **venda**: uma Lendária dropada no andar 1 vende por 1.050 a
1.470 de ouro — mais que a renda acumulada dos seis primeiros andares.

**`[não existe]`** Um ralo de ouro. Ver **Decisões pendentes, D2**.

---

## Personagens (Gladiadores)

**`[implementado]`** 10 slots. Um personagem é definido por nome, classe, nível,
inventário, equipamento, passivas e skills.

**`[implementado]`** **Morte na Forge Run:** o save é deletado e um troféu é gravado
com nome, classe, nível, andar alcançado e causa.

**`[não existe]`** O troféu não guarda Elo (não há Arena) nem nada que seja lido na
run seguinte. É um registro de mortos, não uma progressão.

**`[implementado]`** O save grava **HP e MP**, e a extração grava o **próximo**
andar. Antes não gravava nenhum dos dois: o herói era reconstruído no nível salvo com
os recursos no máximo, e a extração gravava o andar recém-concluído, que o jogador
então refazia e cujas recompensas recebia de novo.

> Era a jogada ótima do jogo — cura total gratuita e um moedor infinito de XP e ouro.
> Estratégia degenerada não é um defeito entre outros: ela anula todas as demais
> decisões, porque nenhuma escolha de recurso importa se dá para resetar. Corrigido,
> com regressões em `tests/test_extraction.py`.

---

## Ferramentas (não estavam no documento)

**`[implementado]`** **Camada de simulação headless** em `src/sim/`. Roda o mesmo
`mechanics/battle.py` do jogo real, sem UI, e mede balanceamento por telemetria e
por **ablação** — desliga um sistema e mede quantos andares a run perde.

Duas limitações que importam para qualquer decisão de design tirada dela:
- **Não modela o mapa.** A simulação roda todos os encontros do andar; não sabe pular
  luta. Não consegue medir nada sobre "o jogador escolhe brigar ou contornar".
- **Não modela extração.** A run vai do andar 1 ao 20 ou até morrer. O `max_floor = 20`
  é a janela de medição, **não um teto do jogo**.

**`[implementado]`** CI com 404 testes e 128 invariantes de balanceamento, rodando em
Python 3.10, 3.11 e 3.12.

---

## Tom e Atmosfera

- **Brutal mas viciante.** A morte é sua responsabilidade.
- **Texto econômico.** Sem parágrafos. Sem tutoriais.
- **Humor seco opcional.** Nomes como "Espada da Insistência", "Capacete da Teimosia".

---

## O Que o TOJ Nunca Será

- Um JRPG com história linear.
- **Um roguelite com meta-progressão que salva itens/XP.** O personagem *é* o meta:
  ele sobrevive se for extraído, e some se morrer.
- Um jogo com mapa tático ou escolha de rota visual (estilo Slay the Spire).
- Um jogo onde inimigos se adaptam a ataques repetidos.
- Um jogo com crafting complexo (por enquanto).
- Um jogo com multiplayer na Masmorra.

---

## Decisões pendentes

As perguntas abertas, com o que se sabe de cada uma. Nenhuma tem resposta ainda.

### D1 — A faixa da Essência — **DECIDIDO: fica em 0.6x–2.2x**

O documento pedia 0.5x–3.0x e chamava a sorte de pilar ("Caos"). A medição mostrou
que ela explicava 38,7% da profundidade final; a faixa foi estreitada para 0.6x–2.2x
e o peso da sorte caiu para ~12,8%.

A pergunta era se 38,7% era problema ou era o jogo — "xadrez com a morte" quer que a
habilidade decida, "Caos" quer que o sorteio decida, e os dois estão escritos aqui.

**Decisão: a faixa estreitada fica.** O pilar "Caos" continua valendo, mas se expressa
no que ainda é sorteado — composição do encontro, carta oferecida, drop, evento — e
não numa moeda que decide a run inteira antes do jogador agir. A especificação
original de 0.5x–3.0x está superada por esta decisão.

### D2 — O que consome ouro?

O único ralo especificado (reset de atributos por 100 de ouro) depende de um sistema
de atributos que não existe. Sem ele, o ouro entra na run e não sai.

Três respostas possíveis, e cada uma é um jogo diferente:
- **Tensão dentro da run** — o preço acompanha a renda, o catálogo não acaba, e a
  escolha é poção agora contra arma depois.
- **Recompensa de risco** — o ouro só vira permanente na extração, e aí o troféu
  precisa guardá-lo (o que colide com "sem meta-progressão").
- **Nada** — assume-se, remove-se o ouro, e a loja vira troca por item dropado.

### D3 — Pontos de atributo distribuíveis fazem sentido hoje?

Foram especificados quando os stats subiam por valores fixos por classe. Hoje os
atributos são derivados do nível por uma razão única, e a identidade da classe vem
dos pesos de `CLASS_WEIGHTS`. Um sistema de distribuição livre **compete** com essa
identidade — ou a reforça, se os pontos forem limitados aos atributos que a classe já
usa.

Vale notar que ele não é só um sistema de progressão: é o ralo de ouro do D2.

### D4 — A Arena ainda é o destino?

É a resposta escrita para "por que o jogador recomeça". Se continua valendo, ela é o
maior bloco de trabalho restante e tudo sobre extração deve ser projetado para
alimentá-la. Se não, o jogo precisa de outra resposta para a mesma pergunta — e hoje
não tem nenhuma.

### D5 — Quanto tempo dura uma run?

A run mediana morre no andar 6. **Ninguém sabe quantos minutos isso é, porque ninguém
jogou.** Quinze minutos e três horas são jogos diferentes: mudam o custo de morrer, o
tamanho da build e quanto conteúdo é preciso.

Nenhuma simulação responde isso.

### D6 — Limite de 4 skills equipadas: ainda vale?

Foi especificado junto com "aprende automaticamente". Como hoje o jogador **escolhe**
a skill, um teto de 4 transforma cada escolha em uma troca — o que é mais interessante
e mais próximo do TFT que o documento cita como referência. Mas é uma mecânica nova,
não um conserto.

### D7 — Conteúdo procedural infinito?

Levantado depois deste documento: gerar itens, skills e passivas em vez de listá-los
em JSON, para dar sensação de infinidade numa masmorra infinita.

O que se sabe: gerador desenha de um vocabulário finito, então "item infinito" é
"afixos finitos × combinatória" — o trabalho de design muda de lugar, não some. E há
evidência contrária vinda do próprio jogo: as 29 passivas produzem 22 cartas de
identidade, enquanto os 159 itens produzem 0,28 upgrade por visita à loja no andar 13.
Quantidade não é o eixo.

Gerador é bom em **adjetivo** (números num slot — item) e ruim em **verbo** (ação nova
no combate — skill).

### D8 — O nome do arquivo

`GAME_DESING.md` tem um erro de digitação e é referenciado pelo `README.md` e pelo
`GAME_GUIDE.md`. Renomear é barato; só precisa ser decidido.

---

## Métricas de Sucesso

Uma feature está pronta quando:
1. Um novo jogador entende o que fazer sem instruções externas.
2. A arquitetura não é violada (nenhum `print()` fora de `ui/`, sem imports cruzados).
3. Sessões longas rodam sem crashes.
4. **A afirmação correspondente neste documento foi atualizada.** Três relatórios de
   balanceamento foram escritos sem que este arquivo fosse lido, e uma constante de
   design foi alterada contra a intenção escrita aqui. Documento desatualizado não é
   documentação — é uma armadilha.
