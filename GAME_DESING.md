# GAME DESIGN — Tales of the Journey (vFinal)
> A bússola criativa. O resto é código, suor e tokens.

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

| Modo          | Propósito                                      | Risco                                   |
|---------------|------------------------------------------------|-----------------------------------------|
| **Forge Run** | Criar e fortalecer personagens na masmorra     | Morte permanente. Perde tudo.           |
| **Arena**     | Provar o valor do personagem contra jogadores  | Sem risco de morte. Ranking por Elo.    |

O menu principal tem duas opções: **Forge Run** e **Arena**.
A Arena começa como opção em branco (será implementada no futuro).

---

## Progressão na Forge Run

### Ganho de Nível (Essência)
- Cada monstro derrotado fornece **Essência** (XP), que escala com o andar.
- **O Multiplicador de Essência é re-gerado a cada novo andar da masmorra.**
  O valor é exibido claramente para o jogador (ex: "Andar 5 — Multiplicador 2.1x").
- O multiplicador varia de 0.5x (escassez severa) a 3.0x (fartura lendária),
  com valores intermediários tendendo à normalidade. É puro RNG, e o jogador
  precisa adaptar sua estratégia de exploração a cada andar.
- Itens e passivas podem influenciar o ganho de Essência (ex: "+10% de Essência ganha").

### Subida de Nível
Ao acumular Essência suficiente:
1. **Stats base** aumentam automaticamente com valores fixos por classe
   (ex: Guerreiro +10 HP, +2 Força, +1 Agilidade por nível).
2. O jogador recebe **pontos de atributo** para distribuir livremente (Força,
   Agilidade, Inteligência, etc.). A distribuição pode ser resetada a qualquer
   momento fora de combate, pagando 100 de ouro.
3. O jogador escolhe **1 entre 3 Passivas Permanentes** exibidas em formato
   de cartas.

---

## Passivas Permanentes (O Coração da Build)

As passivas são o principal diferenciador de cada personagem. Elas são permanentes
para a run e, se o personagem for extraído com sucesso, vão com ele para a Arena.

### Taxonomia
- **[Stats]:** Atributos e recursos. Ex: "+15 HP", "+10 MP", "+5% Resistência a Fogo".
- **[Recursos]:** Modificadores de ganho/perda. Ex: "Inimigos dropam 20% mais ouro",
  "Poções curam 15% a mais", "+10% de Essência ganha".
- **[Combate]:** Regras que afetam mecânicas de luta. Ex: "Ataques corpo a corpo têm
  10% de chance de atordoar", "Ganhe 20% de velocidade por 1 turno ao sofrer crítico".

### Regras
- **Raridade:** Comum, Raro, Épico, Lendário. Define o poder e a frequência.
- **Acúmulo:** Permitido. O jogador decide se acumular a mesma passiva é inteligente
  ou desperdício.
- **Apresentação:** Cada carta mostra nome, efeito curto, tag de categoria e cor
  da raridade. Sempre 3 opções por nível. Totalmente aleatório.
- **Limite:** Sem limite máximo de passivas acumuladas.

---

## Habilidades (Ativas em Combate)

- Cada classe começa com **4 habilidades iniciais**.
- Ao atingir certos níveis (ex: 10, 20), o personagem aprende novas habilidades
  automaticamente conforme a tabela da classe.
- O personagem sempre carrega **exatamente 4 habilidades equipadas** por vez.
- Em combate, as habilidades consomem recursos (MP, cooldowns).

---

## Combate Tático (MiniXadrez)

### Recursos Gerenciados a Cada Turno
- **Cooldowns:** Habilidades têm tempo de recarga em turnos. Sem spam.
- **Iniciativa dinâmica:** A ordem dos turnos muda conforme ações (velocidade,
  atordoamento, surpresa). O herói NEM SEMPRE começa atacando.

### Comportamento Inimigo
- Inimigos são encontros isolados (estilo Pokémon).
- Cada espécie de monstro tem seu próprio padrão de ataque e stats base,
  escalados pelo nível do inimigo (definido pelo EnemyScaler).

### Itens em Combate
- Uso livre de itens no turno (gasta a ação).
- Variedade de itens com efeitos diversos.

---

## Exploração

- A masmorra é dividida em **andares numerados**, sempre visíveis ao jogador.
- Ao entrar em um andar, o multiplicador de Essência daquele andar é exibido.
- O jogador caminha pelo andar e encontra salas aleatoriamente:
  - **Combate:** encontro com 1 ou mais monstros.
  - **Evento Aleatório:** Mercador Errante, Altar de Sacrifício, Fonte de Cura,
    Armadilha (a implementar).
  - **Boss:** a cada N andares, uma luta mais difícil com recompensa especial.
- Entre um andar e outro, o jogador pode optar por **sair da masmorra** e salvar
  o personagem para a Arena.

---

## Personagens (Gladiadores)

- **10 slots** para personagens salvos.
- Um personagem é definido por: nome, classe, nível, andar mais profundo alcançado,
  Elo (ranking da Arena), habilidades equipadas, passivas acumuladas e itens.
- **Morte na Forge Run:** Personagem é DELETADO de tudo (inclusive da Arena).
- **Criação:** Livre se houver slot vazio. Com 10 slots cheios, é necessário
  deletar um gladiador existente para liberar espaço.

---

## Arena (Futuro)

- Modo PvP puro.
- Cada personagem tem seu próprio **Elo** individual.
- Tiers de Elo (provisórios): Madeira, Pedra, Ferro, Bronze, Prata, Ouro, Platina,
  Esmeralda, Rubi, Diamante, Obsidian, Mestre, Grão-Mestre, Absoluto.
- Matchmaking por tiers.
- Personagem não morre na Arena; apenas ganha/perde pontos.

---

## Tom e Atmosfera

- **Brutal mas viciante.** A morte é sua responsabilidade.
- **Texto econômico.** Sem parágrafos. Sem tutoriais.
- **Humor seco opcional.** Nomes como "Espada da Insistência", "Capacete da Teimosia".
  E, claro, a certeza de que alguém vai culpar o RNG pela própria ruína. O jogo
  não se desculpa.

---

## O Que o TOJ Nunca Será

- Um JRPG com história linear.
- Um roguelite com meta-progressão que salva itens/XP.
- Um jogo com mapa tático ou escolha de rota visual (estilo Slay the Spire).
- Um jogo onde inimigos se adaptam a ataques repetidos.
- Um jogo com crafting complexo (por enquanto).
- Um jogo com multiplayer na Masmorra.

---

## Métricas de Sucesso

Uma feature está pronta quando:
1. O bot BFS completa um run sem crash.
2. Um novo jogador entende o que fazer sem instruções externas.
3. A arquitetura não é violada (nenhum print() fora de ui/, sem imports cruzados).

---

## A Experiência do Jogador (Mapa da Jornada)

> Este é o percurso emocional e mecânico de uma Forge Run ideal, do menu à glória ou ruína.

**1. Menu Principal.** Duas opções: Forge Run e Arena. Arena está em branco. O jogador
   escolhe Forge Run.

**2. Seleção de Gladiador.** Uma lista de slots (até 10). O jogador escolhe um slot vazio
   e cria um novo personagem: nome, classe (Guerreiro, Mago, Ladino). Se todos os slots
   estiverem cheios, deve deletar um gladiador existente — uma decisão com peso emocional
   desde o primeiro instante.

**3. O Início da Run.** A masmorra se materializa. O jogo exibe: **"Andar 1 —
   Multiplicador 1.7x"**. O jogador sente um frio na espinha ou um sorriso, dependendo
   do número. Ele avança.

**4. Primeiro Combate.** Um monstro aparece. O combate começa, mas o herói NÃO age
   primeiro — a iniciativa é do inimigo. O jogador já sente o peso do sistema tático.
   Ele usa "Ataque Normal". O monstro revida. Ele usa uma de suas 4 habilidades,
   gasta MP, o cooldown começa a contar. O monstro cai. Essência recebida (multiplicada
   por 1.7x). Ouro discreto no inventário. Drop: uma poção comum.

**5. Subindo de Nível.** Após alguns combates, o personagem acumula Essência suficiente.
   A tela brilha. Stats sobem automaticamente. Pontos de atributo são concedidos.
   Então, a janela aparece: três cartas.

   - Carta 1: **[Stats] Comum — +15 HP máximo.**
   - Carta 2: **[Recursos] Raro — Inimigos dropam 20% mais ouro.**
   - Carta 3: **[Combate] Épico — Seus ataques corpo a corpo têm 10% de chance de atordoar.**

   O jogador analisa sua build atual. Está frágil, precisa de HP. Mas a carta Épica
   pode definir sua run. Ele escolhe a Carta 3. A passiva é gravada no personagem.
   Para sempre. Levará isso para a Arena, se sobreviver.

**6. Evento Aleatório.** Algumas salas depois, ele encontra um Altar de Sacrifício.
   "Ofereça 30% da sua vida máxima para ganhar +15% de Multiplicador de Essência
   permanentemente nesta run." O jogador hesita. Está com vida cheia, mas sabe que
   o próximo andar tem um Boss. Decide arriscar. Sente o Caos agindo.

**7. O Boss do Andar.** A cada N andares, uma sala de Boss. O chefe tem duas fases:
   ao chegar a 50% de HP, muda seu padrão de ataque e fica mais agressivo. O jogador
   usa sua passiva de atordoamento para controlar o ritmo. O Boss cai. Loot lendário:
   uma arma que ele não pode usar (é para outra classe), mas que pode ser vendida
   por muito ouro.

**8. Novo Andar, Novo Multiplicador.** O jogador desce para o Andar 2. O jogo gera um
   novo multiplicador: **"Andar 2 — Multiplicador 0.6x"**. A fartura acabou. A Essência
   está escassa. Ele percebe que precisa jogar com mais cautela — os inimigos estão
   ficando mais fortes, mas seu ganho de níveis será mais lento.

**9. A Grande Decisão.** Após derrotar o Boss do Andar 5, o jogador está no Nível 8,
   com 4 passivas acumuladas, 2 delas raras. Ele abre o menu e vê a opção: "Sair da
   Masmorra". Se sair agora, este personagem estará salvo, pronto para a Arena com
   suas passivas e itens. Se continuar, pode ficar ainda mais forte, mas arrisca
   perder tudo. Ele pensa no multiplicador atual e nos andares que virão. Decide
   continuar. A ganância fala mais alto.

**10. A Morte.** Três andares depois, um grupo de inimigos com sinergia de veneno o pega
    desprevenido. Ele usa todas as poções, gerencia cooldowns, mas a iniciativa dos
    inimigos é implacável. O personagem cai no **Andar 8**. Tela escura. Surge o Troféu
    de Fracasso: nome do herói, classe, nível máximo, andar mais profundo alcançado,
    passivas coletadas, inimigos derrotados, dano total causado. O jogo compara com o
    recorde anterior e destaca: "Novo recorde de profundidade!" O jogador sente a
    frustração da perda, mas um sorriso escapa. O botão "Nova Run" pulsa. Ele aperta.
    O ciclo recomeça. Em algum lugar, uma futura audiência da Twitch digita "RNG
    injusto!". O jogo permanece em silêncio.