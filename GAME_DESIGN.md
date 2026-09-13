# GAME DESIGN — Tales of the Journey

> O estado **atual** do design. O que ainda está em redesign não é
> descrito aqui como se existisse — hoje isso vale para o sistema de
> equipamento, que está em nova fase de desenho.

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

> **Skills V2.** A regra que organiza tudo abaixo: **a skill define COMO o personagem
> transforma os atributos dele numa ação. O poder vem do personagem, não de um número
> que a carta carrega.** Não existe um segundo sistema de dano ao lado do combate.

### Aquisição

**`[implementado]`** No **nível 1** o personagem recebe **uma** habilidade: a assinatura
da classe, fixa e declarada no JSON (Golpe Poderoso, Bola de Fogo, Ataque Furtivo).
Eram quatro, entregues uma por nível até a quarta — o jogador chegava ao nível 4 com o
deck cheio sem ter escolhido nada, e a primeira decisão do jogo acontecia depois de ele
já estar montado.

**`[implementado]`** A partir daí, **a cada 3 níveis** (3, 6, 9, 12, …) o jogo oferece
**3 cartas e o jogador escolhe 1** — mesmo formato das passivas. Subir de nível não
entrega mais nada de graça.

**`[implementado]`** O deck tem **teto de 4 habilidades ativas**. Ao aprender a quinta,
o jogo mostra a carta nova ao lado das 4 atuais e o jogador **escolhe qual esquecer ou
recusa a nova**. O motor nunca decide por ele.

**`[implementado]`** Regras da oferta:
- carta que já está **ativa nunca aparece** — oferecê-la gastaria um dos três espaços;
- **inéditas têm prioridade**: o jogo lembra o que já mostrou nesta run;
- **repetição só depois** de esgotarem as inéditas elegíveis;
- o pool é **classe + Neutral**. Skill exclusiva continua exclusiva: um Guerreiro nunca
  vê uma carta de Mago.

**`[pendente — conteúdo]`** O pool **Neutral existe no código e está vazio no JSON**:
nenhuma carta declara `skill_class: "Neutral"` ainda. O caminho funciona; falta conteúdo.

**`[pendente — conteúdo]`** Na primeira oferta (nível 3) existem exatamente **3
candidatas** por classe, então o menu mostra tudo o que existe — o que ainda não é
escolher. A partir do nível 6 há mais candidatas que vagas.

### O que uma carta declara

**`[implementado]`** `scaling`: de quais atributos o golpe nasce, **no máximo 2**, com
os **pesos somando 1.0**. `power`: o peso da ação — golpe leve, médio, pesado. Juntos
constroem o BASE, e é só isso que a carta produz:

```
BASE = Σ(atributo_resolvido × peso) × (1 + arma%) × power × (1 + bônus%)
```

Os atributos entram já resolvidos: nível, equipamento, gemas, `+N` e efeitos ativos
chegam sozinhos. Daí em diante quem resolve é **o pipeline global de dano de sempre** —
acerto, crítico, encantamento, defesa e mitigação. A carta não tem funil próprio.

**`[implementado]`** `accuracy_modifier`: quanto a ação ajuda ou atrapalha a mira. Entra
na **mesma conta de acerto** que evasão, medo e o efeito **Precisão** — não existe uma
segunda rolagem. O ataque básico passa 0 e é a régua contra a qual as skills se comparam.

**`[implementado]`** `secondary`: **no máximo um** efeito extra, e sempre do **catálogo
global de efeitos**. A carta escolhe chance, duração e intensidade; o que `poison`
significa é do catálogo. Nenhuma carta redefine um efeito.

**`[implementado]`** `requires`: requisito de equipamento (tipo de peça, número de mãos,
duas armas). Ele **bloqueia o USO, nunca a aquisição** — o jogador pega a carta de escudo
e vai atrás de um escudo. A carta fica no deck, visível, com o que falta escrito na tela.
É o que permite pivotar uma build em vez de só reagir ao que caiu.

**`[implementado]`** **Herói e monstro usam a MESMA `SkillCard` e a mesma gramática.**
Não existe `MonsterSkill` nem um segundo resolvedor: o que muda é a origem da carta e os
atributos de quem a lança.

**`[implementado]`** Todo conteúdo de skill — dos dois lados — passa por um **validador
estático** antes de entrar no jogo: escala válida, no máximo 2 atributos somando 1.0, MP
e recarga obrigatórios, acerto dentro da faixa, efeito do catálogo global, orçamento não
absurdo. O orçamento é medido contra um personagem de referência (a classe, para o herói;
o arquétipo, para o monstro), porque a Agilidade 92 do Ladino e a Força 191 do Guerreiro
não são o mesmo número.

### Custo

**`[implementado]`** Skills consomem MP e têm recarga por skill, definida em
`skills.json`. Os cooldowns batem com a especificação:

| Raridade | Cooldown especificado | Cooldown no JSON |
|---|---|---|
| Common | 1-2 | 1-2 ✓ |
| Rare | 3 | 3 ✓ |
| Epic | 3 | 3 ✓ |
| Legendary | 4-5 | 4-5 ✓ |

**`[implementado]`** A tabela de preços das skills foi reescrita por curva: o dano
cresce com o nível exigido e a mana com o dano. Antes havia **13 pares dominados** —
skills que custavam mais mana e mais recarga para entregar menos dano que a skill de
nível 1 da classe. Hoje são zero.

**`[bug conhecido — balanceamento]`** *"com prêmio para recarga longa"* não é verdade.
Medido em dano por ponto percentual de mana, as skills de recarga longa rendem **~21**
contra **~29** das de recarga curta: trocar frequência por pico custa mais caro por
ponto de dano, e não menos. A regra parecia cumprida porque a medição antiga dividia um
percentual de bônus por uma mana absoluta — duas unidades diferentes. Medido na mesma
unidade sobre os dados anteriores à V2, a razão **já estava invertida**. Está registrado
como falha esperada no teste e é backlog de balanceamento, não de código.

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

## Métricas de Sucesso

Uma feature está pronta quando:
1. Um novo jogador entende o que fazer sem instruções externas.
2. A arquitetura não é violada (nenhum `print()` fora de `ui/`, sem imports cruzados).
3. Sessões longas rodam sem crashes.
4. **A afirmação correspondente neste documento foi atualizada.** Três relatórios de
   balanceamento foram escritos sem que este arquivo fosse lido, e uma constante de
   design foi alterada contra a intenção escrita aqui. Documento desatualizado não é
   documentação — é uma armadilha.

---

## Combate — a matemática

### Filosofia Central

O sistema de combate do ToJ é um **pipeline determinístico de redução de contexto**.
Nenhum sistema gera dano diretamente — todos injetam operadores matemáticos num contexto
de combate imutável que é colapsado em sequência.

Inspirado na arquitetura do Balatro: matemática simples, profundidade emergente via interações.

---

### Fórmula Universal de Dano

$$DAMAGE_{final} = \Big[\big(BASE\_POWER + \sum FLAT\big) \times \prod MULT \times \prod XMULT_{capped}\Big] \times DEFENSE\_MODIFIER$$

Uma única fórmula para todas as classes, skills e situações.
A identidade vem dos **pesos e modificadores**, não de equações separadas.

---

### Geração do Poder Base

$$BASE\_POWER = (W \cdot A) \times (1 + weapon\%)$$

Onde:
- `A` = vetor de atributos **já resolvidos** (nível, equipamento, gemas, `+N`, efeitos)
- `W` = vetor de pesos **da ação**
- `weapon%` = percentual de dano das armas empunhadas

**De onde vêm os pesos.** É aqui que o ataque básico e uma skill se diferenciam, e é a
única diferença entre eles:

| Ação | Pesos | Peso da ação |
|---|---|---|
| Ataque básico | fixos, da **classe** (tabela abaixo) | 1 (é a régua) |
| Skill (V2) | os que a **carta** declara em `scaling`, até 2, somando 1.0 | `power` |

O ataque básico é, literalmente, a skill de pesos fixos: mesma função, mesma conta,
mesma arma. Uma skill de Ladino pode nascer de `0.6 AG + 0.4 ST` e uma de Tanque de
`0.6 ST + 0.4 DF` — a carta escolhe **de onde** o golpe vem, nunca **quanto** ele vale.
Vale igual para monstro: os arquétipos usam a mesma gramática.

### Matriz de Pesos por Classe (ataque básico)

| Classe  | w_ST | w_MG | w_AG |
|---------|------|------|------|
| Warrior | 1.6  | 0.4  | 0.0  |
| Mage    | 0.3  | 1.9  | 0.0  |
| Rogue   | 0.8  | 0.4  | 1.7  |

> **Nota:** Warrior e Mage não usam AG no **ataque básico**.
> AG para essas classes alimenta Speed (ordem de turno) e hit_chance — e pode alimentar
> uma skill, se a carta declarar `ag` no `scaling` dela.

---

### Pipeline de Modificadores

Os sistemas do jogo não geram dano — injetam operadores no pipeline.

### 3.1 Modificadores Aditivos (FLAT e MULT)

Bônus lineares. Acumulam-se de forma previsível.

$$\prod MULT = 1 + \sum \Delta mult$$

**Fontes:** skills comuns, buffs de buff, equipamentos passivos, atributos secundários.

### 3.2 Modificadores Multiplicativos (XMULT)

Multiplicadores puros. Reservados para gatilhos de alto impacto.

$$\prod XMULT_{raw} = \prod_{i=1}^{n} xmult_i$$

**Fontes:** cartas de dungeon, passivas de alto risco, condições críticas de estado.

### 3.3 Teto Obrigatório de XMULT

Para evitar explosão numérica por empilhamento de multiplicadores:

$$\prod XMULT_{capped} = \min\!\Big(\prod XMULT_{raw},\ 5.0\Big)$$

> Exemplo sem teto: Full House (3.0) × Execute (2.0) × Glass Soul (1.8) × Crit (1.5) = **16.2×**
> Com teto de 5.0: resultado máximo é **5.0×** — previsível e balanceável.

---

### Resolução de Crítico

O crítico injeta no produtório de XMULT **antes** do teto ser aplicado.

```
Se rand(0, 100) <= crit_chance:
    XMULT_raw *= crit_damage_multiplier
```

**Limites obrigatórios:**

| Parâmetro          | Valor  |
|--------------------|--------|
| crit_chance máximo | 75%    |
| crit_damage padrão | 1.5×   |

---

### Curva de Mitigação de Defesa

Curva hiperbólica de rendimento decrescente. O dano **nunca** chega a zero.

$$DEFENSE\_MODIFIER = \frac{k}{k + defense_{target}}$$

Onde `k = 100` (constante de calibração).

| defense | Mitigação | Dano recebido |
|---------|-----------|---------------|
| 0       | 0%        | 100%          |
| 30      | 23%       | 77%           |
| 100     | 50%       | 50%           |
| 200     | 67%       | 33%           |
| 300     | 75%       | 25%           |
| 500     | 83%       | 17%           |
| 1000    | 91%       | 9%            |

---

### Injeção por Sistema

### Skills
Skill **não injeta** no pipeline: ela constrói o BASE e para. Era o desenho antigo, e
manter os dois caminhos abertos daria à mesma carta dois jeitos de ficar mais forte —
um deles fora do alcance do validador.

| Skill            | O que ela declara                                             |
|------------------|---------------------------------------------------------------|
| Bola de Fogo     | `scaling: mg 1.0`, `power: 3.49`, custo em % da mana máxima    |
| Assassinato      | `scaling: ag 0.6 + st 0.4`, `power: 5.59`, `bonus_condition`   |

A condição situacional (`bonus_condition` + `bonus_percent`) multiplica o BASE **antes**
do funil, e não depois — ela é parte da construção do golpe, não um XMULT escondido.

### Equipamentos
| Item          | Injeção                                              |
|---------------|------------------------------------------------------|
| Sword         | `FLAT += 25`                                         |
| Ancient Staff | `ΔMULT += 0.20`                                      |
| Cursed Dagger | `crit_chance += 15`, trigger: `hp_drain = 5/turno`   |

### Cartas de Dungeon
| Carta        | Injeção                                                       |
|--------------|---------------------------------------------------------------|
| 7 of Blades  | `ΔMULT += 0.25`                                               |
| Full House   | `XMULT *= 3.0`, `healing_modifier *= 0.5`                     |
| Ace of Death | `damage_incoming *= 1.5`, `crit_chance += 20`                 |

#### Apenas exemplo, cartas não foi introduzida ainda.

### Passivas
| Passiva      | Injeção                                                       |
|--------------|---------------------------------------------------------------|
| Battle Focus | `ΔMULT += 0.05 × stack_combo`                                 |
| Glass Soul   | `XMULT *= 1.8`, `DEFENSE_MODIFIER *= 0.7`                     |

---

### Economia de Recursos (Condição de Contorno)

A jogada só é executada se o custo for viável:

$$Cost_{vector} = \begin{bmatrix} \Delta HP \\ \Delta MP \\ \Delta Essence \\ \Delta Corruption \end{bmatrix}$$

Se qualquer componente do vetor exceder o recurso disponível, a ação é bloqueada pelo sistema — independente do DAMAGE_final calculado.

---

### Constantes de Calibração

| Constante           | Valor | Descrição                            |
|---------------------|-------|--------------------------------------|
| `DEFENSE_K`         | 100   | Curva de mitigação                   |
| `XMULT_CAP`         | 5.0   | Teto de multiplicadores puros        |
| `CRIT_CHANCE_CAP`   | 75    | % máximo de chance crítica           |
| `CRIT_DAMAGE_BASE`  | 1.5   | Multiplicador padrão de crítico      |

> Estas constantes residem em `src/shared/constants.py` e são os únicos valores
> a serem ajustados durante o balanceamento. Nunca hardcode esses valores inline.

---

## Apêndice — como adicionar passivas

### Contexto

Este guia serve para gerar dezenas/centenas de novas passivas para o catálogo `src/data/passives.json` do jogo TOJ (Tales of the Journey).

---

### Estrutura do Arquivo

O arquivo `src/data/passives.json` tem esta estrutura:

```json
{
  "description": "...",
  "version": "1.0",
  "rarity_weights": { "Common": 60, "Rare": 28, "Epic": 10, "Legendary": 2 },
  "passives": [
    { ... cada passiva é um objeto ... }
  ]
}
```

Cada passiva dentro do array `"passives"` deve ter **exatamente** estes 7 campos:

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | string | Identificador único, snake_case, sem acentos | `"coracao_ferro"` |
| `name` | string | Nome exibido, pode ter acentos | `"Coração de Ferro"` |
| `category` | string | Uma das 3 categorias: `Stats`, `Recursos`, `Combate` | `"Stats"` |
| `rarity` | string | Uma das 4: `Common`, `Rare`, `Epic`, `Legendary` | `"Common"` |
| `description` | string | Texto curto exibido na carta | `"+15 HP máximo"` |
| `effect_type` | string | Identificador do efeito (ver tabela abaixo) | `"max_hp"` |
| `effect_value` | number | Valor numérico (inteiro ou float) | `15` |

---

### Effect Types Válidos

### Stats (alteram atributos base do jogador)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `max_hp` | Aumenta HP máximo | Common: 10-30, Rare: 30-60, Epic: 60-120, Legendary: 120-250 |
| `max_mp` | Aumenta MP máximo | Common: 8-20, Rare: 20-40, Epic: 40-80, Legendary: 80-150 |
| `strength` | Aumenta força base | Common: 2-5, Rare: 6-12, Epic: 12-20, Legendary: 20-40 |
| `defense` | Aumenta defesa base | Common: 2-5, Rare: 5-10, Epic: 10-20, Legendary: 20-35 |
| `agility` | Aumenta agilidade base (cap: 95) | Common: 1-3, Rare: 3-6, Epic: 6-12, Legendary: 12-20 |

### Recursos (afetam economia e ganhos)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `essence_bonus` | Bônus % no multiplicador de essência | Common: 5-15, Rare: 15-25, Epic: 25-45, Legendary: 45-70 |
| `gold_drop_bonus` | Bônus % em ouro dropado | Common: 5-15, Rare: 15-30, Epic: 30-50, Legendary: 40-60 |
| `potion_heal_bonus` | Bônus % na cura de poções | Common: 5-12, Rare: 12-20, Epic: 20-35, Legendary: 30-50 |

### Combate (afetam mecânicas de luta)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `crit_chance` | Chance % de ataque crítico | Common: 3-8, Rare: 8-15, Epic: 15-25, Legendary: 25-40 |
| `dodge_chance` | Chance % de esquiva | Common: 3-6, Rare: 6-12, Epic: 10-18, Legendary: 15-25 |
| `damage_reduction` | % de redução de dano recebido | Common: 2-5, Rare: 5-10, Epic: 10-18, Legendary: 15-25 |
| `stun_chance` | Chance % de atordoar | Common: 3-6, Rare: 6-10, Epic: 10-15, Legendary: 12-20 |
| `death_ignore` | Quantas mortes ignorar (inteiro, não %) | Epic: 1, Legendary: 1-2 |

---

### Regras Críticas

1. **IDs devem ser únicos** — nunca repetir um `id` existente no arquivo
2. **IDs sem acentos** — usar `coracao` em vez de `coração`, `lamina` em vez de `lâmina`
3. **IDs em snake_case** — `nome_da_passiva`, sem camelCase ou kebab-case
4. **Nomes com acentos são ok** — `"Coração de Ferro"` está correto no campo `name`
5. **`effect_value` deve ser número** — `15`, não `"15"`
6. **Categorias fixas** — exatamente `"Stats"`, `"Recursos"` ou `"Combate"`
7. **Raridades fixas** — exatamente `"Common"`, `"Rare"`, `"Epic"` ou `"Legendary"`
8. **Escalabilidade por raridade** — valores de Legendary devem ser significativamente maiores que Common
9. **Descriptions concisas** — máximo ~40 caracteres, formato: `"+X Y"` ou `"descrição curta"`
10. **JSON válido** — aspas duplas em tudo, vírgulas entre objetos, sem trailing comma no último elemento

---

### Template para Gerar em Massa

```json
{
  "id": "nome_unico_snake_case",
  "name": "Nome da Passiva",
  "category": "Stats",
  "rarity": "Common",
  "description": "+15 HP máximo",
  "effect_type": "max_hp",
  "effect_value": 15
}
```

---

### Onde os Dados São Usados

| Arquivo | Uso |
|---|---|
| `src/content/passives.py` | Carrega o JSON, cria `PassiveCard` dataclasses, gera escolhas ponderadas |
| `src/entities/heroes.py` | Aplica stats (`max_hp`, `max_mp`, `strength`, `defense`, `agility`) ao escolher passiva |
| `src/mechanics/combat.py` | Usa `crit_chance` e `dodge_chance` em cálculos de combate |
| `src/storage/save_manager.py` | Salva/carrega apenas os IDs das passivas |

---

### Notas sobre Integração

- **Stats** (`max_hp`, `max_mp`, `strength`, `defense`, `agility`) são aplicados **imediatamente** ao escolher a passiva, sem chamar `rest()`.
- **Combate** (`crit_chance`, `dodge_chance`) é lido pelo `combat.py` via `player.get_passive_bonus()`.
- **Recursos** (`essence_bonus`, `gold_drop_bonus`, `potion_heal_bonus`) e **Combate avançado** (`damage_reduction`, `stun_chance`, `death_ignore`) ainda não têm integração ativa no motor — ficarão para tarefas futuras.
- Novos `effect_type` podem ser adicionados, mas requerem código em `_apply_passive_stats()` (heroes.py) e/ou `combat.py`.

---

### Checklist Pós-Criação

- [ ] Todos os IDs são únicos (sem duplicatas)
- [ ] JSON válido (validar com `python3 -c "import json; json.load(open('src/data/passives.json'))"`)
- [ ] Nenhuma passiva tem `effect_value` como string
- [ ] Distribuição por raridade está balanceada
- [ ] Ruff check passa: `python3 -m ruff check src/content/passives.py`
