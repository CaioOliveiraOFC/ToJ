# Etapa 0 — instrumentação e baseline da fundação PvE

| | |
|---|---|
| **Branch** | `phase/game-core`, criada da `master` em `97965ae` (`v0.3-pve`) |
| **Trabalho** | `feature/etapa0-instrumentacao`, integrada à `phase/game-core` com `--no-ff` |
| **Gameplay** | nenhum arquivo de `src/`, `tools/bot_padrao.py` ou `tools/arena_alvo.py` mudou |
| **Fora do escopo** | correções do Altar, do Mercador, de equipamento, de gemas e da inteligência do bot; refatoração do RNG; `master`, `phase/pvp-arena`, os 186 gladiadores e a calibração da Ranked |

A Etapa 0 não corrige nada. Ela registra o PvE como ele está, mede o que o
BotPadrão de fato exercita e trava em teste quais efeitos declarados não fazem
nada. As etapas seguintes vão se medir contra isto.

---

## Resumo

- **B0:** 300 de 300 runs idênticas à `d3105edc`, campo a campo. A passada com
  as sondas instaladas também reproduz as 300, o que prova que as sondas só
  observam.
- **Efeitos declarados:** 92 pares (fonte, efeito), testados A/B pelos
  consumidores do motor:
  - 85 funcionais;
  - 7 sem efeito e ao alcance do jogador, todos em `xfail` estrito.

  Dos sete, 5 são bugs; dois deles são novos: os buffs de vida e mana máxima
  (KI-008) e o efeito `defense` de equipamento (KI-009). Os outros 2 são
  pendências de design: `true_damage` e `armageddon` (KI-013).
- **Cobertura do bot:** o BotPadrão quase só usa skills de dano. De 17.408
  turnos com buff disponível, escolheu buff 10 vezes. A troca de equipamento na
  posição errada aparece em 76 runs, 72 delas com perda líquida, e em 69 das 73
  builds extraídas. Poção de mana, recuperação de MP, retirar gema e reencantar
  nunca foram usados.
- **RNG:** a reprodução é exata (mesma seed, mesmo código, mesma run). O
  pareamento entre versões é frágil. Um único sorteio a mais, que não muda regra
  nenhuma, altera o desfecho de 25% a 62% das runs, e em 60 pares produziu um
  Δ médio de +3,0 andares (erro padrão 1,1). Com 100 seeds por classe, o efeito
  mínimo detectável fica em ~2 a 3 andares por classe. Nada foi refatorado.
- **CI:** a `phase/game-core` e os PRs para ela passam a ser validados. O
  balanceamento roda em quatro fatias, porque num job só ele estourou os 25
  minutos na `master` (`97965ae`) e o gate nunca chegou a verificar nada.

---

## 1. Baseline B0

Protocolo da `d3105edc` sem alteração, com o coletor dela rodado sem cópia:
- BotPadrão conservador;
- Starter Kit;
- seeds 1–100 × 3 classes;
- teto 200;
- um processo por run.

| Métrica | Todas (n=300) | Warrior | Mage | Rogue |
|---|---:|---:|---:|---:|
| mortes / extrações | 227 / 73 | 74 / 26 | 68 / 32 | 85 / 15 |
| andar médio | 9,18 | 10,25 | 10,10 | 7,19 |
| andar mediana · P90 · máx | 6 · 22 · 28 | 8 · 22 · 25 | 6 · 22,1 · 28 | 4 · 21 · 27 |
| morte no andar 1 / até 5 | 32 / 145 | 10 / 34 | 7 / 49 | 15 / 62 |
| chegou ao 10 / ao 20 | 94 / 67 | 37 / 25 | 36 / 26 | 21 / 16 |

- `tools/cobertura_pve.py conferir`: 300 medidas, 0 divergentes.
- O agregador histórico dá diferença zero em todas as linhas.
- Protocolo, comandos e hashes: [`baselines/progression/97965ae/`](../../baselines/progression/97965ae/README.md).

---

## 2. Efeito declarado sem implementação funcional

`tests/test_cobertura_de_efeitos.py` gera os casos a partir do conteúdo.
Um efeito novo no JSON entra sozinho. Para cada par (fonte, efeito), o teste
monta a mesma entidade com e sem o efeito (valor inflado, mesmas seeds) e
compara o que os consumidores do motor devolvem:
- atributos resolvidos;
- baldes de dano e chance de acerto;
- golpes dados e recebidos;
- início de turno;
- resistência a status;
- cura de poção;
- golpe letal;
- recompensa pós-combate;
- seis lutas semeadas contra `bruiser` e `controller`.

A diferença para o `test_placebo` é o critério de prova: lá basta o
`active_buffs` mudar; aqui o combate precisa ler o efeito.

| fonte | funcional | pendência: bug | pendência: design |
|---|---:|---:|---:|
| passiva | 23 | | |
| equipamento | 17 | 1 | 2 |
| consumível | 10 | | |
| encantamento | 11 | | |
| gema | 6 | | |
| skill de herói (canal) | 11 | 2 | |
| skill de monstro (canal) | 5 | 1 | |
| passiva de monstro | 1 | | |
| evento do mapa | 1 | 1 | |
| **total (92)** | **85** | **5** | **2** |

**Pendências** (`PENDENCIAS`, todas em `xfail` estrito: a correção transforma o
XPASS em reprovação):

| caso | tipo | id | o que acontece |
|---|---|---|---|
| `evento:altar` | bug | PVE-01 / KI-007 | a bênção é gravada sem `stat`; o jogador paga 30% do HP máximo por nada |
| `skill-heroi:buff:hp` e `buff:mp` | bug | N10 / KI-008 | seis skills de herói ("+40% de vida máxima" e afins) gravam um buff que o teto de HP/MP não lê |
| `skill-monstro:buff:hp` | bug | N10 / KI-008 | `mob_raizes_fundas` e `mob_folego_emprestado`: mesmo defeito no monstro |
| `equipamento:defense` | bug | N11 / KI-009 | o `elif` de `equipment_percent` nunca lê `effect_type: defense`; o Amuleto de Argila mostra "+3" e entrega o `defense_bonus` 1 |
| `equipamento:true_damage` | design | N4 / KI-013 | a Espada do Universo (lendária, cai como drop) mostra "true_damage +20"; não existe mecânica de dano verdadeiro |
| `equipamento:armageddon` | design | N4 / KI-013 | o Cajado da Galáxia (lendário, cai como drop) mostra "armageddon +50"; não existe mecânica de armageddon |

Nenhum efeito ao alcance do jogador é tratado como inerte de propósito. Deixar
um deles assim exigiria uma decisão de design, e nenhuma foi tomada.

**Fontes do catálogo** (`TestFontesDoCatalogo`):
- **Efeitos sem fonte:** são exatamente os sete efeitos positivos dos pares
  opostos (`empowered`, `arcane_surge`, `quickened`, `fortified`, `vitality`,
  `focused`, `precision`).
- **Leis inalcançáveis pelo conteúdo:** são exatamente as sete leis de par
  (PVE-02).
- Os dois conjuntos ficam travados: um efeito ou uma lei a mais reprova.
- O travamento serve para notar mudança, e não para validar o estado atual.
  Nenhuma decisão registrada diz que isso é intencional (KI-014).

A matriz completa, com o consumidor que muda em cada caso, está em
[`matriz_efeitos.md`](matriz_efeitos.md).

---

## 3. O que o BotPadrão exercita

A passada instrumentada usa as sondas da auditoria de cobertura, portadas da
`phase/pvp-arena` sem merge (`tools/cobertura_pve.py`). Ela mede, por sistema,
quantas runs tiveram oportunidade, quantas usaram e quantas ficaram com efeito.
Matriz completa: [`matriz_cobertura.md`](../../baselines/progression/97965ae/matriz_cobertura.md).

Recorte (n = 300 runs; entre parênteses, as 73 extraídas quando muda a leitura):

| sistema | oportunidade | uso | efeito | leitura |
|---|---:|---:|---:|---|
| Loot de equipamento | 226 | 210 | 210 | usado |
| Ferreiro (casa) | 261 | 171 | 133 | usado |
| +N (aprimorar) | 156 | 125 | 118 | usado |
| Gemas (engastar) | 92 | 91 | 85 | usado quando há gema e socket |
| Encantar | 171 | 64 | 55 | parcial |
| Retirar gema · Reencantar | 171 | 0 | — | **nunca** |
| Recuperação paga de HP | 235 | 224 | 224 | usado |
| Recuperação paga de MP | 235 | 0 | — | **nunca** |
| Poção de mana | 37 | 0 | 0 | **nunca** |
| Elixires | 68 | 2 | 2 | quase nunca |
| Reroll de oferta de skill/passiva | 253 | 0 | — | **nunca** (o driver não tem caminho) |
| Reroll da Loja | 235 | 3 | — | quase nunca |
| Evento Altar | 144 | 56 | 0 | aceito e sem efeito (KI-007) |
| Evento Mercador | 135 | 51 | 43 | tratado como uma segunda Loja (N1) |
| Troca na posição errada | 210 | 76 | 72 | defeito do bot (BOT-01); 69 das 73 extraídas |

**Skills em combate.** Pelos turnos em que cada tipo estava disponível:

| tipo | turnos disponível | escolhido | (run, skill) disponível 20+ turnos e nunca escolhida |
|---|---:|---:|---:|
| dano | 48.784 | 27.448 | — |
| buff | 17.408 | 10 | 166 |
| redução de dano | 15.222 | 19 | 76 |
| cura | 18.086 | 40 | 56 |
| status | 9.973 | 16 | 121 |

Na prática, o bot joga com o deck de dano e trata o resto como peso morto.
Por isso a cobertura de buff, cura e status pelo bot é próxima de zero, e as
leis de interação que dependem do herói mal aparecem.

**Leis de interação, medidas em jogo.**
- As sete leis de par e a `toxicidade` disparam zero vezes em 300 runs.
- `toxicidade` é alcançável pelo conteúdo: `frailty` vem das skills do
  `support`. Mesmo assim, não foi observada.
- As demais disparam: `emboscada` 79, `sleep_damage` 55, `colapso_mental` 49,
  `ferida_septica` 23, `panico` 11, `ferida_aberta` 7, `quebra_gelida` 3 e
  `hemorragia_fria` 2.

**Outros sinais da matriz:**
- 119 dos 608 andares com chefe terminaram com o chefe vivo.
- 48 runs acabaram com gema na bolsa e socket vazio equipado.
- A mediana do ouro parado no fim é 26% do que foi ganho.

### Limite conhecido da instrumentação e proposta de correção

Registrado como KI-015. Não é defeito do jogo, é defeito da medição.

**O problema.**
- A tabela de status aplicados conta o evento `<status>_applied`.
- `combat.try_apply_status` só publica esse evento quando quem chama passa
  `applied_kind`. Os secundários de skill, os procs de acerto e o atordoamento
  passam; o ramo principal das skills de status (`effect_type == "status"`) não.
- Na passada da B0, `frozen`, `sleep` e `invisible` aparecem com zero
  aplicações, embora `quebra_gelida`, `sleep_damage` e `emboscada`, que dependem
  deles, disparem 3, 55 e 79 vezes.
- O contador de leis lê o evento `interaction` e é confiável. A contagem de
  status não é, e justo para o que a IA de combate vai mudar: o uso de skills de
  status, hoje 16 escolhas em 9.973 turnos disponíveis.

**A proposta.** Só ferramenta: nada em `src/` muda.

1. **Contar na porta única.** A sonda passa a embrulhar
   `effect_core.apply_effect`, o único ponto por onde um status entra numa
   entidade. Em `src/`, o único chamador é `try_apply_status`.
   - Conta cada aplicação que devolveu instância, por efeito, por lado (herói ou
     monstro) e por origem.
   - A origem é a skill (primária ou secundária), o proc de acerto ou outra.
     Ela vem do `source_id` e de qual chamador do `try_apply_status` está ativo.
   - Usa o mesmo filtro das outras sondas: só o monstro da batalha real, fora
     dos duelos de benchmark do OP e antes do fim da run.
2. **Contar também as tentativas.** Embrulhar o próprio `try_apply_status` dá
   tentativas, aplicações e resistências por status. Com isso, a taxa de acerto
   de cada carta fica medida: o número de que a IA de combate precisa para
   valer uma skill de status.
3. **Manter o contador antigo ao lado**, rotulado como "eventos publicados",
   para que a diferença entre os dois fique visível na matriz.
4. **Conferência de consistência no agregador.** Em toda run em que uma lei
   disparou, cada efeito que ela exige precisa ter ao menos uma aplicação
   contada (`quebra_gelida` ⇒ `frozen`, `emboscada` ⇒ `invisible`…). Qualquer
   violação é erro de instrumentação e reprova a matriz.
5. **Validação.**
   - Um teste em `tests/` roda uma luta dirigida com uma skill de status
     primária (por exemplo `mob_teia_de_gelo`) e exige que a sonda conte o
     `frozen`.
   - A passada de 300 runs é refeita: `conferir` precisa continuar dando 0
     divergentes contra a B0 (não interferência), e a matriz nova só pode
     mudar na seção de status.

**A alternativa descartada por ora.** Fazer o motor publicar
`<status>_applied` em toda aplicação, com `applied_kind` padrão no
`try_apply_status`. Isso muda `src/` e o fluxo de eventos que a interface
recebe. É uma decisão de produto, e não de medição.

**Por que antes da IA de combate.** As melhorias do bot em skills de status e
buff vão ser julgadas pela matriz. Com o contador atual, uma IA que passasse a
congelar e adormecer bem apareceria com zero aplicações dos dois status.

---

## 4. RNG compartilhado e pareamento entre versões

O jogo sorteia por duas fontes:
- **o gerador da run** (`BotPadrao.rng`): combate e decisões;
- **o `random` global:** mapa, vitrine da Loja, loot, gema, chave, encanto e
  nomes.

Uma mudança de código que consome um sorteio a mais desloca tudo o que vem
depois na mesma fonte. Isso não quebra a reprodução, mas quebra o pareamento:
"a seed 42 na versão nova" deixa de ser a mesma run da seed 42 na antiga.

**Experimento** (`tools/rng_pareamento.py`, só medição, nada refatorado).
- **Protocolo:** o histórico, em seeds 1–20 × 3 classes (60 runs por braço).
- **Braços:** quatro, que só diferem num sorteio a mais no andar 2:
  - **controle:** nada muda;
  - **`global`:** um `random.random()` antes de gerar o mapa;
  - **`global_pos_mapa`:** o mesmo sorteio logo depois do mapa. É onde cai uma
    mudança típica de versão: um sorteio a mais no loot, na Loja ou num evento;
  - **`run`:** um sorteio a mais no gerador da run, como faria uma mudança no
    combate ou numa decisão.

O controle reproduz a baseline publicada em **60/60**, então as sondas do
experimento não interferem.

| braço | mapa diverge (das 55 que chegam ao andar 2) | estado do herói diverge | desfecho final igual | Δ andar: média (EP) · mediana | ρ do andar final |
|---|---:|---:|---:|---|---:|
| `global` (antes do mapa) | 16/55 | 15/55 | 45/60 | +0,42 (0,82) · 0 | 0,66 |
| `global_pos_mapa` | 24/55 | 26/55 | 39/60 | +1,85 (0,85) · 0 | 0,70 |
| `run` | 41/55 | 47/55 | 23/60 | +3,03 (1,07) · 0 | 0,51 |

**Leitura.**
- **A reprodução é exata.** B0, passada instrumentada e controle repetem as
  runs publicadas campo a campo.
- **O gerador de mapa absorve parte da perturbação global.** O gerador é uma
  caminhada aleatória com rejeição na borda. Dois trajetos deslocados acoplam
  ao bater nas mesmas paredes, e o mapa sai idêntico, com o gerador global no
  mesmo estado.
  - Antes do mapa, 39 das 55 perturbações foram absorvidas assim (71%).
  - Depois do mapa, mais da metade é absorvida no andar seguinte.

  Isso é sorte do algoritmo, e não uma garantia: ninguém deve contar com isso.
- **Quando a perturbação escapa, o efeito é tudo ou nada.** O Δ de andar por
  run é 0 na maioria dos pares e de ±16 a ±22 andares no resto: uma run que
  morria cedo passa a ir fundo, ou o contrário. O gerador da run é o mais
  sensível: o desfecho muda em 37 de 60 runs.
- **Um sorteio a mais já parece um efeito.** No braço `run`, que por
  construção não muda regra nenhuma, a média subiu +3,0 andares com t ≈ 2,8
  em 60 pares. Lido sem cuidado, isso seria uma "melhoria".

**Quanto custa comparar versões.** Usa a variância da B0. O efeito mínimo
detectável tem poder de 80% e α de 5%, no protocolo atual de 100 seeds por
classe:

| | σ(andar) | não pareado | pareado com o ρ medido (0,51–0,70) | pareado ideal (ρ = 0,9) |
|---|---:|---:|---:|---:|
| warrior | 7,76 | 3,1 andares | 1,7–2,2 | 1,0 |
| mage | 8,42 | 3,3 andares | 1,8–2,3 | 1,1 |
| rogue | 7,29 | 2,9 andares | 1,6–2,0 | 0,9 |
| todas (n=300) | 7,96 | 1,8 andares | 1,0–1,3 | 0,6 |

Para a taxa de extração, o efeito mínimo detectável sem pareamento é de 14 a 18
p.p. por classe e 9,8 p.p. no total. Para detectar Δ = 1 andar por classe sem
pareamento seriam 835 a 1.115 runs por classe e por braço.

**Implicações para as próximas etapas. Nenhuma foi implementada.**
- Comparação run a run entre versões ("a seed 42 piorou") não é evidência
  depois do primeiro sorteio divergente. Só agregados valem.
- Com 100 seeds por classe, mudanças menores que ~2 andares por classe, ou
  ~1 andar no total, não aparecem. Uma correção pequena precisa de mais seeds
  ou de uma métrica mais sensível que o andar final.
- Separar as fontes por subsistema (N5) aumentaria o ρ. Pelo efeito mínimo
  detectável, levar o ρ de ~0,6 para ~0,9 reduz a amostra necessária em 3 a 4
  vezes. Isso também precisa ser medido antes da refatoração, com este mesmo
  experimento.

Dados: [`baselines/progression/97965ae/rng/`](../../baselines/progression/97965ae/README.md#arquivos).

---

## 5. CI

`.github/workflows/ci.yml` (commit `b9f7419`):
- **Gatilhos:** push em `master` e `phase/game-core`; pull request para as
  duas. As branches `fix/*` e `feature/*` são validadas pelo PR. Um gatilho de
  push nelas faria cada execução rodar duas vezes.
- **Balanceamento em quatro fatias por arquivo**, cada uma com 60 minutos:
  - `bandas`;
  - `scout`;
  - `pick_skill`;
  - `arena` (`test_arena_power` e `test_arena_alvo`).

  Os fixtures são por classe e por módulo, então a fatia não refaz simulação.
  Nenhum threshold mudou.
- **Job novo, "Fatias cobrem todo o balanceamento".** Só coleta e reprova se um
  teste `balance` aparecer fora das fatias.
- **Por que mudou.** Na `master`, o job único de balanceamento estourou os 25
  minutos no push da `v0.3-pve` (`97965ae`, run 39963944308) e saiu como falha
  sem ter rodado inteiro. Localmente, a suíte inteira leva 34 minutos num
  processo.

O resultado da execução remota fica no GitHub Actions: workflow `CI`, push na
`phase/game-core`. Este relatório não o afirma, porque foi escrito antes dessa
execução.

---

## 6. Testes executados

| o quê | onde | resultado |
|---|---|---|
| Suíte padrão (`pytest -q`) | local, Python 3.13 | 3196 passed, 3 skipped, 118 deselected (`balance`), 6 xfailed (5 desta etapa + o custo × recarga anterior) |
| `tests/test_cobertura_de_efeitos.py` | local | 92 passed, 5 xfailed, em ~12 s |
| `ruff check` e `ruff format --check` | `src/`, `tests/` e as ferramentas novas | limpo |
| `-m balance` | só na CI, por fatias | ver seção 5 |
| B0 (300 runs) | `run_auditoria.py` da `d3105edc` | 300/300 idênticas |
| Passada instrumentada (300 runs) | `tools/cobertura_pve.py` | 300/300 idênticas à `d3105edc` |
| Experimento de RNG | `tools/rng_pareamento.py` | ver seção 4 |

---

## 7. Problemas encontrados

| | problema | classificação | registro |
|---|---|---|---|
| 1 | Buffs de vida e mana máxima (6 skills de herói, 2 de monstro) não fazem nada | bug/mecânica, **novo** | KI-008, `xfail` |
| 2 | `effect_type: defense` de equipamento nunca é lido | bug/mecânica, **novo** | KI-009, `xfail` |
| 3 | Bênção do Altar sem efeito | bug/mecânica | KI-007, `xfail` |
| 4 | Vender peça engastada destrói as gemas; o preço ignora `+N` e encantos | bug/integração | KI-010 |
| 5 | `true_damage` e `armageddon`: armas lendárias que caem como drop e mostram efeitos sem mecânica | pendência de design e implementação | KI-013, `xfail` |
| 6 | Os sete efeitos positivos dos pares opostos não têm fonte; as sete leis de par nunca disparam | pendência de design e conteúdo | KI-014 |
| 7 | O gate de balanceamento da CI na `master` nunca terminou (timeout em `97965ae`) | infraestrutura | fatiado na `phase/game-core` (resultado na seção 5); a `master` continua como está |
| 8 | A sonda de status aplicados subconta as skills de status primárias | limite da instrumentação | KI-015; proposta na seção 3 |
| 9 | Um sorteio a mais muda o desfecho de 25% a 62% das runs; com 100 seeds por classe, o efeito mínimo detectável é de ~2 a 3 andares por classe | medição/instrumento | KI-012, seção 4 |
| 10 | O `test_placebo` aceita "o `active_buffs` mudou" como prova de efeito | lacuna de teste | coberto pelo teste novo |

---

## 8. O que a Etapa 0 entrega para a decisão

- A linha de partida (B0) e o instrumento que vai medir cada correção: a
  cobertura por sistema e os casos `xfail` que viram reprovação quando o
  defeito for corrigido.
- Uma lista fechada de efeitos sem função, separada em bugs e pendências de
  design.
- Um retrato do que o BotPadrão não exercita. As correções de mecânica das
  etapas seguintes só aparecem na régua se o bot as usar.
- O custo do RNG compartilhado para comparar versões.

A Etapa 1 não foi iniciada.
