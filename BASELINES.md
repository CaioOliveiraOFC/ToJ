# Baselines

Índice das réguas e medições de referência do projeto. Cada linha aponta para a
fonte que guarda o protocolo e os números completos; este arquivo só diz **o
que cada uma mede e quando ela pode ser comparada**.

| Baseline | Commit | Régua | Estado | Fonte |
|---|---|---|---|---|
| Pre-balance | `88190c5f` | BotPadrão da época, largada nua (`create_player_from_data`), `max_andar` 20, seeds 20260000–20260999, 3.000 runs | **histórica** | [`reports/BASELINE_PRE_BALANCE.md`](reports/BASELINE_PRE_BALANCE.md) |
| Combat/Class E8 | `bc815fcd` | `expected loadout` (`simulate_run`, política `smart`) | **fechada** | `tests/balance/` (`pytest -m balance`) e [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md#etapa-8--class-balance) |
| Progression real | `fb321d4e` | jornada real: BotPadrão conservador + Starter Kit, seeds 1–100 × 3 classes, teto técnico 200 | **pendente de calibração** — referência atual | [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md) |
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

**Alvo de extração.** É o poder de referência contra o qual o BotPadrão decide
se a build "superou a Arena" e vale extrair.
- Não é baseline de balance, e não é a Arena como modo de jogo.
- Um teste falha se o número se deslocar.

---

## Quando comparar

- **A `fb321d4e` é a referência atual para qualquer mudança de progressão.**
  - Uma mudança se compara rodando o mesmo protocolo no commit novo e agregando
    com o mesmo script: `run_baseline.py` e `agrega.py` do diretório dela.
  - Mudou o protocolo (seeds, teto, perfil ou versão do bot)? Então é outra
    baseline, e não uma comparação.
- **A largada nua antiga não é mais baseline oficial de progressão.**
  - Desde o `fb321d4e`, toda nova jornada começa com uma peça de Starter Kit.
  - O `loadout="naked"` do `src/sim/harness` continua existindo como opção de
    ferramenta, mas não representa a jornada real.
- **O `expected loadout` não representa a largada da dungeon.** Ele só serve para
  comparar classes, nunca para medir progressão real. A progressão real não serve
  para fechar ou reabrir balance de classe sem isolar a causa (ver
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#duas-réguas-de-balanceamento)).
- **A Pre-balance não se compara com a `fb321d4e` número a número.** É outro
  jogo: antes da reforma, sem Starter Kit, com outra janela, outras seeds e outra
  versão do bot. Dá para usar a direção das tendências como contexto, não como
  delta.
- **O alvo de extração se move por decisão, nunca por arrasto.** Se ele for
  remedido, a decisão de extrair do bot muda junto, e as medições de progressão
  de antes e de depois deixam de ser comparáveis sem remedir a baseline.
