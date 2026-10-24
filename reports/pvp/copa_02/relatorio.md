# Copa Arena 02 — 64 gladiadores

Campeonato técnico da Arena PvP, gerado por `tools/arena_copa_02.py`. Experimento de diagnóstico do duelo sob uma política fixa.

> Os nomes são apenas identificadores de personagens simulados, tirados de canais da Twitch. Não existe participação, autorização ou endosso dessas pessoas. Classe, build, força e posição na chave foram atribuídas por sorteio e não têm relação com a pessoa real nem com o desempenho dela.
>
> Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por confronto. Ela aponta casos para investigar; não prova balanceamento entre classes.

## Resumo

- **Campeão: aspaszin (G43)**, Mago nível 23, OP 29.52, build *Prisma do arauto* (vulnerabilidade e dano).
- Vice: SkipNhO (G18), Guerreiro nível 22, OP 28.71, build *Fortaleza*.
- 64 participantes (22 Guerreiros, 21 Magos, 21 Ladinos); OP médio 25.17 (mínimo 20.07, máximo 29.52).
- 63 partidas, 597 rodadas, 702 golpes (575 conectados), 99 críticos.
- O favorito (OP maior) venceu 52 das 63 partidas; houve 11 zebras.
- As 63 partidas rodaram duas vezes, sem e com auditoria, e coincidiram em todas as verificações (tabela de auditoria resumida).

Arquivos desta Copa: [`final_detalhada.md`](final_detalhada.md) (auditoria integral da final), [`final_trace.json`](final_trace.json), [`dashboard.html`](dashboard.html), [`relatorio_visual.pdf`](relatorio_visual.pdf) e [`calibracao.json`](calibracao.json).

## Como a Copa foi montada

- **Builds legais.** Classe e nível por `make_hero`; deck de até 4 cartas da oferta da classe (classe + Neutral), cada carta além da inicial com uma oferta própria (níveis 3, 6, 9, …) de nível ≥ `level_required`, e requisito de equipamento atendido; `nível − 1` passivas, sem Lendária, no máximo uma Épica e duas cópias por Rara; equipamento do `expected loadout` do nível, com trocas só por peças que caem de loot, servem à classe e à posição e não superam em dano+defesa a melhor peça da mesma categoria do loadout.
- **Poder.** `overall_power` canônico, sem cache, medido de novo nesta execução.
- **Calibração.** Só o nível muda; no máximo 4 medições por participante, a partir de um palpite por classe e faixa (tabela abaixo).
- **Chave.** Seed principal `20261024`; `random.Random(seed).shuffle` dos 64 IDs, pares em ordem, sem cabeças de chave. Seed de cada partida: os 8 primeiros bytes (big-endian) de `sha256(f"{seed}:{fase}:{índice}")`, o mesmo esquema da Copa 01.
- **Nomes.** Sorteados para os IDs com uma seed derivada própria (`sha256(f"{seed}:nomes")`), independente das builds e da chave.
- **Política.** `PoliticaCopa` da Copa 01, igual para os 64: cura com HP ≤ 50%; senão buff ou redução ainda não ativos; senão status que o adversário não carrega; senão a primeira skill de dano legal; senão ataque básico. Lê só a `DuelView` e o próprio deck.
- **Partida.** Preparação nova a cada duelo (HP e MP cheios, sem recarga nem efeito). Limite técnico do laço: 500 rodadas (inconclusivo, nunca empate); não foi atingido.
- **Isolamento.** Bonecos só em memória; nenhum save, slot ou coleção de gladiadores.
- **Fora do catálogo desta Copa.** A carta `fantasma` (status `invisible` com alvo próprio): `apply_skill` aplica todo status no adversário, então ela tornaria o RIVAL invisível. É uma peculiaridade do motor, também no PvE, registrada aqui e não corrigida: `src/` não muda nesta Copa.

## Calibração

| ID | Gladiador | Build | Classe | Faixa pedida | Nível | OP medido | Faixa medida | Tentativas (nível→OP) |
|---|---|---|---|---|---|---|---|---|
| G01 | fnxLNTC | Muralha de maça | Guerreiro | 1 | 16 | 21.34 | 1 | L16→21.34 |
| G02 | yeTz | Açougueiro | Guerreiro | 1 | 13 | 20.53 | 1 | L16→25.26; L13→20.53 |
| G03 | suetam1v4 | Duelista | Guerreiro | 1 | 16 | 22.38 | 1 | L16→22.38 |
| G04 | DavyJones | Berserker | Guerreiro | 1 | 16 | 21.68 | 1 | L16→21.68 |
| G05 | calango | Carcereiro | Guerreiro | 1 | 16 | 21.34 | 1 | L16→21.34 |
| G06 | YoDa | Escudeiro de forja | Guerreiro | 1 | 16 | 22.49 | 1 | L16→22.49 |
| G07 | Neskwga | Regenerador | Guerreiro | 2 | 18 | 24.57 | 2 | L18→24.57 |
| G08 | liminhag0d | Ariete | Guerreiro | 2 | 18 | 24.10 | 2 | L18→24.10 |
| G09 | jovirone | Muralha pesada | Guerreiro | 2 | 18 | 23.18 | 2 | L18→23.18 |
| G10 | Gaules | Lenhador | Guerreiro | 2 | 18 | 24.68 | 2 | L18→24.68 |
| G11 | fer | Rompe-guarda | Guerreiro | 2 | 18 | 24.10 | 2 | L18→24.10 |
| G12 | gafallen | Fúria | Guerreiro | 3 | 20 | 25.95 | 3 | L20→25.95 |
| G13 | gabepeixe | Colhedor | Guerreiro | 4 | 19 | 29.52 | 4 | L22→36.09; L19→29.52 |
| G14 | blackoutz | Veterano | Guerreiro | 3 | 20 | 27.10 | 3 | L20→27.10 |
| G15 | aXtLOL | Bigorna | Guerreiro | 3 | 20 | 25.72 | 3 | L20→25.72 |
| G16 | brino | Sentinela de ferro | Guerreiro | 3 | 20 | 25.26 | 3 | L20→25.26 |
| G17 | TheBurntPeanut | Machado pesado | Guerreiro | 3 | 18 | 26.29 | 3 | L20→30.33; L17 ilegal; L18→26.29 |
| G18 | SkipNhO | Fortaleza | Guerreiro | 4 | 22 | 28.71 | 4 | L22→28.71 |
| G19 | MeikodRJ | Imortal | Guerreiro | 4 | 22 | 28.37 | 4 | L22→28.37 |
| G20 | LuquEt4 | Condenado | Guerreiro | 4 | 22 | 28.48 | 4 | L22→28.48 |
| G21 | k13tv | Postura impecável | Guerreiro | 3 | 20 | 26.75 | 3 | L20→26.75 |
| G22 | tteuw | Pacto de ferro | Guerreiro | 4 | 22 | 28.71 | 4 | L22→28.71 |
| G23 | hastad | Piromante | Mago | 1 | 14 | 20.07 | 1 | L16→23.07; L14→20.07 |
| G24 | Tealzlol | Geomante | Mago | 1 | 15 | 21.80 | 1 | L16→22.84; L15→21.80 |
| G25 | xandfps | Criomante | Mago | 1 | 16 | 21.57 | 1 | L16→21.57 |
| G26 | lubatv | Curandeira | Mago | 1 | 16 | 22.38 | 1 | L16→22.38 |
| G27 | mount | Sonhador | Mago | 1 | 16 | 21.92 | 1 | L16→21.92 |
| G28 | G0ularte | Arcanista crítico | Mago | 2 | 18 | 24.10 | 2 | L18→24.10 |
| G29 | PlayHard | Égide rúnica | Mago | 2 | 18 | 23.07 | 2 | L18→23.07 |
| G30 | JonVlogs | Tempestuoso | Mago | 2 | 18 | 24.45 | 2 | L18→24.45 |
| G31 | jukes | Prisma | Mago | 2 | 18 | 24.68 | 2 | L18→24.68 |
| G32 | Baiano | Grilhões | Mago | 2 | 18 | 23.99 | 2 | L18→23.99 |
| G33 | Coringa | Dreno | Mago | 2 | 18 | 24.68 | 2 | L18→24.68 |
| G34 | XANDAOOGOD | Ressurgente | Mago | 3 | 19 | 26.64 | 3 | L20→27.79; L19→26.64 |
| G35 | casimito | Hora parada | Mago | 3 | 20 | 25.83 | 3 | L20→25.83 |
| G36 | alanzoka | Pacto do vazio | Mago | 3 | 20 | 25.60 | 3 | L20→25.60 |
| G37 | yayahuz | Escudo e fogo | Mago | 3 | 21 | 25.49 | 3 | L20→24.57; L21→25.49 |
| G38 | NOBRU | Coveiro arcano | Mago | 3 | 20 | 26.99 | 3 | L20→26.99 |
| G39 | babi | Apocalipse | Mago | 4 | 23 | 28.71 | 4 | L23→28.71 |
| G40 | frttt | Dividendo | Mago | 4 | 24 | 28.14 | 4 | L23→27.22; L24→28.14 |
| G41 | Forever | Mestre do gelo | Mago | 4 | 23 | 29.29 | 4 | L23→29.29 |
| G42 | Dilera | Sanguessuga | Mago | 4 | 20 | 29.17 | 4 | L23→32.40; L20→29.17 |
| G43 | aspaszin | Prisma do arauto | Mago | 4 | 23 | 29.52 | 4 | L23→29.52 |
| G44 | brtt | Assassino de adaga | Ladino | 1 | 14 | 21.11 | 1 | L15→22.61; L14→21.11 |
| G45 | Bisteconee | Arqueiro | Ladino | 1 | 15 | 21.22 | 1 | L15→21.22 |
| G46 | Bagi | Envenenador | Ladino | 1 | 14 | 22.03 | 1 | L15→22.95; L14→22.03 |
| G47 | boltz | Esquivo | Ladino | 1 | 15 | 21.92 | 1 | L15→21.92 |
| G48 | sofiaespanha | Trapaceiro | Ladino | 1 | 15 | 20.53 | 1 | L15→20.53 |
| G49 | belrodrigues | Sangrador | Ladino | 2 | 16 | 24.57 | 2 | L17→26.87; L14→21.34; L16→24.57 |
| G50 | Smzinho | Duas lâminas | Ladino | 2 | 17 | 24.57 | 2 | L17→24.57 |
| G51 | RazaH | Caçador | Ladino | 2 | 17 | 23.99 | 2 | L17→23.99 |
| G52 | Tenz | Ladrão de mana | Ladino | 2 | 17 | 24.91 | 2 | L17→24.91 |
| G53 | PaulinhoLOKObr | Couro endurecido | Ladino | 2 | 17 | 23.41 | 2 | L17→23.41 |
| G54 | dona | Lobo | Ladino | 3 | 16 | 25.60 | 3 | L19→28.71; L17→28.02; L16→25.60 |
| G55 | Felps | Dançarino | Ladino | 3 | 19 | 27.10 | 3 | L19→27.10 |
| G56 | RNakano | Silêncio | Ladino | 3 | 20 | 25.60 | 3 | L19→24.91; L20→25.60 |
| G57 | sacy | Testamento | Ladino | 3 | 18 | 27.45 | 3 | L19→27.79; L18→27.45 |
| G58 | bakzera | Gancho | Ladino | 3 | 20 | 25.95 | 3 | L19→24.91; L20→25.95 |
| G59 | tioorochitwitch | Morte súbita | Ladino | 4 | 21 | 28.48 | 4 | L21→28.48 |
| G60 | Patriota | Cobrador | Ladino | 4 | 19 | 28.14 | 4 | L21→31.02; L19→28.14 |
| G61 | loud_thurzin | Evasão perfeita | Ladino | 4 | 21 | 28.60 | 4 | L21→28.60 |
| G62 | coldzin | Chuva de ferrões | Ladino | 4 | 21 | 29.52 | 4 | L21→29.52 |
| G63 | furq | Arauto | Ladino | 4 | 23 | 28.48 | 4 | L21→26.29; L23→28.48 |
| G64 | Hayashii | Sombra mortal | Ladino | 4 | 22 | 28.25 | 4 | L21→27.33; L22→28.25 |

Por faixa medida: {1: 16, 2: 16, 3: 16, 4: 16}. Nenhum fora da faixa pedida.

Faixas inviáveis registradas na calibração:

- **Colhedor**: faixa 3 → 4. O nível legal mais baixo é 18 (Colheita de Ferro pede oferta no 15, Juramento da Muralha e Mão Dupla pedem ofertas no 12 ou acima), e ali a build já mede OP 27,56, acima do teto da faixa 3 (27,5).
- **Postura impecável**: faixa 4 → 3. Movida para a faixa 3 para manter 16 por faixa; nenhuma carta dela trava o nível.

## Participantes

| ID | Gladiador | Grupo | Classe | Nível | OP | HP | MP | ST | MG | AG | DF | Build | Skills | Passivas | Equipamento |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G13 | gabepeixe | A | Guerreiro | 19 | 29.52 | 3509 | 567 | 377 | 231 | 77 | 322 | Colhedor: duas armas: sangramento pesado | Golpe Poderoso, Colheita de Ferro, Juramento da Muralha, Mão Dupla | Agulha no Osso ×2, Fio Serrilhado ×6, Sangue de Guerreiro ×5, Ódio Baixo ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Lâmina da Tempestade; Weapon2: Espada Lendária; Body: Armadura de Espinhos; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G43 | aspaszin | C | Mago | 23 | 29.52 | 4477 | 1694 | 395 | 666 | 97 | 412 | Prisma do arauto: vulnerabilidade e dano | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | Lâmina Afiada ×2, Oráculo Partido, Sangue de Vidente ×7, Olho de Águia ×6, Pulso Certeiro ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G62 | coldzin | D | Ladino | 21 | 29.52 | 3029 | 868 | 504 | 309 | 251 | 322 | Chuva de ferrões: arco: crítico e sangramento | Chuva de Ferrões, Olho do Falcão, Marca do Caçador, Flecha pela Fresta | Instinto Frio ×2, Lâmina do Juízo, Olho de Caçador ×6, Olho de Águia ×6, Pulso Certeiro ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G41 | Forever | B | Mago | 23 | 29.29 | 4477 | 1804 | 395 | 647 | 97 | 412 | Mestre do gelo: congelar e quebrar | Grilhões de Gelo, Raio Congelante, Lasca de Gelo, Tempestade | Instinto Frio ×2, Poço Fundo, Mente Serena ×7, Sangue de Vidente ×6, Olho de Caçador ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G42 | Dilera | C | Mago | 20 | 29.17 | 3262 | 1206 | 281 | 448 | 69 | 293 | Sanguessuga: roubo de vida e cura | Sanguessuga Arcana, Drenar Vida, Ressurgir, Bola de Fogo | Sede Silenciosa ×2, Voracidade, Boca de Sangue ×6, Coração de Ferro ×5, Respiração Contada ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G18 | SkipNhO | B | Guerreiro | 22 | 28.71 | 5004 | 648 | 576 | 324 | 108 | 505 | Fortaleza: carta lendária e guarda dupla | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | Escudo da Fé ×2, Alma Eterna, Sangue de Guerreiro ×6, Pele Grossa ×6, Postura Fechada ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G22 | tteuw | D | Guerreiro | 22 | 28.71 | 4844 | 648 | 576 | 324 | 104 | 505 | Pacto de ferro: maça: redução, cura e roubo de vida | Pacto de Ferro, Tomar Fôlego, Tremor de Bigorna, Golpe Poderoso | Sede Silenciosa ×2, Voracidade, Coração de Ferro ×6, Boca de Sangue ×6, Pele Grossa ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Clava Pesada; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G39 | babi | B | Mago | 23 | 28.71 | 4477 | 1694 | 395 | 682 | 97 | 412 | Apocalipse: carta lendária de dano | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | Herança do Abismo ×2, Oráculo Partido, Sangue de Vidente ×7, Ódio Baixo ×6, Olho de Águia ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G61 | loud_thurzin | B | Ladino | 21 | 28.60 | 3029 | 868 | 504 | 309 | 287 | 322 | Evasão perfeita: evasão máxima com adaga | Evasão Perfeita, Leitura de Terreno, Ataque Furtivo, Lâmina no Escuro | Reflexos Rápidos ×2, Vulto, Passos Leves ×6, Passo de Corça ×6, Olho de Águia ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G20 | LuquEt4 | B | Guerreiro | 22 | 28.48 | 4754 | 648 | 596 | 324 | 108 | 480 | Condenado: medo e vulnerabilidade | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | Voz no Escuro ×2, Presença Errada, Olho de Caçador ×6, Músculos de Aço ×6, Pele de Sal ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G59 | tioorochitwitch | B | Ladino | 21 | 28.48 | 3029 | 868 | 504 | 309 | 271 | 322 | Morte súbita: carta lendária e crítico | Morte Súbita, Ataque Furtivo, Assassinato, Respiração de Ladrão | Lâmina Afiada ×2, Sede de Sangue, Olho de Águia ×6, Pulso Certeiro ×6, Passo de Corça ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G63 | furq | C | Ladino | 23 | 28.48 | 3799 | 1089 | 652 | 387 | 315 | 406 | Arauto: medo | Hora do Arauto, Pó nos Olhos, Ataque Furtivo, Assassinato | Voz no Escuro ×2, Presença Errada, Olho de Caçador ×7, Músculos de Aço ×6, Pele de Sal ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G19 | MeikodRJ | C | Guerreiro | 22 | 28.37 | 4844 | 648 | 596 | 324 | 108 | 480 | Imortal: redução extrema com espada | Imortal, Golpe Poderoso, Golpe Devastador, Veterania | Lâmina Afiada ×2, Pele de Adamântio, Coração de Ferro ×6, Olho de Águia ×6, Músculos de Aço ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G64 | Hayashii | D | Ladino | 22 | 28.25 | 3392 | 972 | 619 | 346 | 305 | 361 | Sombra mortal: Força do Ladino e crítico | Golpe nas Sombras, Assassinato, Ataque Furtivo, Mão Leve | Fúria Berserker ×2, Toque do Dragão, Músculos de Aço ×6, Olho de Águia ×6, Passo de Corça ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G40 | frttt | C | Mago | 24 | 28.14 | 5014 | 2177 | 443 | 705 | 108 | 461 | Dividendo: mana: queimar a do rival | Dividendo de Mana, Dreno de Mana, Bola de Fogo, Reserva Profunda | Poço Fundo ×2, Ritmo Profano ×2, Reserva Arcana ×7, Mente Serena ×6, Respiração Contada ×6 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G60 | Patriota | C | Ladino | 19 | 28.14 | 2490 | 851 | 369 | 246 | 220 | 257 | Cobrador: sangramento máximo | Cobrança de Juros, Joelho Torto, Corte de Passagem, Ataque Furtivo | Agulha no Osso ×2, Fio Serrilhado ×6, Passo de Corça ×5, Coração de Ferro ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Adaga Mortal; Weapon2: Arco Élfico; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G57 | sacy | D | Ladino | 18 | 27.45 | 2216 | 760 | 330 | 220 | 214 | 225 | Testamento: duas armas e veneno | Testamento do Ladrão, Duas Mãos, Um Tempo, Envenenar, Ataque Furtivo | Unha Suja ×2, Sangue Tóxico, Boca de Sangue ×5, Passo de Corça ×5, Coração de Ferro ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Adaga Mortal; Weapon2: Arco do Silêncio; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G14 | blackoutz | B | Guerreiro | 20 | 27.10 | 3790 | 517 | 459 | 258 | 96 | 383 | Veterano: evasão e crítico de espada | Veterania, Fio no Rebite, Golpe Poderoso, Golpe Devastador | Lâmina Afiada ×2, Sede de Sangue, Olho de Águia ×6, Pulso Certeiro ×5, Passos Leves ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G55 | Felps | A | Ladino | 19 | 27.10 | 2415 | 851 | 384 | 246 | 230 | 257 | Dançarino: dança de lâminas e Agilidade | Dança das Lâminas, Sombra Rápida, Ataque Furtivo, Golpe nas Sombras | Reflexos Rápidos ×2, Vulto, Passo de Corça ×5, Passos Leves ×5, Músculos de Aço ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Adaga Mortal; Weapon2: Arco Élfico; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G38 | NOBRU | B | Mago | 20 | 26.99 | 3187 | 1206 | 281 | 466 | 69 | 293 | Coveiro arcano: veneno e fragilidade | Maldição de Cinzas, Paciência do Coveiro, Marca Ardente, Bola de Fogo | Unha Suja ×2, Sangue Tóxico, Sangue de Vidente ×6, Ódio Baixo ×5, Pele de Sal ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G21 | k13tv | D | Guerreiro | 20 | 26.75 | 3790 | 517 | 493 | 258 | 86 | 383 | Postura impecável: acúmulo de Força | Postura Impecável, Grito de Guerra, Cutelada, Golpe Poderoso | Fúria Berserker ×2, Ódio Antigo ×2, Músculos de Aço ×5, Ódio Baixo ×5, Pulso Certeiro ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G34 | XANDAOOGOD | B | Mago | 19 | 26.64 | 3070 | 1386 | 231 | 500 | 62 | 272 | Ressurgente: cura grande e vida máxima | Ressurgir, Bola de Fogo, Égide de Runas, Vigor Emprestado | Essência Fluída ×2, Bênção Divina, Coração de Ferro ×5, Respiração Contada ×5, Mente Serena ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Cajado do Vazio; Weapon2: Cajado Eterno; Body: Peitoral de Ferro; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G17 | TheBurntPeanut | A | Guerreiro | 18 | 26.29 | 3021 | 506 | 351 | 206 | 69 | 323 | Machado pesado: machado: defesa e sangramento | Resistência Heróica, Rasgo de Gancho, Marca do Açougueiro, Golpe Poderoso | Casco Calejado ×2, Músculos de Aço ×5, Pele Grossa ×5, Fio Serrilhado ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Lâmina da Tempestade; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G12 | gafallen | B | Guerreiro | 20 | 25.95 | 3790 | 517 | 513 | 258 | 96 | 383 | Fúria: buffs de Agilidade e Força | Fúria, Grito de Guerra, Golpe Poderoso, Esmagar | Toque do Dragão, Fúria Berserker ×2, Músculos de Aço ×6, Passos Leves ×5, Ódio Baixo ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G58 | bakzera | B | Ladino | 20 | 25.95 | 2704 | 775 | 469 | 276 | 244 | 288 | Gancho: atordoar e expor | Gancho e Corda, Marcar a Presa, Corte de Tendão, Ataque Furtivo | Instinto Frio ×2, Olho de Caçador ×6, Músculos de Aço ×6, Passo de Corça ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G35 | casimito | A | Mago | 20 | 25.83 | 3187 | 1306 | 281 | 498 | 69 | 293 | Hora parada: sono e explosão | Hora Parada, Bola de Fogo, Marca Ardente, Explosão Arcana | Herança do Abismo ×2, Oráculo Partido, Sangue de Vidente ×6, Reserva Arcana ×5, Ódio Baixo ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G15 | aXtLOL | D | Guerreiro | 20 | 25.72 | 3865 | 517 | 459 | 258 | 83 | 408 | Bigorna: maça: atordoamento e crítico | Tremor de Bigorna, A Mão que Não Treme, Golpe Poderoso, Baluarte | Cabeça Dura ×2, Punho Atordoante, Pele Grossa ×6, Coração de Ferro ×5, Olho de Águia ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Clava Pesada; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G36 | alanzoka | A | Mago | 20 | 25.60 | 3187 | 1206 | 281 | 463 | 69 | 293 | Pacto do vazio: dano crítico | Pacto do Vazio, Míssil Mágico, Mão Firme, Relâmpago | Lâmina Afiada ×2, Lâmina do Juízo, Olho de Águia ×6, Pulso Certeiro ×5, Sangue de Vidente ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G54 | dona | C | Ladino | 16 | 25.60 | 2114 | 493 | 263 | 175 | 153 | 172 | Lobo: adaga: sangramento e roubo de vida | Hora do Lobo, Lâmina no Escuro, Ataque Furtivo, Sangria Lenta | Agulha no Osso ×2, Sede de Sangue, Fio Serrilhado ×4, Olho de Águia ×4, Boca de Sangue ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Guerra; Weapon2: Adaga do Assassino; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G56 | RNakano | D | Ladino | 20 | 25.60 | 2704 | 775 | 450 | 276 | 248 | 288 | Silêncio: sono e atordoamento | Silêncio de Seda, Nó Corredio, Ataque Furtivo, Golpe nas Sombras | Cabeça Dura ×2, Olho de Caçador ×6, Passo de Corça ×6, Pele de Sal ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Arco Élfico; Weapon2: Adaga Mortal; Body: Colete da Sombra; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G37 | yayahuz | D | Mago | 21 | 25.49 | 3659 | 1350 | 315 | 517 | 77 | 352 | Escudo e fogo: defesa em camadas | Escudo Mágico, Pele de Quartzo, Couro Batido, Bola de Fogo | Escudo da Fé ×2, Pele de Adamântio, Coração de Ferro ×6, Pele Grossa ×6, Sangue de Vidente ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G16 | brino | A | Guerreiro | 20 | 25.26 | 4165 | 517 | 459 | 258 | 86 | 383 | Sentinela de ferro: vida máxima e lentidão | Golpe Poderoso, Respiração de Forja, Fôlego de Marcha, Quebra-Ossos | Essência Fluída ×2, Bênção Divina, Sangue de Guerreiro ×6, Coração de Ferro ×5, Pele de Sal ×5 | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada Lendária; Weapon2: Lâmina da Tempestade; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda |
| G52 | Tenz | A | Ladino | 17 | 24.91 | 2367 | 552 | 294 | 196 | 193 | 198 | Ladrão de mana: queima de mana e névoa | Bolso Furado, Ataque Furtivo, Cortina de Fumaça, Golpe nas Sombras | Voz no Escuro, Sede Silenciosa ×2, Passo de Corça ×5, Boca de Sangue ×4, Pele de Sal ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Arco do Silêncio; Weapon2: Machado de Guerra; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G10 | Gaules | A | Guerreiro | 18 | 24.68 | 3021 | 506 | 351 | 206 | 69 | 288 | Lenhador: machado com roubo de vida | Golpe Poderoso, Sede de Batalha, Peso do Machado, Cutelada | Ódio Antigo ×2, Músculos de Aço ×5, Boca de Sangue ×5, Ódio Baixo ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Machado de Batalha; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G31 | jukes | B | Mago | 18 | 24.68 | 2540 | 1182 | 206 | 475 | 68 | 236 | Prisma: vulnerável e dano de cajado | Prisma de Devastação, Lente de Obsidiana, Bola de Fogo, Clarividência | Herança do Abismo, Instinto Frio ×2, Sangue de Vidente ×5, Olho de Caçador ×5, Passos Leves ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G33 | Coringa | A | Mago | 18 | 24.68 | 2540 | 1305 | 206 | 446 | 59 | 236 | Dreno: queima de mana e drenos | Dreno de Mana, Troca de Sangue, Bola de Fogo, Drenar Vida | Ritmo Profano ×2, Respiração Contada ×5, Reserva Arcana ×5, Boca de Sangue ×5 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G07 | Neskwga | D | Guerreiro | 18 | 24.57 | 3136 | 506 | 348 | 206 | 69 | 283 | Regenerador: sustentação: cura e roubo de vida | Golpe Poderoso, Tomar Fôlego, Curativo de Campo, Investida | Sede Silenciosa ×2, Essência Fluída, Boca de Sangue ×5, Coração de Ferro ×5, Músculos de Aço ×4 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Lâmina da Tempestade; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G49 | belrodrigues | D | Ladino | 16 | 24.57 | 2188 | 493 | 263 | 175 | 170 | 173 | Sangrador: sangramento acumulado | Joelho Torto, Corte de Passagem, Corte de Tendão, Marcar a Presa | Agulha no Osso ×2, Fio Serrilhado ×5, Passo de Corça ×4, Coração de Ferro ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Guerra; Weapon2: Espada de Aço; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G50 | Smzinho | C | Ladino | 17 | 24.57 | 2367 | 552 | 309 | 196 | 189 | 198 | Duas lâminas: duas armas e crítico | Ataque Furtivo, Duas Mãos, Um Tempo, Mão Leve, Assassinato | Lâmina Afiada ×2, Músculos de Aço ×5, Olho de Águia ×5, Passo de Corça ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Arco do Silêncio; Weapon2: Machado de Guerra; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G30 | JonVlogs | B | Mago | 18 | 24.45 | 2540 | 1182 | 206 | 485 | 59 | 236 | Tempestuoso: raio e atordoamento | Tempestade, Bola de Fogo, Relâmpago, Foco do Estudante | Herança do Abismo ×2, Sangue de Vidente ×5, Ódio Baixo ×5, Olho de Águia ×5 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G08 | liminhag0d | D | Guerreiro | 18 | 24.10 | 3021 | 506 | 351 | 206 | 69 | 303 | Ariete: atordoar com espada e defesa | Investida de Aríete, Pisada de Ferro, Golpe Poderoso, Postura de Muro | Instinto Frio ×2, Olho de Caçador ×5, Pele Grossa ×5, Músculos de Aço ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Lâmina da Tempestade; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G11 | fer | D | Guerreiro | 18 | 24.10 | 3021 | 506 | 359 | 206 | 69 | 283 | Rompe-guarda: enfraquecer e expor | Soco de Placa, Quebra-Guarda, Provocação, Golpe Devastador | Fúria Berserker, Instinto Frio, Olho de Caçador ×5, Músculos de Aço ×5, Pele de Sal ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Lâmina da Tempestade; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G28 | G0ularte | A | Mago | 18 | 24.10 | 2540 | 1182 | 206 | 465 | 59 | 236 | Arcanista crítico: crítico arcano | Míssil Mágico, Mão Firme, Foco do Estudante, Relâmpago | Lâmina Afiada ×2, Olho de Águia ×5, Pulso Certeiro ×5, Sangue de Vidente ×5 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G32 | Baiano | A | Mago | 18 | 23.99 | 2540 | 1341 | 206 | 465 | 59 | 236 | Grilhões: controle pesado: congelar e medo | Grilhões de Gelo, Lasca de Gelo, Cerco de Espelhos, Bola de Fogo | Poço Fundo ×2, Mente Serena ×5, Sangue de Vidente ×5, Pele de Sal ×5 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G51 | RazaH | C | Ladino | 17 | 23.99 | 2367 | 552 | 294 | 196 | 180 | 194 | Caçador: arco neutro de alto poder | Marca do Caçador, Olho Treinado, Flecha pela Fresta, Ataque Furtivo | Instinto Frio, Lâmina Afiada, Olho de Caçador ×5, Olho de Águia ×5, Passos Leves ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Arco Longbow; Weapon2: Machado de Guerra; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G53 | PaulinhoLOKObr | B | Ladino | 17 | 23.41 | 2460 | 552 | 294 | 196 | 189 | 235 | Couro endurecido: Ladino defensivo | Couro Endurecido, Capa Rasgada, Ataque Furtivo, Assassinato | Casco Calejado ×2, Escudo da Fé, Coração de Ferro ×5, Pele Grossa ×4, Passo de Corça ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Arco do Silêncio; Weapon2: Machado de Guerra; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G09 | jovirone | C | Guerreiro | 18 | 23.18 | 3236 | 506 | 336 | 206 | 66 | 292 | Muralha pesada: tanque de maça com redução dupla | Golpe Poderoso, Baluarte, Couro Batido, Pacto de Ferro | Pele de Adamântio, Coração de Ferro ×6, Sangue de Guerreiro ×5, Postura Fechada ×5 | Helmet: Elmo de Aço; Amulet: Amuleto de Ouro; Weapon1: Clava Pesada; Weapon2: Machado de Guerra; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G29 | PlayHard | C | Mago | 18 | 23.07 | 2615 | 1243 | 206 | 446 | 59 | 262 | Égide rúnica: tanque arcano | Égide de Runas, Escudo Mágico, Bola de Fogo, Palavra de Pavor | Escudo da Fé ×2, Casco Calejado, Coração de Ferro ×5, Mente Serena ×5, Pele Grossa ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro; Weapon1: Cajado Eterno; Weapon2: Machado de Guerra; Body: Peitoral de Ferro; Legs: Perneiras de Ferro; Hands: Luvas de Aço; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| G06 | YoDa | A | Guerreiro | 16 | 22.49 | 3115 | 328 | 268 | 164 | 59 | 259 | Escudeiro de forja: duas armas: guarda e sangramento | Golpe Poderoso, Guarda Cruzada, Disciplina de Forja, Mão Dupla | Casco Calejado ×2, Sangue de Guerreiro ×5, Pele Grossa ×4, Ódio Baixo ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada da Vingança; Weapon2: Espada de Aço; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G03 | suetam1v4 | C | Guerreiro | 16 | 22.38 | 2961 | 328 | 280 | 164 | 59 | 224 | Duelista: crítico de espada | Golpe Poderoso, Quebra-Guarda, Fio no Rebite, Golpe Devastador | Lâmina Afiada ×2, Olho de Águia ×5, Pulso Certeiro ×4, Músculos de Aço ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada da Vingança; Weapon2: Espada de Aço; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G26 | lubatv | A | Mago | 16 | 22.38 | 2583 | 766 | 164 | 285 | 47 | 181 | Curandeira: cura e roubo de vida | Bola de Fogo, Drenar Vida, Pele de Quartzo, Sanguessuga Arcana | Sede Silenciosa ×2, Coração de Ferro ×5, Respiração Contada ×4, Boca de Sangue ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Guerra; Weapon2: Cajado do Equilíbrio; Body: Colete da Resistência; Legs: Perneiras de Ferro; Hands: Bastão Mágico; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G46 | Bagi | A | Ladino | 14 | 22.03 | 1415 | 393 | 209 | 156 | 149 | 139 | Envenenador: veneno | Envenenar, Dose da Viúva, Ataque Furtivo, Golpe nas Sombras | Unha Suja ×2, Boca de Sangue ×4, Passo de Corça ×4, Coração de Ferro ×3 | Helmet: Elmo de Ferro; Amulet: Amuleto da Agilidade; Weapon1: Cajado de Cristal; Weapon2: Adaga do Assassino; Body: Colete da Resistência; Legs: Calça de Cota; Hands: Escudo Torre; Shoes: Botas Fantasma; Ring1: Anel do Rubi; Ring2: Anel de Aço |
| G27 | mount | B | Mago | 16 | 21.92 | 2564 | 846 | 164 | 300 | 47 | 181 | Sonhador: sono e maldição | Sono Profundo, Bola de Fogo, Explosão Arcana, Dissonância | Ritmo Profano ×2, Sangue de Vidente ×5, Reserva Arcana ×4, Coração de Ferro ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Guerra; Weapon2: Cajado do Equilíbrio; Body: Colete da Resistência; Legs: Perneiras de Ferro; Hands: Bastão Mágico; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G47 | boltz | C | Ladino | 15 | 21.92 | 1888 | 440 | 235 | 174 | 170 | 156 | Esquivo: evasão e Agilidade | Evasão, Sombra Rápida, Corte de Tendão, Golpe nas Sombras | Reflexos Rápidos ×2, Passo de Corça ×4, Passos Leves ×4, Olho de Águia ×4 | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada de Aço; Weapon2: Cajado de Cristal; Body: Peitoral de Ferro; Legs: Calça de Cota; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel do Rubi; Ring2: Anel da Esmeralda |
| G24 | Tealzlol | D | Mago | 15 | 21.80 | 2223 | 844 | 147 | 266 | 42 | 162 | Geomante: cajado: lentidão, atordoar e vulnerável | Bola de Fogo, Pulso de Força, Lançar Pedra, Lente de Obsidiana | Poço Fundo ×2, Sangue de Vidente ×4, Reserva Arcana ×4, Olho de Caçador ×4 | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata; Weapon1: Cajado do Equilíbrio; Weapon2: Machado de Guerra; Body: Colete da Resistência; Legs: Perneiras de Ferro; Hands: Bastão Mágico; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G04 | DavyJones | A | Guerreiro | 16 | 21.68 | 3035 | 328 | 299 | 164 | 59 | 224 | Berserker: Força bruta e fragilidade | Golpe Poderoso, Grito de Guerra, Cutelada, Golpe Duplo | Fúria Berserker ×2, Músculos de Aço ×5, Ódio Baixo ×4, Coração de Ferro ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada da Vingança; Weapon2: Espada de Aço; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G25 | xandfps | D | Mago | 16 | 21.57 | 2490 | 816 | 164 | 297 | 47 | 181 | Criomante: gelo: congelar e lentidão | Lasca de Gelo, Raio Congelante, Palavra de Torpor, Bola de Fogo | Ritmo Profano, Mente Serena ×5, Pele de Sal ×5, Sangue de Vidente ×4 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Guerra; Weapon2: Cajado do Equilíbrio; Body: Colete da Resistência; Legs: Perneiras de Ferro; Hands: Bastão Mágico; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G01 | fnxLNTC | D | Guerreiro | 16 | 21.34 | 3109 | 328 | 268 | 164 | 57 | 246 | Muralha de maça: defesa: reduções de dano com maça | Golpe Poderoso, Baluarte, Couraça Improvisada, Tremor de Bigorna | Escudo da Fé ×2, Pele Grossa ×4, Postura Fechada ×3, Coração de Ferro ×3, Sangue de Guerreiro ×3 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Clava Pesada; Weapon2: Espada de Aço; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G05 | calango | A | Guerreiro | 16 | 21.34 | 3017 | 328 | 268 | 164 | 59 | 235 | Carcereiro: controle: atordoar, medo e enfraquecer | Investida, Berro de Ferro, Pancada de Elmo, Ferro Contra Ferro | Cabeça Dura ×2, Olho de Caçador ×4, Pele de Sal ×3, Coração de Ferro ×3, Pele Grossa ×3 | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada da Vingança; Weapon2: Espada de Aço; Body: Armadura de Cota de Malha; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi |
| G45 | Bisteconee | B | Ladino | 15 | 21.22 | 1888 | 440 | 235 | 174 | 152 | 154 | Arqueiro: arco: sangramento e crítico | Ataque Furtivo, Flecha pela Fresta, Olho do Falcão, Chuva de Ferrões | Instinto Frio ×2, Olho de Caçador ×4, Olho de Águia ×4, Passos Leves ×4 | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata; Weapon1: Arco Composto; Weapon2: Cajado de Cristal; Body: Peitoral de Ferro; Legs: Calça de Cota; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel do Rubi; Ring2: Anel da Esmeralda |
| G44 | brtt | C | Ladino | 14 | 21.11 | 1370 | 393 | 209 | 156 | 145 | 139 | Assassino de adaga: adaga e crítico | Ataque Furtivo, Picada Certeira, Lâmina no Escuro, Leitura de Guarda | Lâmina Afiada ×2, Olho de Águia ×4, Pulso Certeiro ×4, Passo de Corça ×3 | Helmet: Elmo de Ferro; Amulet: Amuleto da Agilidade; Weapon1: Cajado de Cristal; Weapon2: Adaga do Assassino; Body: Colete da Resistência; Legs: Calça de Cota; Hands: Escudo Torre; Shoes: Botas Fantasma; Ring1: Anel do Rubi; Ring2: Anel de Aço |
| G02 | yeTz | C | Guerreiro | 13 | 20.53 | 1714 | 234 | 203 | 117 | 48 | 161 | Açougueiro: sangramento com machado | Golpe Poderoso, Marca do Açougueiro, Peso do Machado, Rasgo de Gancho | Agulha no Osso ×2, Músculos de Aço ×4, Fio Serrilhado ×3, Ódio Baixo ×3 | Helmet: Elmo de Ferro; Amulet: Amuleto da Agilidade; Weapon1: Machado de Batalha; Weapon2: Tridente do Guerreiro; Body: Peitoral de Ferro; Legs: Calça de Cota; Hands: Escudo Torre; Shoes: Botas de Corrida; Ring1: Anel do Rubi; Ring2: Anel de Aço |
| G48 | sofiaespanha | D | Ladino | 15 | 20.53 | 1888 | 440 | 235 | 174 | 161 | 156 | Trapaceiro: controle sujo | Golpe Baixo, Pó nos Olhos, Ataque Furtivo, Marcar a Presa | Cabeça Dura, Voz no Escuro ×2, Olho de Caçador ×4, Passo de Corça ×4, Pele de Sal ×3 | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada de Aço; Weapon2: Cajado de Cristal; Body: Peitoral de Ferro; Legs: Calça de Cota; Hands: Garras de Ferro; Shoes: Botas de Corrida; Ring1: Anel do Rubi; Ring2: Anel da Esmeralda |
| G23 | hastad | C | Mago | 14 | 20.07 | 1614 | 611 | 131 | 255 | 44 | 145 | Piromante: fogo e veneno | Bola de Fogo, Marca Ardente, Relâmpago, Maldição de Cinzas | Herança do Abismo ×2, Sangue de Vidente ×4, Ódio Baixo ×4, Olho de Águia ×3 | Helmet: Elmo de Ferro; Amulet: Amuleto da Agilidade; Weapon1: Cajado do Equilíbrio; Weapon2: Espada de Aço; Body: Peitoral de Cota; Legs: Calça de Cota; Hands: Bastão Mágico; Shoes: Botas Encantadas; Ring1: Anel do Rubi; Ring2: Anel da Esmeralda |

## Chave

```
Fase de 64
   1. Forever (29.3) × RazaH (24.0)  →  Forever
   2. yayahuz (25.5) × bakzera (25.9)  →  bakzera
   3. dona (25.6) × aXtLOL (25.7)  →  dona
   4. brino (25.3) × Neskwga (24.6)  →  brino
   5. sacy (27.4) × fnxLNTC (21.3)  →  sacy
   6. brtt (21.1) × furq (28.5)  →  furq
   7. k13tv (26.8) × loud_thurzin (28.6)  →  k13tv
   8. NOBRU (27.0) × aspaszin (29.5)  →  aspaszin
   9. liminhag0d (24.1) × Bisteconee (21.2)  →  liminhag0d
  10. babi (28.7) × jovirone (23.2)  →  babi
  11. xandfps (21.6) × Felps (27.1)  →  Felps
  12. casimito (25.8) × Gaules (24.7)  →  casimito
  13. coldzin (29.5) × PlayHard (23.1)  →  coldzin
  14. blackoutz (27.1) × JonVlogs (24.5)  →  blackoutz
  15. tioorochitwitch (28.5) × mount (21.9)  →  tioorochitwitch
  16. suetam1v4 (22.4) × MeikodRJ (28.4)  →  MeikodRJ
  17. belrodrigues (24.6) × Tealzlol (21.8)  →  Tealzlol
  18. TheBurntPeanut (26.3) × SkipNhO (28.7)  →  SkipNhO
  19. Baiano (24.0) × G0ularte (24.1)  →  Baiano
  20. jukes (24.7) × gafallen (25.9)  →  gafallen
  21. fer (24.1) × Bagi (22.0)  →  fer
  22. lubatv (22.4) × Hayashii (28.3)  →  Hayashii
  23. frttt (28.1) × PaulinhoLOKObr (23.4)  →  frttt
  24. Tenz (24.9) × Coringa (24.7)  →  Coringa
  25. tteuw (28.7) × YoDa (22.5)  →  tteuw
  26. alanzoka (25.6) × Patriota (28.1)  →  Patriota
  27. sofiaespanha (20.5) × DavyJones (21.7)  →  DavyJones
  28. Smzinho (24.6) × RNakano (25.6)  →  RNakano
  29. XANDAOOGOD (26.6) × gabepeixe (29.5)  →  gabepeixe
  30. yeTz (20.5) × Dilera (29.2)  →  Dilera
  31. LuquEt4 (28.5) × calango (21.3)  →  LuquEt4
  32. boltz (21.9) × hastad (20.1)  →  boltz
Fase de 32
   1. Forever (29.3) × bakzera (25.9)  →  Forever
   2. dona (25.6) × brino (25.3)  →  dona
   3. sacy (27.4) × furq (28.5)  →  furq
   4. k13tv (26.8) × aspaszin (29.5)  →  aspaszin
   5. liminhag0d (24.1) × babi (28.7)  →  babi
   6. Felps (27.1) × casimito (25.8)  →  Felps
   7. coldzin (29.5) × blackoutz (27.1)  →  coldzin
   8. tioorochitwitch (28.5) × MeikodRJ (28.4)  →  MeikodRJ
   9. Tealzlol (21.8) × SkipNhO (28.7)  →  SkipNhO
  10. Baiano (24.0) × gafallen (25.9)  →  gafallen
  11. fer (24.1) × Hayashii (28.3)  →  Hayashii
  12. frttt (28.1) × Coringa (24.7)  →  frttt
  13. tteuw (28.7) × Patriota (28.1)  →  Patriota
  14. DavyJones (21.7) × RNakano (25.6)  →  RNakano
  15. gabepeixe (29.5) × Dilera (29.2)  →  gabepeixe
  16. LuquEt4 (28.5) × boltz (21.9)  →  LuquEt4
Oitavas
   1. Forever (29.3) × dona (25.6)  →  Forever
   2. furq (28.5) × aspaszin (29.5)  →  aspaszin
   3. babi (28.7) × Felps (27.1)  →  babi
   4. coldzin (29.5) × MeikodRJ (28.4)  →  MeikodRJ
   5. SkipNhO (28.7) × gafallen (25.9)  →  SkipNhO
   6. Hayashii (28.3) × frttt (28.1)  →  frttt
   7. Patriota (28.1) × RNakano (25.6)  →  RNakano
   8. gabepeixe (29.5) × LuquEt4 (28.5)  →  LuquEt4
Quartas
   1. Forever (29.3) × aspaszin (29.5)  →  aspaszin
   2. babi (28.7) × MeikodRJ (28.4)  →  babi
   3. SkipNhO (28.7) × frttt (28.1)  →  SkipNhO
   4. RNakano (25.6) × LuquEt4 (28.5)  →  LuquEt4
Semifinal
   1. aspaszin (29.5) × babi (28.7)  →  aspaszin
   2. SkipNhO (28.7) × LuquEt4 (28.5)  →  SkipNhO
Final
   1. aspaszin (29.5) × SkipNhO (28.7)  →  aspaszin
Campeão: aspaszin (G43)
```

## Resultados por fase

### Fase de 64

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Forever (29.29) | RazaH (23.99) | **Forever** | 4 | 4477/4477 | +5.30 |  |
| 2 | yayahuz (25.49) | bakzera (25.95) | **bakzera** | 23 | 1560/2704 | +0.46 |  |
| 3 | dona (25.60) | aXtLOL (25.72) | **dona** | 9 | 572/2114 | -0.12 | sim |
| 4 | brino (25.26) | Neskwga (24.57) | **brino** | 20 | 2439/4165 | +0.69 |  |
| 5 | sacy (27.45) | fnxLNTC (21.34) | **sacy** | 7 | 2166/2216 | +6.11 |  |
| 6 | brtt (21.11) | furq (28.48) | **furq** | 3 | 3799/3799 | +7.38 |  |
| 7 | k13tv (26.75) | loud_thurzin (28.60) | **k13tv** | 12 | 1485/3790 | -1.84 | sim |
| 8 | NOBRU (26.99) | aspaszin (29.52) | **aspaszin** | 4 | 3894/4477 | +2.54 |  |
| 9 | liminhag0d (24.10) | Bisteconee (21.22) | **liminhag0d** | 6 | 1420/3021 | +2.88 |  |
| 10 | babi (28.71) | jovirone (23.18) | **babi** | 12 | 3070/4477 | +5.53 |  |
| 11 | xandfps (21.57) | Felps (27.10) | **Felps** | 14 | 1865/2415 | +5.53 |  |
| 12 | casimito (25.83) | Gaules (24.68) | **casimito** | 5 | 2809/3187 | +1.15 |  |
| 13 | coldzin (29.52) | PlayHard (23.07) | **coldzin** | 7 | 1577/3029 | +6.45 |  |
| 14 | blackoutz (27.10) | JonVlogs (24.45) | **blackoutz** | 4 | 3790/3790 | +2.65 |  |
| 15 | tioorochitwitch (28.48) | mount (21.92) | **tioorochitwitch** | 16 | 1424/3029 | +6.57 |  |
| 16 | suetam1v4 (22.38) | MeikodRJ (28.37) | **MeikodRJ** | 5 | 4506/4844 | +5.99 |  |
| 17 | belrodrigues (24.57) | Tealzlol (21.80) | **Tealzlol** | 6 | 587/2223 | -2.77 | sim |
| 18 | TheBurntPeanut (26.29) | SkipNhO (28.71) | **SkipNhO** | 11 | 753/5004 | +2.42 |  |
| 19 | Baiano (23.99) | G0ularte (24.10) | **Baiano** | 9 | 362/2540 | -0.12 | sim |
| 20 | jukes (24.68) | gafallen (25.95) | **gafallen** | 11 | 729/3790 | +1.27 |  |
| 21 | fer (24.10) | Bagi (22.03) | **fer** | 6 | 2086/3021 | +2.07 |  |
| 22 | lubatv (22.38) | Hayashii (28.25) | **Hayashii** | 5 | 3392/3392 | +5.88 |  |
| 23 | frttt (28.14) | PaulinhoLOKObr (23.41) | **frttt** | 4 | 4538/5014 | +4.72 |  |
| 24 | Tenz (24.91) | Coringa (24.68) | **Coringa** | 24 | 562/2540 | -0.23 | sim |
| 25 | tteuw (28.71) | YoDa (22.49) | **tteuw** | 12 | 4844/4844 | +6.22 |  |
| 26 | alanzoka (25.60) | Patriota (28.14) | **Patriota** | 5 | 1843/2490 | +2.54 |  |
| 27 | sofiaespanha (20.53) | DavyJones (21.68) | **DavyJones** | 8 | 1768/3035 | +1.15 |  |
| 28 | Smzinho (24.57) | RNakano (25.60) | **RNakano** | 6 | 2179/2704 | +1.04 |  |
| 29 | XANDAOOGOD (26.64) | gabepeixe (29.52) | **gabepeixe** | 9 | 2910/3509 | +2.88 |  |
| 30 | yeTz (20.53) | Dilera (29.17) | **Dilera** | 4 | 3199/3262 | +8.64 |  |
| 31 | LuquEt4 (28.48) | calango (21.34) | **LuquEt4** | 8 | 4542/4754 | +7.14 |  |
| 32 | boltz (21.92) | hastad (20.07) | **boltz** | 7 | 1039/1888 | +1.84 |  |

### Fase de 32

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Forever (29.29) | bakzera (25.95) | **Forever** | 3 | 4477/4477 | +3.34 |  |
| 2 | dona (25.60) | brino (25.26) | **dona** | 13 | 725/2114 | +0.35 |  |
| 3 | sacy (27.45) | furq (28.48) | **furq** | 3 | 3799/3799 | +1.04 |  |
| 4 | k13tv (26.75) | aspaszin (29.52) | **aspaszin** | 4 | 3551/4477 | +2.77 |  |
| 5 | liminhag0d (24.10) | babi (28.71) | **babi** | 6 | 3328/4477 | +4.61 |  |
| 6 | Felps (27.10) | casimito (25.83) | **Felps** | 13 | 807/2415 | +1.27 |  |
| 7 | coldzin (29.52) | blackoutz (27.10) | **coldzin** | 8 | 897/3029 | +2.42 |  |
| 8 | tioorochitwitch (28.48) | MeikodRJ (28.37) | **MeikodRJ** | 11 | 1555/4844 | -0.12 | sim |
| 9 | Tealzlol (21.80) | SkipNhO (28.71) | **SkipNhO** | 5 | 4759/5004 | +6.91 |  |
| 10 | Baiano (23.99) | gafallen (25.95) | **gafallen** | 9 | 2709/3790 | +1.96 |  |
| 11 | fer (24.10) | Hayashii (28.25) | **Hayashii** | 4 | 3193/3392 | +4.15 |  |
| 12 | frttt (28.14) | Coringa (24.68) | **frttt** | 4 | 4725/5014 | +3.46 |  |
| 13 | tteuw (28.71) | Patriota (28.14) | **Patriota** | 11 | 882/2490 | -0.58 | sim |
| 14 | DavyJones (21.68) | RNakano (25.60) | **RNakano** | 9 | 1973/2704 | +3.92 |  |
| 15 | gabepeixe (29.52) | Dilera (29.17) | **gabepeixe** | 17 | 2751/3509 | +0.35 |  |
| 16 | LuquEt4 (28.48) | boltz (21.92) | **LuquEt4** | 7 | 3953/4754 | +6.57 |  |

### Oitavas

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Forever (29.29) | dona (25.60) | **Forever** | 4 | 4477/4477 | +3.69 |  |
| 2 | furq (28.48) | aspaszin (29.52) | **aspaszin** | 9 | 202/4477 | +1.04 |  |
| 3 | babi (28.71) | Felps (27.10) | **babi** | 3 | 3570/4477 | +1.61 |  |
| 4 | coldzin (29.52) | MeikodRJ (28.37) | **MeikodRJ** | 11 | 1996/4844 | -1.15 | sim |
| 5 | SkipNhO (28.71) | gafallen (25.95) | **SkipNhO** | 17 | 3362/5004 | +2.77 |  |
| 6 | Hayashii (28.25) | frttt (28.14) | **frttt** | 8 | 1665/5014 | -0.12 | sim |
| 7 | Patriota (28.14) | RNakano (25.60) | **RNakano** | 9 | 1200/2704 | -2.54 | sim |
| 8 | gabepeixe (29.52) | LuquEt4 (28.48) | **LuquEt4** | 14 | 2812/4754 | -1.04 | sim |

### Quartas

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Forever (29.29) | aspaszin (29.52) | **aspaszin** | 10 | 708/4477 | +0.23 |  |
| 2 | babi (28.71) | MeikodRJ (28.37) | **babi** | 14 | 1134/4477 | +0.35 |  |
| 3 | SkipNhO (28.71) | frttt (28.14) | **SkipNhO** | 24 | 2337/5004 | +0.58 |  |
| 4 | RNakano (25.60) | LuquEt4 (28.48) | **LuquEt4** | 6 | 3880/4754 | +2.88 |  |

### Semifinal

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | aspaszin (29.52) | babi (28.71) | **aspaszin** | 6 | 2018/4477 | +0.81 |  |
| 2 | SkipNhO (28.71) | LuquEt4 (28.48) | **SkipNhO** | 34 | 499/5004 | +0.23 |  |

### Final

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | aspaszin (29.52) | SkipNhO (28.71) | **aspaszin** | 15 | 1369/4477 | +0.81 |  |

## Estatísticas agregadas

> Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por confronto. Ela aponta casos para investigar; não prova balanceamento entre classes.

### Desempenho por classe

| Classe | Participantes | OP médio | Vitórias | Derrotas | Taxa | Dano por partida | Acerto | Críticos (taxa) | Cura total | Ações perdidas por controle |
|---|---|---|---|---|---|---|---|---|---|---|
| Guerreiro | 22 | 25.06 | 23 | 22 | 51.1% | 2636 | 80.4% | 19 (7.0%) | 7933 | 24 |
| Mago | 21 | 25.15 | 21 | 20 | 51.2% | 2751 | 72.1% | 25 (18.2%) | 12262 | 24 |
| Ladino | 21 | 25.31 | 19 | 21 | 47.5% | 2554 | 95.5% | 55 (32.7%) | 2894 | 35 |

Quantos de cada classe chegaram a cada fase:

| Classe | Fase de 64 | Fase de 32 | Oitavas | Quartas | Semifinal | Final | Campeão |
|---|---|---|---|---|---|---|---|
| Guerreiro | 22 | 12 | 5 | 3 | 2 | 1 |  |
| Mago | 21 | 9 | 4 | 4 | 2 | 1 | sim |
| Ladino | 21 | 11 | 7 | 1 | 0 | 0 |  |

Vitórias da classe da linha sobre a da coluna:

| Vencedor \ Perdedor | Guerreiro | Mago | Ladino |
|---|---|---|---|
| Guerreiro | 8 | 7 | 8 |
| Mago | 7 | 5 | 9 |
| Ladino | 7 | 8 | 4 |

### Overall Power dos vencedores por fase

| Fase | Partidas | OP médio de quem entrou (mín–máx) | OP médio dos vencedores (mín–máx) | OP médio dos perdedores | Favorito venceu |
|---|---|---|---|---|---|
| Fase de 64 | 32 | 25.17 (20.07–29.52) | 26.76 (21.68–29.52) | 23.58 | 27/32 |
| Fase de 32 | 16 | 26.76 (21.68–29.52) | 28.09 (25.60–29.52) | 25.44 | 14/16 |
| Oitavas | 8 | 28.09 (25.60–29.52) | 28.35 (25.60–29.52) | 27.82 | 4/8 |
| Quartas | 4 | 28.35 (25.60–29.52) | 28.86 (28.48–29.52) | 27.85 | 4/4 |
| Semifinal | 2 | 28.86 (28.48–29.52) | 29.12 (28.71–29.52) | 28.60 | 2/2 |
| Final | 1 | 29.12 (28.71–29.52) | 29.52 (29.52–29.52) | 28.71 | 1/1 |

### Confrontos com as maiores diferenças de OP

| Partida | Vencedor (OP) | Perdedor (OP) | ΔOP | Rodadas |
|---|---|---|---|---|
| Fase de 64 30 — yeTz × Dilera | Dilera (29.17) | yeTz (20.53) | +8.64 | 4 |
| Fase de 64 6 — brtt × furq | furq (28.48) | brtt (21.11) | +7.38 | 3 |
| Fase de 64 31 — LuquEt4 × calango | LuquEt4 (28.48) | calango (21.34) | +7.14 | 8 |
| Fase de 32 9 — Tealzlol × SkipNhO | SkipNhO (28.71) | Tealzlol (21.80) | +6.91 | 5 |
| Fase de 64 15 — tioorochitwitch × mount | tioorochitwitch (28.48) | mount (21.92) | +6.57 | 16 |
| Fase de 32 16 — LuquEt4 × boltz | LuquEt4 (28.48) | boltz (21.92) | +6.57 | 7 |
| Fase de 64 13 — coldzin × PlayHard | coldzin (29.52) | PlayHard (23.07) | +6.45 | 7 |
| Fase de 64 25 — tteuw × YoDa | tteuw (28.71) | YoDa (22.49) | +6.22 | 12 |
| Fase de 64 5 — sacy × fnxLNTC | sacy (27.45) | fnxLNTC (21.34) | +6.11 | 7 |
| Fase de 64 16 — suetam1v4 × MeikodRJ | MeikodRJ (28.37) | suetam1v4 (22.38) | +5.99 | 5 |

### Vitórias de quem tinha o OP menor (11 zebras)

| Partida | Vencedor (OP) | Perdedor (OP) | ΔOP | Rodadas |
|---|---|---|---|---|
| Fase de 64 17 — belrodrigues × Tealzlol | Tealzlol (21.80) | belrodrigues (24.57) | -2.77 | 6 |
| Oitavas 7 — Patriota × RNakano | RNakano (25.60) | Patriota (28.14) | -2.54 | 9 |
| Fase de 64 7 — k13tv × loud_thurzin | k13tv (26.75) | loud_thurzin (28.60) | -1.84 | 12 |
| Oitavas 4 — coldzin × MeikodRJ | MeikodRJ (28.37) | coldzin (29.52) | -1.15 | 11 |
| Oitavas 8 — gabepeixe × LuquEt4 | LuquEt4 (28.48) | gabepeixe (29.52) | -1.04 | 14 |
| Fase de 32 13 — tteuw × Patriota | Patriota (28.14) | tteuw (28.71) | -0.58 | 11 |
| Fase de 64 24 — Tenz × Coringa | Coringa (24.68) | Tenz (24.91) | -0.23 | 24 |
| Fase de 64 3 — dona × aXtLOL | dona (25.60) | aXtLOL (25.72) | -0.12 | 9 |
| Fase de 64 19 — Baiano × G0ularte | Baiano (23.99) | G0ularte (24.10) | -0.12 | 9 |
| Fase de 32 8 — tioorochitwitch × MeikodRJ | MeikodRJ (28.37) | tioorochitwitch (28.48) | -0.12 | 11 |
| Oitavas 6 — Hayashii × frttt | frttt (28.14) | Hayashii (28.25) | -0.12 | 8 |

Vencedor × perdedor por faixa medida (1 = 20–22,5 … 4 = 27,5–30): 1→1: 2, 1→2: 1, 2→1: 2, 2→2: 2, 3→1: 3, 3→2: 6, 3→3: 4, 3→4: 2, 4→1: 9, 4→2: 7, 4→3: 12, 4→4: 13

### Maiores golpes

| Dano | Crítico | Atacante | Alvo | Ação | Partida | Rodada |
|---|---|---|---|---|---|---|
| 2912 | sim | aspaszin (G43) | NOBRU (G38) | Bola de Fogo | Fase de 64 8 — NOBRU × aspaszin | 4 |
| 2802 | sim | aspaszin (G43) | Forever (G41) | Bola de Fogo | Quartas 1 — Forever × aspaszin | 10 |
| 2777 | sim | aspaszin (G43) | Forever (G41) | Prisma de Devastação | Quartas 1 — Forever × aspaszin | 8 |
| 2664 | sim | babi (G39) | MeikodRJ (G19) | Apocalipse | Quartas 2 — babi × MeikodRJ | 14 |
| 2626 | sim | aspaszin (G43) | NOBRU (G38) | Lente de Obsidiana | Fase de 64 8 — NOBRU × aspaszin | 3 |
| 2607 | sim | coldzin (G62) | blackoutz (G14) | Marca do Caçador | Fase de 32 7 — coldzin × blackoutz | 8 |
| 2454 |  | frttt (G40) | Coringa (G33) | Dividendo de Mana | Fase de 32 12 — frttt × Coringa | 3 |
| 2310 |  | Forever (G41) | RazaH (G51) | Tempestade | Fase de 64 1 — Forever × RazaH | 4 |
| 2302 |  | babi (G39) | Felps (G55) | Apocalipse | Oitavas 3 — babi × Felps | 2 |
| 2282 | sim | blackoutz (G14) | coldzin (G62) | Golpe Devastador | Fase de 32 7 — coldzin × blackoutz | 5 |

Críticos: 99 em 575 golpes conectados; o maior, 2912 de dano de aspaszin (G43) (Bola de Fogo).

### Partidas mais longas e mais curtas

Mais longas: Semifinal 2 — SkipNhO × LuquEt4 (34 rodadas); Fase de 64 24 — Tenz × Coringa (24 rodadas); Quartas 3 — SkipNhO × frttt (24 rodadas); Fase de 64 2 — yayahuz × bakzera (23 rodadas); Fase de 64 4 — brino × Neskwga (20 rodadas)

Mais curtas: Fase de 32 1 — Forever × bakzera (3 rodadas); Fase de 32 3 — sacy × furq (3 rodadas); Fase de 64 6 — brtt × furq (3 rodadas); Oitavas 3 — babi × Felps (3 rodadas); Fase de 32 11 — fer × Hayashii (4 rodadas)

Rodadas por partida: 3: 4, 4: 9, 5: 5, 6: 7, 7: 4, 8: 4, 9: 7, 10: 1, 11: 5, 12: 3, 13: 2, 14: 3, 15: 1, 16: 1, 17: 2, 20: 1, 23: 1, 24: 2, 34: 1.

### Uso de skills, buffs, controles e curas

Skills mais usadas: Golpe Poderoso ×118, Bola de Fogo ×79, Ataque Furtivo ×52, Juramento da Muralha ×17, Golpe Devastador ×16, Golpe nas Sombras ×16, Dreno de Mana ×16, Foco do Estudante ×14, Lasca de Gelo ×13, Hora do Arauto ×13, Sombra Rápida ×13, Grito de Guerra ×12, Assassinato ×11, Prisma de Devastação ×11, Lente de Obsidiana ×11.

Buffs ativados: Juramento da Muralha ×17, Foco do Estudante ×14, Sombra Rápida ×13, Grito de Guerra ×12, Olho do Falcão ×9, Guarda Cruzada ×9, Reserva Profunda ×9, Escudo Mágico ×7, Couro Batido ×7, Baluarte ×7, Veterania ×7, Respiração de Ladrão ×7, Imortal ×7, Pele de Quartzo ×6, Sangria Lenta ×6, Pacto de Ferro ×6, Fúria ×6, Sanguessuga Arcana ×5, Mão Leve ×5, Respiração de Forja ×4, Fôlego de Marcha ×4, Curativo de Campo ×4, Postura de Muro ×4, Égide de Runas ×4, Fio no Rebite ×4, Evasão ×4, Postura Impecável ×3, Evasão Perfeita ×3, Leitura de Terreno ×3, Clarividência ×3, A Mão que Não Treme ×2, Resistência Heróica ×2, Mão Firme ×2, Disciplina de Forja ×2, Vigor Emprestado ×2, Olho Treinado ×1, Couraça Improvisada ×1, Leitura de Guarda ×1, Sede de Batalha ×1, Couro Endurecido ×1, Capa Rasgada ×1, Pacto do Vazio ×1.

Status aplicados: bleed ×95, stun ×48, fear ×47, vulnerable ×35, slowed ×27, poison ×27, mana_burn ×24, frozen ×12, weakened ×11, clouded ×10, sleep ×10, hexed ×4, frailty ×2. Tentativas que não pegaram: stun ×380, bleed ×295, poison ×120, fear ×69, slowed ×25, vulnerable ×22, mana_burn ×9, weakened ×6, frozen ×4, hexed ×4, sleep ×3, frailty ×3, clouded ×1.

Controles que tiram a vez (atordoar, sono, congelar) aplicados: stun ×48, sleep ×10, frozen ×12; ações perdidas por controle no total: 83.

Cura total (skill + roubo de vida): 23089. Quem mais curou: Dilera (G42) 6770, Coringa (G33) 3212, tteuw (G22) 2018, XANDAOOGOD (G34) 1688, Neskwga (G07) 1517.

Critério que decidiu a ordem, por rodada: score ×597.

### Quem mais eliminou

| Gladiador | Classe | OP | Vitórias | Fase alcançada |
|---|---|---|---|---|
| aspaszin (G43) | Mago | 29.52 | 6 | Campeão |
| SkipNhO (G18) | Guerreiro | 28.71 | 5 | Final |
| babi (G39) | Mago | 28.71 | 4 | Semifinal |
| LuquEt4 (G20) | Guerreiro | 28.48 | 4 | Semifinal |
| Forever (G41) | Mago | 29.29 | 3 | Quartas |
| frttt (G40) | Mago | 28.14 | 3 | Quartas |
| MeikodRJ (G19) | Guerreiro | 28.37 | 3 | Quartas |
| RNakano (G56) | Ladino | 25.60 | 3 | Quartas |
| gabepeixe (G13) | Guerreiro | 29.52 | 2 | Oitavas |
| coldzin (G62) | Ladino | 29.52 | 2 | Oitavas |

## O campeão

**aspaszin (G43)**, Mago nível 23, OP 29.52 (faixa 4), build *Prisma do arauto*: vulnerabilidade e dano.

- Skills: Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo
- Passivas: Lâmina Afiada ×2, Oráculo Partido, Sangue de Vidente ×7, Olho de Águia ×6, Pulso Certeiro ×6
- Equipamento: Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Cajado do Vazio; Weapon2: Cajado do Oblivion; Body: Armadura de Cota de Malha; Legs: Calça de Ferro; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel da Esmeralda
- HP 4477, MP 1694, ST 395, MG 666, AG 97, DF 412

| Fase | Adversário (OP) | Rodadas | Dano causado | Dano recebido | Cura | MP | Acertos/erros | Críticos | HP final |
|---|---|---|---|---|---|---|---|---|---|
| Fase de 64 | NOBRU (26.99) | 4 | 5538 | 583 | 0 | 414 | 2/1 | 2 | 3894/4477 |
| Fase de 32 | k13tv (26.75) | 4 | 5125 | 926 | 0 | 414 | 3/0 | 3 | 3551/4477 |
| Oitavas | furq (28.48) | 9 | 4200 | 4275 | 0 | 828 | 3/4 | 1 | 202/4477 |
| Quartas | Forever (29.29) | 10 | 6347 | 3769 | 0 | 414 | 3/0 | 2 | 708/4477 |
| Semifinal | babi (28.71) | 6 | 4553 | 2459 | 0 | 479 | 4/1 | 3 | 2018/4477 |
| Final | SkipNhO (28.71) | 15 | 5913 | 3108 | 0 | 1307 | 11/1 | 7 | 1369/4477 |

Totais: 48 rodadas, 31676 de dano causado, 15120 recebido, 0 de cura, 3856 de MP, 38 skills e 4 ataques básicos, 26 acertos, 7 erros, 18 críticos.

## Curiosidades

- Maior zebra: Tealzlol (G24), OP 21.80, eliminou belrodrigues (G49), OP 24.57 (Fase de 64, diferença de 2.77).
- Vitória mais apertada: aspaszin (G43) terminou com 202/4477 de HP contra furq (G63) (Oitavas).
- Golpe que mais passou do necessário: blackoutz (G14) terminou com -2512 de HP (Fase de 32 7 — coldzin × blackoutz).
- Nenhum `death_ignore` disparou: nenhum dos 64 tem essa fonte.
- 14 partida(s) terminaram num golpe crítico; o maior deles tirou 2912 de HP.
- 18 partida(s) foram vencidas por quem NUNCA agiu primeiro, como k13tv (G21) em Fase de 64 7 — k13tv × loud_thurzin.
- A ordem de iniciativa mudou dentro de 14 partida(s); o recorde foi 4 virada(s) em Fase de 64 18 — TheBurntPeanut × SkipNhO.
- De 597 rodadas, 597 tiveram a ordem decidida pelo score; 0 precisaram de desempate.
- Partida com mais ações perdidas por controle: Fase de 64 15 — tioorochitwitch × mount, com 8.
- Maior absorção da Égide de Mana num golpe: 513 de dano, em Fase de 64 8 — NOBRU × aspaszin.
- Leis de interação disparadas: FERIDA SÉPTICA ×6, COLAPSO MENTAL ×5, FERIDA ABERTA ×3, PÂNICO ×3.
- 33 das 63 vitórias saíram sem nenhum crítico do vencedor.
- Em 1 partida(s) o vencedor terminou com HP atual acima do teto do fim da luta, como aspaszin (G43) em Fase de 64 8 — NOBRU × aspaszin (3894 de HP com teto 3581, contra 4477 no início): `frailty` corta o HP máximo e o motor não corta o HP atual.

## Auditoria resumida das 63 partidas

Cada partida rodou sem instrumentação e auditada, com a mesma seed. As verificações são as da Copa 01: ações, ordem, leituras de iniciativa, passos, HP/MP por rodada, estado completo por rodada, eventos do motor, resultado, conclusividade e posição final do gerador; e a coerência do trace com o motor (sorteios classificados, contagem igual à do gerador, dano e MP por passo, ações executadas).

| Partida | Seed | Rodadas | Sorteios | Fidelidade | Coerência |
|---|---|---|---|---|---|
| Fase de 64 1 — Forever × RazaH | `1276147252682839545` | 4 | 9 | idêntica | ok |
| Fase de 64 2 — yayahuz × bakzera | `564756010209876112` | 23 | 89 | idêntica | ok |
| Fase de 64 3 — dona × aXtLOL | `14505410068851618312` | 9 | 36 | idêntica | ok |
| Fase de 64 4 — brino × Neskwga | `13545221713024457720` | 20 | 97 | idêntica | ok |
| Fase de 64 5 — sacy × fnxLNTC | `9029261661178098076` | 7 | 34 | idêntica | ok |
| Fase de 64 6 — brtt × furq | `16096858426396843879` | 3 | 12 | idêntica | ok |
| Fase de 64 7 — k13tv × loud_thurzin | `3232498854063970220` | 12 | 41 | idêntica | ok |
| Fase de 64 8 — NOBRU × aspaszin | `7159840557879327360` | 4 | 15 | idêntica | ok |
| Fase de 64 9 — liminhag0d × Bisteconee | `18192568439522344477` | 6 | 37 | idêntica | ok |
| Fase de 64 10 — babi × jovirone | `7585000514516361731` | 12 | 34 | idêntica | ok |
| Fase de 64 11 — xandfps × Felps | `3972462507393710712` | 14 | 36 | idêntica | ok |
| Fase de 64 12 — casimito × Gaules | `16831186955136908409` | 5 | 16 | idêntica | ok |
| Fase de 64 13 — coldzin × PlayHard | `13003453084419314162` | 7 | 32 | idêntica | ok |
| Fase de 64 14 — blackoutz × JonVlogs | `13577834637185633063` | 4 | 11 | idêntica | ok |
| Fase de 64 15 — tioorochitwitch × mount | `734813972235294848` | 16 | 36 | idêntica | ok |
| Fase de 64 16 — suetam1v4 × MeikodRJ | `5616022084380011036` | 5 | 20 | idêntica | ok |
| Fase de 64 17 — belrodrigues × Tealzlol | `8852153440130150304` | 6 | 34 | idêntica | ok |
| Fase de 64 18 — TheBurntPeanut × SkipNhO | `8721210466602292163` | 11 | 55 | idêntica | ok |
| Fase de 64 19 — Baiano × G0ularte | `5671513696900419138` | 9 | 30 | idêntica | ok |
| Fase de 64 20 — jukes × gafallen | `1817340695540484023` | 11 | 49 | idêntica | ok |
| Fase de 64 21 — fer × Bagi | `3315330788876156439` | 6 | 31 | idêntica | ok |
| Fase de 64 22 — lubatv × Hayashii | `15955446086312003275` | 5 | 14 | idêntica | ok |
| Fase de 64 23 — frttt × PaulinhoLOKObr | `13647429566868377544` | 4 | 12 | idêntica | ok |
| Fase de 64 24 — Tenz × Coringa | `10172409037477872466` | 24 | 104 | idêntica | ok |
| Fase de 64 25 — tteuw × YoDa | `6811398301582065085` | 12 | 46 | idêntica | ok |
| Fase de 64 26 — alanzoka × Patriota | `3956753177955526443` | 5 | 21 | idêntica | ok |
| Fase de 64 27 — sofiaespanha × DavyJones | `16376724242456928258` | 8 | 38 | idêntica | ok |
| Fase de 64 28 — Smzinho × RNakano | `8705380721711465627` | 6 | 22 | idêntica | ok |
| Fase de 64 29 — XANDAOOGOD × gabepeixe | `9358423812746425229` | 9 | 34 | idêntica | ok |
| Fase de 64 30 — yeTz × Dilera | `11695585345081819962` | 4 | 16 | idêntica | ok |
| Fase de 64 31 — LuquEt4 × calango | `17575010425553476582` | 8 | 43 | idêntica | ok |
| Fase de 64 32 — boltz × hastad | `2272127964721152814` | 7 | 20 | idêntica | ok |
| Fase de 32 1 — Forever × bakzera | `8562169872728424794` | 3 | 9 | idêntica | ok |
| Fase de 32 2 — dona × brino | `10537839222058908872` | 13 | 61 | idêntica | ok |
| Fase de 32 3 — sacy × furq | `8364832807771394593` | 3 | 13 | idêntica | ok |
| Fase de 32 4 — k13tv × aspaszin | `13420971126866494973` | 4 | 14 | idêntica | ok |
| Fase de 32 5 — liminhag0d × babi | `1982898959702197520` | 6 | 21 | idêntica | ok |
| Fase de 32 6 — Felps × casimito | `10511953610061698433` | 13 | 40 | idêntica | ok |
| Fase de 32 7 — coldzin × blackoutz | `1924334077511213662` | 8 | 34 | idêntica | ok |
| Fase de 32 8 — tioorochitwitch × MeikodRJ | `11215953123595852302` | 11 | 54 | idêntica | ok |
| Fase de 32 9 — Tealzlol × SkipNhO | `3646511995625357798` | 5 | 27 | idêntica | ok |
| Fase de 32 10 — Baiano × gafallen | `9185615275984556589` | 9 | 35 | idêntica | ok |
| Fase de 32 11 — fer × Hayashii | `16407087863604853934` | 4 | 18 | idêntica | ok |
| Fase de 32 12 — frttt × Coringa | `1455861312395978412` | 4 | 11 | idêntica | ok |
| Fase de 32 13 — tteuw × Patriota | `7594704525375918654` | 11 | 47 | idêntica | ok |
| Fase de 32 14 — DavyJones × RNakano | `12761548428170422022` | 9 | 31 | idêntica | ok |
| Fase de 32 15 — gabepeixe × Dilera | `3609054038807378005` | 17 | 59 | idêntica | ok |
| Fase de 32 16 — LuquEt4 × boltz | `6600561904627291676` | 7 | 32 | idêntica | ok |
| Oitavas 1 — Forever × dona | `7721911110119933238` | 4 | 9 | idêntica | ok |
| Oitavas 2 — furq × aspaszin | `15223661065245555588` | 9 | 51 | idêntica | ok |
| Oitavas 3 — babi × Felps | `8947670749788689304` | 3 | 13 | idêntica | ok |
| Oitavas 4 — coldzin × MeikodRJ | `1996998103972129108` | 11 | 56 | idêntica | ok |
| Oitavas 5 — SkipNhO × gafallen | `18338950524184299450` | 17 | 85 | idêntica | ok |
| Oitavas 6 — Hayashii × frttt | `14378117799292324843` | 8 | 34 | idêntica | ok |
| Oitavas 7 — Patriota × RNakano | `4383623172331005430` | 9 | 34 | idêntica | ok |
| Oitavas 8 — gabepeixe × LuquEt4 | `11812667810472321170` | 14 | 91 | idêntica | ok |
| Quartas 1 — Forever × aspaszin | `2429615464796324789` | 10 | 30 | idêntica | ok |
| Quartas 2 — babi × MeikodRJ | `6243117697485473690` | 14 | 54 | idêntica | ok |
| Quartas 3 — SkipNhO × frttt | `16773338749684197360` | 24 | 105 | idêntica | ok |
| Quartas 4 — RNakano × LuquEt4 | `12923774737184472967` | 6 | 38 | idêntica | ok |
| Semifinal 1 — aspaszin × babi | `4403250353137019007` | 6 | 18 | idêntica | ok |
| Semifinal 2 — SkipNhO × LuquEt4 | `17702946004754375332` | 34 | 245 | idêntica | ok |
| Final — aspaszin × SkipNhO | `3846561752997802364` | 15 | 77 | idêntica | ok |

## As 63 partidas em detalhe

### Fase de 64: detalhes

#### Fase de 64 1 — Forever × RazaH

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G41 | Forever | Mago | 23 | 29.29 | Grilhões de Gelo, Raio Congelante, Lasca de Gelo, Tempestade | congelar e quebrar |
| p2 | G51 | RazaH | Ladino | 17 | 23.99 | Marca do Caçador, Olho Treinado, Flecha pela Fresta, Ataque Furtivo | arco neutro de alto poder |

- Seed da partida: `1276147252682839545`
- Rodadas: **4**
- Vencedor: **Forever** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4477/4477 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Forever | RazaH |
|---|---|---|
| Dano causado (golpes + DoT) | 4064 (4064 + 0) | 0 (0 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 423 | 38 |
| Skills / ataques básicos | 4 / 0 | 1 / 0 |
| Acertos / erros | 2 / 0 | 0 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 4 | 0 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- Forever aplicou: frozen (rodada 1), vulnerable (rodada 1), slowed (rodada 2)
- Forever tentou sem sucesso: frozen (rodada 3), stun (rodada 4)
- RazaH ativou: Olho Treinado ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Forever (p1) | RazaH (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −117 | Olho Treinado — cancelada por controle | 4477 / 2367 | 1687 / 552 |
| 2 | p1 → p2 (score) | Lasca de Gelo — executada, dano 1754, MP −73 | Olho Treinado — cancelada por controle | 4477 / 613 | 1670 / 552 |
| 3 | p1 → p2 (score) | Raio Congelante — executada, dano 0, MP −91 | Olho Treinado — executada, dano 0, MP −38 | 4477 / 613 | 1635 / 514 |
| 4 | p1 → p2 (score) | Tempestade — executada, dano 2310, MP −142 | Marca do Caçador — cancelada por morte | 4477 / -1697 | 1549 / 514 |

#### Fase de 64 2 — yayahuz × bakzera

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G37 | yayahuz | Mago | 21 | 25.49 | Escudo Mágico, Pele de Quartzo, Couro Batido, Bola de Fogo | defesa em camadas |
| p2 | G58 | bakzera | Ladino | 20 | 25.95 | Gancho e Corda, Marcar a Presa, Corte de Tendão, Ataque Furtivo | atordoar e expor |

- Seed da partida: `564756010209876112`
- Rodadas: **23**
- Vencedor: **bakzera** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1560/2704 (57.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | yayahuz | bakzera |
|---|---|---|
| Dano causado (golpes + DoT) | 1262 (1262 + 0) | 3722 (3178 + 544) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 118 (0 + 118) |
| MP gasto em ações | 1210 | 1090 |
| Skills / ataques básicos | 19 / 0 | 17 / 6 |
| Acertos / erros | 2 / 1 | 17 / 2 |
| Críticos (dano) | 0 (0) | 4 (904) |
| Agiu primeiro (rodadas) | 0 | 23 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- yayahuz ativou: Escudo Mágico ×6, Pele de Quartzo ×5, Couro Batido ×5
- Égide de yayahuz: absorveu 553 de dano por 272 MP
- bakzera aplicou: stun (rodada 1), vulnerable (rodada 1), vulnerable (rodada 12), stun (rodada 16), vulnerable (rodada 16), poison (rodada 17), slowed (rodada 18), stun (rodada 20), poison (rodada 20), poison (rodada 22), poison (rodada 23), slowed (rodada 23)
- bakzera tentou sem sucesso: stun (rodada 3), poison (rodada 3), slowed (rodada 3), stun (rodada 4), poison (rodada 4), stun (rodada 5), poison (rodada 5), stun (rodada 6), stun (rodada 7), poison (rodada 7), vulnerable (rodada 7), stun (rodada 8), poison (rodada 8), slowed (rodada 8), stun (rodada 9), poison (rodada 9), stun (rodada 10), poison (rodada 10), stun (rodada 11), stun (rodada 12), poison (rodada 12), stun (rodada 13), poison (rodada 13), slowed (rodada 13), stun (rodada 14), poison (rodada 14), stun (rodada 17), vulnerable (rodada 17), stun (rodada 18), poison (rodada 18), stun (rodada 19), poison (rodada 19), stun (rodada 21), poison (rodada 21), stun (rodada 22), stun (rodada 23)

Rodada a rodada:

| Rodada | Ordem (critério) | yayahuz (p1) | bakzera (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Mágico — cancelada por controle | Gancho e Corda — executada, dano 0, MP −83 | 3659 / 2704 | 1350 / 692 |
| 2 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Marcar a Presa — executada, dano 0, MP −62 | 3659 / 2704 | 1271 / 645 |
| 3 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −60 | Corte de Tendão — executada, dano 347, MP −58 | 3312 / 2704 | 1228 / 602 |
| 4 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −56 | Ataque Furtivo — executada, dano 286, MP −55 | 3026 / 2704 | 1194 / 562 |
| 5 | p2 → p1 (score) | Bola de Fogo — executada, dano 631, MP −52 | Ataque básico — executada, dano 53 | 2973 / 2073 | 1185 / 577 |
| 6 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Gancho e Corda — executada, dano 0, MP −83 | 2973 / 2073 | 1153 / 509 |
| 7 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −60 | Marcar a Presa — executada, dano 319, MP −62 | 2654 / 2088 | 1112 / 462 |
| 8 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −56 | Corte de Tendão — executada, dano 182, MP −58 | 2472 / 2097 | 1087 / 419 |
| 9 | p2 → p1 (score) | Bola de Fogo — executada, dano 631, MP −52 | Ataque Furtivo — executada, dano 78, MP −55 | 2394 / 1469 | 1076 / 379 |
| 10 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Ataque básico — executada, dano 107 | 2287 / 1474 | 1035 / 394 |
| 11 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −60 | Gancho e Corda — executada, dano 0, MP −83 | 2287 / 1474 | 1022 / 326 |
| 12 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −56 | Marcar a Presa — executada, dano 176, MP −62 | 2111 / 1482 | 998 / 279 |
| 13 | p2 → p1 (score) | Bola de Fogo — executada, dano 0, MP −52 | Corte de Tendão — executada, dano 130, MP −58 | 1981 / 1488 | 982 / 236 |
| 14 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Ataque Furtivo — executada, dano 312, MP −55 | 1669 / 1503 | 923 / 196 |
| 15 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −60 | Ataque básico — executada, dano 0 | 1669 / 1503 | 910 / 211 |
| 16 | p2 → p1 (score) | Couro Batido — cancelada por controle | Gancho e Corda — executada, dano 0, MP −83 | 1669 / 1503 | 957 / 143 |
| 17 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −56 | Marcar a Presa — executada, dano 201, MP −62 | 1414 / 1513 | 931 / 96 |
| 18 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Corte de Tendão — executada, dano 286, MP −58 | 1074 / 1527 | 874 / 53 |
| 19 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −60 | Ataque básico — executada, dano 135 | 885 / 1533 | 850 / 68 |
| 20 | p2 → p1 (score) | Bola de Fogo — cancelada por controle | Ataque Furtivo — executada, dano 125, MP −55 | 651 / 1539 | 887 / 28 |
| 21 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −56 | Ataque básico — executada, dano 81 | 461 / 1543 | 871 / 43 |
| 22 | p2 → p1 (score) | Escudo Mágico — executada, dano 0, MP −79 | Ataque básico — executada, dano 171 | 126 / 1551 | 824 / 58 |
| 23 | p2 → p1 (score) | Pele de Quartzo — cancelada por morte | Corte de Tendão — executada, dano 189, MP −58 | -63 / 1560 | 808 / 15 |

#### Fase de 64 3 — dona × aXtLOL

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G54 | dona | Ladino | 16 | 25.60 | Hora do Lobo, Lâmina no Escuro, Ataque Furtivo, Sangria Lenta | adaga: sangramento e roubo de vida |
| p2 | G15 | aXtLOL | Guerreiro | 20 | 25.72 | Tremor de Bigorna, A Mão que Não Treme, Golpe Poderoso, Baluarte | maça: atordoamento e crítico |

- Seed da partida: `14505410068851618312`
- Rodadas: **9**
- Vencedor: **dona** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 572/2114 (27.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | dona | aXtLOL |
|---|---|---|
| Dano causado (golpes + DoT) | 4328 (1857 + 2471) | 1894 (1894 + 0) |
| Cura (skill + roubo de vida) | 352 (0 + 352) | 94 (0 + 94) |
| MP gasto em ações | 388 | 488 |
| Skills / ataques básicos | 8 / 0 | 7 / 1 |
| Acertos / erros | 6 / 0 | 2 / 2 |
| Críticos (dano) | 6 (1857) | 2 (1894) |
| Agiu primeiro (rodadas) | 9 | 0 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- dona aplicou: bleed (rodada 2), vulnerable (rodada 3), bleed (rodada 4), bleed (rodada 7), bleed (rodada 7), bleed (rodada 8), vulnerable (rodada 8), bleed (rodada 9)
- dona tentou sem sucesso: poison (rodada 2), bleed (rodada 2), bleed (rodada 3), poison (rodada 3), poison (rodada 4), poison (rodada 7), poison (rodada 8), poison (rodada 9)
- dona ativou: Sangria Lenta ×2
- aXtLOL aplicou: stun (rodada 4)
- aXtLOL tentou sem sucesso: stun (rodada 5)
- aXtLOL ativou: A Mão que Não Treme ×2, Baluarte ×2
- Leis disparadas por aXtLOL: FERIDA ABERTA (rodada 4), FERIDA ABERTA (rodada 9)

Rodada a rodada:

| Rodada | Ordem (critério) | dona (p1) | aXtLOL (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Sangria Lenta — executada, dano 0, MP −53 | A Mão que Não Treme — executada, dano 0, MP −104 | 2114 / 3865 | 440 / 413 |
| 2 | p1 → p2 (score) | Hora do Lobo — executada, dano 583, MP −65 | Baluarte — executada, dano 0, MP −75 | 2114 / 3128 | 384 / 348 |
| 3 | p1 → p2 (score) | Lâmina no Escuro — executada, dano 206, MP −41 | Tremor de Bigorna — executada, dano 0, MP −56 | 2114 / 2768 | 352 / 302 |
| 4 | p1 → p2 (score) | Ataque Furtivo — executada, dano 161, MP −35 | Golpe Poderoso — executada, dano 1366, MP −37 | 748 / 2366 | 326 / 275 |
| 5 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 528 | 220 / 2083 | 335 / 285 |
| 6 | p1 → p2 (score) | Sangria Lenta — executada, dano 0, MP −53 | Golpe Poderoso — executada, dano 0, MP −37 | 220 / 2083 | 291 / 258 |
| 7 | p1 → p2 (score) | Hora do Lobo — executada, dano 416, MP −65 | A Mão que Não Treme — executada, dano 0, MP −104 | 398 / 1358 | 235 / 164 |
| 8 | p1 → p2 (score) | Lâmina no Escuro — executada, dano 330, MP −41 | Baluarte — executada, dano 0, MP −75 | 539 / 565 | 203 / 99 |
| 9 | p1 → p2 (score) | Ataque Furtivo — executada, dano 161, MP −35 | Tremor de Bigorna — cancelada por morte | 572 / -369 | 177 / 109 |

#### Fase de 64 4 — brino × Neskwga

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G16 | brino | Guerreiro | 20 | 25.26 | Golpe Poderoso, Respiração de Forja, Fôlego de Marcha, Quebra-Ossos | vida máxima e lentidão |
| p2 | G07 | Neskwga | Guerreiro | 18 | 24.57 | Golpe Poderoso, Tomar Fôlego, Curativo de Campo, Investida | sustentação: cura e roubo de vida |

- Seed da partida: `13545221713024457720`
- Rodadas: **20**
- Vencedor: **brino** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2439/4165 (58.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | brino | Neskwga |
|---|---|---|
| Dano causado (golpes + DoT) | 4825 (4825 + 0) | 1962 (1962 + 0) |
| Cura (skill + roubo de vida) | 236 (0 + 236) | 1517 (752 + 765) |
| MP gasto em ações | 697 | 670 |
| Skills / ataques básicos | 13 / 7 | 18 / 0 |
| Acertos / erros | 13 / 1 | 8 / 4 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 20 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- brino aplicou: slowed (rodada 3), stun (rodada 6), slowed (rodada 9)
- brino tentou sem sucesso: bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), bleed (rodada 6), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 18), bleed (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20)
- brino ativou: Respiração de Forja ×2, Fôlego de Marcha ×2
- Neskwga tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 5), stun (rodada 9), bleed (rodada 9), stun (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 15), stun (rodada 16), bleed (rodada 16)
- Neskwga ativou: Curativo de Campo ×4

Rodada a rodada:

| Rodada | Ordem (critério) | brino (p1) | Neskwga (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Respiração de Forja — executada, dano 0, MP −91 | Curativo de Campo — executada, dano 0, MP −49 | 4165 / 3136 | 426 / 457 |
| 2 | p1 → p2 (score) | Fôlego de Marcha — executada, dano 0, MP −58 | Golpe Poderoso — executada, dano 0, MP −29 | 4165 / 3136 | 378 / 438 |
| 3 | p1 → p2 (score) | Quebra-Ossos — executada, dano 0, MP −70 | Investida — executada, dano 271, MP −33 | 3894 / 3136 | 318 / 415 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 492, MP −37 | Golpe Poderoso — executada, dano 243, MP −29 | 3675 / 2743 | 291 / 396 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Investida — executada, dano 276, MP −33 | 3412 / 2595 | 301 / 373 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 492, MP −37 | Curativo de Campo — cancelada por controle | 3436 / 2103 | 274 / 383 |
| 7 | p1 → p2 (score) | Respiração de Forja — executada, dano 0, MP −91 | Curativo de Campo — executada, dano 0, MP −49 | 3436 / 2103 | 193 / 344 |
| 8 | p1 → p2 (score) | Fôlego de Marcha — executada, dano 0, MP −58 | Golpe Poderoso — executada, dano 0, MP −29 | 3436 / 2103 | 145 / 325 |
| 9 | p1 → p2 (score) | Quebra-Ossos — executada, dano 0, MP −70 | Investida — executada, dano 271, MP −33 | 3165 / 2254 | 85 / 302 |
| 10 | p1 → p2 (score) | Golpe Poderoso — executada, dano 455, MP −37 | Golpe Poderoso — executada, dano 225, MP −29 | 2962 / 1891 | 58 / 283 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Investida — executada, dano 0, MP −33 | 2975 / 1630 | 68 / 260 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 455, MP −37 | Curativo de Campo — executada, dano 0, MP −49 | 2997 / 1175 | 41 / 221 |
| 13 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Tomar Fôlego — executada, dano 0, MP −53 | 3010 / 1290 | 51 / 178 |
| 14 | p1 → p2 (score) | Golpe Poderoso — executada, dano 455, MP −37 | Golpe Poderoso — executada, dano 225, MP −29 | 2807 / 961 | 24 / 159 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 226, MP −33 | 2581 / 1053 | 34 / 136 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Golpe Poderoso — executada, dano 225, MP −29 | 2369 / 884 | 44 / 117 |
| 17 | p1 → p2 (score) | Golpe Poderoso — executada, dano 455, MP −37 | Curativo de Campo — executada, dano 0, MP −49 | 2391 / 429 | 17 / 78 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Tomar Fôlego — executada, dano 0, MP −53 | 2404 / 544 | 27 / 35 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 261 | Golpe Poderoso — executada, dano 0, MP −29 | 2417 / 283 | 37 / 16 |
| 20 | p1 → p2 (score) | Golpe Poderoso — executada, dano 455, MP −37 | Ataque básico — cancelada por morte | 2439 / -172 | 10 / 16 |

#### Fase de 64 5 — sacy × fnxLNTC

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G57 | sacy | Ladino | 18 | 27.45 | Testamento do Ladrão, Duas Mãos, Um Tempo, Envenenar, Ataque Furtivo | duas armas e veneno |
| p2 | G01 | fnxLNTC | Guerreiro | 16 | 21.34 | Golpe Poderoso, Baluarte, Couraça Improvisada, Tremor de Bigorna | defesa: reduções de dano com maça |

- Seed da partida: `9029261661178098076`
- Rodadas: **7**
- Vencedor: **sacy** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2166/2216 (97.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | sacy | fnxLNTC |
|---|---|---|
| Dano causado (golpes + DoT) | 3139 (1480 + 1659) | 281 (281 + 0) |
| Cura (skill + roubo de vida) | 231 (0 + 231) | 14 (0 + 14) |
| MP gasto em ações | 392 | 207 |
| Skills / ataques básicos | 6 / 1 | 6 / 0 |
| Acertos / erros | 6 / 0 | 1 / 2 |
| Críticos (dano) | 1 (391) | 0 (0) |
| Agiu primeiro (rodadas) | 7 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- sacy aplicou: poison (rodada 1), poison (rodada 2), bleed (rodada 3), poison (rodada 3), poison (rodada 4), poison (rodada 5), poison (rodada 7), poison (rodada 7)
- sacy tentou sem sucesso: bleed (rodada 2), poison (rodada 2), bleed (rodada 3), bleed (rodada 4), bleed (rodada 5), bleed (rodada 6), poison (rodada 6), bleed (rodada 6), bleed (rodada 7)
- fnxLNTC tentou sem sucesso: stun (rodada 3)
- fnxLNTC ativou: Baluarte ×2, Couraça Improvisada ×1
- Leis disparadas por fnxLNTC: FERIDA SÉPTICA (rodada 3), FERIDA SÉPTICA (rodada 4), FERIDA SÉPTICA (rodada 5)

Rodada a rodada:

| Rodada | Ordem (critério) | sacy (p1) | fnxLNTC (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Envenenar — executada, dano 0, MP −94 | Baluarte — executada, dano 0, MP −47 | 2216 / 3063 | 666 / 281 |
| 2 | p1 → p2 (score) | Testamento do Ladrão — executada, dano 391, MP −82 | Couraça Improvisada — executada, dano 0, MP −31 | 2216 / 2579 | 599 / 256 |
| 3 | p1 → p2 (score) | Duas Mãos, Um Tempo — executada, dano 158, MP −45 | Golpe Poderoso — executada, dano 281, MP −23 | 1935 / 2172 | 569 / 239 |
| 4 | p1 → p2 (score) | Ataque Furtivo — executada, dano 90, MP −44 | Tremor de Bigorna — executada, dano 0, MP −36 | 1957 / 1772 | 540 / 209 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 179 | Golpe Poderoso — executada, dano 0, MP −23 | 2001 / 1236 | 555 / 192 |
| 6 | p1 → p2 (score) | Duas Mãos, Um Tempo — executada, dano 402, MP −45 | Baluarte — executada, dano 0, MP −47 | 2101 / 477 | 525 / 151 |
| 7 | p1 → p2 (score) | Testamento do Ladrão — executada, dano 260, MP −82 | Couraça Improvisada — cancelada por morte | 2166 / -16 | 458 / 157 |

#### Fase de 64 6 — brtt × furq

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G44 | brtt | Ladino | 14 | 21.11 | Ataque Furtivo, Picada Certeira, Lâmina no Escuro, Leitura de Guarda | adaga e crítico |
| p2 | G63 | furq | Ladino | 23 | 28.48 | Hora do Arauto, Pó nos Olhos, Ataque Furtivo, Assassinato | medo |

- Seed da partida: `16096858426396843879`
- Rodadas: **3**
- Vencedor: **furq** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3799/3799 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | brtt | furq |
|---|---|---|
| Dano causado (golpes + DoT) | 0 (0 + 0) | 3528 (3528 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 31 | 346 |
| Skills / ataques básicos | 1 / 0 | 3 / 0 |
| Acertos / erros | 0 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 3 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- brtt ativou: Leitura de Guarda ×1
- furq aplicou: fear (rodada 1), vulnerable (rodada 1), stun (rodada 2), fear (rodada 3)
- furq tentou sem sucesso: poison (rodada 2), fear (rodada 2), stun (rodada 3), poison (rodada 3)

Rodada a rodada:

| Rodada | Ordem (critério) | brtt (p1) | furq (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Leitura de Guarda — executada, dano 0, MP −31 | Hora do Arauto — executada, dano 0, MP −140 | 1370 / 3799 | 362 / 949 |
| 2 | p2 → p1 (score) | Ataque Furtivo — cancelada por controle | Ataque Furtivo — executada, dano 1308, MP −77 | 62 / 3799 | 369 / 893 |
| 3 | p2 → p1 (score) | Ataque Furtivo — cancelada por morte | Assassinato — executada, dano 2220, MP −129 | -2158 / 3799 | 369 / 785 |

#### Fase de 64 7 — k13tv × loud_thurzin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G21 | k13tv | Guerreiro | 20 | 26.75 | Postura Impecável, Grito de Guerra, Cutelada, Golpe Poderoso | acúmulo de Força |
| p2 | G61 | loud_thurzin | Ladino | 21 | 28.60 | Evasão Perfeita, Leitura de Terreno, Ataque Furtivo, Lâmina no Escuro | evasão máxima com adaga |

- Seed da partida: `3232498854063970220`
- Rodadas: **12**
- Vencedor: **k13tv** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1485/3790 (39.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | k13tv | loud_thurzin |
|---|---|---|
| Dano causado (golpes + DoT) | 3107 (3107 + 0) | 2458 (2458 + 0) |
| Cura (skill + roubo de vida) | 153 (0 + 153) | 63 (0 + 63) |
| MP gasto em ações | 615 | 842 |
| Skills / ataques básicos | 9 / 2 | 11 / 1 |
| Acertos / erros | 3 / 3 | 6 / 0 |
| Críticos (dano) | 0 (0) | 1 (686) |
| Agiu primeiro (rodadas) | 0 | 12 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- k13tv tentou sem sucesso: stun (rodada 4), bleed (rodada 4), stun (rodada 9), bleed (rodada 9), stun (rodada 12), bleed (rodada 12)
- k13tv ativou: Postura Impecável ×2, Grito de Guerra ×3
- loud_thurzin aplicou: stun (rodada 8)
- loud_thurzin tentou sem sucesso: stun (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), vulnerable (rodada 4), stun (rodada 6), poison (rodada 6), poison (rodada 8), vulnerable (rodada 8), stun (rodada 10), poison (rodada 10), stun (rodada 11), poison (rodada 11)
- loud_thurzin ativou: Evasão Perfeita ×3, Leitura de Terreno ×3

Rodada a rodada:

| Rodada | Ordem (critério) | k13tv (p1) | loud_thurzin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −104 | Evasão Perfeita — executada, dano 0, MP −83 | 3790 / 3029 | 413 / 785 |
| 2 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −71 | Leitura de Terreno — executada, dano 0, MP −88 | 3790 / 3029 | 352 / 714 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 0, MP −60 | Ataque Furtivo — executada, dano 686, MP −61 | 3104 / 3029 | 302 / 670 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 1214, MP −37 | Lâmina no Escuro — executada, dano 472, MP −73 | 2692 / 1815 | 275 / 614 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Evasão Perfeita — executada, dano 0, MP −83 | 2692 / 1815 | 285 / 548 |
| 6 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −71 | Ataque Furtivo — executada, dano 312, MP −61 | 2380 / 1830 | 224 / 504 |
| 7 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −104 | Leitura de Terreno — executada, dano 0, MP −88 | 2380 / 1830 | 130 / 433 |
| 8 | p2 → p1 (score) | Cutelada — cancelada por controle | Lâmina no Escuro — executada, dano 472, MP −73 | 1908 / 1853 | 140 / 377 |
| 9 | p2 → p1 (score) | Cutelada — executada, dano 1078, MP −60 | Evasão Perfeita — executada, dano 0, MP −83 | 1961 / 775 | 90 / 311 |
| 10 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −71 | Ataque Furtivo — executada, dano 312, MP −61 | 1649 / 790 | 29 / 267 |
| 11 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 204 | 1445 / 800 | 39 / 284 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 815, MP −37 | Leitura de Terreno — executada, dano 0, MP −88 | 1485 / -15 | 12 / 213 |

#### Fase de 64 8 — NOBRU × aspaszin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G38 | NOBRU | Mago | 20 | 26.99 | Maldição de Cinzas, Paciência do Coveiro, Marca Ardente, Bola de Fogo | veneno e fragilidade |
| p2 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |

- Seed da partida: `7159840557879327360`
- Rodadas: **4**
- Vencedor: **aspaszin** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3894/3581 (108.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | NOBRU | aspaszin |
|---|---|---|
| Dano causado (golpes + DoT) | 583 (424 + 159) | 5538 (5538 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 187 | 414 |
| Skills / ataques básicos | 3 / 0 | 4 / 0 |
| Acertos / erros | 1 / 1 | 2 / 1 |
| Críticos (dano) | 0 (0) | 2 (5538) |
| Agiu primeiro (rodadas) | 0 | 4 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- NOBRU aplicou: poison (rodada 1), frailty (rodada 1)
- NOBRU tentou sem sucesso: poison (rodada 3), poison (rodada 3)
- Égide de NOBRU: absorveu 976 de dano por 487 MP
- aspaszin aplicou: fear (rodada 1), vulnerable (rodada 3)
- aspaszin tentou sem sucesso: vulnerable (rodada 1)
- Égide de aspaszin: absorveu 74 de dano por 37 MP

Rodada a rodada:

| Rodada | Ordem (critério) | NOBRU (p1) | aspaszin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Paciência do Coveiro — executada, dano 0, MP −100 | Hora do Arauto — executada, dano 0, MP −140 | 3187 / 4477 | 1106 / 1554 |
| 2 | p2 → p1 (score) | Maldição de Cinzas — executada, dano 0, MP −46 | Prisma de Devastação — executada, dano 0, MP −131 | 3187 / 4424 | 1104 / 1476 |
| 3 | p2 → p1 (score) | Marca Ardente — executada, dano 424, MP −41 | Lente de Obsidiana — executada, dano 2626, MP −78 | 561 / 3947 | 876 / 1414 |
| 4 | p2 → p1 (score) | Bola de Fogo — cancelada por morte | Bola de Fogo — executada, dano 2912, MP −65 | -2351 / 3894 | 620 / 1402 |

#### Fase de 64 9 — liminhag0d × Bisteconee

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G08 | liminhag0d | Guerreiro | 18 | 24.10 | Investida de Aríete, Pisada de Ferro, Golpe Poderoso, Postura de Muro | atordoar com espada e defesa |
| p2 | G45 | Bisteconee | Ladino | 15 | 21.22 | Ataque Furtivo, Flecha pela Fresta, Olho do Falcão, Chuva de Ferrões | arco: sangramento e crítico |

- Seed da partida: `18192568439522344477`
- Rodadas: **6**
- Vencedor: **liminhag0d** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1420/3021 (47.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | liminhag0d | Bisteconee |
|---|---|---|
| Dano causado (golpes + DoT) | 2311 (2311 + 0) | 1715 (992 + 723) |
| Cura (skill + roubo de vida) | 114 (0 + 114) | 36 (0 + 36) |
| MP gasto em ações | 225 | 218 |
| Skills / ataques básicos | 6 / 0 | 6 / 0 |
| Acertos / erros | 4 / 0 | 4 / 0 |
| Críticos (dano) | 0 (0) | 1 (297) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- liminhag0d tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 2), stun (rodada 3), bleed (rodada 3), slowed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 6)
- liminhag0d ativou: Postura de Muro ×2
- Bisteconee aplicou: bleed (rodada 4), bleed (rodada 4)
- Bisteconee tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), slowed (rodada 3), stun (rodada 4), stun (rodada 5), bleed (rodada 5)
- Bisteconee ativou: Olho do Falcão ×2

Rodada a rodada:

| Rodada | Ordem (critério) | liminhag0d (p1) | Bisteconee (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −43 | Olho do Falcão — executada, dano 0, MP −45 | 3021 / 1888 | 463 / 395 |
| 2 | p2 → p1 (score) | Investida de Aríete — executada, dano 663, MP −36 | Ataque Furtivo — executada, dano 222, MP −31 | 2832 / 1225 | 437 / 372 |
| 3 | p2 → p1 (score) | Pisada de Ferro — executada, dano 562, MP −38 | Flecha pela Fresta — executada, dano 214, MP −30 | 2646 / 673 | 409 / 350 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 509, MP −29 | Chuva de Ferrões — executada, dano 259, MP −36 | 2171 / 176 | 390 / 322 |
| 5 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −43 | Ataque Furtivo — executada, dano 297, MP −31 | 1633 / 190 | 357 / 299 |
| 6 | p2 → p1 (score) | Investida de Aríete — executada, dano 577, MP −36 | Olho do Falcão — executada, dano 0, MP −45 | 1420 / -387 | 331 / 262 |

#### Fase de 64 10 — babi × jovirone

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G39 | babi | Mago | 23 | 28.71 | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | carta lendária de dano |
| p2 | G09 | jovirone | Guerreiro | 18 | 23.18 | Golpe Poderoso, Baluarte, Couro Batido, Pacto de Ferro | tanque de maça com redução dupla |

- Seed da partida: `7585000514516361731`
- Rodadas: **12**
- Vencedor: **babi** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3070/4477 (68.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | babi | jovirone |
|---|---|---|
| Dano causado (golpes + DoT) | 3469 (3469 + 0) | 1407 (691 + 716) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 32 (0 + 32) |
| MP gasto em ações | 1251 | 514 |
| Skills / ataques básicos | 12 / 0 | 10 / 1 |
| Acertos / erros | 9 / 0 | 4 / 0 |
| Críticos (dano) | 1 (424) | 0 (0) |
| Agiu primeiro (rodadas) | 12 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- babi ativou: Foco do Estudante ×3
- Égide de babi: absorveu 120 de dano por 59 MP
- jovirone aplicou: bleed (rodada 5), bleed (rodada 8)
- jovirone tentou sem sucesso: stun (rodada 4), bleed (rodada 4), stun (rodada 5), stun (rodada 8), stun (rodada 10), bleed (rodada 10)
- jovirone ativou: Baluarte ×3, Couro Batido ×2, Pacto de Ferro ×2

Rodada a rodada:

| Rodada | Ordem (critério) | babi (p1) | jovirone (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Baluarte — executada, dano 0, MP −59 | 4477 / 3236 | 1618 / 447 |
| 2 | p1 → p2 (score) | Apocalipse — executada, dano 812, MP −242 | Couro Batido — executada, dano 0, MP −39 | 4477 / 2424 | 1429 / 418 |
| 3 | p1 → p2 (score) | Bola de Fogo — executada, dano 424, MP −65 | Pacto de Ferro — executada, dano 0, MP −86 | 4477 / 2000 | 1417 / 342 |
| 4 | p1 → p2 (score) | Relâmpago — executada, dano 224, MP −93 | Golpe Poderoso — executada, dano 199, MP −29 | 4278 / 1785 | 1360 / 323 |
| 5 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Ataque básico — executada, dano 108 | 4170 / 1790 | 1328 / 333 |
| 6 | p1 → p2 (score) | Bola de Fogo — executada, dano 332, MP −65 | Baluarte — executada, dano 0, MP −59 | 3991 / 1458 | 1316 / 284 |
| 7 | p1 → p2 (score) | Relâmpago — executada, dano 291, MP −93 | Couro Batido — executada, dano 0, MP −39 | 3812 / 1167 | 1276 / 255 |
| 8 | p1 → p2 (score) | Apocalipse — executada, dano 339, MP −242 | Golpe Poderoso — executada, dano 199, MP −29 | 3613 / 837 | 1070 / 236 |
| 9 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Pacto de Ferro — executada, dano 0, MP −86 | 3434 / 837 | 1047 / 160 |
| 10 | p1 → p2 (score) | Bola de Fogo — executada, dano 332, MP −65 | Golpe Poderoso — executada, dano 185, MP −29 | 3070 / 514 | 1019 / 141 |
| 11 | p1 → p2 (score) | Relâmpago — executada, dano 511, MP −93 | Baluarte — executada, dano 0, MP −59 | 3070 / 3 | 979 / 92 |
| 12 | p1 → p2 (score) | Bola de Fogo — executada, dano 204, MP −65 | Couro Batido — cancelada por morte | 3070 / -201 | 967 / 92 |

#### Fase de 64 11 — xandfps × Felps

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G25 | xandfps | Mago | 16 | 21.57 | Lasca de Gelo, Raio Congelante, Palavra de Torpor, Bola de Fogo | gelo: congelar e lentidão |
| p2 | G55 | Felps | Ladino | 19 | 27.10 | Dança das Lâminas, Sombra Rápida, Ataque Furtivo, Golpe nas Sombras | dança de lâminas e Agilidade |

- Seed da partida: `3972462507393710712`
- Rodadas: **14**
- Vencedor: **Felps** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1865/2415 (77.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | xandfps | Felps |
|---|---|---|
| Dano causado (golpes + DoT) | 591 (495 + 96) | 3095 (3095 + 0) |
| Cura (skill + roubo de vida) | 24 (0 + 24) | 41 (0 + 41) |
| MP gasto em ações | 396 | 547 |
| Skills / ataques básicos | 12 / 0 | 8 / 0 |
| Acertos / erros | 1 / 5 | 4 / 0 |
| Críticos (dano) | 0 (0) | 1 (611) |
| Agiu primeiro (rodadas) | 0 | 14 |
| Ações perdidas por controle | 1 | 6 |

Efeitos relevantes:
- xandfps aplicou: frozen (rodada 1), slowed (rodada 2), clouded (rodada 2), frozen (rodada 5), slowed (rodada 6), clouded (rodada 6), frozen (rodada 10), slowed (rodada 11), clouded (rodada 11), bleed (rodada 13)
- Égide de xandfps: absorveu 545 de dano por 272 MP
- Felps aplicou: weakened (rodada 5), stun (rodada 9), weakened (rodada 9), stun (rodada 14)
- Felps tentou sem sucesso: stun (rodada 5), poison (rodada 5), poison (rodada 9), stun (rodada 10), poison (rodada 10), poison (rodada 14), weakened (rodada 14)
- Felps ativou: Sombra Rápida ×4

Rodada a rodada:

| Rodada | Ordem (critério) | xandfps (p1) | Felps (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Raio Congelante — executada, dano 0, MP −41 | Sombra Rápida — executada, dano 0, MP −57 | 2490 / 2415 | 775 / 794 |
| 2 | p2 → p1 (score) | Palavra de Torpor — executada, dano 0, MP −29 | Dança das Lâminas — cancelada por controle | 2490 / 2415 | 787 / 811 |
| 3 | p2 → p1 (score) | Lasca de Gelo — executada, dano 0, MP −33 | Dança das Lâminas — cancelada por controle | 2490 / 2415 | 783 / 680 |
| 4 | p2 → p1 (score) | Bola de Fogo — executada, dano 0, MP −29 | Sombra Rápida — executada, dano 0, MP −57 | 2490 / 2415 | 787 / 623 |
| 5 | p2 → p1 (score) | Raio Congelante — executada, dano 0, MP −41 | Dança das Lâminas — executada, dano 828, MP −90 | 1662 / 2415 | 715 / 546 |
| 6 | p2 → p1 (score) | Palavra de Torpor — executada, dano 0, MP −29 | Ataque Furtivo — cancelada por controle | 1662 / 2415 | 728 / 563 |
| 7 | p2 → p1 (score) | Lasca de Gelo — executada, dano 0, MP −33 | Sombra Rápida — cancelada por controle | 1662 / 2415 | 737 / 576 |
| 8 | p2 → p1 (score) | Bola de Fogo — executada, dano 0, MP −29 | Sombra Rápida — executada, dano 0, MP −57 | 1662 / 2415 | 750 / 532 |
| 9 | p2 → p1 (score) | Raio Congelante — cancelada por controle | Dança das Lâminas — executada, dano 828, MP −90 | 834 / 2415 | 719 / 455 |
| 10 | p2 → p1 (score) | Raio Congelante — executada, dano 0, MP −41 | Ataque Furtivo — executada, dano 611, MP −49 | 223 / 2415 | 667 / 423 |
| 11 | p2 → p1 (score) | Palavra de Torpor — executada, dano 0, MP −29 | Sombra Rápida — cancelada por controle | 223 / 2415 | 680 / 440 |
| 12 | p2 → p1 (score) | Lasca de Gelo — executada, dano 0, MP −33 | Sombra Rápida — cancelada por controle | 223 / 2415 | 689 / 453 |
| 13 | p2 → p1 (score) | Bola de Fogo — executada, dano 495, MP −29 | Sombra Rápida — executada, dano 0, MP −57 | 247 / 1920 | 702 / 409 |
| 14 | p2 → p1 (score) | Raio Congelante — cancelada por morte | Dança das Lâminas — executada, dano 828, MP −90 | -581 / 1865 | 629 / 332 |

#### Fase de 64 12 — casimito × Gaules

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G35 | casimito | Mago | 20 | 25.83 | Hora Parada, Bola de Fogo, Marca Ardente, Explosão Arcana | sono e explosão |
| p2 | G10 | Gaules | Guerreiro | 18 | 24.68 | Golpe Poderoso, Sede de Batalha, Peso do Machado, Cutelada | machado com roubo de vida |

- Seed da partida: `16831186955136908409`
- Rodadas: **5**
- Vencedor: **casimito** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2809/3187 (88.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | casimito | Gaules |
|---|---|---|
| Dano causado (golpes + DoT) | 3297 (3297 + 0) | 378 (378 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 162 (0 + 162) |
| MP gasto em ações | 337 | 136 |
| Skills / ataques básicos | 5 / 0 | 3 / 0 |
| Acertos / erros | 4 / 0 | 1 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 5 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- casimito aplicou: sleep (rodada 1)
- casimito tentou sem sucesso: hexed (rodada 1), poison (rodada 3)
- Égide de casimito: absorveu 66 de dano por 33 MP
- Gaules tentou sem sucesso: stun (rodada 3), bleed (rodada 3)
- Gaules ativou: Sede de Batalha ×1

Rodada a rodada:

| Rodada | Ordem (critério) | casimito (p1) | Gaules (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Hora Parada — executada, dano 0, MP −116 | Sede de Batalha — cancelada por controle | 3187 / 3021 | 1190 / 506 |
| 2 | p1 → p2 (score) | Bola de Fogo — executada, dano 1003, MP −46 | Sede de Batalha — executada, dano 0, MP −66 | 3187 / 2018 | 1190 / 440 |
| 3 | p1 → p2 (score) | Marca Ardente — executada, dano 702, MP −41 | Golpe Poderoso — executada, dano 378, MP −29 | 2809 / 1478 | 1162 / 421 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 729, MP −46 | Peso do Machado — executada, dano 0, MP −41 | 2809 / 749 | 1162 / 390 |
| 5 | p1 → p2 (score) | Explosão Arcana — executada, dano 863, MP −88 | Golpe Poderoso — cancelada por morte | 2809 / -114 | 1120 / 390 |

#### Fase de 64 13 — coldzin × PlayHard

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G62 | coldzin | Ladino | 21 | 29.52 | Chuva de Ferrões, Olho do Falcão, Marca do Caçador, Flecha pela Fresta | arco: crítico e sangramento |
| p2 | G29 | PlayHard | Mago | 18 | 23.07 | Égide de Runas, Escudo Mágico, Bola de Fogo, Palavra de Pavor | tanque arcano |

- Seed da partida: `13003453084419314162`
- Rodadas: **7**
- Vencedor: **coldzin** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1577/3029 (52.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | coldzin | PlayHard |
|---|---|---|
| Dano causado (golpes + DoT) | 2949 (1723 + 1226) | 894 (894 + 0) |
| Cura (skill + roubo de vida) | -558 (0 + -558) | 43 (0 + 43) |
| MP gasto em ações | 491 | 292 |
| Skills / ataques básicos | 6 / 1 | 5 / 1 |
| Acertos / erros | 5 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 4 | 3 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- coldzin aplicou: bleed (rodada 2), bleed (rodada 3), slowed (rodada 4), poison (rodada 5), bleed (rodada 7)
- coldzin tentou sem sucesso: stun (rodada 2), poison (rodada 2), stun (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), stun (rodada 5), stun (rodada 7), poison (rodada 7)
- coldzin ativou: Olho do Falcão ×2
- PlayHard aplicou: fear (rodada 3), frailty (rodada 3)
- PlayHard tentou sem sucesso: bleed (rodada 4), bleed (rodada 5)
- PlayHard ativou: Égide de Runas ×2, Escudo Mágico ×1
- Leis disparadas por PlayHard: FERIDA SÉPTICA (rodada 5), FERIDA SÉPTICA (rodada 7)
- Égide de PlayHard: absorveu 302 de dano por 149 MP

Rodada a rodada:

| Rodada | Ordem (critério) | coldzin (p1) | PlayHard (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Égide de Runas — executada, dano 0, MP −73 | 3029 / 2615 | 780 / 1170 |
| 2 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 284, MP −71 | Escudo Mágico — executada, dano 0, MP −56 | 3029 / 2227 | 726 / 1113 |
| 3 | p2 → p1 (score) | Marca do Caçador — executada, dano 452, MP −113 | Palavra de Pavor — executada, dano 0, MP −53 | 2423 / 1671 | 630 / 1045 |
| 4 | p2 → p1 (score) | Flecha pela Fresta — executada, dano 393, MP −60 | Bola de Fogo — executada, dano 656, MP −37 | 1786 / 1101 | 587 / 998 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 224 | Ataque básico — executada, dano 238 | 1559 / 679 | 604 / 1003 |
| 6 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Égide de Runas — executada, dano 0, MP −73 | 1559 / 431 | 533 / 954 |
| 7 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 370, MP −71 | Escudo Mágico — cancelada por morte | 1577 / -291 | 479 / 946 |

#### Fase de 64 14 — blackoutz × JonVlogs

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G14 | blackoutz | Guerreiro | 20 | 27.10 | Veterania, Fio no Rebite, Golpe Poderoso, Golpe Devastador | evasão e crítico de espada |
| p2 | G30 | JonVlogs | Mago | 18 | 24.45 | Tempestade, Bola de Fogo, Relâmpago, Foco do Estudante | raio e atordoamento |

- Seed da partida: `13577834637185633063`
- Rodadas: **4**
- Vencedor: **blackoutz** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3790/3790 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | blackoutz | JonVlogs |
|---|---|---|
| Dano causado (golpes + DoT) | 2679 (2679 + 0) | 0 (0 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 259 | 212 |
| Skills / ataques básicos | 4 / 0 | 4 / 0 |
| Acertos / erros | 2 / 0 | 0 / 3 |
| Críticos (dano) | 2 (2679) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 4 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- blackoutz tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4)
- blackoutz ativou: Veterania ×1, Fio no Rebite ×1
- JonVlogs ativou: Foco do Estudante ×1
- Égide de JonVlogs: absorveu 472 de dano por 236 MP

Rodada a rodada:

| Rodada | Ordem (critério) | blackoutz (p1) | JonVlogs (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Veterania — executada, dano 0, MP −79 | Foco do Estudante — executada, dano 0, MP −43 | 3790 / 2540 | 438 / 1139 |
| 2 | p2 → p1 (score) | Fio no Rebite — executada, dano 0, MP −58 | Tempestade — executada, dano 0, MP −80 | 3790 / 2540 | 390 / 1082 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 1202, MP −37 | Bola de Fogo — executada, dano 0, MP −37 | 3790 / 1338 | 363 / 962 |
| 4 | p2 → p1 (score) | Golpe Devastador — executada, dano 1477, MP −85 | Relâmpago — executada, dano 0, MP −52 | 3790 / -139 | 288 / 803 |

#### Fase de 64 15 — tioorochitwitch × mount

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G59 | tioorochitwitch | Ladino | 21 | 28.48 | Morte Súbita, Ataque Furtivo, Assassinato, Respiração de Ladrão | carta lendária e crítico |
| p2 | G27 | mount | Mago | 16 | 21.92 | Sono Profundo, Bola de Fogo, Explosão Arcana, Dissonância | sono e maldição |

- Seed da partida: `734813972235294848`
- Rodadas: **16**
- Vencedor: **tioorochitwitch** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1424/3029 (47.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | tioorochitwitch | mount |
|---|---|---|
| Dano causado (golpes + DoT) | 3279 (3203 + 76) | 1763 (1400 + 363) |
| Cura (skill + roubo de vida) | 158 (0 + 158) | 21 (0 + 21) |
| MP gasto em ações | 774 | 692 |
| Skills / ataques básicos | 8 / 0 | 15 / 0 |
| Acertos / erros | 3 / 1 | 3 / 4 |
| Críticos (dano) | 1 (1788) | 0 (0) |
| Agiu primeiro (rodadas) | 16 | 0 |
| Ações perdidas por controle | 8 | 0 |

Efeitos relevantes:
- tioorochitwitch aplicou: poison (rodada 14), poison (rodada 16)
- tioorochitwitch tentou sem sucesso: stun (rodada 14), stun (rodada 15), poison (rodada 15), stun (rodada 16)
- tioorochitwitch ativou: Respiração de Ladrão ×4
- mount aplicou: sleep (rodada 1), bleed (rodada 3), sleep (rodada 5), sleep (rodada 9), hexed (rodada 10), clouded (rodada 10), hexed (rodada 14), clouded (rodada 14), bleed (rodada 15)
- mount tentou sem sucesso: hexed (rodada 2), hexed (rodada 6), bleed (rodada 12), sleep (rodada 13)
- Égide de mount: absorveu 564 de dano por 281 MP

Rodada a rodada:

| Rodada | Ordem (critério) | tioorochitwitch (p1) | mount (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Sono Profundo — executada, dano 0, MP −71 | 3029 / 2564 | 812 / 775 |
| 2 | p1 → p2 (score) | Morte Súbita — cancelada por controle | Dissonância — executada, dano 0, MP −31 | 3029 / 2564 | 829 / 794 |
| 3 | p1 → p2 (score) | Morte Súbita — cancelada por controle | Bola de Fogo — executada, dano 423, MP −29 | 2606 / 2564 | 846 / 815 |
| 4 | p1 → p2 (score) | Morte Súbita — executada, dano 0, MP −193 | Explosão Arcana — executada, dano 0, MP −56 | 2485 / 2564 | 670 / 790 |
| 5 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Sono Profundo — executada, dano 0, MP −71 | 2364 / 2564 | 631 / 769 |
| 6 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Dissonância — executada, dano 0, MP −31 | 2364 / 2564 | 648 / 788 |
| 7 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Bola de Fogo — executada, dano 0, MP −29 | 2364 / 2564 | 665 / 809 |
| 8 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Explosão Arcana — executada, dano 0, MP −56 | 2364 / 2564 | 682 / 790 |
| 9 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Sono Profundo — executada, dano 0, MP −71 | 2364 / 2564 | 643 / 769 |
| 10 | p1 → p2 (score) | Morte Súbita — cancelada por controle | Dissonância — executada, dano 0, MP −31 | 2364 / 2564 | 660 / 788 |
| 11 | p1 → p2 (score) | Morte Súbita — cancelada por controle | Bola de Fogo — executada, dano 0, MP −29 | 2364 / 2564 | 673 / 809 |
| 12 | p1 → p2 (score) | Morte Súbita — cancelada por controle | Explosão Arcana — executada, dano 554, MP −56 | 1810 / 2564 | 686 / 790 |
| 13 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Sono Profundo — executada, dano 0, MP −71 | 1810 / 2564 | 643 / 769 |
| 14 | p1 → p2 (score) | Morte Súbita — executada, dano 938, MP −193 | Dissonância — executada, dano 0, MP −31 | 1856 / 1588 | 467 / 706 |
| 15 | p1 → p2 (score) | Ataque Furtivo — executada, dano 477, MP −61 | Bola de Fogo — executada, dano 423, MP −29 | 1456 / 1094 | 419 / 685 |
| 16 | p1 → p2 (score) | Assassinato — executada, dano 1788, MP −103 | Explosão Arcana — cancelada por morte | 1424 / -694 | 329 / 528 |

#### Fase de 64 16 — suetam1v4 × MeikodRJ

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G03 | suetam1v4 | Guerreiro | 16 | 22.38 | Golpe Poderoso, Quebra-Guarda, Fio no Rebite, Golpe Devastador | crítico de espada |
| p2 | G19 | MeikodRJ | Guerreiro | 22 | 28.37 | Imortal, Golpe Poderoso, Golpe Devastador, Veterania | redução extrema com espada |

- Seed da partida: `5616022084380011036`
- Rodadas: **5**
- Vencedor: **MeikodRJ** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4506/4844 (93.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | suetam1v4 | MeikodRJ |
|---|---|---|
| Dano causado (golpes + DoT) | 442 (442 + 0) | 3289 (3289 + 0) |
| Cura (skill + roubo de vida) | 21 (0 + 21) | 104 (0 + 104) |
| MP gasto em ações | 115 | 504 |
| Skills / ataques básicos | 4 / 0 | 5 / 0 |
| Acertos / erros | 2 / 1 | 3 / 0 |
| Críticos (dano) | 1 (277) | 2 (2611) |
| Agiu primeiro (rodadas) | 0 | 5 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- suetam1v4 tentou sem sucesso: stun (rodada 3), vulnerable (rodada 3), stun (rodada 4)
- suetam1v4 ativou: Fio no Rebite ×1
- MeikodRJ tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5)
- MeikodRJ ativou: Imortal ×1, Veterania ×1

Rodada a rodada:

| Rodada | Ordem (critério) | suetam1v4 (p1) | MeikodRJ (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Fio no Rebite — executada, dano 0, MP −37 | Imortal — executada, dano 0, MP −204 | 2961 / 4844 | 291 / 444 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −23 | Veterania — executada, dano 0, MP −99 | 2961 / 4844 | 274 / 357 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 165, MP −32 | Golpe Poderoso — executada, dano 1172, MP −47 | 1797 / 4679 | 248 / 322 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 277, MP −23 | Golpe Devastador — executada, dano 1439, MP −107 | 371 / 4473 | 231 / 227 |
| 5 | p2 → p1 (score) | Fio no Rebite — cancelada por morte | Golpe Poderoso — executada, dano 678, MP −47 | -307 / 4506 | 231 / 192 |

#### Fase de 64 17 — belrodrigues × Tealzlol

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G49 | belrodrigues | Ladino | 16 | 24.57 | Joelho Torto, Corte de Passagem, Corte de Tendão, Marcar a Presa | sangramento acumulado |
| p2 | G24 | Tealzlol | Mago | 15 | 21.80 | Bola de Fogo, Pulso de Força, Lançar Pedra, Lente de Obsidiana | cajado: lentidão, atordoar e vulnerável |

- Seed da partida: `8852153440130150304`
- Rodadas: **6**
- Vencedor: **Tealzlol** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 587/2223 (26.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | belrodrigues | Tealzlol |
|---|---|---|
| Dano causado (golpes + DoT) | 1748 (774 + 974) | 2663 (2663 + 0) |
| Cura (skill + roubo de vida) | 37 (0 + 37) | 112 (0 + 112) |
| MP gasto em ações | 276 | 150 |
| Skills / ataques básicos | 6 / 0 | 6 / 0 |
| Acertos / erros | 2 / 0 | 6 / 0 |
| Críticos (dano) | 0 (0) | 1 (571) |
| Agiu primeiro (rodadas) | 6 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- belrodrigues aplicou: slowed (rodada 1), bleed (rodada 2), bleed (rodada 3), bleed (rodada 4), vulnerable (rodada 4), bleed (rodada 6)
- belrodrigues tentou sem sucesso: bleed (rodada 1), slowed (rodada 3), slowed (rodada 5)
- Tealzlol aplicou: slowed (rodada 2)
- Tealzlol tentou sem sucesso: bleed (rodada 1), bleed (rodada 2), bleed (rodada 3), bleed (rodada 4), stun (rodada 4), bleed (rodada 5), bleed (rodada 6), slowed (rodada 6)
- Leis disparadas por Tealzlol: FERIDA ABERTA (rodada 6)
- Égide de Tealzlol: absorveu 136 de dano por 67 MP

Rodada a rodada:

| Rodada | Ordem (critério) | belrodrigues (p1) | Tealzlol (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Joelho Torto — executada, dano 0, MP −34 | Bola de Fogo — executada, dano 388, MP −26 | 1800 / 2223 | 459 / 818 |
| 2 | p1 → p2 (score) | Corte de Passagem — executada, dano 0, MP −66 | Pulso de Força — executada, dano 381, MP −24 | 1419 / 2154 | 402 / 820 |
| 3 | p1 → p2 (score) | Corte de Tendão — executada, dano 416, MP −37 | Bola de Fogo — executada, dano 562, MP −26 | 877 / 1589 | 374 / 792 |
| 4 | p1 → p2 (score) | Marcar a Presa — executada, dano 358, MP −39 | Lançar Pedra — executada, dano 373, MP −24 | 521 / 983 | 344 / 771 |
| 5 | p1 → p2 (score) | Joelho Torto — executada, dano 0, MP −34 | Bola de Fogo — executada, dano 388, MP −26 | 133 / 736 | 319 / 779 |
| 6 | p1 → p2 (score) | Corte de Passagem — executada, dano 0, MP −66 | Pulso de Força — executada, dano 571, MP −24 | -438 / 587 | 262 / 789 |

#### Fase de 64 18 — TheBurntPeanut × SkipNhO

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G17 | TheBurntPeanut | Guerreiro | 18 | 26.29 | Resistência Heróica, Rasgo de Gancho, Marca do Açougueiro, Golpe Poderoso | machado: defesa e sangramento |
| p2 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |

- Seed da partida: `8721210466602292163`
- Rodadas: **11**
- Vencedor: **SkipNhO** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 753/5004 (15.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | TheBurntPeanut | SkipNhO |
|---|---|---|
| Dano causado (golpes + DoT) | 4378 (378 + 4000) | 3117 (2637 + 480) |
| Cura (skill + roubo de vida) | 12 (0 + 12) | 127 (0 + 127) |
| MP gasto em ações | 317 | 750 |
| Skills / ataques básicos | 7 / 1 | 8 / 3 |
| Acertos / erros | 6 / 0 | 6 / 2 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 8 | 3 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- TheBurntPeanut aplicou: bleed (rodada 2), bleed (rodada 3), bleed (rodada 3), bleed (rodada 7), bleed (rodada 9), bleed (rodada 10)
- TheBurntPeanut tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 3), stun (rodada 7), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), bleed (rodada 8), stun (rodada 9), stun (rodada 10)
- TheBurntPeanut ativou: Resistência Heróica ×2
- SkipNhO aplicou: stun (rodada 3), stun (rodada 4), bleed (rodada 4), bleed (rodada 8)
- SkipNhO tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 5), bleed (rodada 5), stun (rodada 8), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11)
- SkipNhO ativou: Juramento da Muralha ×2, Guarda Cruzada ×1

Rodada a rodada:

| Rodada | Ordem (critério) | TheBurntPeanut (p1) | SkipNhO (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Resistência Heróica — executada, dano 0, MP −63 | Juramento da Muralha — executada, dano 0, MP −136 | 3021 / 5004 | 443 / 512 |
| 2 | p1 → p2 (score) | Rasgo de Gancho — executada, dano 68, MP −46 | Guarda Cruzada — executada, dano 0, MP −99 | 3021 / 4736 | 407 / 425 |
| 3 | p1 → p2 (score) | Marca do Açougueiro — executada, dano 44, MP −35 | Fortaleza Viva — executada, dano 776, MP −191 | 2245 / 4130 | 382 / 246 |
| 4 | p1 → p2 (score) | Golpe Poderoso — cancelada por controle | Golpe Poderoso — executada, dano 375, MP −47 | 1870 / 3548 | 392 / 211 |
| 5 | p1 → p2 (score) | Golpe Poderoso — cancelada por controle | Ataque básico — executada, dano 297 | 1453 / 2962 | 402 / 223 |
| 6 | p2 → p1 (score) | Resistência Heróica — executada, dano 0, MP −63 | Golpe Poderoso — executada, dano 0, MP −47 | 1333 / 2962 | 349 / 188 |
| 7 | p1 → p2 (score) | Rasgo de Gancho — executada, dano 156, MP −46 | Juramento da Muralha — executada, dano 0, MP −136 | 1340 / 2606 | 313 / 64 |
| 8 | p1 → p2 (score) | Marca do Açougueiro — executada, dano 44, MP −35 | Golpe Poderoso — executada, dano 375, MP −47 | 967 / 2380 | 288 / 29 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 42, MP −29 | Ataque básico — executada, dano 0 | 849 / 1938 | 269 / 41 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 24 | Ataque básico — executada, dano 297 | 433 / 1328 | 279 / 53 |
| 11 | p2 → p1 (score) | Resistência Heróica — cancelada por morte | Golpe Poderoso — executada, dano 517, MP −47 | -84 / 753 | 279 / 18 |

#### Fase de 64 19 — Baiano × G0ularte

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G32 | Baiano | Mago | 18 | 23.99 | Grilhões de Gelo, Lasca de Gelo, Cerco de Espelhos, Bola de Fogo | controle pesado: congelar e medo |
| p2 | G28 | G0ularte | Mago | 18 | 24.10 | Míssil Mágico, Mão Firme, Foco do Estudante, Relâmpago | crítico arcano |

- Seed da partida: `5671513696900419138`
- Rodadas: **9**
- Vencedor: **Baiano** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 362/2540 (14.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Baiano | G0ularte |
|---|---|---|
| Dano causado (golpes + DoT) | 3408 (3408 + 0) | 2269 (2269 + 0) |
| Cura (skill + roubo de vida) | 91 (0 + 91) | 112 (0 + 112) |
| MP gasto em ações | 460 | 172 |
| Skills / ataques básicos | 8 / 1 | 4 / 0 |
| Acertos / erros | 5 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 1 (1572) |
| Agiu primeiro (rodadas) | 7 | 2 |
| Ações perdidas por controle | 0 | 4 |

Efeitos relevantes:
- Baiano aplicou: frozen (rodada 1), vulnerable (rodada 1), fear (rodada 2), slowed (rodada 2), frozen (rodada 6), vulnerable (rodada 6)
- Baiano tentou sem sucesso: bleed (rodada 3), slowed (rodada 3), bleed (rodada 4), bleed (rodada 5), bleed (rodada 7), slowed (rodada 7), fear (rodada 8), bleed (rodada 9)
- Égide de Baiano: absorveu 400 de dano por 199 MP
- G0ularte tentou sem sucesso: bleed (rodada 5), bleed (rodada 6)
- G0ularte ativou: Mão Firme ×1, Foco do Estudante ×1
- Égide de G0ularte: absorveu 599 de dano por 298 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Baiano (p1) | G0ularte (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −66 | Mão Firme — cancelada por controle | 2540 / 2540 | 1275 / 1182 |
| 2 | p1 → p2 (score) | Cerco de Espelhos — executada, dano 0, MP −86 | Mão Firme — cancelada por controle | 2540 / 2540 | 1215 / 1182 |
| 3 | p1 → p2 (score) | Lasca de Gelo — executada, dano 855, MP −41 | Mão Firme — executada, dano 0, MP −46 | 2540 / 1685 | 1200 / 1084 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 709, MP −37 | Foco do Estudante — executada, dano 0, MP −43 | 2540 / 976 | 1189 / 1002 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 256 | Míssil Mágico — executada, dano 1572, MP −31 | 980 / 798 | 1077 / 972 |
| 6 | p2 → p1 (score) | Grilhões de Gelo — executada, dano 0, MP −66 | Relâmpago — executada, dano 697, MP −52 | 283 / 832 | 976 / 943 |
| 7 | p1 → p2 (score) | Lasca de Gelo — executada, dano 764, MP −41 | Mão Firme — cancelada por controle | 321 / 68 | 961 / 899 |
| 8 | p1 → p2 (score) | Cerco de Espelhos — executada, dano 0, MP −86 | Mão Firme — cancelada por controle | 321 / 68 | 901 / 922 |
| 9 | p1 → p2 (score) | Bola de Fogo — executada, dano 824, MP −37 | Mão Firme — cancelada por morte | 362 / -756 | 890 / 850 |

#### Fase de 64 20 — jukes × gafallen

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G31 | jukes | Mago | 18 | 24.68 | Prisma de Devastação, Lente de Obsidiana, Bola de Fogo, Clarividência | vulnerável e dano de cajado |
| p2 | G12 | gafallen | Guerreiro | 20 | 25.95 | Fúria, Grito de Guerra, Golpe Poderoso, Esmagar | buffs de Agilidade e Força |

- Seed da partida: `1817340695540484023`
- Rodadas: **11**
- Vencedor: **gafallen** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 729/3790 (19.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | jukes | gafallen |
|---|---|---|
| Dano causado (golpes + DoT) | 3206 (3206 + 0) | 2949 (2949 + 0) |
| Cura (skill + roubo de vida) | 132 (0 + 132) | 145 (0 + 145) |
| MP gasto em ações | 487 | 605 |
| Skills / ataques básicos | 9 / 1 | 8 / 3 |
| Acertos / erros | 6 / 1 | 6 / 2 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 10 | 1 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- jukes aplicou: vulnerable (rodada 2), vulnerable (rodada 3), vulnerable (rodada 7), vulnerable (rodada 8)
- jukes tentou sem sucesso: bleed (rodada 2), bleed (rodada 3), bleed (rodada 5), bleed (rodada 7), bleed (rodada 8), bleed (rodada 9)
- jukes ativou: Clarividência ×3
- Égide de jukes: absorveu 518 de dano por 256 MP
- gafallen aplicou: stun (rodada 9)
- gafallen tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11)
- gafallen ativou: Fúria ×2, Grito de Guerra ×1

Rodada a rodada:

| Rodada | Ordem (critério) | jukes (p1) | gafallen (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Clarividência — executada, dano 0, MP −59 | Fúria — executada, dano 0, MP −136 | 2540 / 3790 | 1123 / 381 |
| 2 | p1 → p2 (score) | Prisma de Devastação — executada, dano 523, MP −74 | Grito de Guerra — executada, dano 0, MP −71 | 2540 / 3267 | 1072 / 320 |
| 3 | p2 → p1 (score) | Lente de Obsidiana — executada, dano 655, MP −44 | Golpe Poderoso — executada, dano 826, MP −37 | 1746 / 2653 | 979 / 293 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 0, MP −37 | Esmagar — executada, dano 0, MP −114 | 1746 / 2653 | 965 / 189 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 222 | Fúria — executada, dano 0, MP −136 | 1757 / 2431 | 988 / 63 |
| 6 | p1 → p2 (score) | Clarividência — executada, dano 0, MP −59 | Golpe Poderoso — executada, dano 574, MP −37 | 1183 / 2459 | 902 / 36 |
| 7 | p1 → p2 (score) | Prisma de Devastação — executada, dano 523, MP −74 | Ataque básico — executada, dano 325 | 884 / 1952 | 823 / 46 |
| 8 | p1 → p2 (score) | Lente de Obsidiana — executada, dano 524, MP −44 | Golpe Poderoso — executada, dano 0, MP −37 | 910 / 1428 | 802 / 19 |
| 9 | p1 → p2 (score) | Bola de Fogo — executada, dano 759, MP −37 | Ataque básico — executada, dano 325 | 622 / 685 | 760 / 29 |
| 10 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 325 | 297 / 701 | 755 / 39 |
| 11 | p1 → p2 (score) | Clarividência — executada, dano 0, MP −59 | Golpe Poderoso — executada, dano 574, MP −37 | -277 / 729 | 669 / 12 |

#### Fase de 64 21 — fer × Bagi

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G11 | fer | Guerreiro | 18 | 24.10 | Soco de Placa, Quebra-Guarda, Provocação, Golpe Devastador | enfraquecer e expor |
| p2 | G46 | Bagi | Ladino | 14 | 22.03 | Envenenar, Dose da Viúva, Ataque Furtivo, Golpe nas Sombras | veneno |

- Seed da partida: `3315330788876156439`
- Rodadas: **6**
- Vencedor: **fer** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2086/3021 (69.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fer | Bagi |
|---|---|---|
| Dano causado (golpes + DoT) | 1644 (1644 + 0) | 1016 (881 + 135) |
| Cura (skill + roubo de vida) | 81 (0 + 81) | 98 (0 + 98) |
| MP gasto em ações | 222 | 196 |
| Skills / ataques básicos | 6 / 0 | 5 / 0 |
| Acertos / erros | 3 / 1 | 3 / 0 |
| Críticos (dano) | 0 (0) | 1 (355) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- fer aplicou: weakened (rodada 1), stun (rodada 4), weakened (rodada 5)
- fer tentou sem sucesso: stun (rodada 2), bleed (rodada 2), weakened (rodada 2), bleed (rodada 4), weakened (rodada 4), stun (rodada 6), bleed (rodada 6), weakened (rodada 6)
- Bagi aplicou: poison (rodada 4)
- Bagi tentou sem sucesso: poison (rodada 1), poison (rodada 2), poison (rodada 2), poison (rodada 3), poison (rodada 6), poison (rodada 6)

Rodada a rodada:

| Rodada | Ordem (critério) | fer (p1) | Bagi (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Provocação — executada, dano 0, MP −40 | Envenenar — executada, dano 0, MP −59 | 3021 / 1415 | 466 / 334 |
| 2 | p2 → p1 (score) | Soco de Placa — executada, dano 548, MP −34 | Dose da Viúva — executada, dano 263, MP −25 | 2785 / 867 | 442 / 316 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −40 | Ataque Furtivo — executada, dano 355, MP −28 | 2430 / 923 | 412 / 295 |
| 4 | p2 → p1 (score) | Soco de Placa — executada, dano 548, MP −34 | Envenenar — executada, dano 0, MP −59 | 2412 / 375 | 388 / 243 |
| 5 | p2 → p1 (score) | Provocação — executada, dano 0, MP −40 | Dose da Viúva — cancelada por controle | 2367 / 375 | 358 / 250 |
| 6 | p2 → p1 (score) | Soco de Placa — executada, dano 548, MP −34 | Dose da Viúva — executada, dano 263, MP −25 | 2086 / -131 | 334 / 232 |

#### Fase de 64 22 — lubatv × Hayashii

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G26 | lubatv | Mago | 16 | 22.38 | Bola de Fogo, Drenar Vida, Pele de Quartzo, Sanguessuga Arcana | cura e roubo de vida |
| p2 | G64 | Hayashii | Ladino | 22 | 28.25 | Golpe nas Sombras, Assassinato, Ataque Furtivo, Mão Leve | Força do Ladino e crítico |

- Seed da partida: `15955446086312003275`
- Rodadas: **5**
- Vencedor: **Hayashii** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3392/3392 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | lubatv | Hayashii |
|---|---|---|
| Dano causado (golpes + DoT) | 0 (0 + 0) | 2614 (2614 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 118 | 486 |
| Skills / ataques básicos | 3 / 0 | 5 / 0 |
| Acertos / erros | 0 / 1 | 3 / 1 |
| Críticos (dano) | 0 (0) | 2 (1879) |
| Agiu primeiro (rodadas) | 0 | 5 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- lubatv ativou: Pele de Quartzo ×1, Sanguessuga Arcana ×1
- Égide de lubatv: absorveu 460 de dano por 229 MP
- Hayashii aplicou: stun (rodada 4), stun (rodada 5)
- Hayashii tentou sem sucesso: stun (rodada 3), poison (rodada 3), poison (rodada 4), poison (rodada 5)
- Hayashii ativou: Mão Leve ×1

Rodada a rodada:

| Rodada | Ordem (critério) | lubatv (p1) | Hayashii (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pele de Quartzo — executada, dano 0, MP −34 | Mão Leve — executada, dano 0, MP −136 | 2583 / 3392 | 732 / 836 |
| 2 | p2 → p1 (score) | Sanguessuga Arcana — executada, dano 0, MP −55 | Golpe nas Sombras — executada, dano 0, MP −83 | 2583 / 3392 | 711 / 772 |
| 3 | p2 → p1 (score) | Bola de Fogo — executada, dano 0, MP −29 | Assassinato — executada, dano 976, MP −115 | 1607 / 3392 | 645 / 676 |
| 4 | p2 → p1 (score) | Ataque básico — cancelada por controle | Ataque Furtivo — executada, dano 903, MP −69 | 704 / 3392 | 615 / 626 |
| 5 | p2 → p1 (score) | Drenar Vida — cancelada por morte | Golpe nas Sombras — executada, dano 735, MP −83 | -31 / 3392 | 551 / 562 |

#### Fase de 64 23 — frttt × PaulinhoLOKObr

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G40 | frttt | Mago | 24 | 28.14 | Dividendo de Mana, Dreno de Mana, Bola de Fogo, Reserva Profunda | mana: queimar a do rival |
| p2 | G53 | PaulinhoLOKObr | Ladino | 17 | 23.41 | Couro Endurecido, Capa Rasgada, Ataque Furtivo, Assassinato | Ladino defensivo |

- Seed da partida: `13647429566868377544`
- Rodadas: **4**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4538/5014 (90.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | PaulinhoLOKObr |
|---|---|---|
| Dano causado (golpes + DoT) | 3009 (3009 + 0) | 476 (476 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 13 (0 + 13) |
| MP gasto em ações | 404 | 192 |
| Skills / ataques básicos | 4 / 0 | 4 / 0 |
| Acertos / erros | 2 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 1 | 3 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- frttt aplicou: mana_burn (rodada 2), mana_burn (rodada 3)
- frttt ativou: Reserva Profunda ×1
- Égide de frttt: absorveu 82 de dano por 40 MP
- PaulinhoLOKObr tentou sem sucesso: bleed (rodada 3), bleed (rodada 4)
- PaulinhoLOKObr ativou: Couro Endurecido ×1, Capa Rasgada ×1

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | PaulinhoLOKObr (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Reserva Profunda — executada, dano 0, MP −72 | Couro Endurecido — executada, dano 0, MP −53 | 5014 / 2460 | 2105 / 499 |
| 2 | p2 → p1 (score) | Dreno de Mana — executada, dano 0, MP −80 | Capa Rasgada — executada, dano 0, MP −35 | 5014 / 2460 | 2097 / 475 |
| 3 | p2 → p1 (score) | Dividendo de Mana — executada, dano 1679, MP −179 | Ataque Furtivo — executada, dano 216, MP −39 | 4798 / 781 | 1998 / 435 |
| 4 | p2 → p1 (score) | Bola de Fogo — executada, dano 1330, MP −73 | Assassinato — executada, dano 260, MP −65 | 4538 / -536 | 2006 / 369 |

#### Fase de 64 24 — Tenz × Coringa

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G52 | Tenz | Ladino | 17 | 24.91 | Bolso Furado, Ataque Furtivo, Cortina de Fumaça, Golpe nas Sombras | queima de mana e névoa |
| p2 | G33 | Coringa | Mago | 18 | 24.68 | Dreno de Mana, Troca de Sangue, Bola de Fogo, Drenar Vida | queima de mana e drenos |

- Seed da partida: `10172409037477872466`
- Rodadas: **24**
- Vencedor: **Coringa** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 562/2540 (22.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Tenz | Coringa |
|---|---|---|
| Dano causado (golpes + DoT) | 5118 (4310 + 808) | 3611 (3423 + 188) |
| Cura (skill + roubo de vida) | 844 (0 + 844) | 3140 (2286 + 854) |
| MP gasto em ações | 679 | 947 |
| Skills / ataques básicos | 15 / 9 | 23 / 1 |
| Acertos / erros | 16 / 0 | 4 / 8 |
| Críticos (dano) | 1 (386) | 0 (0) |
| Agiu primeiro (rodadas) | 24 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Tenz aplicou: clouded (rodada 2), mana_burn (rodada 5), clouded (rodada 5), bleed (rodada 7), fear (rodada 7), clouded (rodada 8), bleed (rodada 11), clouded (rodada 12), fear (rodada 13), mana_burn (rodada 14), bleed (rodada 16), bleed (rodada 20), mana_burn (rodada 23), clouded (rodada 23)
- Tenz tentou sem sucesso: mana_burn (rodada 1), bleed (rodada 3), fear (rodada 3), bleed (rodada 4), fear (rodada 4), bleed (rodada 6), fear (rodada 6), mana_burn (rodada 9), bleed (rodada 10), fear (rodada 10), fear (rodada 11), bleed (rodada 13), clouded (rodada 14), bleed (rodada 15), fear (rodada 15), fear (rodada 16), bleed (rodada 17), fear (rodada 17), bleed (rodada 18), fear (rodada 18), bleed (rodada 19), fear (rodada 19), fear (rodada 20), bleed (rodada 21), fear (rodada 21), bleed (rodada 22), fear (rodada 22), bleed (rodada 24), fear (rodada 24)
- Coringa aplicou: mana_burn (rodada 1), mana_burn (rodada 5), mana_burn (rodada 9), bleed (rodada 10), mana_burn (rodada 18)
- Coringa tentou sem sucesso: frailty (rodada 10), mana_burn (rodada 13), bleed (rodada 16), bleed (rodada 19), frailty (rodada 19), mana_burn (rodada 22), bleed (rodada 24), frailty (rodada 24)
- Leis disparadas por Coringa: COLAPSO MENTAL (rodada 5), COLAPSO MENTAL (rodada 6), PÂNICO (rodada 7), COLAPSO MENTAL (rodada 14), COLAPSO MENTAL (rodada 23), COLAPSO MENTAL (rodada 24)
- Égide de Coringa: absorveu 759 de dano por 378 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Tenz (p1) | Coringa (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Bolso Furado — executada, dano 0, MP −35 | Dreno de Mana — executada, dano 0, MP −40 | 2367 / 2540 | 517 / 1265 |
| 2 | p1 → p2 (score) | Cortina de Fumaça — executada, dano 0, MP −69 | Troca de Sangue — executada, dano 0, MP −52 | 2367 / 2540 | 447 / 992 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 353, MP −39 | Bola de Fogo — executada, dano 0, MP −37 | 2367 / 2187 | 407 / 980 |
| 4 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 568, MP −47 | Ataque básico — executada, dano 0 | 2367 / 1619 | 371 / 986 |
| 5 | p1 → p2 (score) | Bolso Furado — executada, dano 0, MP −35 | Dreno de Mana — executada, dano 0, MP −40 | 2367 / 1619 | 347 / 984 |
| 6 | p1 → p2 (score) | Ataque Furtivo — executada, dano 257, MP −39 | Troca de Sangue — executada, dano 0, MP −52 | 2367 / 1362 | 307 / 948 |
| 7 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 568, MP −47 | Bola de Fogo — executada, dano 0, MP −37 | 2367 / 693 | 259 / 917 |
| 8 | p1 → p2 (score) | Cortina de Fumaça — executada, dano 0, MP −69 | Drenar Vida — executada, dano 0, MP −35 | 2367 / 973 | 201 / 938 |
| 9 | p1 → p2 (score) | Bolso Furado — executada, dano 0, MP −35 | Dreno de Mana — executada, dano 0, MP −40 | 2367 / 973 | 177 / 954 |
| 10 | p1 → p2 (score) | Ataque Furtivo — executada, dano 257, MP −39 | Troca de Sangue — executada, dano 934, MP −52 | 1433 / 949 | 137 / 936 |
| 11 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 391, MP −47 | Drenar Vida — executada, dano 0, MP −35 | 1483 / 838 | 89 / 929 |
| 12 | p1 → p2 (score) | Cortina de Fumaça — executada, dano 0, MP −69 | Bola de Fogo — executada, dano 0, MP −37 | 1389 / 737 | 31 / 948 |
| 13 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Dreno de Mana — executada, dano 0, MP −40 | 1451 / 567 | 42 / 949 |
| 14 | p1 → p2 (score) | Bolso Furado — executada, dano 0, MP −35 | Drenar Vida — executada, dano 0, MP −35 | 1451 / 948 | 18 / 952 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Troca de Sangue — executada, dano 0, MP −52 | 1513 / 778 | 29 / 935 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Bola de Fogo — executada, dano 621, MP −37 | 954 / 662 | 40 / 945 |
| 17 | p1 → p2 (score) | Ataque Furtivo — executada, dano 386, MP −39 | Drenar Vida — executada, dano 0, MP −35 | 1096 / 556 | 12 / 938 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Dreno de Mana — executada, dano 0, MP −40 | 1158 / 386 | 23 / 945 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Troca de Sangue — executada, dano 934, MP −52 | 286 / 449 | 22 / 940 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Drenar Vida — executada, dano 0, MP −35 | 348 / 559 | 21 / 952 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Bola de Fogo — executada, dano 0, MP −37 | 410 / 288 | 32 / 962 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Dreno de Mana — executada, dano 0, MP −40 | 472 / 118 | 43 / 969 |
| 23 | p1 → p2 (score) | Bolso Furado — executada, dano 0, MP −35 | Drenar Vida — executada, dano 0, MP −35 | 472 / 499 | 19 / 972 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Troca de Sangue — executada, dano 934, MP −52 | -400 / 562 | 30 / 943 |

#### Fase de 64 25 — tteuw × YoDa

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G22 | tteuw | Guerreiro | 22 | 28.71 | Pacto de Ferro, Tomar Fôlego, Tremor de Bigorna, Golpe Poderoso | maça: redução, cura e roubo de vida |
| p2 | G06 | YoDa | Guerreiro | 16 | 22.49 | Golpe Poderoso, Guarda Cruzada, Disciplina de Forja, Mão Dupla | duas armas: guarda e sangramento |

- Seed da partida: `6811398301582065085`
- Rodadas: **12**
- Vencedor: **tteuw** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4844/4844 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | tteuw | YoDa |
|---|---|---|
| Dano causado (golpes + DoT) | 3283 (3283 + 0) | 410 (410 + 0) |
| Cura (skill + roubo de vida) | 410 (0 + 410) | 19 (0 + 19) |
| MP gasto em ações | 602 | 379 |
| Skills / ataques básicos | 8 / 4 | 10 / 0 |
| Acertos / erros | 10 / 0 | 4 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 4 | 8 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- tteuw aplicou: stun (rodada 2), stun (rodada 2), stun (rodada 4)
- tteuw tentou sem sucesso: stun (rodada 3), stun (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12)
- tteuw ativou: Pacto de Ferro ×2
- YoDa tentou sem sucesso: stun (rodada 4), stun (rodada 7), stun (rodada 9), stun (rodada 10), bleed (rodada 10)
- YoDa ativou: Guarda Cruzada ×3, Disciplina de Forja ×2

Rodada a rodada:

| Rodada | Ordem (critério) | tteuw (p1) | YoDa (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Pacto de Ferro — executada, dano 0, MP −136 | Guarda Cruzada — executada, dano 0, MP −50 | 4844 / 3115 | 512 / 278 |
| 2 | p1 → p2 (score) | Tremor de Bigorna — executada, dano 449, MP −71 | Disciplina de Forja — cancelada por controle | 4844 / 2666 | 453 / 284 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 395, MP −47 | Disciplina de Forja — executada, dano 0, MP −47 | 4844 / 2271 | 418 / 243 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 243 | Golpe Poderoso — executada, dano 75, MP −23 | 4844 / 2031 | 430 / 226 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 424, MP −47 | Mão Dupla — cancelada por controle | 4844 / 1607 | 395 / 232 |
| 6 | p2 → p1 (score) | Ataque básico — executada, dano 163 | Guarda Cruzada — executada, dano 0, MP −50 | 4844 / 1444 | 407 / 188 |
| 7 | p2 → p1 (score) | Pacto de Ferro — executada, dano 0, MP −136 | Golpe Poderoso — executada, dano 160, MP −23 | 4684 / 1452 | 283 / 171 |
| 8 | p1 → p2 (score) | Tremor de Bigorna — executada, dano 449, MP −71 | Disciplina de Forja — executada, dano 0, MP −47 | 4844 / 1003 | 224 / 130 |
| 9 | p2 → p1 (score) | Golpe Poderoso — executada, dano 424, MP −47 | Golpe Poderoso — executada, dano 75, MP −23 | 4844 / 582 | 189 / 113 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 243 | Mão Dupla — executada, dano 100, MP −43 | 4844 / 344 | 201 / 76 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 284, MP −47 | Guarda Cruzada — executada, dano 0, MP −50 | 4844 / 60 | 166 / 32 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 209 | Golpe Poderoso — executada, dano 0, MP −23 | 4844 / -149 | 178 / 15 |

#### Fase de 64 26 — alanzoka × Patriota

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G36 | alanzoka | Mago | 20 | 25.60 | Pacto do Vazio, Míssil Mágico, Mão Firme, Relâmpago | dano crítico |
| p2 | G60 | Patriota | Ladino | 19 | 28.14 | Cobrança de Juros, Joelho Torto, Corte de Passagem, Ataque Furtivo | sangramento máximo |

- Seed da partida: `3956753177955526443`
- Rodadas: **5**
- Vencedor: **Patriota** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1843/2490 (74.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | alanzoka | Patriota |
|---|---|---|
| Dano causado (golpes + DoT) | 647 (647 + 0) | 3505 (1502 + 2003) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 222 | 248 |
| Skills / ataques básicos | 3 / 0 | 4 / 1 |
| Acertos / erros | 1 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 1 (461) |
| Agiu primeiro (rodadas) | 0 | 5 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- alanzoka ativou: Pacto do Vazio ×1, Mão Firme ×1
- Égide de alanzoka: absorveu 263 de dano por 130 MP
- Patriota aplicou: slowed (rodada 1), bleed (rodada 1), bleed (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 4), poison (rodada 4)
- Patriota tentou sem sucesso: stun (rodada 2), poison (rodada 2), bleed (rodada 3), poison (rodada 3), stun (rodada 4), slowed (rodada 5)

Rodada a rodada:

| Rodada | Ordem (critério) | alanzoka (p1) | Patriota (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pacto do Vazio — executada, dano 0, MP −125 | Joelho Torto — executada, dano 0, MP −48 | 3060 / 2490 | 1081 / 803 |
| 2 | p2 → p1 (score) | Mão Firme — executada, dano 0, MP −58 | Cobrança de Juros — executada, dano 850, MP −103 | 1828 / 2490 | 993 / 717 |
| 3 | p2 → p1 (score) | Míssil Mágico — cancelada por controle | Ataque Furtivo — executada, dano 461, MP −49 | 985 / 2490 | 997 / 685 |
| 4 | p2 → p1 (score) | Míssil Mágico — executada, dano 647, MP −39 | Ataque básico — executada, dano 191 | 238 / 1843 | 986 / 702 |
| 5 | p2 → p1 (score) | Relâmpago — cancelada por morte | Joelho Torto — executada, dano 0, MP −48 | -318 / 1843 | 1030 / 671 |

#### Fase de 64 27 — sofiaespanha × DavyJones

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G48 | sofiaespanha | Ladino | 15 | 20.53 | Golpe Baixo, Pó nos Olhos, Ataque Furtivo, Marcar a Presa | controle sujo |
| p2 | G04 | DavyJones | Guerreiro | 16 | 21.68 | Golpe Poderoso, Grito de Guerra, Cutelada, Golpe Duplo | Força bruta e fragilidade |

- Seed da partida: `16376724242456928258`
- Rodadas: **8**
- Vencedor: **DavyJones** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1768/3035 (58.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | sofiaespanha | DavyJones |
|---|---|---|
| Dano causado (golpes + DoT) | 1389 (1389 + 0) | 2489 (2489 + 0) |
| Cura (skill + roubo de vida) | 43 (0 + 43) | 122 (0 + 122) |
| MP gasto em ações | 228 | 235 |
| Skills / ataques básicos | 8 / 0 | 7 / 0 |
| Acertos / erros | 3 / 0 | 4 / 1 |
| Críticos (dano) | 2 (874) | 0 (0) |
| Agiu primeiro (rodadas) | 8 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- sofiaespanha aplicou: weakened (rodada 1), stun (rodada 1), weakened (rodada 4), fear (rodada 6), slowed (rodada 6), weakened (rodada 7)
- sofiaespanha tentou sem sucesso: fear (rodada 2), stun (rodada 3), bleed (rodada 3), fear (rodada 3), stun (rodada 4), stun (rodada 5), bleed (rodada 5), fear (rodada 5), vulnerable (rodada 5), stun (rodada 7), stun (rodada 8), bleed (rodada 8), fear (rodada 8)
- DavyJones tentou sem sucesso: stun (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 8)
- DavyJones ativou: Grito de Guerra ×2

Rodada a rodada:

| Rodada | Ordem (critério) | sofiaespanha (p1) | DavyJones (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Baixo — executada, dano 0, MP −25 | Grito de Guerra — cancelada por controle | 1888 / 3035 | 415 / 328 |
| 2 | p1 → p2 (score) | Pó nos Olhos — executada, dano 0, MP −28 | Grito de Guerra — executada, dano 0, MP −45 | 1888 / 3035 | 395 / 283 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 505, MP −31 | Golpe Poderoso — executada, dano 675, MP −23 | 1213 / 2563 | 372 / 266 |
| 4 | p1 → p2 (score) | Golpe Baixo — executada, dano 0, MP −25 | Cutelada — executada, dano 619, MP −38 | 594 / 2593 | 355 / 234 |
| 5 | p1 → p2 (score) | Marcar a Presa — executada, dano 515, MP −35 | Golpe Poderoso — executada, dano 468, MP −23 | 151 / 2101 | 328 / 217 |
| 6 | p1 → p2 (score) | Pó nos Olhos — executada, dano 0, MP −28 | Grito de Guerra — executada, dano 0, MP −45 | 151 / 2101 | 308 / 178 |
| 7 | p1 → p2 (score) | Golpe Baixo — executada, dano 0, MP −25 | Golpe Poderoso — executada, dano 0, MP −23 | 151 / 2101 | 291 / 161 |
| 8 | p1 → p2 (score) | Ataque Furtivo — executada, dano 369, MP −31 | Cutelada — executada, dano 727, MP −38 | -558 / 1768 | 268 / 129 |

#### Fase de 64 28 — Smzinho × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G50 | Smzinho | Ladino | 17 | 24.57 | Ataque Furtivo, Duas Mãos, Um Tempo, Mão Leve, Assassinato | duas armas e crítico |
| p2 | G56 | RNakano | Ladino | 20 | 25.60 | Silêncio de Seda, Nó Corredio, Ataque Furtivo, Golpe nas Sombras | sono e atordoamento |

- Seed da partida: `8705380721711465627`
- Rodadas: **6**
- Vencedor: **RNakano** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2179/2704 (80.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Smzinho | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 565 (565 + 0) | 3171 (3171 + 0) |
| Cura (skill + roubo de vida) | 28 (0 + 28) | 40 (0 + 40) |
| MP gasto em ações | 116 | 371 |
| Skills / ataques básicos | 2 / 0 | 5 / 1 |
| Acertos / erros | 1 / 0 | 4 / 0 |
| Críticos (dano) | 1 (565) | 3 (2465) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- Smzinho tentou sem sucesso: bleed (rodada 5)
- Smzinho ativou: Mão Leve ×1
- RNakano aplicou: sleep (rodada 1), mana_burn (rodada 1), stun (rodada 4), stun (rodada 6)
- RNakano tentou sem sucesso: stun (rodada 2), stun (rodada 3), poison (rodada 3), poison (rodada 4), stun (rodada 5), poison (rodada 5), poison (rodada 6)

Rodada a rodada:

| Rodada | Ordem (critério) | Smzinho (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Mão Leve — cancelada por controle | Silêncio de Seda — executada, dano 0, MP −108 | 2367 / 2704 | 551 / 667 |
| 2 | p2 → p1 (score) | Mão Leve — cancelada por controle | Nó Corredio — executada, dano 0, MP −87 | 2367 / 2704 | 550 / 595 |
| 3 | p2 → p1 (score) | Mão Leve — executada, dano 0, MP −77 | Ataque Furtivo — executada, dano 1117, MP −55 | 1250 / 2704 | 475 / 555 |
| 4 | p2 → p1 (score) | Ataque Furtivo — cancelada por controle | Golpe nas Sombras — executada, dano 706, MP −66 | 544 / 2704 | 486 / 504 |
| 5 | p2 → p1 (score) | Ataque Furtivo — executada, dano 565, MP −39 | Ataque básico — executada, dano 533 | 39 / 2139 | 458 / 519 |
| 6 | p2 → p1 (score) | Duas Mãos, Um Tempo — cancelada por morte | Ataque Furtivo — executada, dano 815, MP −55 | -776 / 2179 | 458 / 479 |

#### Fase de 64 29 — XANDAOOGOD × gabepeixe

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G34 | XANDAOOGOD | Mago | 19 | 26.64 | Ressurgir, Bola de Fogo, Égide de Runas, Vigor Emprestado | cura grande e vida máxima |
| p2 | G13 | gabepeixe | Guerreiro | 19 | 29.52 | Golpe Poderoso, Colheita de Ferro, Juramento da Muralha, Mão Dupla | duas armas: sangramento pesado |

- Seed da partida: `9358423812746425229`
- Rodadas: **9**
- Vencedor: **gabepeixe** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2910/3509 (82.9%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | XANDAOOGOD | gabepeixe |
|---|---|---|
| Dano causado (golpes + DoT) | 722 (722 + 0) | 4856 (2525 + 2331) |
| Cura (skill + roubo de vida) | 1688 (1688 + 0) | 123 (0 + 123) |
| MP gasto em ações | 547 | 540 |
| Skills / ataques básicos | 7 / 1 | 9 / 0 |
| Acertos / erros | 3 / 0 | 6 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 9 | 0 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- XANDAOOGOD ativou: Égide de Runas ×2, Vigor Emprestado ×2
- Égide de XANDAOOGOD: absorveu 443 de dano por 219 MP
- gabepeixe aplicou: bleed (rodada 3), bleed (rodada 3), bleed (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), bleed (rodada 8), bleed (rodada 9), bleed (rodada 9)
- gabepeixe tentou sem sucesso: stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), stun (rodada 8), stun (rodada 9)
- gabepeixe ativou: Juramento da Muralha ×2

Rodada a rodada:

| Rodada | Ordem (critério) | XANDAOOGOD (p1) | gabepeixe (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Égide de Runas — executada, dano 0, MP −82 | Juramento da Muralha — executada, dano 0, MP −96 | 3070 / 3509 | 1304 / 471 |
| 2 | p1 → p2 (score) | Vigor Emprestado — executada, dano 0, MP −74 | Golpe Poderoso — executada, dano 0, MP −33 | 3070 / 3509 | 1277 / 449 |
| 3 | p1 → p2 (score) | Bola de Fogo — executada, dano 286, MP −41 | Colheita de Ferro — executada, dano 406, MP −78 | 2664 / 3243 | 1248 / 382 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Golpe Poderoso — executada, dano 393, MP −33 | 2026 / 3112 | 1261 / 360 |
| 5 | p1 → p2 (score) | Bola de Fogo — executada, dano 286, MP −41 | Mão Dupla — executada, dano 554, MP −60 | 1227 / 2853 | 1219 / 311 |
| 6 | p1 → p2 (score) | Ressurgir — executada, dano 0, MP −153 | Golpe Poderoso — executada, dano 393, MP −33 | 2031 / 2872 | 1079 / 289 |
| 7 | p1 → p2 (score) | Égide de Runas — cancelada por controle | Juramento da Muralha — executada, dano 0, MP −96 | 1417 / 2872 | 1126 / 204 |
| 8 | p1 → p2 (score) | Égide de Runas — executada, dano 0, MP −82 | Golpe Poderoso — executada, dano 255, MP −33 | 548 / 2884 | 1069 / 182 |
| 9 | p1 → p2 (score) | Vigor Emprestado — executada, dano 0, MP −74 | Colheita de Ferro — executada, dano 524, MP −78 | -98 / 2910 | 996 / 115 |

#### Fase de 64 30 — yeTz × Dilera

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G02 | yeTz | Guerreiro | 13 | 20.53 | Golpe Poderoso, Marca do Açougueiro, Peso do Machado, Rasgo de Gancho | sangramento com machado |
| p2 | G42 | Dilera | Mago | 20 | 29.17 | Sanguessuga Arcana, Drenar Vida, Ressurgir, Bola de Fogo | roubo de vida e cura |

- Seed da partida: `11695585345081819962`
- Rodadas: **4**
- Vencedor: **Dilera** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3199/3262 (98.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | yeTz | Dilera |
|---|---|---|
| Dano causado (golpes + DoT) | 1184 (534 + 650) | 2064 (2064 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 1121 (0 + 1121) |
| MP gasto em ações | 54 | 179 |
| Skills / ataques básicos | 3 / 0 | 3 / 1 |
| Acertos / erros | 3 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 4 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- yeTz aplicou: bleed (rodada 1), bleed (rodada 2)
- yeTz tentou sem sucesso: bleed (rodada 2), bleed (rodada 3)
- Dilera ativou: Sanguessuga Arcana ×1
- Égide de Dilera: absorveu 92 de dano por 45 MP

Rodada a rodada:

| Rodada | Ordem (critério) | yeTz (p1) | Dilera (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Golpe Poderoso — executada, dano 179, MP −17 | Sanguessuga Arcana — executada, dano 0, MP −87 | 1714 / 3083 | 217 / 1104 |
| 2 | p2 → p1 (score) | Marca do Açougueiro — executada, dano 176, MP −20 | Bola de Fogo — executada, dano 813, MP −46 | 901 / 3086 | 201 / 1107 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 179, MP −17 | Ataque básico — executada, dano 438 | 463 / 2988 | 188 / 1156 |
| 4 | p2 → p1 (score) | Peso do Machado — cancelada por morte | Bola de Fogo — executada, dano 813, MP −46 | -350 / 3199 | 188 / 1160 |

#### Fase de 64 31 — LuquEt4 × calango

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G20 | LuquEt4 | Guerreiro | 22 | 28.48 | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | medo e vulnerabilidade |
| p2 | G05 | calango | Guerreiro | 16 | 21.34 | Investida, Berro de Ferro, Pancada de Elmo, Ferro Contra Ferro | controle: atordoar, medo e enfraquecer |

- Seed da partida: `17575010425553476582`
- Rodadas: **8**
- Vencedor: **LuquEt4** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4542/4754 (95.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | LuquEt4 | calango |
|---|---|---|
| Dano causado (golpes + DoT) | 3423 (3423 + 0) | 334 (334 + 0) |
| Cura (skill + roubo de vida) | 122 (0 + 122) | 16 (0 + 16) |
| MP gasto em ações | 717 | 252 |
| Skills / ataques básicos | 6 / 2 | 7 / 0 |
| Acertos / erros | 5 / 1 | 2 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 8 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- LuquEt4 aplicou: fear (rodada 4)
- LuquEt4 tentou sem sucesso: fear (rodada 1), stun (rodada 3), bleed (rodada 3), fear (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), fear (rodada 5), stun (rodada 6), bleed (rodada 6), fear (rodada 6), fear (rodada 7), stun (rodada 8), bleed (rodada 8), fear (rodada 8)
- calango aplicou: hexed (rodada 1)
- calango tentou sem sucesso: fear (rodada 1), stun (rodada 2), stun (rodada 3), stun (rodada 3), hexed (rodada 5), stun (rodada 6), stun (rodada 6), stun (rodada 7)

Rodada a rodada:

| Rodada | Ordem (critério) | LuquEt4 (p1) | calango (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Silêncio do Veterano — executada, dano 0, MP −120 | Berro de Ferro — executada, dano 0, MP −26 | 4754 / 3017 | 528 / 302 |
| 2 | p1 → p2 (score) | Carga do Condenado — executada, dano 0, MP −119 | Pancada de Elmo — executada, dano 0, MP −55 | 4754 / 3017 | 421 / 253 |
| 3 | p1 → p2 (score) | Esmagar — executada, dano 935, MP −144 | Investida — executada, dano 167, MP −26 | 4587 / 2090 | 289 / 233 |
| 4 | p1 → p2 (score) | Golpe Devastador — executada, dano 870, MP −107 | Ferro Contra Ferro — executada, dano 0, MP −38 | 4630 / 1220 | 194 / 201 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 374 | Berro de Ferro — executada, dano 0, MP −26 | 4648 / 846 | 206 / 181 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 374 | Investida — executada, dano 167, MP −26 | 4499 / 480 | 218 / 161 |
| 7 | p1 → p2 (score) | Silêncio do Veterano — executada, dano 0, MP −120 | Pancada de Elmo — executada, dano 0, MP −55 | 4499 / 480 | 110 / 112 |
| 8 | p1 → p2 (score) | Golpe Devastador — executada, dano 870, MP −107 | Berro de Ferro — cancelada por morte | 4542 / -390 | 15 / 112 |

#### Fase de 64 32 — boltz × hastad

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G47 | boltz | Ladino | 15 | 21.92 | Evasão, Sombra Rápida, Corte de Tendão, Golpe nas Sombras | evasão e Agilidade |
| p2 | G23 | hastad | Mago | 14 | 20.07 | Bola de Fogo, Marca Ardente, Relâmpago, Maldição de Cinzas | fogo e veneno |

- Seed da partida: `2272127964721152814`
- Rodadas: **7**
- Vencedor: **boltz** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1039/1888 (55.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | boltz | hastad |
|---|---|---|
| Dano causado (golpes + DoT) | 2087 (2087 + 0) | 915 (915 + 0) |
| Cura (skill + roubo de vida) | 66 (0 + 66) | 45 (0 + 45) |
| MP gasto em ações | 225 | 144 |
| Skills / ataques básicos | 7 / 0 | 6 / 0 |
| Acertos / erros | 3 / 0 | 2 / 4 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 7 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- boltz aplicou: slowed (rodada 3), slowed (rodada 7)
- boltz tentou sem sucesso: bleed (rodada 3), bleed (rodada 4), bleed (rodada 7)
- boltz ativou: Evasão ×2, Sombra Rápida ×2
- hastad tentou sem sucesso: poison (rodada 6)
- Égide de hastad: absorveu 367 de dano por 182 MP

Rodada a rodada:

| Rodada | Ordem (critério) | boltz (p1) | hastad (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Evasão — executada, dano 0, MP −25 | Bola de Fogo — executada, dano 0, MP −23 | 1888 / 1614 | 415 / 588 |
| 2 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −36 | Marca Ardente — executada, dano 0, MP −21 | 1888 / 1614 | 387 / 590 |
| 3 | p1 → p2 (score) | Corte de Tendão — executada, dano 744, MP −33 | Bola de Fogo — executada, dano 466, MP −23 | 1422 / 893 | 362 / 532 |
| 4 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 678, MP −37 | Relâmpago — executada, dano 0, MP −33 | 1455 / 215 | 333 / 470 |
| 5 | p1 → p2 (score) | Evasão — executada, dano 0, MP −25 | Bola de Fogo — executada, dano 0, MP −23 | 1455 / 215 | 316 / 477 |
| 6 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −36 | Marca Ardente — executada, dano 449, MP −21 | 1006 / 237 | 288 / 486 |
| 7 | p1 → p2 (score) | Corte de Tendão — executada, dano 665, MP −33 | Bola de Fogo — cancelada por morte | 1039 / -428 | 263 / 428 |

### Fase de 32: detalhes

#### Fase de 32 1 — Forever × bakzera

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G41 | Forever | Mago | 23 | 29.29 | Grilhões de Gelo, Raio Congelante, Lasca de Gelo, Tempestade | congelar e quebrar |
| p2 | G58 | bakzera | Ladino | 20 | 25.95 | Gancho e Corda, Marcar a Presa, Corte de Tendão, Ataque Furtivo | atordoar e expor |

- Seed da partida: `8562169872728424794`
- Rodadas: **3**
- Vencedor: **Forever** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4477/4477 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Forever | bakzera |
|---|---|---|
| Dano causado (golpes + DoT) | 3519 (3519 + 0) | 0 (0 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 332 | 83 |
| Skills / ataques básicos | 3 / 0 | 1 / 0 |
| Acertos / erros | 2 / 0 | 0 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 2 | 1 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- Forever aplicou: frozen (rodada 1), vulnerable (rodada 1), stun (rodada 3)
- Forever tentou sem sucesso: slowed (rodada 2)
- bakzera tentou sem sucesso: stun (rodada 1)

Rodada a rodada:

| Rodada | Ordem (critério) | Forever (p1) | bakzera (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Grilhões de Gelo — executada, dano 0, MP −117 | Gancho e Corda — executada, dano 0, MP −83 | 4477 / 2704 | 1687 / 692 |
| 2 | p1 → p2 (score) | Lasca de Gelo — executada, dano 1397, MP −73 | Marcar a Presa — cancelada por controle | 4477 / 1307 | 1670 / 707 |
| 3 | p1 → p2 (score) | Tempestade — executada, dano 2122, MP −142 | Marcar a Presa — cancelada por morte | 4477 / -815 | 1584 / 707 |

#### Fase de 32 2 — dona × brino

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G54 | dona | Ladino | 16 | 25.60 | Hora do Lobo, Lâmina no Escuro, Ataque Furtivo, Sangria Lenta | adaga: sangramento e roubo de vida |
| p2 | G16 | brino | Guerreiro | 20 | 25.26 | Golpe Poderoso, Respiração de Forja, Fôlego de Marcha, Quebra-Ossos | vida máxima e lentidão |

- Seed da partida: `10537839222058908872`
- Rodadas: **13**
- Vencedor: **dona** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 725/2114 (34.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | dona | brino |
|---|---|---|
| Dano causado (golpes + DoT) | 4497 (2667 + 1830) | 1648 (1648 + 0) |
| Cura (skill + roubo de vida) | 259 (0 + 259) | 81 (0 + 81) |
| MP gasto em ações | 547 | 586 |
| Skills / ataques básicos | 11 / 1 | 10 / 2 |
| Acertos / erros | 9 / 0 | 3 / 3 |
| Críticos (dano) | 4 (1414) | 0 (0) |
| Agiu primeiro (rodadas) | 7 | 6 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- dona aplicou: bleed (rodada 5), bleed (rodada 7), bleed (rodada 9), bleed (rodada 12), bleed (rodada 13), vulnerable (rodada 13)
- dona tentou sem sucesso: bleed (rodada 2), poison (rodada 2), bleed (rodada 2), bleed (rodada 3), poison (rodada 3), vulnerable (rodada 3), bleed (rodada 4), poison (rodada 4), poison (rodada 5), bleed (rodada 7), poison (rodada 7), bleed (rodada 8), poison (rodada 8), vulnerable (rodada 8), poison (rodada 9), poison (rodada 12), bleed (rodada 12), poison (rodada 13)
- dona ativou: Sangria Lenta ×3
- brino aplicou: slowed (rodada 3), slowed (rodada 9), stun (rodada 10)
- brino tentou sem sucesso: bleed (rodada 3), bleed (rodada 9), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12)
- brino ativou: Respiração de Forja ×2, Fôlego de Marcha ×2

Rodada a rodada:

| Rodada | Ordem (critério) | dona (p1) | brino (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Sangria Lenta — executada, dano 0, MP −53 | Respiração de Forja — executada, dano 0, MP −91 | 2114 / 4165 | 440 / 426 |
| 2 | p1 → p2 (score) | Hora do Lobo — executada, dano 408, MP −65 | Fôlego de Marcha — executada, dano 0, MP −58 | 2114 / 3757 | 384 / 378 |
| 3 | p1 → p2 (score) | Lâmina no Escuro — executada, dano 347, MP −41 | Quebra-Ossos — executada, dano 0, MP −70 | 2114 / 3410 | 352 / 318 |
| 4 | p2 → p1 (score) | Ataque Furtivo — executada, dano 283, MP −35 | Golpe Poderoso — executada, dano 0, MP −37 | 2114 / 3127 | 326 / 291 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 90 | Ataque básico — executada, dano 0 | 2114 / 3037 | 335 / 301 |
| 6 | p2 → p1 (score) | Sangria Lenta — executada, dano 0, MP −53 | Golpe Poderoso — executada, dano 0, MP −37 | 2114 / 2871 | 291 / 274 |
| 7 | p1 → p2 (score) | Hora do Lobo — executada, dano 437, MP −65 | Respiração de Forja — executada, dano 0, MP −91 | 2114 / 2101 | 235 / 193 |
| 8 | p1 → p2 (score) | Lâmina no Escuro — executada, dano 347, MP −41 | Fôlego de Marcha — executada, dano 0, MP −58 | 2114 / 1421 | 203 / 145 |
| 9 | p1 → p2 (score) | Ataque Furtivo — executada, dano 152, MP −35 | Quebra-Ossos — executada, dano 0, MP −70 | 2114 / 770 | 177 / 85 |
| 10 | p2 → p1 (score) | Ataque básico — cancelada por controle | Golpe Poderoso — executada, dano 671, MP −37 | 1443 / 304 | 186 / 58 |
| 11 | p2 → p1 (score) | Sangria Lenta — executada, dano 0, MP −53 | Ataque básico — executada, dano 356 | 1087 / 321 | 142 / 68 |
| 12 | p2 → p1 (score) | Hora do Lobo — executada, dano 291, MP −65 | Golpe Poderoso — executada, dano 621, MP −37 | 591 / 61 | 86 / 41 |
| 13 | p1 → p2 (score) | Lâmina no Escuro — executada, dano 312, MP −41 | Ataque básico — cancelada por morte | 725 / -251 | 54 / 41 |

#### Fase de 32 3 — sacy × furq

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G57 | sacy | Ladino | 18 | 27.45 | Testamento do Ladrão, Duas Mãos, Um Tempo, Envenenar, Ataque Furtivo | duas armas e veneno |
| p2 | G63 | furq | Ladino | 23 | 28.48 | Hora do Arauto, Pó nos Olhos, Ataque Furtivo, Assassinato | medo |

- Seed da partida: `8364832807771394593`
- Rodadas: **3**
- Vencedor: **furq** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3799/3799 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | sacy | furq |
|---|---|---|
| Dano causado (golpes + DoT) | 0 (0 + 0) | 3386 (3353 + 33) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 94 | 346 |
| Skills / ataques básicos | 1 / 0 | 3 / 0 |
| Acertos / erros | 0 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 1 (1627) |
| Agiu primeiro (rodadas) | 0 | 3 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- sacy tentou sem sucesso: poison (rodada 1)
- furq aplicou: fear (rodada 1), vulnerable (rodada 1), stun (rodada 2), poison (rodada 2), fear (rodada 3)
- furq tentou sem sucesso: fear (rodada 2), stun (rodada 3), poison (rodada 3)

Rodada a rodada:

| Rodada | Ordem (critério) | sacy (p1) | furq (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Envenenar — executada, dano 0, MP −94 | Hora do Arauto — executada, dano 0, MP −140 | 2216 / 3799 | 666 / 949 |
| 2 | p2 → p1 (score) | Testamento do Ladrão — cancelada por controle | Ataque Furtivo — executada, dano 1627, MP −77 | 556 / 3799 | 681 / 893 |
| 3 | p2 → p1 (score) | Testamento do Ladrão — cancelada por morte | Assassinato — executada, dano 1726, MP −129 | -1170 / 3799 | 681 / 785 |

#### Fase de 32 4 — k13tv × aspaszin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G21 | k13tv | Guerreiro | 20 | 26.75 | Postura Impecável, Grito de Guerra, Cutelada, Golpe Poderoso | acúmulo de Força |
| p2 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |

- Seed da partida: `13420971126866494973`
- Rodadas: **4**
- Vencedor: **aspaszin** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3551/4477 (79.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | k13tv | aspaszin |
|---|---|---|
| Dano causado (golpes + DoT) | 926 (926 + 0) | 5125 (5125 + 0) |
| Cura (skill + roubo de vida) | 46 (0 + 46) | 0 (0 + 0) |
| MP gasto em ações | 272 | 414 |
| Skills / ataques básicos | 4 / 0 | 4 / 0 |
| Acertos / erros | 1 / 1 | 3 / 0 |
| Críticos (dano) | 0 (0) | 3 (5125) |
| Agiu primeiro (rodadas) | 2 | 2 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- k13tv tentou sem sucesso: stun (rodada 3), bleed (rodada 3)
- k13tv ativou: Postura Impecável ×1, Grito de Guerra ×1
- aspaszin tentou sem sucesso: fear (rodada 1), vulnerable (rodada 2), vulnerable (rodada 3)
- Égide de aspaszin: absorveu 163 de dano por 81 MP

Rodada a rodada:

| Rodada | Ordem (critério) | k13tv (p1) | aspaszin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −104 | Hora do Arauto — executada, dano 0, MP −140 | 3790 / 4477 | 413 / 1554 |
| 2 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −71 | Prisma de Devastação — executada, dano 2029, MP −131 | 1761 / 4477 | 352 / 1476 |
| 3 | p1 → p2 (score) | Cutelada — executada, dano 926, MP −60 | Lente de Obsidiana — executada, dano 1708, MP −78 | 99 / 3551 | 302 / 1370 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −37 | Bola de Fogo — executada, dano 1388, MP −65 | -1289 / 3551 | 275 / 1358 |

#### Fase de 32 5 — liminhag0d × babi

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G08 | liminhag0d | Guerreiro | 18 | 24.10 | Investida de Aríete, Pisada de Ferro, Golpe Poderoso, Postura de Muro | atordoar com espada e defesa |
| p2 | G39 | babi | Mago | 23 | 28.71 | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | carta lendária de dano |

- Seed da partida: `1982898959702197520`
- Rodadas: **6**
- Vencedor: **babi** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3328/4477 (74.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | liminhag0d | babi |
|---|---|---|
| Dano causado (golpes + DoT) | 1149 (791 + 358) | 3541 (3541 + 0) |
| Cura (skill + roubo de vida) | 24 (0 + 24) | 0 (0 + 0) |
| MP gasto em ações | 189 | 617 |
| Skills / ataques básicos | 5 / 0 | 6 / 0 |
| Acertos / erros | 3 / 0 | 3 / 1 |
| Críticos (dano) | 0 (0) | 1 (1429) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- liminhag0d aplicou: bleed (rodada 2)
- liminhag0d tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), bleed (rodada 3), slowed (rodada 3), stun (rodada 4), bleed (rodada 4)
- liminhag0d ativou: Postura de Muro ×2
- babi ativou: Foco do Estudante ×2
- Égide de babi: absorveu 138 de dano por 68 MP

Rodada a rodada:

| Rodada | Ordem (critério) | liminhag0d (p1) | babi (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −43 | Foco do Estudante — executada, dano 0, MP −76 | 3021 / 4477 | 463 / 1618 |
| 2 | p2 → p1 (score) | Investida de Aríete — executada, dano 280, MP −36 | Apocalipse — executada, dano 0, MP −242 | 3021 / 4197 | 437 / 1405 |
| 3 | p2 → p1 (score) | Pisada de Ferro — executada, dano 296, MP −38 | Bola de Fogo — executada, dano 1056, MP −65 | 1979 / 3722 | 409 / 1367 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 215, MP −29 | Relâmpago — executada, dano 1429, MP −93 | 560 / 3328 | 390 / 1309 |
| 5 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −43 | Foco do Estudante — executada, dano 0, MP −76 | 560 / 3328 | 357 / 1286 |
| 6 | p2 → p1 (score) | Investida de Aríete — cancelada por morte | Bola de Fogo — executada, dano 1056, MP −65 | -496 / 3328 | 357 / 1274 |

#### Fase de 32 6 — Felps × casimito

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G55 | Felps | Ladino | 19 | 27.10 | Dança das Lâminas, Sombra Rápida, Ataque Furtivo, Golpe nas Sombras | dança de lâminas e Agilidade |
| p2 | G35 | casimito | Mago | 20 | 25.83 | Hora Parada, Bola de Fogo, Marca Ardente, Explosão Arcana | sono e explosão |

- Seed da partida: `10511953610061698433`
- Rodadas: **13**
- Vencedor: **Felps** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 807/2415 (33.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Felps | casimito |
|---|---|---|
| Dano causado (golpes + DoT) | 3471 (3471 + 0) | 1731 (1731 + 0) |
| Cura (skill + roubo de vida) | 123 (0 + 123) | 0 (0 + 0) |
| MP gasto em ações | 655 | 632 |
| Skills / ataques básicos | 10 / 0 | 10 / 0 |
| Acertos / erros | 6 / 0 | 2 / 6 |
| Críticos (dano) | 1 (1094) | 0 (0) |
| Agiu primeiro (rodadas) | 13 | 0 |
| Ações perdidas por controle | 3 | 2 |

Efeitos relevantes:
- Felps aplicou: weakened (rodada 2), stun (rodada 5), stun (rodada 6), weakened (rodada 12)
- Felps tentou sem sucesso: stun (rodada 2), poison (rodada 2), stun (rodada 3), poison (rodada 3), poison (rodada 5), poison (rodada 6), weakened (rodada 6), stun (rodada 12), poison (rodada 12), stun (rodada 13), poison (rodada 13)
- Felps ativou: Sombra Rápida ×4
- casimito aplicou: sleep (rodada 7), hexed (rodada 7)
- casimito tentou sem sucesso: sleep (rodada 1)
- Égide de casimito: absorveu 607 de dano por 303 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Felps (p1) | casimito (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −57 | Hora Parada — executada, dano 0, MP −116 | 2415 / 3187 | 794 / 1190 |
| 2 | p1 → p2 (score) | Dança das Lâminas — executada, dano 683, MP −90 | Bola de Fogo — executada, dano 0, MP −46 | 2415 / 2504 | 721 / 1130 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 301, MP −49 | Marca Ardente — executada, dano 0, MP −41 | 2415 / 2203 | 689 / 1109 |
| 4 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −57 | Bola de Fogo — executada, dano 793, MP −46 | 1622 / 2203 | 649 / 1109 |
| 5 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 566, MP −59 | Explosão Arcana — cancelada por controle | 1650 / 1637 | 607 / 1106 |
| 6 | p1 → p2 (score) | Dança das Lâminas — executada, dano 526, MP −90 | Bola de Fogo — cancelada por controle | 1676 / 1111 | 534 / 1106 |
| 7 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −57 | Hora Parada — executada, dano 0, MP −116 | 1676 / 1111 | 494 / 1036 |
| 8 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Bola de Fogo — executada, dano 0, MP −46 | 1676 / 1111 | 511 / 1036 |
| 9 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Marca Ardente — executada, dano 0, MP −41 | 1676 / 1111 | 528 / 1041 |
| 10 | p1 → p2 (score) | Sombra Rápida — cancelada por controle | Bola de Fogo — executada, dano 0, MP −46 | 1676 / 1111 | 545 / 1041 |
| 11 | p1 → p2 (score) | Sombra Rápida — executada, dano 0, MP −57 | Explosão Arcana — executada, dano 938, MP −88 | 738 / 1111 | 505 / 999 |
| 12 | p1 → p2 (score) | Dança das Lâminas — executada, dano 1094, MP −90 | Bola de Fogo — executada, dano 0, MP −46 | 792 / 17 | 432 / 903 |
| 13 | p1 → p2 (score) | Ataque Furtivo — executada, dano 301, MP −49 | Hora Parada — cancelada por morte | 807 / -284 | 400 / 877 |

#### Fase de 32 7 — coldzin × blackoutz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G62 | coldzin | Ladino | 21 | 29.52 | Chuva de Ferrões, Olho do Falcão, Marca do Caçador, Flecha pela Fresta | arco: crítico e sangramento |
| p2 | G14 | blackoutz | Guerreiro | 20 | 27.10 | Veterania, Fio no Rebite, Golpe Poderoso, Golpe Devastador | evasão e crítico de espada |

- Seed da partida: `1924334077511213662`
- Rodadas: **8**
- Vencedor: **coldzin** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 897/3029 (29.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | coldzin | blackoutz |
|---|---|---|
| Dano causado (golpes + DoT) | 6416 (5205 + 1211) | 2282 (2282 + 0) |
| Cura (skill + roubo de vida) | 150 (0 + 150) | 114 (0 + 114) |
| MP gasto em ações | 604 | 396 |
| Skills / ataques básicos | 7 / 1 | 6 / 0 |
| Acertos / erros | 6 / 0 | 1 / 1 |
| Críticos (dano) | 2 (3147) | 1 (2282) |
| Agiu primeiro (rodadas) | 8 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- coldzin aplicou: stun (rodada 2), bleed (rodada 2), bleed (rodada 3), bleed (rodada 7), bleed (rodada 8)
- coldzin tentou sem sucesso: poison (rodada 2), stun (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), slowed (rodada 4), stun (rodada 5), poison (rodada 5), stun (rodada 7), poison (rodada 7), stun (rodada 8), poison (rodada 8)
- coldzin ativou: Olho do Falcão ×2
- blackoutz tentou sem sucesso: stun (rodada 5), bleed (rodada 5)
- blackoutz ativou: Veterania ×2, Fio no Rebite ×2

Rodada a rodada:

| Rodada | Ordem (critério) | coldzin (p1) | blackoutz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Veterania — executada, dano 0, MP −79 | 3029 / 3790 | 780 / 438 |
| 2 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 410, MP −71 | Fio no Rebite — cancelada por controle | 3029 / 3229 | 726 / 448 |
| 3 | p1 → p2 (score) | Marca do Caçador — executada, dano 814, MP −113 | Fio no Rebite — executada, dano 0, MP −58 | 3029 / 2112 | 630 / 400 |
| 4 | p1 → p2 (score) | Flecha pela Fresta — executada, dano 424, MP −60 | Golpe Poderoso — executada, dano 0, MP −37 | 3029 / 1385 | 587 / 373 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 540 | Golpe Devastador — executada, dano 2282, MP −85 | 747 / 656 | 604 / 298 |
| 6 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Veterania — executada, dano 0, MP −79 | 747 / 656 | 533 / 229 |
| 7 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 410, MP −71 | Fio no Rebite — executada, dano 0, MP −58 | 767 / 95 | 479 / 181 |
| 8 | p1 → p2 (score) | Marca do Caçador — executada, dano 2607, MP −113 | Golpe Poderoso — cancelada por morte | 897 / -2512 | 383 / 181 |

#### Fase de 32 8 — tioorochitwitch × MeikodRJ

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G59 | tioorochitwitch | Ladino | 21 | 28.48 | Morte Súbita, Ataque Furtivo, Assassinato, Respiração de Ladrão | carta lendária e crítico |
| p2 | G19 | MeikodRJ | Guerreiro | 22 | 28.37 | Imortal, Golpe Poderoso, Golpe Devastador, Veterania | redução extrema com espada |

- Seed da partida: `11215953123595852302`
- Rodadas: **11**
- Vencedor: **MeikodRJ** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1555/4844 (32.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | tioorochitwitch | MeikodRJ |
|---|---|---|
| Dano causado (golpes + DoT) | 3455 (3023 + 432) | 3639 (3397 + 242) |
| Cura (skill + roubo de vida) | 98 (0 + 98) | 166 (0 + 166) |
| MP gasto em ações | 943 | 755 |
| Skills / ataques básicos | 10 / 1 | 7 / 3 |
| Acertos / erros | 7 / 1 | 6 / 1 |
| Críticos (dano) | 5 (2593) | 3 (1841) |
| Agiu primeiro (rodadas) | 11 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- tioorochitwitch aplicou: stun (rodada 6), poison (rodada 6), poison (rodada 11)
- tioorochitwitch tentou sem sucesso: stun (rodada 2), poison (rodada 2), stun (rodada 3), poison (rodada 3), stun (rodada 7), poison (rodada 7), stun (rodada 8), poison (rodada 8), stun (rodada 10), poison (rodada 10), stun (rodada 11)
- tioorochitwitch ativou: Respiração de Ladrão ×3
- MeikodRJ aplicou: bleed (rodada 8)
- MeikodRJ tentou sem sucesso: stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11)
- MeikodRJ ativou: Imortal ×2, Veterania ×1

Rodada a rodada:

| Rodada | Ordem (critério) | tioorochitwitch (p1) | MeikodRJ (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Imortal — executada, dano 0, MP −204 | 3029 / 4844 | 812 / 444 |
| 2 | p1 → p2 (score) | Morte Súbita — executada, dano 293, MP −193 | Veterania — executada, dano 0, MP −99 | 3029 / 4551 | 636 / 357 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 717, MP −61 | Golpe Poderoso — executada, dano 0, MP −47 | 3029 / 3834 | 592 / 322 |
| 4 | p1 → p2 (score) | Assassinato — executada, dano 0, MP −103 | Golpe Devastador — executada, dano 712, MP −107 | 2317 / 3869 | 506 / 227 |
| 5 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Golpe Poderoso — executada, dano 537, MP −47 | 1780 / 3895 | 467 / 192 |
| 6 | p1 → p2 (score) | Ataque Furtivo — executada, dano 717, MP −61 | Ataque básico — cancelada por controle | 1815 / 3106 | 423 / 204 |
| 7 | p1 → p2 (score) | Ataque básico — executada, dano 343 | Imortal — executada, dano 0, MP −204 | 1832 / 2691 | 440 / 12 |
| 8 | p1 → p2 (score) | Morte Súbita — executada, dano 117, MP −193 | Ataque básico — executada, dano 491 | 1346 / 2526 | 264 / 24 |
| 9 | p1 → p2 (score) | Respiração de Ladrão — executada, dano 0, MP −56 | Ataque básico — executada, dano 491 | 734 / 2478 | 225 / 36 |
| 10 | p1 → p2 (score) | Ataque Furtivo — executada, dano 523, MP −61 | Ataque básico — executada, dano 307 | 332 / 1898 | 181 / 48 |
| 11 | p1 → p2 (score) | Assassinato — executada, dano 313, MP −103 | Golpe Poderoso — executada, dano 859, MP −47 | -512 / 1555 | 95 / 13 |

#### Fase de 32 9 — Tealzlol × SkipNhO

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G24 | Tealzlol | Mago | 15 | 21.80 | Bola de Fogo, Pulso de Força, Lançar Pedra, Lente de Obsidiana | cajado: lentidão, atordoar e vulnerável |
| p2 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |

- Seed da partida: `3646511995625357798`
- Rodadas: **5**
- Vencedor: **SkipNhO** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4759/5004 (95.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Tealzlol | SkipNhO |
|---|---|---|
| Dano causado (golpes + DoT) | 366 (166 + 200) | 2434 (2434 + 0) |
| Cura (skill + roubo de vida) | 3 (0 + 3) | 121 (0 + 121) |
| MP gasto em ações | 100 | 473 |
| Skills / ataques básicos | 4 / 0 | 4 / 1 |
| Acertos / erros | 4 / 0 | 3 / 0 |
| Críticos (dano) | 1 (53) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 5 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Tealzlol aplicou: bleed (rodada 4)
- Tealzlol tentou sem sucesso: bleed (rodada 1), bleed (rodada 2), slowed (rodada 2), bleed (rodada 3), stun (rodada 4)
- Égide de Tealzlol: absorveu 428 de dano por 213 MP
- SkipNhO tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5)
- SkipNhO ativou: Juramento da Muralha ×1, Guarda Cruzada ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Tealzlol (p1) | SkipNhO (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Bola de Fogo — executada, dano 53, MP −26 | Juramento da Muralha — executada, dano 0, MP −136 | 2223 / 4951 | 818 / 512 |
| 2 | p2 → p1 (score) | Pulso de Força — executada, dano 35, MP −24 | Guarda Cruzada — executada, dano 0, MP −99 | 2223 / 4916 | 820 / 425 |
| 3 | p2 → p1 (score) | Bola de Fogo — executada, dano 35, MP −26 | Fortaleza Viva — executada, dano 1383, MP −191 | 841 / 4950 | 706 / 246 |
| 4 | p2 → p1 (score) | Lançar Pedra — executada, dano 43, MP −24 | Golpe Poderoso — executada, dano 667, MP −47 | 176 / 4940 | 658 / 211 |
| 5 | p2 → p1 (score) | Bola de Fogo — cancelada por morte | Ataque básico — executada, dano 384 | -208 / 4759 | 625 / 223 |

#### Fase de 32 10 — Baiano × gafallen

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G32 | Baiano | Mago | 18 | 23.99 | Grilhões de Gelo, Lasca de Gelo, Cerco de Espelhos, Bola de Fogo | controle pesado: congelar e medo |
| p2 | G12 | gafallen | Guerreiro | 20 | 25.95 | Fúria, Grito de Guerra, Golpe Poderoso, Esmagar | buffs de Agilidade e Força |

- Seed da partida: `9185615275984556589`
- Rodadas: **9**
- Vencedor: **gafallen** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2709/3790 (71.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Baiano | gafallen |
|---|---|---|
| Dano causado (golpes + DoT) | 1218 (1218 + 0) | 2770 (2770 + 0) |
| Cura (skill + roubo de vida) | 9 (0 + 9) | 137 (0 + 137) |
| MP gasto em ações | 423 | 531 |
| Skills / ataques básicos | 7 / 1 | 6 / 1 |
| Acertos / erros | 3 / 1 | 4 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 5 | 4 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- Baiano aplicou: frozen (rodada 1), fear (rodada 2), slowed (rodada 2), fear (rodada 8)
- Baiano tentou sem sucesso: vulnerable (rodada 1), bleed (rodada 3), slowed (rodada 3), bleed (rodada 4), bleed (rodada 5), frozen (rodada 6), slowed (rodada 8)
- Égide de Baiano: absorveu 487 de dano por 242 MP
- gafallen tentou sem sucesso: stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9)
- gafallen ativou: Fúria ×2, Grito de Guerra ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Baiano (p1) | gafallen (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −66 | Fúria — cancelada por controle | 2540 / 3790 | 1275 / 517 |
| 2 | p1 → p2 (score) | Cerco de Espelhos — executada, dano 0, MP −86 | Fúria — cancelada por controle | 2540 / 3790 | 1215 / 517 |
| 3 | p1 → p2 (score) | Lasca de Gelo — executada, dano 527, MP −41 | Fúria — executada, dano 0, MP −136 | 2540 / 3263 | 1200 / 381 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 508, MP −37 | Grito de Guerra — executada, dano 0, MP −71 | 2540 / 2755 | 1189 / 320 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 183 | Golpe Poderoso — executada, dano 826, MP −37 | 1723 / 2613 | 1143 / 293 |
| 6 | p2 → p1 (score) | Grilhões de Gelo — executada, dano 0, MP −66 | Esmagar — executada, dano 1045, MP −114 | 678 / 2665 | 1011 / 189 |
| 7 | p1 → p2 (score) | Lasca de Gelo — executada, dano 0, MP −41 | Fúria — executada, dano 0, MP −136 | 678 / 2665 | 996 / 63 |
| 8 | p2 → p1 (score) | Cerco de Espelhos — executada, dano 0, MP −86 | Golpe Poderoso — executada, dano 574, MP −37 | 104 / 2693 | 886 / 36 |
| 9 | p2 → p1 (score) | Bola de Fogo — cancelada por morte | Ataque básico — executada, dano 325 | -221 / 2709 | 858 / 46 |

#### Fase de 32 11 — fer × Hayashii

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G11 | fer | Guerreiro | 18 | 24.10 | Soco de Placa, Quebra-Guarda, Provocação, Golpe Devastador | enfraquecer e expor |
| p2 | G64 | Hayashii | Ladino | 22 | 28.25 | Golpe nas Sombras, Assassinato, Ataque Furtivo, Mão Leve | Força do Ladino e crítico |

- Seed da partida: `16407087863604853934`
- Rodadas: **4**
- Vencedor: **Hayashii** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3193/3392 (94.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fer | Hayashii |
|---|---|---|
| Dano causado (golpes + DoT) | 302 (302 + 0) | 3193 (3193 + 0) |
| Cura (skill + roubo de vida) | 15 (0 + 15) | 103 (0 + 103) |
| MP gasto em ações | 74 | 403 |
| Skills / ataques básicos | 2 / 0 | 4 / 0 |
| Acertos / erros | 1 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 3 (3193) |
| Agiu primeiro (rodadas) | 0 | 4 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- fer aplicou: weakened (rodada 1)
- fer tentou sem sucesso: stun (rodada 2), bleed (rodada 2), weakened (rodada 2)
- Hayashii aplicou: stun (rodada 3)
- Hayashii tentou sem sucesso: stun (rodada 2), poison (rodada 2), poison (rodada 3), stun (rodada 4), poison (rodada 4)
- Hayashii ativou: Mão Leve ×1

Rodada a rodada:

| Rodada | Ordem (critério) | fer (p1) | Hayashii (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Provocação — executada, dano 0, MP −40 | Mão Leve — executada, dano 0, MP −136 | 3021 / 3392 | 466 / 836 |
| 2 | p2 → p1 (score) | Soco de Placa — executada, dano 302, MP −34 | Golpe nas Sombras — executada, dano 1115, MP −83 | 1921 / 3090 | 442 / 772 |
| 3 | p2 → p1 (score) | Quebra-Guarda — cancelada por controle | Assassinato — executada, dano 1221, MP −115 | 700 / 3151 | 452 / 676 |
| 4 | p2 → p1 (score) | Soco de Placa — cancelada por morte | Ataque Furtivo — executada, dano 857, MP −69 | -157 / 3193 | 452 / 626 |

#### Fase de 32 12 — frttt × Coringa

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G40 | frttt | Mago | 24 | 28.14 | Dividendo de Mana, Dreno de Mana, Bola de Fogo, Reserva Profunda | mana: queimar a do rival |
| p2 | G33 | Coringa | Mago | 18 | 24.68 | Dreno de Mana, Troca de Sangue, Bola de Fogo, Drenar Vida | queima de mana e drenos |

- Seed da partida: `1455861312395978412`
- Rodadas: **4**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4725/5014 (94.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | Coringa |
|---|---|---|
| Dano causado (golpes + DoT) | 3274 (3274 + 0) | 289 (289 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 72 (0 + 72) |
| MP gasto em ações | 404 | 129 |
| Skills / ataques básicos | 4 / 0 | 3 / 0 |
| Acertos / erros | 2 / 0 | 1 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 4 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- frttt aplicou: mana_burn (rodada 2)
- frttt tentou sem sucesso: mana_burn (rodada 3)
- frttt ativou: Reserva Profunda ×1
- Égide de frttt: absorveu 51 de dano por 25 MP
- Coringa aplicou: mana_burn (rodada 1)
- Coringa tentou sem sucesso: bleed (rodada 3)
- Égide de Coringa: absorveu 577 de dano por 288 MP

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | Coringa (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Reserva Profunda — executada, dano 0, MP −72 | Dreno de Mana — executada, dano 0, MP −40 | 5014 / 2540 | 2105 / 1265 |
| 2 | p1 → p2 (score) | Dreno de Mana — executada, dano 0, MP −80 | Troca de Sangue — executada, dano 0, MP −52 | 5014 / 2540 | 2097 / 1253 |
| 3 | p1 → p2 (score) | Dividendo de Mana — executada, dano 2454, MP −179 | Bola de Fogo — executada, dano 289, MP −37 | 4725 / 158 | 1973 / 1050 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 820, MP −73 | Drenar Vida — cancelada por morte | 4725 / -662 | 2003 / 978 |

#### Fase de 32 13 — tteuw × Patriota

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G22 | tteuw | Guerreiro | 22 | 28.71 | Pacto de Ferro, Tomar Fôlego, Tremor de Bigorna, Golpe Poderoso | maça: redução, cura e roubo de vida |
| p2 | G60 | Patriota | Ladino | 19 | 28.14 | Cobrança de Juros, Joelho Torto, Corte de Passagem, Ataque Furtivo | sangramento máximo |

- Seed da partida: `7594704525375918654`
- Rodadas: **11**
- Vencedor: **Patriota** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 882/2490 (35.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | tteuw | Patriota |
|---|---|---|
| Dano causado (golpes + DoT) | 1633 (1633 + 0) | 6600 (985 + 5615) |
| Cura (skill + roubo de vida) | 1608 (581 + 1027) | 25 (0 + 25) |
| MP gasto em ações | 591 | 685 |
| Skills / ataques básicos | 7 / 2 | 10 / 0 |
| Acertos / erros | 3 / 3 | 5 / 0 |
| Críticos (dano) | 0 (0) | 1 (192) |
| Agiu primeiro (rodadas) | 0 | 11 |
| Ações perdidas por controle | 1 | 1 |

Efeitos relevantes:
- tteuw aplicou: stun (rodada 10)
- tteuw tentou sem sucesso: stun (rodada 4), stun (rodada 5), stun (rodada 10)
- tteuw ativou: Pacto de Ferro ×2
- Patriota aplicou: slowed (rodada 1), bleed (rodada 3), bleed (rodada 3), bleed (rodada 4), slowed (rodada 5), bleed (rodada 6), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), bleed (rodada 8), bleed (rodada 10)
- Patriota tentou sem sucesso: bleed (rodada 1), bleed (rodada 2), stun (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), bleed (rodada 5), stun (rodada 7), poison (rodada 7), poison (rodada 8), slowed (rodada 9), stun (rodada 10), poison (rodada 10)

Rodada a rodada:

| Rodada | Ordem (critério) | tteuw (p1) | Patriota (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pacto de Ferro — executada, dano 0, MP −136 | Joelho Torto — executada, dano 0, MP −48 | 4844 / 2490 | 512 / 803 |
| 2 | p2 → p1 (score) | Tremor de Bigorna — executada, dano 0, MP −71 | Corte de Passagem — executada, dano 0, MP −94 | 4844 / 2490 | 453 / 726 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Cobrança de Juros — executada, dano 259, MP −103 | 4198 / 2490 | 418 / 640 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 325 | Ataque Furtivo — executada, dano 192, MP −49 | 3629 / 2165 | 430 / 608 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 612, MP −47 | Joelho Torto — executada, dano 0, MP −48 | 3433 / 1553 | 395 / 577 |
| 6 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Corte de Passagem — executada, dano 0, MP −94 | 3240 / 1553 | 407 / 500 |
| 7 | p2 → p1 (score) | Pacto de Ferro — executada, dano 0, MP −136 | Ataque Furtivo — executada, dano 187, MP −49 | 2666 / 1562 | 283 / 468 |
| 8 | p2 → p1 (score) | Tremor de Bigorna — cancelada por controle | Cobrança de Juros — executada, dano 259, MP −103 | 1632 / 1574 | 295 / 382 |
| 9 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Joelho Torto — executada, dano 0, MP −48 | 1438 / 1574 | 224 / 351 |
| 10 | p2 → p1 (score) | Tremor de Bigorna — executada, dano 696, MP −71 | Ataque Furtivo — executada, dano 88, MP −49 | 820 / 882 | 165 / 319 |
| 11 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — cancelada por controle | -148 / 882 | 177 / 336 |

#### Fase de 32 14 — DavyJones × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G04 | DavyJones | Guerreiro | 16 | 21.68 | Golpe Poderoso, Grito de Guerra, Cutelada, Golpe Duplo | Força bruta e fragilidade |
| p2 | G56 | RNakano | Ladino | 20 | 25.60 | Silêncio de Seda, Nó Corredio, Ataque Furtivo, Golpe nas Sombras | sono e atordoamento |

- Seed da partida: `12761548428170422022`
- Rodadas: **9**
- Vencedor: **RNakano** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1973/2704 (73.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | DavyJones | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 768 (768 + 0) | 3275 (3095 + 180) |
| Cura (skill + roubo de vida) | 38 (0 + 38) | 37 (0 + 37) |
| MP gasto em ações | 106 | 621 |
| Skills / ataques básicos | 3 / 0 | 8 / 1 |
| Acertos / erros | 1 / 1 | 5 / 0 |
| Críticos (dano) | 1 (768) | 2 (1498) |
| Agiu primeiro (rodadas) | 0 | 9 |
| Ações perdidas por controle | 5 | 0 |

Efeitos relevantes:
- DavyJones tentou sem sucesso: stun (rodada 6)
- DavyJones ativou: Grito de Guerra ×1
- RNakano aplicou: sleep (rodada 1), stun (rodada 3), poison (rodada 5), sleep (rodada 7), stun (rodada 8), slowed (rodada 8)
- RNakano tentou sem sucesso: mana_burn (rodada 1), stun (rodada 2), poison (rodada 3), stun (rodada 4), poison (rodada 4), stun (rodada 5), stun (rodada 6), poison (rodada 6), mana_burn (rodada 7), stun (rodada 9), poison (rodada 9)

Rodada a rodada:

| Rodada | Ordem (critério) | DavyJones (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Grito de Guerra — cancelada por controle | Silêncio de Seda — executada, dano 0, MP −108 | 3035 / 2704 | 328 / 667 |
| 2 | p2 → p1 (score) | Grito de Guerra — cancelada por controle | Nó Corredio — executada, dano 0, MP −87 | 3035 / 2704 | 328 / 595 |
| 3 | p2 → p1 (score) | Grito de Guerra — cancelada por controle | Ataque Furtivo — executada, dano 642, MP −55 | 2393 / 2704 | 328 / 555 |
| 4 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −45 | Golpe nas Sombras — executada, dano 649, MP −66 | 1744 / 2704 | 283 / 504 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −23 | Ataque básico — executada, dano 306 | 1393 / 2704 | 266 / 519 |
| 6 | p2 → p1 (score) | Cutelada — executada, dano 768, MP −38 | Ataque Furtivo — executada, dano 749, MP −55 | 637 / 1936 | 234 / 479 |
| 7 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Silêncio de Seda — executada, dano 0, MP −108 | 592 / 1936 | 240 / 386 |
| 8 | p2 → p1 (score) | Grito de Guerra — cancelada por controle | Nó Corredio — executada, dano 0, MP −87 | 547 / 1936 | 246 / 314 |
| 9 | p2 → p1 (score) | Grito de Guerra — cancelada por morte | Ataque Furtivo — executada, dano 749, MP −55 | -202 / 1973 | 246 / 274 |

#### Fase de 32 15 — gabepeixe × Dilera

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G13 | gabepeixe | Guerreiro | 19 | 29.52 | Golpe Poderoso, Colheita de Ferro, Juramento da Muralha, Mão Dupla | duas armas: sangramento pesado |
| p2 | G42 | Dilera | Mago | 20 | 29.17 | Sanguessuga Arcana, Drenar Vida, Ressurgir, Bola de Fogo | roubo de vida e cura |

- Seed da partida: `3609054038807378005`
- Rodadas: **17**
- Vencedor: **gabepeixe** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2751/3509 (78.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gabepeixe | Dilera |
|---|---|---|
| Dano causado (golpes + DoT) | 9040 (3958 + 5082) | 950 (950 + 0) |
| Cura (skill + roubo de vida) | 192 (0 + 192) | 5649 (5055 + 594) |
| MP gasto em ações | 699 | 967 |
| Skills / ataques básicos | 13 / 3 | 13 / 3 |
| Acertos / erros | 10 / 4 | 4 / 4 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 17 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- gabepeixe aplicou: bleed (rodada 3), bleed (rodada 4), bleed (rodada 5), bleed (rodada 8), bleed (rodada 10), bleed (rodada 11), bleed (rodada 11), bleed (rodada 12), bleed (rodada 13), bleed (rodada 14), bleed (rodada 15)
- gabepeixe tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15)
- gabepeixe ativou: Juramento da Muralha ×2
- Dilera ativou: Sanguessuga Arcana ×3
- Égide de Dilera: absorveu 694 de dano por 345 MP

Rodada a rodada:

| Rodada | Ordem (critério) | gabepeixe (p1) | Dilera (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −96 | Sanguessuga Arcana — executada, dano 0, MP −87 | 3509 / 3262 | 471 / 1119 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −33 | Bola de Fogo — executada, dano 0, MP −46 | 3509 / 3262 | 449 / 1137 |
| 3 | p2 → p1 (score) | Colheita de Ferro — executada, dano 591, MP −78 | Ataque básico — executada, dano 149 | 3389 / 2671 | 382 / 1149 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 372, MP −33 | Bola de Fogo — executada, dano 0, MP −46 | 3407 / 2169 | 360 / 1128 |
| 5 | p2 → p1 (score) | Mão Dupla — executada, dano 525, MP −60 | Ataque básico — executada, dano 149 | 3284 / 1470 | 311 / 1146 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −33 | Drenar Vida — executada, dano 0, MP −44 | 3284 / 1568 | 289 / 1162 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −96 | Ressurgir — executada, dano 0, MP −172 | 3284 / 2971 | 204 / 1034 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 397, MP −33 | Sanguessuga Arcana — executada, dano 0, MP −87 | 3303 / 2574 | 182 / 976 |
| 9 | p2 → p1 (score) | Colheita de Ferro — executada, dano 0, MP −78 | Bola de Fogo — executada, dano 0, MP −46 | 3303 / 2444 | 115 / 994 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 372, MP −33 | Ataque básico — executada, dano 149 | 3172 / 2058 | 93 / 1026 |
| 11 | p2 → p1 (score) | Mão Dupla — executada, dano 525, MP −60 | Bola de Fogo — executada, dano 0, MP −46 | 3198 / 1403 | 44 / 998 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 372, MP −33 | Drenar Vida — executada, dano 0, MP −44 | 3216 / 1129 | 22 / 986 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 216 | Ressurgir — executada, dano 0, MP −172 | 3226 / 2186 | 33 / 859 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 372, MP −33 | Sanguessuga Arcana — executada, dano 0, MP −87 | 3244 / 1162 | 11 / 804 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 216 | Drenar Vida — executada, dano 0, MP −44 | 3254 / 783 | 22 / 805 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Bola de Fogo — executada, dano 503, MP −46 | 2751 / 523 | 33 / 823 |
| 17 | p2 → p1 (score) | Golpe Poderoso — não alcançada (o duelo acabou antes) | Ataque básico — cancelada por morte | 2751 / -129 | 33 / 887 |

#### Fase de 32 16 — LuquEt4 × boltz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G20 | LuquEt4 | Guerreiro | 22 | 28.48 | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | medo e vulnerabilidade |
| p2 | G47 | boltz | Ladino | 15 | 21.92 | Evasão, Sombra Rápida, Corte de Tendão, Golpe nas Sombras | evasão e Agilidade |

- Seed da partida: `6600561904627291676`
- Rodadas: **7**
- Vencedor: **LuquEt4** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3953/4754 (83.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | LuquEt4 | boltz |
|---|---|---|
| Dano causado (golpes + DoT) | 2258 (2258 + 0) | 912 (912 + 0) |
| Cura (skill + roubo de vida) | 111 (0 + 111) | 15 (0 + 15) |
| MP gasto em ações | 610 | 225 |
| Skills / ataques básicos | 5 / 2 | 7 / 0 |
| Acertos / erros | 3 / 2 | 3 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 7 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- LuquEt4 aplicou: fear (rodada 1), vulnerable (rodada 1), fear (rodada 6), vulnerable (rodada 6), stun (rodada 7)
- LuquEt4 tentou sem sucesso: stun (rodada 4), bleed (rodada 4), fear (rodada 4), stun (rodada 5), bleed (rodada 5), fear (rodada 5), bleed (rodada 7), fear (rodada 7)
- boltz aplicou: slowed (rodada 3)
- boltz tentou sem sucesso: bleed (rodada 3), bleed (rodada 4), bleed (rodada 7), slowed (rodada 7)
- boltz ativou: Evasão ×2, Sombra Rápida ×2

Rodada a rodada:

| Rodada | Ordem (critério) | LuquEt4 (p1) | boltz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Silêncio do Veterano — executada, dano 0, MP −120 | Evasão — executada, dano 0, MP −25 | 4754 / 1888 | 528 / 415 |
| 2 | p2 → p1 (score) | Carga do Condenado — executada, dano 0, MP −119 | Sombra Rápida — executada, dano 0, MP −36 | 4754 / 1888 | 421 / 387 |
| 3 | p2 → p1 (score) | Esmagar — executada, dano 0, MP −144 | Corte de Tendão — executada, dano 313, MP −33 | 4441 / 1888 | 289 / 362 |
| 4 | p2 → p1 (score) | Golpe Devastador — executada, dano 1174, MP −107 | Golpe nas Sombras — executada, dano 286, MP −37 | 4213 / 714 | 194 / 333 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 506 | Evasão — executada, dano 0, MP −25 | 4238 / 208 | 206 / 316 |
| 6 | p2 → p1 (score) | Silêncio do Veterano — executada, dano 0, MP −120 | Sombra Rápida — executada, dano 0, MP −36 | 4238 / 208 | 98 / 288 |
| 7 | p2 → p1 (score) | Ataque básico — executada, dano 578 | Corte de Tendão — executada, dano 313, MP −33 | 3953 / -355 | 110 / 263 |

### Oitavas: detalhes

#### Oitavas 1 — Forever × dona

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G41 | Forever | Mago | 23 | 29.29 | Grilhões de Gelo, Raio Congelante, Lasca de Gelo, Tempestade | congelar e quebrar |
| p2 | G54 | dona | Ladino | 16 | 25.60 | Hora do Lobo, Lâmina no Escuro, Ataque Furtivo, Sangria Lenta | adaga: sangramento e roubo de vida |

- Seed da partida: `7721911110119933238`
- Rodadas: **4**
- Vencedor: **Forever** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4477/4477 (100.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Forever | dona |
|---|---|---|
| Dano causado (golpes + DoT) | 3439 (3439 + 0) | 0 (0 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 423 | 53 |
| Skills / ataques básicos | 4 / 0 | 1 / 0 |
| Acertos / erros | 2 / 0 | 0 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 4 | 0 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- Forever aplicou: frozen (rodada 1), vulnerable (rodada 1)
- Forever tentou sem sucesso: slowed (rodada 2), frozen (rodada 3), stun (rodada 4)
- dona ativou: Sangria Lenta ×1

Rodada a rodada:

| Rodada | Ordem (critério) | Forever (p1) | dona (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −117 | Sangria Lenta — cancelada por controle | 4477 / 2114 | 1687 / 493 |
| 2 | p1 → p2 (score) | Lasca de Gelo — executada, dano 1879, MP −73 | Sangria Lenta — cancelada por controle | 4477 / 235 | 1670 / 493 |
| 3 | p1 → p2 (score) | Raio Congelante — executada, dano 0, MP −91 | Sangria Lenta — executada, dano 0, MP −53 | 4477 / 235 | 1635 / 440 |
| 4 | p1 → p2 (score) | Tempestade — executada, dano 1560, MP −142 | Hora do Lobo — cancelada por morte | 4477 / -1325 | 1549 / 440 |

#### Oitavas 2 — furq × aspaszin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G63 | furq | Ladino | 23 | 28.48 | Hora do Arauto, Pó nos Olhos, Ataque Furtivo, Assassinato | medo |
| p2 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |

- Seed da partida: `15223661065245555588`
- Rodadas: **9**
- Vencedor: **aspaszin** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 202/4477 (4.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | furq | aspaszin |
|---|---|---|
| Dano causado (golpes + DoT) | 4275 (3538 + 737) | 4200 (4200 + 0) |
| Cura (skill + roubo de vida) | 99 (0 + 99) | 0 (0 + 0) |
| MP gasto em ações | 769 | 828 |
| Skills / ataques básicos | 7 / 2 | 8 / 1 |
| Acertos / erros | 6 / 1 | 3 / 4 |
| Críticos (dano) | 2 (1299) | 1 (1919) |
| Agiu primeiro (rodadas) | 9 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- furq aplicou: fear (rodada 1), vulnerable (rodada 1), poison (rodada 2), poison (rodada 3), fear (rodada 4), fear (rodada 7), vulnerable (rodada 7)
- furq tentou sem sucesso: stun (rodada 2), fear (rodada 2), stun (rodada 3), fear (rodada 3), stun (rodada 4), poison (rodada 4), stun (rodada 6), poison (rodada 6), fear (rodada 6), stun (rodada 8), poison (rodada 8), fear (rodada 8), stun (rodada 9), poison (rodada 9), fear (rodada 9)
- aspaszin aplicou: vulnerable (rodada 3), fear (rodada 7)
- aspaszin tentou sem sucesso: fear (rodada 1), vulnerable (rodada 7), vulnerable (rodada 8), vulnerable (rodada 9)
- Égide de aspaszin: absorveu 620 de dano por 308 MP

Rodada a rodada:

| Rodada | Ordem (critério) | furq (p1) | aspaszin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Hora do Arauto — executada, dano 0, MP −140 | Hora do Arauto — executada, dano 0, MP −140 | 3799 / 4477 | 949 / 1554 |
| 2 | p1 → p2 (score) | Ataque Furtivo — executada, dano 929, MP −77 | Prisma de Devastação — executada, dano 0, MP −131 | 3799 / 3481 | 893 / 1395 |
| 3 | p1 → p2 (score) | Assassinato — executada, dano 597, MP −129 | Lente de Obsidiana — executada, dano 959, MP −78 | 2840 / 2750 | 785 / 1318 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 370 | Bola de Fogo — executada, dano 0, MP −65 | 2858 / 2246 | 806 / 1274 |
| 5 | p1 → p2 (score) | Ataque Furtivo — executada, dano 0, MP −77 | Ataque básico — executada, dano 0 | 2858 / 2112 | 750 / 1327 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 232 | Bola de Fogo — executada, dano 0, MP −65 | 2869 / 1746 | 771 / 1295 |
| 7 | p1 → p2 (score) | Hora do Arauto — executada, dano 0, MP −140 | Hora do Arauto — executada, dano 0, MP −140 | 2869 / 1612 | 652 / 1208 |
| 8 | p1 → p2 (score) | Ataque Furtivo — executada, dano 424, MP −77 | Prisma de Devastação — executada, dano 1322, MP −131 | 1568 / 1188 | 596 / 1093 |
| 9 | p1 → p2 (score) | Assassinato — executada, dano 986, MP −129 | Lente de Obsidiana — executada, dano 1919, MP −78 | -302 / 202 | 488 / 982 |

#### Oitavas 3 — babi × Felps

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G39 | babi | Mago | 23 | 28.71 | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | carta lendária de dano |
| p2 | G55 | Felps | Ladino | 19 | 27.10 | Dança das Lâminas, Sombra Rápida, Ataque Furtivo, Golpe nas Sombras | dança de lâminas e Agilidade |

- Seed da partida: `8947670749788689304`
- Rodadas: **3**
- Vencedor: **babi** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3570/4477 (79.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | babi | Felps |
|---|---|---|
| Dano causado (golpes + DoT) | 3760 (3760 + 0) | 907 (840 + 67) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 15 (0 + 15) |
| MP gasto em ações | 383 | 196 |
| Skills / ataques básicos | 3 / 0 | 3 / 0 |
| Acertos / erros | 2 / 0 | 2 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 3 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- babi ativou: Foco do Estudante ×1
- Égide de babi: absorveu 147 de dano por 73 MP
- Felps aplicou: weakened (rodada 2), poison (rodada 3)
- Felps tentou sem sucesso: stun (rodada 2), poison (rodada 2), stun (rodada 3)
- Felps ativou: Sombra Rápida ×1

Rodada a rodada:

| Rodada | Ordem (critério) | babi (p1) | Felps (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Foco do Estudante — executada, dano 0, MP −76 | Sombra Rápida — executada, dano 0, MP −57 | 4477 / 2415 | 1618 / 794 |
| 2 | p2 → p1 (score) | Apocalipse — executada, dano 2302, MP −242 | Dança das Lâminas — executada, dano 524, MP −90 | 3953 / 113 | 1383 / 721 |
| 3 | p2 → p1 (score) | Bola de Fogo — executada, dano 1458, MP −65 | Ataque Furtivo — executada, dano 316, MP −49 | 3570 / -1330 | 1344 / 689 |

#### Oitavas 4 — coldzin × MeikodRJ

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G62 | coldzin | Ladino | 21 | 29.52 | Chuva de Ferrões, Olho do Falcão, Marca do Caçador, Flecha pela Fresta | arco: crítico e sangramento |
| p2 | G19 | MeikodRJ | Guerreiro | 22 | 28.37 | Imortal, Golpe Poderoso, Golpe Devastador, Veterania | redução extrema com espada |

- Seed da partida: `1996998103972129108`
- Rodadas: **11**
- Vencedor: **MeikodRJ** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1996/4844 (41.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | coldzin | MeikodRJ |
|---|---|---|
| Dano causado (golpes + DoT) | 3012 (1658 + 1354) | 3464 (3343 + 121) |
| Cura (skill + roubo de vida) | 65 (0 + 65) | 164 (0 + 164) |
| MP gasto em ações | 752 | 755 |
| Skills / ataques básicos | 9 / 2 | 7 / 3 |
| Acertos / erros | 7 / 1 | 5 / 2 |
| Críticos (dano) | 1 (510) | 2 (1787) |
| Agiu primeiro (rodadas) | 11 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- coldzin aplicou: stun (rodada 2), bleed (rodada 7), bleed (rodada 8), slowed (rodada 9)
- coldzin tentou sem sucesso: poison (rodada 2), bleed (rodada 2), stun (rodada 4), poison (rodada 4), slowed (rodada 4), stun (rodada 5), poison (rodada 5), stun (rodada 7), poison (rodada 7), stun (rodada 8), poison (rodada 8), stun (rodada 9), poison (rodada 9), stun (rodada 10), poison (rodada 10)
- coldzin ativou: Olho do Falcão ×3
- MeikodRJ aplicou: bleed (rodada 10), bleed (rodada 11)
- MeikodRJ tentou sem sucesso: stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 10), stun (rodada 11)
- MeikodRJ ativou: Imortal ×2, Veterania ×1

Rodada a rodada:

| Rodada | Ordem (critério) | coldzin (p1) | MeikodRJ (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Imortal — executada, dano 0, MP −204 | 3029 / 4844 | 780 / 444 |
| 2 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 80, MP −71 | Veterania — cancelada por controle | 3029 / 4764 | 726 / 456 |
| 3 | p1 → p2 (score) | Marca do Caçador — executada, dano 0, MP −113 | Veterania — executada, dano 0, MP −99 | 3029 / 4764 | 630 / 369 |
| 4 | p1 → p2 (score) | Flecha pela Fresta — executada, dano 232, MP −60 | Golpe Poderoso — executada, dano 928, MP −47 | 2101 / 4578 | 587 / 334 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 132 | Golpe Devastador — executada, dano 712, MP −107 | 1395 / 4481 | 604 / 239 |
| 6 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Golpe Poderoso — executada, dano 859, MP −47 | 536 / 4523 | 533 / 204 |
| 7 | p1 → p2 (score) | Chuva de Ferrões — executada, dano 281, MP −71 | Imortal — executada, dano 0, MP −204 | 550 / 4049 | 479 / 12 |
| 8 | p1 → p2 (score) | Marca do Caçador — executada, dano 510, MP −113 | Ataque básico — executada, dano 0 | 575 / 3152 | 383 / 24 |
| 9 | p1 → p2 (score) | Flecha pela Fresta — executada, dano 291, MP −60 | Ataque básico — executada, dano 0 | 589 / 2474 | 340 / 36 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 132 | Ataque básico — executada, dano 307 | 288 / 1970 | 357 / 48 |
| 11 | p1 → p2 (score) | Olho do Falcão — executada, dano 0, MP −88 | Golpe Poderoso — executada, dano 537, MP −47 | -370 / 1996 | 286 / 13 |

#### Oitavas 5 — SkipNhO × gafallen

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |
| p2 | G12 | gafallen | Guerreiro | 20 | 25.95 | Fúria, Grito de Guerra, Golpe Poderoso, Esmagar | buffs de Agilidade e Força |

- Seed da partida: `18338950524184299450`
- Rodadas: **17**
- Vencedor: **SkipNhO** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3362/5004 (67.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | SkipNhO | gafallen |
|---|---|---|
| Dano causado (golpes + DoT) | 3885 (3885 + 0) | 1834 (1034 + 800) |
| Cura (skill + roubo de vida) | 192 (0 + 192) | 43 (0 + 43) |
| MP gasto em ações | 797 | 633 |
| Skills / ataques básicos | 9 / 8 | 9 / 6 |
| Acertos / erros | 12 / 2 | 8 / 2 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 6 | 11 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- SkipNhO aplicou: stun (rodada 3)
- SkipNhO tentou sem sucesso: bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 8), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17)
- SkipNhO ativou: Juramento da Muralha ×2, Guarda Cruzada ×1
- gafallen aplicou: bleed (rodada 7), bleed (rodada 13)
- gafallen tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 7), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 13), stun (rodada 15), bleed (rodada 15)
- gafallen ativou: Fúria ×2, Grito de Guerra ×3

Rodada a rodada:

| Rodada | Ordem (critério) | SkipNhO (p1) | gafallen (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Fúria — executada, dano 0, MP −136 | 5004 / 3790 | 512 / 381 |
| 2 | p2 → p1 (score) | Guarda Cruzada — executada, dano 0, MP −99 | Grito de Guerra — executada, dano 0, MP −71 | 5004 / 3790 | 425 / 320 |
| 3 | p2 → p1 (score) | Fortaleza Viva — executada, dano 798, MP −191 | Golpe Poderoso — executada, dano 111, MP −37 | 4932 / 2992 | 246 / 293 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 385, MP −47 | Esmagar — cancelada por controle | 4951 / 2607 | 211 / 303 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 221 | Fúria — executada, dano 0, MP −136 | 4962 / 2386 | 223 / 177 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Grito de Guerra — executada, dano 0, MP −71 | 4962 / 2386 | 188 / 116 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Golpe Poderoso — executada, dano 316, MP −37 | 4446 / 2401 | 64 / 89 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 385, MP −47 | Ataque básico — executada, dano 57 | 4208 / 2018 | 29 / 99 |
| 9 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 82, MP −37 | 4126 / 2022 | 41 / 72 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 221 | Grito de Guerra — executada, dano 0, MP −71 | 4137 / 1801 | 53 / 11 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 385, MP −47 | Ataque básico — executada, dano 57 | 4099 / 1418 | 18 / 21 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 221 | Ataque básico — executada, dano 163 | 3947 / 1205 | 30 / 31 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 221 | Ataque básico — executada, dano 124 | 3634 / 990 | 42 / 41 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 221 | Golpe Poderoso — executada, dano 0, MP −37 | 3445 / 769 | 54 / 14 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 385, MP −47 | Ataque básico — executada, dano 124 | 3340 / 390 | 19 / 24 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 221 | Ataque básico — executada, dano 0 | 3351 / 169 | 31 / 34 |
| 17 | p1 → p2 (score) | Ataque básico — executada, dano 221 | Ataque básico — cancelada por morte | 3362 / -52 | 43 / 34 |

#### Oitavas 6 — Hayashii × frttt

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G64 | Hayashii | Ladino | 22 | 28.25 | Golpe nas Sombras, Assassinato, Ataque Furtivo, Mão Leve | Força do Ladino e crítico |
| p2 | G40 | frttt | Mago | 24 | 28.14 | Dividendo de Mana, Dreno de Mana, Bola de Fogo, Reserva Profunda | mana: queimar a do rival |

- Seed da partida: `14378117799292324843`
- Rodadas: **8**
- Vencedor: **frttt** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1665/5014 (33.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Hayashii | frttt |
|---|---|---|
| Dano causado (golpes + DoT) | 3349 (3349 + 0) | 5064 (5064 + 0) |
| Cura (skill + roubo de vida) | 98 (0 + 98) | 0 (0 + 0) |
| MP gasto em ações | 705 | 735 |
| Skills / ataques básicos | 7 / 1 | 7 / 0 |
| Acertos / erros | 6 / 0 | 3 / 0 |
| Críticos (dano) | 5 (3148) | 0 (0) |
| Agiu primeiro (rodadas) | 8 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- Hayashii aplicou: stun (rodada 4)
- Hayashii tentou sem sucesso: stun (rodada 2), poison (rodada 2), stun (rodada 3), poison (rodada 3), poison (rodada 4), stun (rodada 5), poison (rodada 5), stun (rodada 6), poison (rodada 6), stun (rodada 8), poison (rodada 8)
- Hayashii ativou: Mão Leve ×2
- frttt aplicou: mana_burn (rodada 2), mana_burn (rodada 3), mana_burn (rodada 7), mana_burn (rodada 8)
- frttt ativou: Reserva Profunda ×2
- Égide de frttt: absorveu 589 de dano por 293 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Hayashii (p1) | frttt (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Mão Leve — executada, dano 0, MP −136 | Reserva Profunda — executada, dano 0, MP −72 | 3392 / 5014 | 836 / 2105 |
| 2 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 647, MP −83 | Dreno de Mana — executada, dano 0, MP −80 | 3392 / 4367 | 772 / 2071 |
| 3 | p1 → p2 (score) | Assassinato — executada, dano 709, MP −115 | Dividendo de Mana — executada, dano 2170, MP −179 | 1222 / 3658 | 664 / 1933 |
| 4 | p1 → p2 (score) | Ataque Furtivo — executada, dano 498, MP −69 | Bola de Fogo — cancelada por controle | 1246 / 3160 | 602 / 1993 |
| 5 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 647, MP −83 | Bola de Fogo — executada, dano 724, MP −73 | 554 / 2513 | 526 / 1966 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 201 | Reserva Profunda — executada, dano 0, MP −72 | 564 / 2312 | 545 / 1980 |
| 7 | p1 → p2 (score) | Mão Leve — executada, dano 0, MP −136 | Dreno de Mana — executada, dano 0, MP −80 | 564 / 2312 | 428 / 2003 |
| 8 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 647, MP −83 | Dividendo de Mana — executada, dano 2170, MP −179 | -1574 / 1665 | 352 / 1870 |

#### Oitavas 7 — Patriota × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G60 | Patriota | Ladino | 19 | 28.14 | Cobrança de Juros, Joelho Torto, Corte de Passagem, Ataque Furtivo | sangramento máximo |
| p2 | G56 | RNakano | Ladino | 20 | 25.60 | Silêncio de Seda, Nó Corredio, Ataque Furtivo, Golpe nas Sombras | sono e atordoamento |

- Seed da partida: `4383623172331005430`
- Rodadas: **9**
- Vencedor: **RNakano** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1200/2704 (44.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Patriota | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 1604 (1012 + 592) | 2955 (2622 + 333) |
| Cura (skill + roubo de vida) | 50 (0 + 50) | 100 (0 + 100) |
| MP gasto em ações | 293 | 621 |
| Skills / ataques básicos | 4 / 0 | 8 / 1 |
| Acertos / erros | 1 / 0 | 4 / 1 |
| Críticos (dano) | 0 (0) | 1 (702) |
| Agiu primeiro (rodadas) | 8 | 1 |
| Ações perdidas por controle | 4 | 0 |

Efeitos relevantes:
- Patriota aplicou: bleed (rodada 4), poison (rodada 6)
- Patriota tentou sem sucesso: slowed (rodada 1), slowed (rodada 5), stun (rodada 6), bleed (rodada 6), bleed (rodada 6)
- RNakano aplicou: sleep (rodada 1), mana_burn (rodada 1), stun (rodada 2), poison (rodada 3), poison (rodada 4), stun (rodada 6), sleep (rodada 7), stun (rodada 8), slowed (rodada 8)
- RNakano tentou sem sucesso: slowed (rodada 2), stun (rodada 3), stun (rodada 4), poison (rodada 6), mana_burn (rodada 7), stun (rodada 9), poison (rodada 9)
- Leis disparadas por RNakano: FERIDA SÉPTICA (rodada 6)

Rodada a rodada:

| Rodada | Ordem (critério) | Patriota (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Joelho Torto — executada, dano 0, MP −48 | Silêncio de Seda — executada, dano 0, MP −108 | 2490 / 2704 | 803 / 667 |
| 2 | p1 → p2 (score) | Corte de Passagem — cancelada por controle | Nó Corredio — executada, dano 0, MP −87 | 2490 / 2704 | 808 / 595 |
| 3 | p1 → p2 (score) | Corte de Passagem — cancelada por controle | Ataque Furtivo — executada, dano 601, MP −55 | 1889 / 2704 | 813 / 555 |
| 4 | p1 → p2 (score) | Corte de Passagem — executada, dano 0, MP −94 | Golpe nas Sombras — executada, dano 881, MP −66 | 971 / 2640 | 736 / 504 |
| 5 | p1 → p2 (score) | Joelho Torto — executada, dano 0, MP −48 | Ataque básico — executada, dano 0 | 897 / 2532 | 705 / 519 |
| 6 | p1 → p2 (score) | Cobrança de Juros — executada, dano 1012, MP −103 | Ataque Furtivo — executada, dano 702, MP −55 | 171 / 1407 | 619 / 479 |
| 7 | p1 → p2 (score) | Ataque Furtivo — cancelada por controle | Silêncio de Seda — executada, dano 0, MP −108 | 97 / 1259 | 636 / 386 |
| 8 | p1 → p2 (score) | Corte de Passagem — cancelada por controle | Nó Corredio — executada, dano 0, MP −87 | 23 / 1219 | 653 / 314 |
| 9 | p2 → p1 (score) | Joelho Torto — cancelada por morte | Ataque Furtivo — executada, dano 438, MP −55 | -415 / 1200 | 653 / 274 |

#### Oitavas 8 — gabepeixe × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G13 | gabepeixe | Guerreiro | 19 | 29.52 | Golpe Poderoso, Colheita de Ferro, Juramento da Muralha, Mão Dupla | duas armas: sangramento pesado |
| p2 | G20 | LuquEt4 | Guerreiro | 22 | 28.48 | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | medo e vulnerabilidade |

- Seed da partida: `11812667810472321170`
- Rodadas: **14**
- Vencedor: **LuquEt4** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2812/4754 (59.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gabepeixe | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 2093 (1333 + 760) | 3639 (3499 + 140) |
| Cura (skill + roubo de vida) | 65 (0 + 65) | 151 (0 + 151) |
| MP gasto em ações | 606 | 717 |
| Skills / ataques básicos | 11 / 1 | 6 / 8 |
| Acertos / erros | 5 / 5 | 12 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 14 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- gabepeixe aplicou: bleed (rodada 4), bleed (rodada 10)
- gabepeixe tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 4), stun (rodada 9), bleed (rodada 9), bleed (rodada 9), stun (rodada 10), stun (rodada 13), bleed (rodada 13)
- gabepeixe ativou: Juramento da Muralha ×2
- Leis disparadas por gabepeixe: PÂNICO (rodada 14)
- LuquEt4 aplicou: fear (rodada 2), fear (rodada 2), fear (rodada 3), stun (rodada 5), fear (rodada 6), fear (rodada 8), fear (rodada 12), bleed (rodada 13), fear (rodada 14)
- LuquEt4 tentou sem sucesso: fear (rodada 1), stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), fear (rodada 4), bleed (rodada 5), fear (rodada 5), vulnerable (rodada 6), stun (rodada 7), bleed (rodada 7), fear (rodada 7), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), fear (rodada 9), stun (rodada 10), bleed (rodada 10), fear (rodada 10), stun (rodada 11), bleed (rodada 11), fear (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 13), fear (rodada 13), stun (rodada 14), bleed (rodada 14)

Rodada a rodada:

| Rodada | Ordem (critério) | gabepeixe (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −96 | Silêncio do Veterano — executada, dano 0, MP −120 | 3509 / 4754 | 471 / 528 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 268, MP −33 | Carga do Condenado — executada, dano 397, MP −119 | 3125 / 4486 | 449 / 421 |
| 3 | p2 → p1 (score) | Colheita de Ferro — executada, dano 0, MP −78 | Esmagar — executada, dano 420, MP −144 | 2705 / 4507 | 382 / 289 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 268, MP −33 | Golpe Devastador — executada, dano 391, MP −107 | 2327 / 4258 | 360 / 194 |
| 5 | p2 → p1 (score) | Mão Dupla — cancelada por controle | Ataque básico — executada, dano 168 | 2159 / 4076 | 371 / 206 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −33 | Silêncio do Veterano — executada, dano 0, MP −120 | 2159 / 3886 | 349 / 98 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −96 | Ataque básico — executada, dano 307 | 1852 / 3901 | 264 / 110 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −33 | Golpe Devastador — executada, dano 391, MP −107 | 1461 / 3920 | 242 / 15 |
| 9 | p2 → p1 (score) | Colheita de Ferro — executada, dano 400, MP −78 | Ataque básico — executada, dano 168 | 1313 / 3528 | 175 / 27 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 251, MP −33 | Ataque básico — executada, dano 168 | 1157 / 3285 | 153 / 39 |
| 11 | p2 → p1 (score) | Mão Dupla — executada, dano 0, MP −60 | Ataque básico — executada, dano 168 | 989 / 3103 | 104 / 51 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −33 | Ataque básico — executada, dano 307 | 682 / 2928 | 82 / 63 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 146 | Ataque básico — executada, dano 307 | 242 / 2797 | 93 / 75 |
| 14 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — executada, dano 307 | -65 / 2812 | 93 / 87 |

### Quartas: detalhes

#### Quartas 1 — Forever × aspaszin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G41 | Forever | Mago | 23 | 29.29 | Grilhões de Gelo, Raio Congelante, Lasca de Gelo, Tempestade | congelar e quebrar |
| p2 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |

- Seed da partida: `2429615464796324789`
- Rodadas: **10**
- Vencedor: **aspaszin** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 708/4477 (15.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Forever | aspaszin |
|---|---|---|
| Dano causado (golpes + DoT) | 3769 (3769 + 0) | 6347 (6347 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 777 | 414 |
| Skills / ataques básicos | 8 / 1 | 4 / 0 |
| Acertos / erros | 5 / 0 | 3 / 0 |
| Críticos (dano) | 0 (0) | 2 (5579) |
| Agiu primeiro (rodadas) | 8 | 2 |
| Ações perdidas por controle | 0 | 6 |

Efeitos relevantes:
- Forever aplicou: frozen (rodada 1), vulnerable (rodada 1), frozen (rodada 3), slowed (rodada 5), frozen (rodada 6), vulnerable (rodada 6), slowed (rodada 9)
- Forever tentou sem sucesso: slowed (rodada 2), stun (rodada 4), frozen (rodada 8)
- Égide de Forever: absorveu 1119 de dano por 559 MP
- aspaszin aplicou: fear (rodada 5), vulnerable (rodada 8), vulnerable (rodada 9)
- aspaszin tentou sem sucesso: vulnerable (rodada 5)
- Égide de aspaszin: absorveu 662 de dano por 330 MP

Rodada a rodada:

| Rodada | Ordem (critério) | Forever (p1) | aspaszin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −117 | Hora do Arauto — cancelada por controle | 4477 / 4477 | 1687 / 1694 |
| 2 | p1 → p2 (score) | Lasca de Gelo — executada, dano 912, MP −73 | Hora do Arauto — cancelada por controle | 4477 / 3565 | 1670 / 1667 |
| 3 | p1 → p2 (score) | Raio Congelante — executada, dano 0, MP −91 | Hora do Arauto — cancelada por controle | 4477 / 3565 | 1635 / 1694 |
| 4 | p1 → p2 (score) | Tempestade — executada, dano 1163, MP −142 | Hora do Arauto — cancelada por controle | 4477 / 2402 | 1549 / 1645 |
| 5 | p1 → p2 (score) | Lasca de Gelo — executada, dano 684, MP −73 | Hora do Arauto — executada, dano 0, MP −140 | 4477 / 1718 | 1532 / 1498 |
| 6 | p1 → p2 (score) | Grilhões de Gelo — executada, dano 0, MP −117 | Prisma de Devastação — cancelada por controle | 4477 / 1718 | 1471 / 1551 |
| 7 | p1 → p2 (score) | Ataque básico — executada, dano 326 | Prisma de Devastação — cancelada por controle | 4477 / 1392 | 1527 / 1576 |
| 8 | p1 → p2 (score) | Raio Congelante — executada, dano 0, MP −91 | Prisma de Devastação — executada, dano 2777, MP −131 | 1700 / 1392 | 1247 / 1498 |
| 9 | p2 → p1 (score) | Lasca de Gelo — executada, dano 684, MP −73 | Lente de Obsidiana — executada, dano 768, MP −78 | 932 / 708 | 1163 / 1413 |
| 10 | p2 → p1 (score) | Tempestade — cancelada por morte | Bola de Fogo — executada, dano 2802, MP −65 | -1870 / 708 | 916 / 1401 |

#### Quartas 2 — babi × MeikodRJ

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G39 | babi | Mago | 23 | 28.71 | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | carta lendária de dano |
| p2 | G19 | MeikodRJ | Guerreiro | 22 | 28.37 | Imortal, Golpe Poderoso, Golpe Devastador, Veterania | redução extrema com espada |

- Seed da partida: `6243117697485473690`
- Rodadas: **14**
- Vencedor: **babi** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1134/4477 (25.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | babi | MeikodRJ |
|---|---|---|
| Dano causado (golpes + DoT) | 6408 (6408 + 0) | 3343 (3343 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 163 (0 + 163) |
| MP gasto em ações | 1476 | 755 |
| Skills / ataques básicos | 13 / 0 | 7 / 6 |
| Acertos / erros | 8 / 1 | 9 / 1 |
| Críticos (dano) | 2 (3126) | 5 (2288) |
| Agiu primeiro (rodadas) | 14 | 0 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- babi ativou: Foco do Estudante ×4
- Égide de babi: absorveu 582 de dano por 289 MP
- MeikodRJ aplicou: stun (rodada 5)
- MeikodRJ tentou sem sucesso: stun (rodada 3), bleed (rodada 3), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 13), bleed (rodada 13)
- MeikodRJ ativou: Imortal ×2, Veterania ×1

Rodada a rodada:

| Rodada | Ordem (critério) | babi (p1) | MeikodRJ (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Imortal — executada, dano 0, MP −204 | 4477 / 4844 | 1618 / 444 |
| 2 | p1 → p2 (score) | Apocalipse — executada, dano 462, MP −242 | Veterania — executada, dano 0, MP −99 | 4477 / 4382 | 1429 / 357 |
| 3 | p1 → p2 (score) | Bola de Fogo — executada, dano 627, MP −65 | Golpe Poderoso — executada, dano 407, MP −47 | 4070 / 3775 | 1382 / 322 |
| 4 | p1 → p2 (score) | Relâmpago — executada, dano 0, MP −93 | Golpe Devastador — executada, dano 0, MP −107 | 4070 / 3775 | 1342 / 227 |
| 5 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Golpe Poderoso — executada, dano 651, MP −47 | 3419 / 3807 | 1262 / 192 |
| 6 | p1 → p2 (score) | Bola de Fogo — cancelada por controle | Ataque básico — executada, dano 216 | 3203 / 3817 | 1297 / 204 |
| 7 | p1 → p2 (score) | Bola de Fogo — executada, dano 627, MP −65 | Imortal — executada, dano 0, MP −204 | 3203 / 3190 | 1285 / 12 |
| 8 | p1 → p2 (score) | Apocalipse — executada, dano 229, MP −242 | Ataque básico — executada, dano 216 | 2987 / 2971 | 1078 / 24 |
| 9 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Ataque básico — executada, dano 345 | 2642 / 2988 | 1025 / 36 |
| 10 | p1 → p2 (score) | Bola de Fogo — executada, dano 627, MP −65 | Ataque básico — executada, dano 216 | 2426 / 2371 | 995 / 48 |
| 11 | p1 → p2 (score) | Relâmpago — executada, dano 690, MP −93 | Golpe Poderoso — executada, dano 602, MP −47 | 1824 / 1711 | 902 / 13 |
| 12 | p1 → p2 (score) | Bola de Fogo — executada, dano 482, MP −65 | Ataque básico — executada, dano 345 | 1479 / 1246 | 860 / 25 |
| 13 | p1 → p2 (score) | Foco do Estudante — executada, dano 0, MP −76 | Ataque básico — executada, dano 345 | 1134 / 1263 | 807 / 37 |
| 14 | p1 → p2 (score) | Apocalipse — executada, dano 2664, MP −242 | Ataque básico — cancelada por morte | 1134 / -1401 | 618 / 37 |

#### Quartas 3 — SkipNhO × frttt

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |
| p2 | G40 | frttt | Mago | 24 | 28.14 | Dividendo de Mana, Dreno de Mana, Bola de Fogo, Reserva Profunda | mana: queimar a do rival |

- Seed da partida: `16773338749684197360`
- Rodadas: **24**
- Vencedor: **SkipNhO** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2337/5004 (46.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | SkipNhO | frttt |
|---|---|---|
| Dano causado (golpes + DoT) | 5183 (4383 + 800) | 2876 (2876 + 0) |
| Cura (skill + roubo de vida) | 209 (0 + 209) | 0 (0 + 0) |
| MP gasto em ações | 750 | 1947 |
| Skills / ataques básicos | 8 / 16 | 19 / 3 |
| Acertos / erros | 18 / 3 | 9 / 3 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 24 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- SkipNhO aplicou: stun (rodada 3), bleed (rodada 10), bleed (rodada 15), stun (rodada 22)
- SkipNhO tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 18), bleed (rodada 18), stun (rodada 21), bleed (rodada 21), bleed (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24)
- SkipNhO ativou: Juramento da Muralha ×2, Guarda Cruzada ×1
- frttt aplicou: mana_burn (rodada 2), mana_burn (rodada 3), mana_burn (rodada 7), mana_burn (rodada 12), mana_burn (rodada 17), mana_burn (rodada 18), mana_burn (rodada 22)
- frttt tentou sem sucesso: mana_burn (rodada 24)
- frttt ativou: Reserva Profunda ×5
- Égide de frttt: absorveu 762 de dano por 373 MP

Rodada a rodada:

| Rodada | Ordem (critério) | SkipNhO (p1) | frttt (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Reserva Profunda — executada, dano 0, MP −72 | 5004 / 5014 | 512 / 2105 |
| 2 | p2 → p1 (score) | Guarda Cruzada — executada, dano 0, MP −99 | Dreno de Mana — executada, dano 0, MP −80 | 5004 / 5014 | 413 / 2097 |
| 3 | p2 → p1 (score) | Fortaleza Viva — executada, dano 687, MP −191 | Dividendo de Mana — executada, dano 330, MP −179 | 4708 / 4327 | 222 / 1938 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 358, MP −47 | Bola de Fogo — cancelada por controle | 4725 / 3969 | 175 / 2010 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Bola de Fogo — executada, dano 110, MP −73 | 4624 / 3778 | 187 / 2024 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 332, MP −47 | Reserva Profunda — executada, dano 0, MP −72 | 4640 / 3446 | 152 / 2026 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Dreno de Mana — executada, dano 0, MP −80 | 4640 / 3446 | 16 / 2049 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dividendo de Mana — executada, dano 0, MP −179 | 4649 / 3255 | 16 / 1957 |
| 9 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Bola de Fogo — executada, dano 110, MP −73 | 4548 / 3064 | 28 / 1971 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Ataque básico — executada, dano 59 | 4498 / 2873 | 40 / 2058 |
| 11 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Reserva Profunda — executada, dano 0, MP −72 | 4507 / 2482 | 52 / 2073 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Dreno de Mana — executada, dano 0, MP −80 | 4507 / 2282 | 5 / 2096 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dividendo de Mana — executada, dano 0, MP −179 | 4516 / 2091 | 5 / 1982 |
| 14 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Bola de Fogo — executada, dano 314, MP −73 | 4211 / 1900 | 17 / 1996 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Ataque básico — executada, dano 169 | 4051 / 1709 | 29 / 2083 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Reserva Profunda — executada, dano 0, MP −72 | 4060 / 1318 | 41 / 2089 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dreno de Mana — executada, dano 0, MP −80 | 4069 / 927 | 41 / 2081 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dividendo de Mana — executada, dano 942, MP −179 | 3136 / 736 | 41 / 1982 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Bola de Fogo — executada, dano 0, MP −73 | 3136 / 736 | 41 / 2012 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 169 | 2967 / 736 | 53 / 2115 |
| 21 | p2 → p1 (score) | Golpe Poderoso — executada, dano 332, MP −47 | Reserva Profunda — executada, dano 0, MP −72 | 2983 / 404 | 18 / 2076 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dreno de Mana — executada, dano 0, MP −80 | 2992 / 213 | 18 / 2081 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dividendo de Mana — cancelada por controle | 3001 / 22 | 18 / 2161 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Dividendo de Mana — executada, dano 673, MP −179 | 2337 / -169 | 30 / 1982 |

#### Quartas 4 — RNakano × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G56 | RNakano | Ladino | 20 | 25.60 | Silêncio de Seda, Nó Corredio, Ataque Furtivo, Golpe nas Sombras | sono e atordoamento |
| p2 | G20 | LuquEt4 | Guerreiro | 22 | 28.48 | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | medo e vulnerabilidade |

- Seed da partida: `12923774737184472967`
- Rodadas: **6**
- Vencedor: **LuquEt4** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3880/4754 (81.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | RNakano | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 969 (969 + 0) | 2833 (2725 + 108) |
| Cura (skill + roubo de vida) | 47 (0 + 47) | 95 (0 + 95) |
| MP gasto em ações | 316 | 490 |
| Skills / ataques básicos | 4 / 1 | 4 / 1 |
| Acertos / erros | 3 / 0 | 4 / 0 |
| Críticos (dano) | 1 (503) | 0 (0) |
| Agiu primeiro (rodadas) | 6 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- RNakano tentou sem sucesso: sleep (rodada 1), stun (rodada 2), stun (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), stun (rodada 5), poison (rodada 5)
- Leis disparadas por RNakano: PÂNICO (rodada 5)
- LuquEt4 aplicou: fear (rodada 1), fear (rodada 4), bleed (rodada 5), fear (rodada 5)
- LuquEt4 tentou sem sucesso: vulnerable (rodada 1), stun (rodada 2), bleed (rodada 2), fear (rodada 2), fear (rodada 2), stun (rodada 3), bleed (rodada 3), fear (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5)

Rodada a rodada:

| Rodada | Ordem (critério) | RNakano (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Silêncio de Seda — executada, dano 0, MP −108 | Silêncio do Veterano — executada, dano 0, MP −120 | 2704 / 4754 | 667 / 528 |
| 2 | p1 → p2 (score) | Nó Corredio — executada, dano 0, MP −87 | Carga do Condenado — executada, dano 785, MP −119 | 1919 / 4754 | 595 / 421 |
| 3 | p1 → p2 (score) | Ataque Furtivo — executada, dano 503, MP −55 | Esmagar — executada, dano 832, MP −144 | 1112 / 4292 | 555 / 289 |
| 4 | p1 → p2 (score) | Golpe nas Sombras — executada, dano 317, MP −66 | Golpe Devastador — executada, dano 774, MP −107 | 353 / 4013 | 504 / 194 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 149 | Ataque básico — executada, dano 334 | 26 / 3880 | 519 / 206 |
| 6 | p1 → p2 (score) | Ataque Furtivo — cancelada por morte | Ataque básico — não alcançada (o duelo acabou antes) | -82 / 3880 | 534 / 206 |

### Semifinal: detalhes

#### Semifinal 1 — aspaszin × babi

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |
| p2 | G39 | babi | Mago | 23 | 28.71 | Apocalipse, Bola de Fogo, Foco do Estudante, Relâmpago | carta lendária de dano |

- Seed da partida: `4403250353137019007`
- Rodadas: **6**
- Vencedor: **aspaszin** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2018/4477 (45.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | aspaszin | babi |
|---|---|---|
| Dano causado (golpes + DoT) | 4553 (4553 + 0) | 2459 (2459 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 479 | 617 |
| Skills / ataques básicos | 5 / 1 | 6 / 0 |
| Acertos / erros | 4 / 1 | 3 / 1 |
| Críticos (dano) | 3 (4029) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 6 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- aspaszin tentou sem sucesso: fear (rodada 1), vulnerable (rodada 3)
- Égide de aspaszin: absorveu 433 de dano por 216 MP
- babi ativou: Foco do Estudante ×2
- Égide de babi: absorveu 801 de dano por 399 MP

Rodada a rodada:

| Rodada | Ordem (critério) | aspaszin (p1) | babi (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Hora do Arauto — executada, dano 0, MP −140 | Foco do Estudante — executada, dano 0, MP −76 | 4477 / 4477 | 1554 / 1618 |
| 2 | p2 → p1 (score) | Prisma de Devastação — executada, dano 0, MP −131 | Apocalipse — executada, dano 0, MP −242 | 4477 / 4477 | 1476 / 1429 |
| 3 | p2 → p1 (score) | Lente de Obsidiana — executada, dano 2016, MP −78 | Bola de Fogo — executada, dano 864, MP −65 | 3613 / 2461 | 1375 / 1240 |
| 4 | p2 → p1 (score) | Bola de Fogo — executada, dano 1310, MP −65 | Relâmpago — executada, dano 731, MP −93 | 2882 / 1151 | 1299 / 1085 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 703 | Foco do Estudante — executada, dano 0, MP −76 | 2882 / 448 | 1352 / 1001 |
| 6 | p2 → p1 (score) | Bola de Fogo — executada, dano 524, MP −65 | Bola de Fogo — executada, dano 864, MP −65 | 2018 / -76 | 1264 / 943 |

#### Semifinal 2 — SkipNhO × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |
| p2 | G20 | LuquEt4 | Guerreiro | 22 | 28.48 | Carga do Condenado, Silêncio do Veterano, Esmagar, Golpe Devastador | medo e vulnerabilidade |

- Seed da partida: `17702946004754375332`
- Rodadas: **34**
- Vencedor: **SkipNhO** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 499/5004 (10.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | SkipNhO | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 5021 (4831 + 190) | 4744 (3944 + 800) |
| Cura (skill + roubo de vida) | 239 (0 + 239) | 183 (0 + 183) |
| MP gasto em ações | 1032 | 931 |
| Skills / ataques básicos | 14 / 18 | 8 / 25 |
| Acertos / erros | 20 / 9 | 30 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 31 | 3 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- SkipNhO aplicou: bleed (rodada 33)
- SkipNhO tentou sem sucesso: stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24), stun (rodada 25), bleed (rodada 25), stun (rodada 29), bleed (rodada 29), stun (rodada 30), bleed (rodada 30), stun (rodada 31), bleed (rodada 31), stun (rodada 32), bleed (rodada 32), stun (rodada 33), stun (rodada 34), bleed (rodada 34)
- SkipNhO ativou: Juramento da Muralha ×2, Guarda Cruzada ×1
- LuquEt4 aplicou: fear (rodada 2), fear (rodada 3), fear (rodada 7), vulnerable (rodada 7), fear (rodada 8), fear (rodada 10), fear (rodada 13), fear (rodada 16), fear (rodada 17), fear (rodada 19), fear (rodada 20), stun (rodada 21), fear (rodada 23), fear (rodada 24), stun (rodada 26), fear (rodada 26), bleed (rodada 28), fear (rodada 30), bleed (rodada 32)
- LuquEt4 tentou sem sucesso: fear (rodada 1), stun (rodada 2), bleed (rodada 2), fear (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 5), bleed (rodada 5), fear (rodada 5), stun (rodada 6), bleed (rodada 6), fear (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), fear (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), fear (rodada 11), stun (rodada 12), bleed (rodada 12), fear (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), fear (rodada 14), stun (rodada 15), bleed (rodada 15), fear (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 18), bleed (rodada 18), fear (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), bleed (rodada 21), fear (rodada 21), stun (rodada 22), bleed (rodada 22), fear (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24), stun (rodada 25), bleed (rodada 25), fear (rodada 25), bleed (rodada 26), stun (rodada 27), bleed (rodada 27), fear (rodada 27), stun (rodada 28), fear (rodada 28), stun (rodada 29), bleed (rodada 29), fear (rodada 29), stun (rodada 30), bleed (rodada 30), stun (rodada 31), bleed (rodada 31), fear (rodada 31), stun (rodada 32), fear (rodada 32), stun (rodada 33), bleed (rodada 33), fear (rodada 33)

Rodada a rodada:

| Rodada | Ordem (critério) | SkipNhO (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Silêncio do Veterano — executada, dano 0, MP −120 | 5004 / 4754 | 512 / 528 |
| 2 | p1 → p2 (score) | Guarda Cruzada — executada, dano 0, MP −99 | Carga do Condenado — executada, dano 100, MP −119 | 4904 / 4754 | 425 / 421 |
| 3 | p1 → p2 (score) | Fortaleza Viva — executada, dano 0, MP −191 | Esmagar — executada, dano 106, MP −144 | 4798 / 4754 | 246 / 289 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 345, MP −47 | Golpe Devastador — executada, dano 0, MP −107 | 4815 / 4409 | 211 / 194 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 121 | 4694 / 4415 | 223 / 206 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 345, MP −47 | Ataque básico — executada, dano 121 | 4590 / 4076 | 188 / 218 |
| 7 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −136 | Silêncio do Veterano — executada, dano 0, MP −120 | 4590 / 4076 | 64 / 110 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 345, MP −47 | Golpe Devastador — executada, dano 119, MP −107 | 4488 / 3736 | 29 / 15 |
| 9 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 51 | 4437 / 3738 | 41 / 27 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 51 | 4395 / 3557 | 53 / 39 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 121 | 4274 / 3563 | 18 / 51 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 121 | 4153 / 3569 | 30 / 63 |
| 13 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 4041 / 3392 | 42 / 75 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 3929 / 3215 | 54 / 87 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 320, MP −47 | Ataque básico — executada, dano 121 | 3824 / 2901 | 19 / 99 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 3712 / 2724 | 31 / 111 |
| 17 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Golpe Devastador — executada, dano 282, MP −107 | 3439 / 2555 | 43 / 16 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 121 | 3318 / 2561 | 55 / 28 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 320, MP −47 | Ataque básico — executada, dano 121 | 3213 / 2247 | 20 / 40 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 3101 / 2070 | 32 / 52 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 121 | 2980 / 2076 | 44 / 64 |
| 22 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 121 | 2859 / 2082 | 56 / 76 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 320, MP −47 | Ataque básico — executada, dano 121 | 2754 / 1768 | 21 / 88 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 2642 / 1591 | 33 / 100 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 2530 / 1414 | 45 / 112 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Devastador — executada, dano 452, MP −107 | 2078 / 1436 | 57 / 17 |
| 27 | p1 → p2 (score) | Golpe Poderoso — cancelada por controle | Ataque básico — executada, dano 121 | 1957 / 1442 | 69 / 29 |
| 28 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 121 | 1836 / 1448 | 34 / 41 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 1524 / 1271 | 46 / 53 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 1212 / 1094 | 58 / 65 |
| 31 | p1 → p2 (score) | Golpe Poderoso — executada, dano 320, MP −47 | Ataque básico — executada, dano 121 | 1107 / 780 | 23 / 77 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 995 / 603 | 35 / 89 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 121 | 683 / 236 | 47 / 101 |
| 34 | p1 → p2 (score) | Golpe Poderoso — executada, dano 320, MP −47 | Ataque básico — cancelada por morte | 499 / -84 | 12 / 101 |

### Final: detalhes

#### Final — aspaszin × SkipNhO

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | G43 | aspaszin | Mago | 23 | 29.52 | Prisma de Devastação, Hora do Arauto, Lente de Obsidiana, Bola de Fogo | vulnerabilidade e dano |
| p2 | G18 | SkipNhO | Guerreiro | 22 | 28.71 | Fortaleza Viva, Golpe Poderoso, Juramento da Muralha, Guarda Cruzada | carta lendária e guarda dupla |

- Seed da partida: `3846561752997802364`
- Rodadas: **15**
- Vencedor: **aspaszin** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1369/4477 (30.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | aspaszin | SkipNhO |
|---|---|---|
| Dano causado (golpes + DoT) | 5913 (5913 + 0) | 3108 (3108 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 152 (0 + 152) |
| MP gasto em ações | 1307 | 750 |
| Skills / ataques básicos | 13 / 2 | 8 / 6 |
| Acertos / erros | 11 / 1 | 10 / 1 |
| Críticos (dano) | 7 (4431) | 0 (0) |
| Agiu primeiro (rodadas) | 15 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- aspaszin aplicou: fear (rodada 1), vulnerable (rodada 1), vulnerable (rodada 2), vulnerable (rodada 3), fear (rodada 7), vulnerable (rodada 8), fear (rodada 13), vulnerable (rodada 13), vulnerable (rodada 14)
- aspaszin tentou sem sucesso: vulnerable (rodada 7), vulnerable (rodada 9), vulnerable (rodada 15)
- Égide de aspaszin: absorveu 543 de dano por 271 MP
- SkipNhO tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14)
- SkipNhO ativou: Juramento da Muralha ×2, Guarda Cruzada ×1

Rodada a rodada:

| Rodada | Ordem (critério) | aspaszin (p1) | SkipNhO (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Hora do Arauto — executada, dano 0, MP −140 | Juramento da Muralha — executada, dano 0, MP −136 | 4477 / 5004 | 1554 / 512 |
| 2 | p1 → p2 (score) | Prisma de Devastação — executada, dano 265, MP −131 | Guarda Cruzada — executada, dano 0, MP −99 | 4477 / 4739 | 1476 / 425 |
| 3 | p1 → p2 (score) | Lente de Obsidiana — executada, dano 240, MP −78 | Fortaleza Viva — executada, dano 582, MP −191 | 3895 / 4528 | 1400 / 246 |
| 4 | p1 → p2 (score) | Bola de Fogo — executada, dano 567, MP −65 | Golpe Poderoso — executada, dano 392, MP −47 | 3503 / 3980 | 1354 / 211 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 167 | Ataque básico — executada, dano 209 | 3294 / 3823 | 1389 / 223 |
| 6 | p1 → p2 (score) | Bola de Fogo — executada, dano 743, MP −65 | Golpe Poderoso — executada, dano 363, MP −47 | 2931 / 3098 | 1345 / 188 |
| 7 | p1 → p2 (score) | Hora do Arauto — executada, dano 0, MP −140 | Juramento da Muralha — executada, dano 0, MP −136 | 2931 / 3098 | 1258 / 64 |
| 8 | p1 → p2 (score) | Prisma de Devastação — executada, dano 221, MP −131 | Golpe Poderoso — executada, dano 363, MP −47 | 2568 / 2895 | 1148 / 29 |
| 9 | p1 → p2 (score) | Lente de Obsidiana — executada, dano 385, MP −78 | Ataque básico — executada, dano 209 | 2359 / 2520 | 1105 / 41 |
| 10 | p1 → p2 (score) | Bola de Fogo — executada, dano 453, MP −65 | Ataque básico — executada, dano 209 | 2150 / 2077 | 1075 / 53 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 363, MP −47 | 1787 / 2095 | 1096 / 18 |
| 12 | p1 → p2 (score) | Bola de Fogo — executada, dano 743, MP −65 | Ataque básico — executada, dano 0 | 1787 / 1352 | 1084 / 30 |
| 13 | p1 → p2 (score) | Hora do Arauto — executada, dano 0, MP −140 | Ataque básico — executada, dano 209 | 1578 / 1362 | 979 / 42 |
| 14 | p1 → p2 (score) | Prisma de Devastação — executada, dano 756, MP −131 | Ataque básico — executada, dano 209 | 1369 / 616 | 883 / 54 |
| 15 | p1 → p2 (score) | Lente de Obsidiana — executada, dano 1373, MP −78 | Golpe Poderoso — cancelada por morte | 1369 / -757 | 858 / 54 |

