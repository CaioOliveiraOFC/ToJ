# Baselines

Índice das réguas e medições de referência do projeto. Cada linha aponta para a
fonte que guarda o protocolo e os números completos; este arquivo só diz **o
que cada uma mede e quando ela pode ser comparada**.

| Baseline | Commit | Régua | Estado | Fonte |
|---|---|---|---|---|
| Pre-balance | `88190c5f` | BotPadrão da época, largada nua (`create_player_from_data`), `max_andar` 20, seeds 20260000–20260999, 3.000 runs | **histórica** | [`reports/BASELINE_PRE_BALANCE.md`](reports/BASELINE_PRE_BALANCE.md) |
| Combat/Class E8 | `bc815fcd` | `expected loadout` (`simulate_run`, política `smart`) | **fechada** | `tests/balance/` (`pytest -m balance`) e [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md#etapa-8--class-balance) |
| Progression real | `fb321d4e` | jornada real: BotPadrão conservador + Starter Kit, seeds 1–100 × 3 classes, teto técnico 200 | **histórica** — o "antes" do instrumento | [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md) |
| Auditoria do instrumento | `0ab837b9` | o mesmo protocolo da `fb321d4e`, com o BotPadrão corrigido | **histórica** — o "antes" da dungeon | [`baselines/progression/0ab837b9/README.md`](baselines/progression/0ab837b9/README.md) |
| Auditoria da dungeon | `4d0a9a0a` | o mesmo protocolo, com o BotPadrão congelado e a dungeon alterada | **histórica** — o "antes" do primeiro level-up | [`baselines/progression/4d0a9a0a/README.md`](baselines/progression/4d0a9a0a/README.md) |
| Auditoria do primeiro level-up | `d3105edc` | o mesmo protocolo, com o BotPadrão congelado e só o custo do primeiro level-up alterado | **referência** — `-m balance` verde no `82ff73ea`; reproduzida pela B0 | [`baselines/progression/d3105edc/README.md`](baselines/progression/d3105edc/README.md) |
| B0 da fundação PvE | `97965ae` | o mesmo protocolo e o mesmo coletor da `d3105edc`, sem mudança de gameplay | **referência atual** da `phase/game-core` — 300/300 runs idênticas à `d3105edc` | [`baselines/progression/97965ae/README.md`](baselines/progression/97965ae/README.md) |
| Alvo de extração | remedido em `bc815fcd` | `overall_power` do snapshot de um Rogue real, `PODER_ESPERADO` | **instrumento** — alarme de deslocamento | `tools/arena_alvo.py`, `src/data/arena_benchmark_v1.json`, `tests/test_arena_alvo.py` |

---

## O que cada uma mede

**Pre-balance.** É o retrato do jogo antes do Balanceamento Global e da reforma
de fundação.
- O bot da época nascia nu: nível 1, sem nenhuma peça.
- A janela era de 20 andares.
- Guarda o histórico de onde o jogo estava. Não descreve o jogo de hoje.

**Combat/Class E8.** Compara as classes **sob condições controladas**.
- O herói recebe sinteticamente o equipamento esperado para o nível
  (`src/sim/loadouts.py`), sem passar pela dungeon.
- As bandas estão em `tests/balance/thresholds.py` e rodam a 250 runs com a
  seed 1337.
- A validação da Etapa 8 usou 3.000 runs por classe; os números estão na
  mensagem do `bc815fcd`.

**Progression real.** Mede **a jornada de verdade**:
- nova jornada com Starter Kit;
- mapa, loot, economia, serviços, fuga e extração;
- jogada pelo BotPadrão.

É a régua de Run/Progression Balance. O protocolo, os 300 resultados e a
classificação dos achados estão no README dela.

**Auditoria do instrumento.** É a mesma régua depois do bloco que corrigiu o
BotPadrão (`9ef74639`…`0ab837b9`). O jogo é o mesmo; só o piloto mudou.
- Guarda as duas coletas, pelo mesmo coletor: o "antes" (`fb321d4e`) e o
  "depois" (`0ab837b9`).
- Nos campos que a `fb321d4e` já tinha, o "antes" reproduz as 300 runs dela
  registro a registro. Por isso a comparação mede só a mudança do instrumento.
- Separa o que era política do bot do que sobrou para a dungeon.

**Auditoria da dungeon.** É a mesma régua depois do bloco Dungeon / Run
Progression (`dfa1ebcc`…`4d0a9a0a`). O bot é o mesmo; só o jogo mudou.
- Guarda as duas coletas, pelo mesmo coletor: o "antes" (`0ab837b9`) e o
  "depois" (`4d0a9a0a`).
- O coletor ganhou sondas passivas para:
  - poções do loot e da Fonte;
  - Essência por andar;
  - taxa por andar.
- Nos campos que a auditoria do instrumento já tinha, o "antes" reproduz as 300
  runs dela registro a registro.

**Auditoria do primeiro level-up.** É a mesma régua depois da última correção
antes da decisão de release (`d3105edc`). O bot é o mesmo; só o custo do
primeiro level-up mudou.
- Guarda as duas coletas, pelo mesmo coletor: o "antes" (`4d0a9a0a`) e o
  "depois" (`d3105edc`).
- O "antes" é cópia byte a byte do `depois.jsonl` da auditoria da dungeon.
- O agregador ganhou o nível ao entrar em cada andar.

**B0 da fundação PvE.** É a mesma régua rodada na ponta da `master`
(`97965ae`), antes de qualquer correção da `phase/game-core`.
- Usa o coletor da `d3105edc` sem cópia e sem edição.
- Nenhum arquivo de jogo ou do bot muda entre os dois commits. Por isso o
  critério é igualdade campo a campo, e as 300 runs saem idênticas.
- Os números são os da `d3105edc`. O que a B0 acrescenta é a garantia de que o
  ponto de partida da `phase/game-core` é aquele retrato, medido de novo.

**Alvo de extração.** É o poder de referência contra o qual o BotPadrão decide
se a build "superou a Arena" e vale extrair.
- Não é baseline de balance, e não é a Arena como modo de jogo.
- Um teste falha se o número se deslocar.

---

## Quando comparar

- **A B0 (`97965ae`) é a referência atual para qualquer mudança de progressão
  na `phase/game-core`.** Ela é idêntica à `d3105edc`, que continua valendo para
  quem compara contra a `master`.
  - Uma mudança se compara rodando o mesmo protocolo no commit novo e agregando
    com o mesmo script: `run_auditoria.py` e `agrega_auditoria.py` do diretório
    da `d3105edc`, com o `b0.jsonl` como o "antes".
  - Uma mudança que consuma sorteio a mais desloca as runs seguintes. Antes de
    ler um delta run a run, veja o experimento de pareamento em
    [`reports/etapa0_fundacao_pve/README.md`](reports/etapa0_fundacao_pve/README.md).
  - A `0ab837b9` mede o jogo de antes do bloco da dungeon. Ela só se compara com
    a `4d0a9a0a`, e isso já está feito.
  - A `4d0a9a0a` mede o jogo de antes do primeiro level-up. Ela só se compara
    com a `d3105edc`, e isso já está feito.
  - Mudou o protocolo (seeds, teto, perfil ou versão do bot)? Então é outra
    baseline, e não uma comparação.
- **A `fb321d4e` não se compara com uma mudança de dungeon.** Ela foi medida com
  o instrumento antigo. Comparar contra ela misturaria a correção do bot com a
  mudança do jogo. Ela continua sendo o registro do "antes" do instrumento.
- **A largada nua antiga não é mais baseline oficial de progressão.**
  - Desde o `fb321d4e`, toda nova jornada começa com uma peça de Starter Kit.
  - O `loadout="naked"` do `src/sim/harness` continua existindo como opção de
    ferramenta, mas não representa a jornada real.
- **O `expected loadout` não representa a largada da dungeon.** Ele só serve para
  comparar classes, nunca para medir progressão real. A progressão real não serve
  para fechar ou reabrir balance de classe sem isolar a causa (ver
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#duas-réguas-de-balanceamento)).
- **A Pre-balance não se compara com a `fb321d4e` nem com a auditoria número a
  número.** É outro
  jogo: antes da reforma, sem Starter Kit, com outra janela, outras seeds e outra
  versão do bot. Dá para usar a direção das tendências como contexto, não como
  delta.
- **O alvo de extração se move por decisão, nunca por arrasto.** Se ele for
  remedido, a decisão de extrair do bot muda junto, e as medições de progressão
  de antes e de depois deixam de ser comparáveis sem remedir a baseline.
