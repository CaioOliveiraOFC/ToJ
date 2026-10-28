# Auditoria de cobertura PvE das runs que geram gladiadores

| | |
|---|---|
| **Commit auditado** | `cab4dfc` (`phase/pvp-arena`) |
| **Escopo** | o caminho real do gerador: `tools/arena_copa_03_geracao.executar` → `BotExperimental` → `BotPadrao` → engine, combate, progressão, economia, serviços e extração |
| **Pergunta** | as avaliações anteriores validaram TODO o PvE, ou o balanceamento foi concluído com sistemas parcialmente ignorados? |
| **Alterações no jogo** | nenhuma. Nada em `src/` ou `tools/` mudou; sem correção antes do diagnóstico |

---

## 1. Veredito

**Não validaram tudo.** O núcleo que o bot compartilha com o jogador está exercitado
de verdade:
- combate 1x1, os 9 arquétipos, os 4 momentos da IA, chefes, loot, nível, Loja,
  Ferreiro, saída, juros, fuga e extração;
- é o mesmo `resolve_encounter` e os mesmos serviços da tela, e as 150 runs
  reexecutadas reproduziram o log real campo a campo.

Mas o balanceamento foi concluído com **um bug mecânico invisível**, **uma família
inteira de leis de efeito sem fonte de conteúdo** e **uma camada de decisões do bot
que ignora sistemas de forma sistemática**:

| # | Achado | Categoria | Tamanho |
|---|---|---|---|
| 1 | A **Benção do Altar não faz nada**. O buff é gravado sem `stat` e não está em `LEGACY_BUFF_STATS`: nenhum funil o lê. Paga-se 30% do HP máximo por zero | **bug mecânico** (afeta o jogador humano também) | aceito em 21% das runs completas e 51% das extraídas; 34.545 HP pagos por nada em 75 builds |
| 2 | **7 das 8 leis "reconhecidas" (os pares opostos) não podem disparar no PvE**: nenhum conteúdo aplica `empowered`, `arcane_surge`, `quickened`, `fortified`, `vitality`, `focused` nem o efeito `precision` | **mecânica / lacuna de conteúdo** (não é o bot) | 0 disparos nas 150 runs da amostra; o único caminho até o núcleo é `try_apply_status` |
| 3 | **O bot equipa na posição errada**: `equip_if_better` compara com o PIOR ocupante, mas chama `equip(item)` sem posição, e o jogo troca a PRIMEIRA (Weapon1/Ring1) | **política do bot** | 93% das builds extraídas; 85,5% dos 186 gladiadores com peça melhor na mochila; 139/186 com arma melhor guardada (+8 pp de dano, mediana) |
| 4 | **Skills que não causam dano são ignoradas**: buff, status, cura e redução de dano estão no deck e quase nunca são escolhidas | **política do bot** | extraídas: 78 escolhas de não-dano em 51.150 turnos disponíveis, contra 18.437 de dano |
| 5 | **Poção de mana e elixires nunca são usados**: o avaliador de combate não lê `mana_restored`, e os elixires nunca vencem o ataque. O elixir `mana_regen` nem entra no cardápio | **política do bot** | 0 usos em 12.261 turnos com poção de mana e 21.376 com elixir (extraídas) |
| 6 | Caminhos que **o bot não tem**: reroll de oferta de passiva/skill, retirar gema, reencantar, recuperação de MP, comprar poção de mana ou elixir | **política do bot** (não exercitado) | 0% em tudo |
| 7 | **Mercador divergente**: o jogo oferece 1–3 itens ponderados por raridade com 10% de desconto; o bot abre a Loja inteira (venda, reparo, poções, 20+ ofertas) | **política do bot** (diverge da jornada real) | 100% das visitas ao Mercador |
| 8 | **Ferreiro subutilizado**: 1 +N e 1 encanto por visita, com teto de 30% do ouro; o +N vai para a peça de melhor peso/custo (anel, amuleto, luvas) | **política do bot** | 72% das armas dos 186 gladiadores em +0; maior +N da população inteira: +3; ouro parado no fim: mediana 5.538 (22% do ganho) nos 186 |
| 9 | **A extração é um filtro de OP, não uma decisão de risco**: só preserva quando a build bate o benchmark da Arena | comportamento intencional **do gerador** | 548 de 550 extrações dos logs em CLOSE_ENOUGH/META_BATIDA/HARD_STOP; 371 runs morreram com a extração disponível, todas abaixo da meta |

O que isso significa para cada régua está na [seção 8](#8-o-que-isso-diz-das-avaliações-anteriores).

---

## 2. Universo e método

**Sonda passiva** — só leitura dos logs reais de geração, sem executar nada:
- `reports/pvp/copa_03/_trabalho/tentativas.jsonl` e `preenchimento.jsonl`
  (Warrior, 1.425 runs);
- `reports/pvp/arena_offline/_trabalho/{mage,rogue}/tentativas.jsonl` (151 e 265);
- **1.841 runs**, 550 extrações.

**Amostra reproduzível** — 150 runs reexecutadas a partir das seeds desses logs,
com sondas instaladas:
- **runs completas: 100**, sorteio uniforme (`random.Random(20261028)`) de todas
  as tentativas, 40 Warrior, 30 Mage, 30 Rogue. Mortes e extrações juntas, como
  aconteceram;
- **builds extraídas: 75**, as 25 extrações que caíram no sorteio acima mais 50
  sorteadas só entre as extrações (20 por classe ao todo);
- os dois universos ficam **sempre separados**: o das completas mede o que a
  jornada exercita; o das extraídas mede o que chega à Arena, e sozinho teria viés
  de sobrevivência.

**População inteira das builds** — os 186 gladiadores publicados em
`src/data/arena_populacao/`, lidos do snapshot, sem amostra.

**Verificações A/B** dirigidas (`ferramentas/verificacoes.py`):
- Altar: a mesma luta com e sem a bênção, 3 classes × 20 seeds;
- a troca de equipamento;
- o cardápio de consumíveis;
- a oferta do Mercador.

**Como as sondas não interferem.**
- Cada sonda é um wrapper no processo da auditoria: chama a função original, não
  sorteia e não altera argumento nem retorno.
- A prova é o determinismo: **150/150 runs reproduziram o log real** em desfecho,
  andar, nível, combates, ações, serviços, ouro e OP.
- Duas fontes de ruído foram isoladas e ficam fora da contagem:
  - os duelos de benchmark que medem OP (o do fim da run e o que o bot roda
    DENTRO da decisão de extração);
  - qualquer coisa depois do fim da run.

**Ausência de telemetria não é ausência de execução.** Onde não foi possível
medir, a matriz diz **NÃO MENSURADO**. Onde a política impede o uso, diz **NÃO
EXERCITADO** e a causa.

---

## 3. Matriz geral

`opp` = runs com oportunidade · `uso` = runs em que o bot usou · `ef` = runs com
efeito mensurável. Percentuais: uso sobre todas as runs · uso sobre as elegíveis.

| Sistema | Impl. | Acesso do bot | Completas (n=100) opp / uso / ef | % uso | Extraídas (n=75) opp / uso / ef | % uso | Ignorado? |
|---|---|---|---|---|---|---|---|
| **Itens** | | | | | | | |
| Loot de equipamento | sim | sim | 76 / 70 / 70 | 70% · 92% | 75 / 75 / 75 | 100% · 100% | não |
| Raridade Epic/Legendary | sim | sim | 41 / 29 / 23 | 29% · 71% | 71 / 65 / 55 | 87% · 92% | não |
| Starter Kit | sim | sim (mesmo caminho) | 100 / 100 / 79¹ | 100% | 75 / 75 / 25¹ | 100% | não |
| Equipar na posição certa | sim | **com defeito** | 27 runs com troca errada | — | **70** com troca errada, 64 com perda líquida | — | **defeito** |
| **Progressão** | | | | | | | |
| Evolução (level-up) | sim | sim | 100 / 84 / 84 | 84% | 75 / 75 / 75 | 100% | não |
| Passivas (1 de 3) | sim | sim | 84 / 84 / NÃO MENSURADO | 84% · 100% | 75 / 75 / NÃO MENSURADO | 100% | não |
| Skills: oferta e aprendizado | sim | sim | 63 / 63 / 48² | 63% · 100% | 75 / 75 / 74² | 100% | não |
| Skills de dano em combate | sim | sim | 100 / 100 / 100 | 100% | 75 / 75 / 75 | 100% | não |
| Skills de buff/status/cura/redução | sim | sim | disponíveis em 50 runs; 31 escolhas | — | disponíveis em 75 runs; 78 escolhas em 51.150 turnos | — | **sim** |
| Reroll de oferta (passiva/skill) | sim | **não** | 84 / 0 | 0% | 75 / 0 | 0% | **NÃO EXERCITADO** |
| **Loja e economia** | | | | | | | |
| Loja (casa) | sim | sim | 83 / 77 / 59 | 77% · 93% | 75 / 75 / 75 | 100% | não |
| Comprar equipamento | sim | sim | 33 runs, 232 itens | — | 75 runs, 600 itens | — | não |
| Comprar poção de cura | sim | sim (até 3) | sim | — | sim | — | não |
| Comprar poção de mana / elixir | sim | **não** | 77 / 0 | 0% | 75 / 0 | 0% | **NÃO EXERCITADO** |
| Reroll da Loja | sim | ≤2, só com vitrine sem nada útil | 77 / 0 | 0% | 75 / 1 | 1,3% | **na prática** |
| Venda | sim | sim (dominados) | 77 / 50 / 50 | 50% · 65% | 75 / 75 / 75 | 100% | não |
| Recuperação paga de HP | sim | sim | 77 / 74 / 74 | 74% · 96% | 75 / 74 / 74 | 99% | não |
| Recuperação paga de MP | sim | **não** | 77 / 0 | 0% | 75 / 0 | 0% | **NÃO EXERCITADO** |
| Taxa de saída | sim | automática | 838 andares, 703 pagos | 84% | 1.545 andares, 1.460 pagos | 94% | — |
| Juros | sim | automáticos | 79 runs | 79% | 75 runs | 100% | — |
| Essência e penalidade | sim | automática | 35 de 838 andares com penalidade | — | 10 de 1.545 | — | — |
| **Ferreiro** | | | | | | | |
| Ferreiro (casa) | sim | sim | 88 / 63 / 48 | 63% · 72% | 75 / 75 / 75 | 100% | não |
| +N | sim | 1 por visita, ≤30% do ouro | 60 / 47 / 45 | 47% · 78% | 75 / 74 / 72 | 99% | parcial |
| +N na arma | sim | idem | 60 / 27 / 18 | 27% · 45% | 75 / 58 / 36 | 77% | **parcial** |
| Gemas (engastar) | sim | sim | 30 / 29 / 29 | 29% · 97% | 75 / 75 / 75 | 100% | parcial³ |
| Retirar gema | sim | **não** | 63 / 0 | 0% | 75 / 0 | 0% | **NÃO EXERCITADO** |
| Encantar | sim | 1 por visita | 63 / 24 / 21 | 24% · 38% | 75 / 63 / 57 | 84% | parcial |
| Reencantar | sim | **não** | 63 / 0 | 0% | 75 / 0 | 0% | **NÃO EXERCITADO** |
| **Eventos** | | | | | | | |
| Fonte | sim | sim | 35 / 19 / 17 | 19% · 54% | 65 / 39 / 35 | 52% · 60% | não |
| Altar | **sim, sem efeito** | sim | 34 / 21 / **0** | 21% · 62% | 58 / 38 / **0** | 51% · 66% | **bug** |
| Mercador | sim | **divergente** | 43 / 17 / 14 | 17% · 40% | 68 / 42 / 40 | 56% · 62% | **diverge** |
| **Consumíveis em combate** | | | | | | | |
| Poção de cura (mapa + combate) | sim | sim | 61 / 58 / 58 | 58% · 95% | 75 / 73 / 73 | 97% | não |
| Poção de mana | sim | sim, mas o avaliador não a pontua | 23 / 0 / 0 | 0% | 41 / 0 / 0 | 0% | **sim** |
| Elixires (7 no cardápio) | sim | sim | 20 / 0 / 0 | 0% | 56 / 0 / 0 | 0% | **sim** |
| Elixir `mana_regen` | sim | **não** (fora do cardápio) | 5 / 0 | 0% | 14 / 0 | 0% | **NÃO EXERCITADO** |
| **Monstros** | | | | | | | |
| trash · bruiser · skirmisher | sim | motor | 95 · 93 · 86 runs | — | 75 · 75 · 75 | — | não |
| tank · glass cannon | sim | motor | 61 · 51 | — | 75 · 75 | — | não |
| controller · support · elite | sim | motor | 34 · 33 · 27 | — | 73 · 62 · 67 | — | não |
| boss | sim | motor | 39 enfrentaram (56 com chefe no mapa) | 39% · 70% | 75 / 75 / 75 | 100% | D4 |
| IA: execução | sim | motor | 87 / 82 | 94% | 60 / 55 | 92% | não |
| IA: sobrevivência | sim | motor | 98 / 29⁴ | 30% | 75 / 55⁴ | 73% | design |
| IA: desespero | sim | motor | 93 / 93 | 100% | 75 / 75 | 100% | não |
| IA: abertura | sim | motor | 61 / 61 | 100% | 75 / 75 | 100% | não |
| **Status e leis** | | | | | | | |
| Status aplicados pelos monstros | sim | motor | 100 / 100 / 67 | 100% | 75 / 75 / 75 | 100% | não |
| Status pela carta de status do herói | sim | sim | 5 runs | 5% | 12 runs | 16% | **sim** |
| Status por secundário e proc do herói | sim | sim | 46 runs | 46% | 74 runs | 99% | não |
| 8 leis novas (qualquer) | sim | motor + bot | 32 runs, 73 disparos | 32% | 59 runs, 263 disparos | 79% | parcial⁵ |
| 7 leis de par oposto | **sem fonte** | — | 0 | 0% | 0 | 0% | **inalcançável** |
| Sono e Dor | sim | motor | 9 runs | 9% | 31 runs | 41% | não |
| **Combate, saída, OP** | | | | | | | |
| Fuga | sim | sim | 79 decidiram; 76 com sucesso | 79% | 69 / 69 | 92% | não |
| Extração | sim | sim (matriz de OP) | 45 / 25 / 25 | 25% · 56% | 75 / 75 / 75 | 100% | — |
| Medição de OP na run | sim | sim | 45 runs, 1.347 medições | — | 75 runs, 3.239 | — | — |

1. Efeito do Starter Kit = ainda equipado no fim. Nas completas é alto porque a
   maioria morre cedo.
2. Efeito = a carta aprendida foi lançada em combate.
3. Gemas: 31 das 75 extraídas terminam com **gema na bolsa E socket vazio
   equipado** (69/186 na população inteira). Em 46 visitas havia gema e nenhum
   socket vazio, e o bot nunca retira para trocar.
4. Sobrevivência: a oportunidade é "HP abaixo do limiar"; só usa quem tem carta de
   cura no deck (suporte, alguns papéis). É design.
5. Toxicidade: 0 disparos nas 150 runs. Quebra Gélida e Hemorragia Fria: 1 cada,
   só por monstros. Sono e Dor fica de fora destas 8 e está na linha própria.
   Detalhe na seção 4.6.

A matriz por sistema, com os eventos (`opp → uso`), está em `matriz.json`. As
contagens brutas por run estão em `resultados.jsonl`.

---

## 4. Evidências por sistema

### 4.1 Altar: o buff que ninguém lê

- `content/factories/dungeons.apply_altar_blessing` grava
  `active_buffs["Benção do Altar"] = {"value": 15, "duration": 5}`, sem `stat`.
- `shared/effects.buff_stat` cai em `LEGACY_BUFF_STATS`, que não tem essa chave, e
  devolve `""`.
- `sum_buffs` nunca soma esse buff a atributo nenhum, e `combat_modifier` também
  não.
- **A/B:** 60 de 60 lutas idênticas com e sem a bênção (3 classes × 20 seeds,
  mesma seed de RNG), e todos os atributos e modificadores iguais.
- O buff estava ativo ao entrar em combate em 30 lutas das extraídas, sem mudar
  nada.
- Nenhum teste cobre o Altar.
- **Afeta o jogo, não só o bot.** `ui/random_event_flow.run_altar_event` chama a
  mesma função.

### 4.2 Equipar: compara com o pior, troca o primeiro

- `sim/progression.equip_if_better` decide contra `_pior_ocupante(...)`.
- Mas executa `hero.equip(item)` sem posição, e `entities/heroes.Player.equip`
  documenta: "com todas ocupadas, substitui a primeira".
- **A/B dirigido:** com Anel da Fênix (peso 13,5) em Ring1 e Anel de Palha (1,0)
  em Ring2, `equip_if_better(Anel de Aço 5,0)` tirou a **Fênix**.
- **Amostra:**
  - completas: 525 trocas erradas, em 27 runs (406 armas, 119 anéis);
  - extraídas: 1.451 trocas erradas (1.059 armas, 392 anéis), em 70 de 75 runs;
    64 runs tiveram troca com perda líquida.
- **População (186):**
  - 159 (85,5%) guardam na mochila uma peça melhor que o pior ocupante da mesma
    categoria;
  - 139 têm uma arma de uma mão melhor que a pior equipada; ganho mediano +8 pp de
    `damage_bonus`, máximo +28 pp.
- A peça melhor que saiu não é vendida, porque `_descartavel` compara com o pior
  ocupante, e volta em ciclos: arma entra, a melhor sai, a melhor volta.
- **Compraram corretamente?** Sim: toda compra passa por `Shop.buy_item`, com
  preço e regra do jogo. Machado e clava em Mago são legais (`classes` vazio).
- **Usaram corretamente o upgrade das armas?** Não. Os motivos estão aqui e em
  [4.4](#44-ferreiro).

### 4.3 Combate do herói: o avaliador só enxerga dano e cura

`src/sim/bot/evaluators.avaliar_combate` pontua uma ação por duas coisas:
- **velocidade:** quantos turnos ela tira da luta;
- **sobrevivência:** fôlego útil.

O ataque básico é a linha de base, e ganha os empates por `tiebreak`.

- **Poção de mana:**
  - `bot_adapter.acoes_do_combate` preenche `mana_restored`, mas o avaliador
    nunca lê o campo;
  - utilidade zero, então o ataque vence sempre;
  - 0 usos em 4.869 turnos disponíveis (completas) e 12.261 (extraídas).
- **Elixires:**
  - passam pela sonda de buff (`outgoing/incoming_damage_after`), mas nunca
    venceram;
  - 0 usos em 5.827 e 21.376 turnos;
  - o elixir `mana_regen` não está em `CURA + MANA + ELIXIR`: nem é oferecido.
- **Skills que não causam dano:**
  - turnos disponíveis × escolhas, nas extraídas:

    | tipo | turnos disponíveis | escolhas |
    |---|---:|---:|
    | buff | 19.225 | 25 |
    | status | 15.740 | 38 |
    | cura | 8.886 | 9 |
    | redução de dano | 7.299 | 6 |
    | dano | 32.372 | 18.437 |

  - das 117 cartas de herói que chegaram a um deck na amostra, 55 foram
    lançadas: todas as 40 de dano, e 15 das 77 demais;
  - as 3 lendárias não apareceram.
- O avaliador recebe `interactions` (as leis que a ação destrava) e não pontua o
  campo explicitamente. O ganho de golpe já vem em `expected_strike_damage`.
  Nas extraídas, a ação que destravava lei foi escolhida em 23 de 450 turnos.

Se essas cartas e consumíveis são fracos de verdade, ou se é o avaliador que não
os enxerga, **não foi medido**: isso pede um A/B por carta, e esta etapa não
altera política.

### 4.4 Ferreiro

- O que a política faz (`progression.visit_forge`):
  - orçamento de 30% do ouro, depois da Loja;
  - engasta todas as gemas que couberem;
  - **1** +N, na peça de maior `peso/custo`;
  - **1** encanto, na peça com menos camadas, empatando pela ordem das posições.
- +N por posição (extraídas):

  | posição | +N | encantos | gemas engastadas |
  |---|---:|---:|---:|
  | arma | 99 | 31 | 132 |
  | amuleto | 87 | 45 | 102 |
  | anel | 74 | — | 26 |
  | luvas | 63 | — | 28 |
  | capacete | 20 | 73 | 65 |
  | corpo | 10 | 1 | 58 |
  | outras | 19 | — | 32 |

- No fim das extraídas, 114 de 150 armas equipadas estão em +0.
- Na população: 266 de 368 armas em +0 (72%). O maior +N dos 186 gladiadores é
  **+3**, e o jogo não tem teto.
- O dinheiro existia: nas extraídas, a mediana de ouro no fim é **5.424** (21% de
  tudo o que ganharam). O limite é a política (1 por visita, 30%), não a
  economia.
- Retirar gema e reencantar: 0 em 599 visitas.

### 4.5 Loja, Mercador, recuperação

- **Loja:** a ordem é vender dominados → reparar HP → repor cura (até 3) →
  equipamento com até 60% do ouro.
  - Nunca compra poção de mana nem elixir, embora todos os 14 consumíveis do
    catálogo sejam vendidos na Loja (`sold_in_shop`).
  - Reroll só quando a vitrine não tem NADA útil (`_tem_o_que_comprar`). Isso
    aconteceu 1 vez nas 150 runs da amostra; na população, 8/186 builds
    rerrolaram alguma vez.
- **Mercador:**
  - o jogo real (`ui/random_event_flow.run_merchant_event` →
    `get_merchant_offers`) mostra 1–3 itens com peso de raridade
    (Common 1, Rare 3, Epic 6) e 10% de desconto;
  - o bot (`BotPadrao._resolver_evento`) chama `_comprar_com_orcamento`, ou seja,
    uma Loja nova e completa (A/B no andar 12: 2 ofertas no jogo, 23 no bot), com
    venda e reparo;
  - **é uma segunda Loja que o jogador não tem.**
- **Recuperação:** `economy.recovery_offers` oferece passos de HP **e MP**;
  `progression._repair` só compra HP.

### 4.6 Status e as 16 leis

**Leis** (100 completas · 75 extraídas; 25 runs estão nos dois universos):

| Lei | Tipo | Disparos (completas · extraídas) | Quem disparou (extraídas) |
|---|---|---|---|
| 7 pares opostos | core | 0 · 0 | **inalcançável**: nenhum conteúdo aplica o lado positivo |
| Sono e Dor | core | 9 · 41 | dano no herói adormecido |
| Quebra Gélida | strike | 0 · 1 | monstro |
| Emboscada | strike | 26 · 44 | monstro |
| Ferida Aberta | apply | 9 · 42 | 35 do monstro, 7 do herói |
| **Toxicidade** | apply | **0 · 0** | ninguém |
| Pânico | apply | 17 · 93 | 87 do monstro, 6 do herói |
| Hemorragia Fria | strike | 0 · 1 | monstro |
| Ferida Séptica | apply | 4 · 51 | 40 do monstro, 11 do herói |
| Colapso Mental | tick | 17 · 31 | sempre com o herói como o drenado |

- As leis que dependem do HERÓI aplicar a peça disparam pouco, porque ele quase
  não lança carta de status (4.3).
- O que dispara é, na maioria, o monstro, ou o proc de passiva.
- **Quebra Gélida (1 disparo)** precisa de alvo congelado + crítico. Na amostra, o
  congelamento só caiu no HERÓI (49 de 92 tentativas, nas extraídas), lançado por
  monstro, e monstro quase não crita (61 críticos em 25.897 turnos de monstro,
  contra 1.481 do herói). O herói nunca congelou um monstro.
- **Toxicidade (0)** precisa de veneno entrando em alvo Frágil. `frailty` nunca
  caiu no herói e só caiu no monstro 12 vezes, em 2 runs das extraídas. O herói
  envenena pouco por carta (4 de 4 tentativas), e o resto vem de proc.

**Status por efeito** — a tabela está em [`status.md`](status.md).
- A contagem por evento `*_applied` não enxerga o status PRINCIPAL de uma carta de
  status, que só aparece no resultado da skill. A primeira passada usou só o
  evento.
- A segunda passada (`resultados.jsonl`) conta os dois caminhos. Ela corrigiu:
  - congelado e sono no herói, lançados por monstro;
  - a invisibilidade que o monstro lança em si mesmo (113 de 113);
  - um amaldiçoado.
- Eles apareciam como zero, e isso era ausência de instrumentação, não de
  execução. A prova indireta já existia: Emboscada (exige invisível) e Sono e Dor
  (exige sono) dispararam.
- **Nunca aplicados por nada na amostra:** os 7 efeitos positivos dos pares
  (`empowered`, `arcane_surge`, `quickened`, `fortified`, `vitality`, `focused`,
  `precision`).
- O herói aplica status no monstro quase todo por secundário de carta de dano,
  `stun` e proc de passiva. Nas extraídas:

  | efeito | aplicações no monstro |
  |---|---:|
  | vulnerable | 1.095 |
  | bleed | 868 |
  | slowed | 765 |
  | fear | 561 |
  | stun | 544 |

  Pela carta de status propriamente dita, foram 30.
- A segunda passada repetiu as 150 runs. **Todos os outros contadores e a ficha
  final saíram idênticos aos da primeira**: o determinismo das sondas foi
  conferido duas vezes.

### 4.7 Extração e OP

- A decisão de extrair (`evaluators._avaliar_extracao`) é a matriz banda da build
  × fôlego.
- A banda vem de `comparar_com_benchmark`, que roda duelos reais DENTRO da
  decisão de mapa sempre que há Chave e casa E (1.347 medições em 45 runs
  completas).
- Nos 1.841 logs:

  | banda × decisão | andares avaliados |
  |---|---:|
  | ABAIXO, sem preservar | 3.092 |
  | HARD_STOP, preservou | 420 |
  | META_BATIDA, preservou | 77 |
  | CLOSE_ENOUGH, preservou | 51 |

- 371 runs morreram com a extração disponível, todas com a build abaixo da meta.
- OP na extração (amostra de 75): mínimo 27,8, mediana 31,0, máximo 40,5.
- A extração do gerador é, portanto, "parar quando o OP chega ao alvo da Arena".
  É legítimo para gerar gladiadores, mas **não** mede a extração como decisão de
  risco de um jogador.

### 4.8 Chefe (D4)

- 19 chefes ficaram vivos em andares concluídos nas runs completas (de 180
  andares com chefe), e 8 nas extraídas (de 413).
- Nas runs completas, 39 de 56 runs com chefe no mapa enfrentaram um.
- Contornar é jogada legal ("combate é opcional"); é a decisão pendente D4, não um
  defeito novo.

---

## 5. Simulação × jornada real

| Ponto | Jogador real | Gerador (BotPadrão) |
|---|---|---|
| Mercador | 1–3 itens raros, −10% | uma Loja inteira, com venda e reparo |
| Equipar | escolhe a posição | sem posição: troca a primeira |
| Ferreiro | sem teto | 1 +N e 1 encanto por visita, 30% do ouro; nunca retira gema nem reencanta |
| Reroll de oferta | paga 15% da renda, dobrando | nunca |
| Reroll da Loja | sem teto | ≤2, só com vitrine inútil, ≤25% do ouro |
| Recuperação | HP e MP | só HP |
| Consumíveis | compra e usa qualquer um | compra só cura; usa só cura |
| Skills | escolhe a carta do turno | quase só dano |
| Extração | decisão de risco | filtro de OP contra o benchmark |
| Altar | paga e não ganha nada (bug do jogo) | idem |
| Leis de par oposto | inalcançáveis (sem conteúdo) | idem |
| Mapa | não vê o monstro antes da colisão | idem (protegido por teste) |
| Encontro, loot, gema, chave, nível | `resolve_encounter` | o mesmo |

---

## 6. Problemas classificados

| Problema | Classificação | Arquivo / função | Evidência |
|---|---|---|---|
| Altar sem efeito | **bug mecânico** | `content/factories/dungeons.apply_altar_blessing`, `shared/effects.buff_stat` | A/B 60/60; sem `stat`, fora de `LEGACY_BUFF_STATS` |
| 7 leis de par oposto inalcançáveis | **mecânica / lacuna de conteúdo** (decisão de design pendente) | `shared/effect_core.OPPOSING_PAIRS`; nenhum conteúdo aplica o lado positivo | 0 disparos; busca nos JSON e no código |
| Troca na posição errada | **política do bot** | `sim/progression.equip_if_better` + `Player.equip` | A/B; 70/75 extraídas; 159/186 |
| Poção de mana nunca usada | **política do bot** | `src/sim/bot/evaluators.avaliar_combate` não lê `mana_restored` | 0 em 4.869 turnos (completas) e 12.261 (extraídas) |
| Elixires nunca usados; `mana_regen` fora do cardápio | **política do bot** | `evaluators.avaliar_combate`; `tools/bot_adapter.ELIXIR` | 0 em 5.827 e 21.376 turnos |
| Skills de não-dano ignoradas | **política do bot** (força real das cartas NÃO MENSURADA) | `evaluators.avaliar_combate` | ~0,2% das escolhas |
| Sem reroll de oferta | **política do bot** (não exercitado) | `BotPadrao._escolher_do_nivel` | 0 em 1.015 ofertas (completas) e 2.233 (extraídas) |
| Sem retirar gema / reencantar | **política do bot** (não exercitado) | `progression.visit_forge` | 0 em 272 e 599 visitas |
| Sem recuperação de MP | **política do bot** (não exercitado) | `progression._repair` | 0 |
| Não compra mana/elixir | **política do bot** (não exercitado) | `progression.visit_shop` | 0 em 332 e 689 vitrines |
| Reroll da Loja quase nunca | **política do bot** | `progression._rerollar_estoque` | 0 em 332 e 1 em 689 vitrines |
| Mercador = Loja inteira | **política do bot** (divergência da jornada) | `BotPadrao._resolver_evento` | A/B 2 × 23 ofertas |
| +N e encanto contidos, armas em +0 | **política do bot** | `progression.visit_forge` (`BOT_MAX_*`, `BOT_FORGE_BUDGET_RATIO`) | 72% das armas em +0; máx +3; ouro parado |
| Gema na bolsa e socket vazio | **política do bot** | `visit_forge` (sem retirar; só engasta em visita) | 31/75; 69/186 |
| Extração = filtro de OP | **comportamento intencional (do gerador)** | `evaluators._avaliar_extracao`, `BotExperimental` | 548/550 nas bandas de meta |
| Chefe contornável | **comportamento intencional de design** (D4) | `engine` `move_player` | 19 e 8 chefes deixados |
| IA sobrevivência só com cura | **comportamento intencional de design** | `mechanics/monster_ai._pick_skill` | 29/98 e 55/75 |
| Efeito por passiva | **ausência de instrumentação** | — | NÃO MENSURADO (exige A/B por carta) |
| Efeito do reroll da Loja | **ausência de instrumentação** | — | NÃO MENSURADO |
| Dano mitigado e dano de cada lei | **ausência de instrumentação** | `Observador` só vê o dano final | NÃO MENSURADO |
| Status principal de carta de status (1ª passada) | **ausência de instrumentação** (corrigida) | o evento sai só em `COMBAT_SKILL_OUTCOME` | corrigido na 2ª passada, 150/150 contadores idênticos |

---

## 7. O que ficou NÃO MENSURADO

- **O efeito de cada passiva.** As 23 famílias aparecem na população (até
  `death_ignore`, em 2 gladiadores), mas medir o efeito de cada uma exige A/B por
  carta.
- **Se as skills de não-dano e os elixires seriam bons.** O bot não os usa, e
  julgar a força deles exige uma política que os use. Não é desta etapa.
- **O dano antes da mitigação e o dano acrescentado por cada lei.** O barramento
  publica o dano final.
- **O efeito do reroll da Loja**, que aconteceu 1 vez na amostra.

---

## 8. O que isso diz das avaliações anteriores

- **Combat/Class Balance (`expected loadout`, `-m balance`).** É sintético: não
  passa por Loja, Ferreiro, eventos nem pelas decisões de equipamento do bot. Os
  defeitos de política não o contaminam.
  - O que ele também não viu: as 7 leis de par oposto, que nenhum conteúdo
    alcança.
  - E as skills que não são de dano, na medida em que o `simulate_run` escolhe
    ação pelas mesmas políticas. Isso não foi auditado aqui; o escopo foi o
    gerador.
- **Run/Progression Balance (`d3105edc`, "CALIBRADO").** Foi medido com o mesmo
  BotPadrão e as mesmas políticas. Portanto foi calibrado:
  - com o Altar custando HP sem dar nada;
  - sem poção de mana, sem elixir e quase sem skill que não seja de dano;
  - sem reroll de oferta;
  - com a troca de equipamento errada;
  - com o Ferreiro contido.

  A curva de dificuldade medida é a de **um jogador que ignora esses sistemas**,
  não a do jogo inteiro. Pelo contrato, isso é "comportamento do bot": não reabre
  sozinho o balance de classe, mas também **não valida** esses sistemas.
- **População da Arena (186 gladiadores, OP 20–30, e o teste de OP 40–70).** O OP
  medido é o da build que o bot montou: arma melhor na mochila em 139/186 e 72%
  das armas em +0. O OP mede bem a força **daquela ficha**, mas **subestima** o que
  a mesma run renderia com a posição certa e o Ferreiro usado. A escala de OP da
  Arena foi calibrada sobre essas fichas.
- **A resposta à pergunta anterior** ("compraram corretamente e usaram o upgrade
  das armas corretamente?"):
  - **as compras são legítimas**;
  - **o uso do upgrade não é correto**, pelos motivos de [4.2](#42-equipar-compara-com-o-pior-troca-o-primeiro)
    e [4.4](#44-ferreiro).

---

## 9. Reproduzir

Os scripts usados estão em `ferramentas/`. Rodam a partir da raiz do repositório e
não alteram nada em `src/` ou `tools/`.

```
python reports/auditoria_pve/ferramentas/passiva.py        # sonda passiva sobre os 1.841 logs
python reports/auditoria_pve/ferramentas/populacao.py      # os 186 gladiadores
python reports/auditoria_pve/ferramentas/verificacoes.py   # A/B: Altar, troca, cardápio, Mercador
python reports/auditoria_pve/ferramentas/amostra.py principal amostra.json
python reports/auditoria_pve/ferramentas/sondas.py rodar <abs>/amostra.json <abs>/resultados.jsonl --trabalhadores 4
python reports/auditoria_pve/ferramentas/matriz.py <abs>/resultados.jsonl matriz.json
```

- Os logs de geração (`_trabalho/`) ficam fora do git. A amostra (`amostra.json`)
  guarda a linha de log de cada tarefa, e é contra ela que `sondas.py` confere a
  reprodução.
- A sonda de status principal entrou na segunda passada. Todos os outros
  contadores da segunda passada são idênticos aos da primeira, e o determinismo
  das sondas foi conferido assim. A conferência é a primeira linha de
  `status.md`: `python reports/auditoria_pve/ferramentas/status.py
  <resultados.jsonl> <primeira_passada.jsonl>`.

---

## Apêndice — onde cada sistema mora e quem o chama no gerador

O gerador é `tools/arena_copa_03_geracao.executar` → `BotExperimental` (subclasse de
`tools/bot_padrao.BotPadrao`). O BotExperimental só troca três coisas: a política de
escolha (`picker`), a linha de aposta por andar e a matriz de extração por perfil.
Todo o resto é o BotPadrão.

| Sistema | Regra (jogo) | Decisão (bot) | Acessível ao bot? |
|---|---|---|---|
| Nova jornada, Starter Kit | `engine/game_logic.create_player_for_new_run`, `content/starter_kit.py` | — | sim, o mesmo caminho do jogador |
| Mapa, população, serviços | `engine/loop._setup_dungeon_map`, `content/factories/monsters.py`, `content/factories/features.py` | `BotPadrao._decidir_no_mapa` → `src/sim/bot/evaluators.decidir_no_mapa`, `tools/bot_adapter.acoes_do_mapa` | sim |
| Encontro (batalha, pós-combate, loot, gema, chave, nível) | `engine/encounter.resolve_encounter` / `process_post_battle`, `mechanics/battle.run_battle` | `BotPadrao._duelo` | sim, o mesmo núcleo da tela |
| Ação de combate do herói | `mechanics/combat.py` | `BotPadrao._decidir_no_combate` → `src/sim/bot.decidir_no_combate`, `tools/bot_adapter.acoes_do_combate` | ataque, skills, poção de cura/mana, 7 elixires, fuga. **Fora: elixir `mana_regen`** |
| IA do monstro | `mechanics/monster_ai.decide_monster_action` / `_pick_skill` | — (lado do motor) | sempre ativa |
| Status e as 16 leis | `shared/effect_core.py`, `shared/interactions.py`, `mechanics/combat.try_apply_status` / `_anunciar_interacoes` | `bot_adapter._interacoes_da_skill` (o avaliador não pontua `interactions` explicitamente; o ganho de golpe já vem em `expected_strike_damage`) | sempre ativas |
| Level-up: passiva | `content/level_up.ofertas_do_nivel` / `aplicar_passiva` | `BotPadrao._escolher_do_nivel` → `pick_policies.pick_passive` | sim |
| Level-up: skill (aprender, substituir, recusar) | `content/level_up.aplicar_skill` | `pick_policies.pick_skill` | sim |
| Reroll de oferta de passiva/skill | `ui/passive_flow.py`, `ui/skill_flow.py` (preço: `content/economy.reroll_cost`) | **nenhum**: `_escolher_do_nivel` não tem caminho de reroll (`sim/progression.on_level_up` tem, mas o BotPadrão não passa por ele) | **não** |
| Loja: comprar, vender, reroll | `content/shop.Shop` / `ShopVisit.reroll` | `BotPadrao._comprar_com_orcamento` → `sim/progression.visit_shop` (`_vender_dominados`, `_repair`, `_rerollar_estoque`) | sim, com tetos do bot: ≤2 rerolls, só com vitrine sem nada útil, ≤25% do ouro; equipamento com ≤60% do ouro |
| Recuperação paga | `content/economy.recovery_offers` / `buy_recovery` (HP **e** MP) | `progression._repair` | **só HP** |
| Ferreiro: +N, engastar, encantar | `content/forge.enhance` / `socket` / `enchant` | `BotPadrao._usar_ferreiro` → `progression.visit_forge` | sim, com tetos do bot: 1 +N e 1 encanto por visita, 30% do ouro |
| Ferreiro: retirar gema, reencantar | `content/forge.unsocket` / `reenchant` | **nenhum** | **não** |
| Equipar | `entities/heroes.Player.equip` (sem posição: 1ª livre, senão **a primeira**) | `progression.equip_if_better` (compara com o PIOR ocupante, mas não passa a posição) | sim, **com defeito** |
| Evento Fonte / Altar | `content/factories/dungeons.apply_fountain_heal` / `apply_altar_blessing` | `BotPadrao._resolver_evento` | sim |
| Evento Mercador | `ui/random_event_flow.run_merchant_event` → `get_merchant_offers` (1–3 itens, peso por raridade, −10%) | `BotPadrao._resolver_evento` → `_comprar_com_orcamento` → **a Loja inteira** | **divergente** |
| Poção no mapa | `Player.use_potion` | `BotPadrao._beber_pocao` (só `max_hp`) | só cura |
| Saída, taxa, descanso, juros, Essência | `content/floor_exit.use_exit` / `effective_essence`, `content/economy.pay_interest` | fim de `BotPadrao._jogar_andar` | automáticos |
| Fuga | `mechanics/battle` (`roll_flee_success`) | uma das ações de `decidir_no_combate` | sim |
| Extração e Chave | `content/extraction.award_key` / `finish_run` | `evaluators._avaliar_extracao` (matriz banda × fôlego; banda pelo OP contra o benchmark) | sim |
| Medição de OP | `tools/arena_alvo.comparar_com_benchmark` → `overall_power` | `bot_adapter._comparacao_com_a_arena` (dentro da decisão de mapa, só quando extrair é possível) e `executar` (no fim) | sim |
