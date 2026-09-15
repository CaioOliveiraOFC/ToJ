# ARCHITECTURE — Tales of the Journey

## As regras

1. Raiz do código em `src/`, só imports absolutos.
2. `engine/` fala com `ui/` pelo EventBus (`src/engine/events.py`). As exceções
   estão listadas abaixo.
3. Nenhuma importação cruzada entre camadas. Todas podem importar `shared/`; é
   por lá que uma camada de baixo alcança o que está acima.
4. Apresentação só em `ui/`: nem `print()`, nem `rich` fora dela. É o que mantém
   `sim/` headless.
5. **Fórmula é código, valor é dado.** O nome de um monstro, o custo de uma skill
   ou o multiplicador de um arquétipo vão para o JSON. Números de balanceamento
   que não cabem no JSON ficam em `shared/constants.py`, com nome.
6. `safe_get_key()` é o único ponto de entrada de teclado.

`tests/test_architecture.py` verifica 1, 3, 4 e 5. Regra que só existe em
Markdown é regra que ninguém checa.

## Camadas

```
ui/ ←── engine/ ←── mechanics/ ←── entities/
         ↑        ↑               ↑
        sim/   content/         shared/
                  ↑
               storage/
                  ↑
                data/
```

| camada | responsabilidade | pode importar |
|---|---|---|
| `shared/` | tipos, constantes, fórmulas, tópicos, efeitos | nada |
| `data/` | leitura dos JSON | shared/ |
| `entities/` | estado (Player, Monster) | shared/ |
| `mechanics/` | regras de combate e matemática | entities/, shared/ |
| `content/` | catálogos e fábricas | entities/, mechanics/, shared/, data/ |
| `sim/` | simulação headless para medir balanceamento | content/, mechanics/, entities/, shared/, data/ |
| `storage/` | save/load | content/, entities/, shared/, data/ |
| `engine/` | orquestração | todas |
| `ui/` | apresentação e input | shared/, content/, entities/, storage/, data/ |

Imports sob `TYPE_CHECKING` não contam: não existem em tempo de execução.

## EventBus

`engine/` publica um tópico; `ui/` registrou um handler para ele. Os tópicos
vivem em `src/shared/combat_topics.py`.

```python
bus = EventBus()
register_ui_handlers(bus)                 # ui/ assina
bus.publish(topics.UI_OPEN_SHOP, {...})   # engine/ publica
```

### Exceções à regra 2

`engine/` pode importar direto de `ui/`: as funções `screens.render_*`,
`clear_screen()`, `safe_get_key()`, os dois `register_*_handlers()` e os fluxos de
menu inicial (`toj_menu`), que rodam antes do laço de jogo existir.

`sim/runner.py` pode usar `print()`: é CLI de desenvolvimento, e importar `ui/`
de dentro de `sim/` quebraria a regra maior de a simulação ser headless.

## Responsabilidade por módulo

Os módulos onde a responsabilidade não é óbvia pelo nome da camada:

| módulo | responsabilidade |
|---|---|
| `shared/formulas.py` | a matemática fundamental: crescimento, dano, acerto, mitigação |
| `shared/economy.py` | **aritmética** econômica pura. Recebe a renda como número; nunca a calcula, porque isso exigiria conhecer o catálogo |
| `shared/effects.py` | `fx.combat_modifier(entidade, nome)` — o **funil único** que soma buff + passiva + equipamento. Nada multiplica dano fora dele |
| `shared/effect_core.py` | o catálogo global de efeitos: famílias, empilhamento, duração |
| `shared/interactions.py` | as 16 **leis** sobre pares de efeitos. Sem estado, sem ator, sem fonte |
| `content/economy.py` | a **ponte**: conhece o catálogo e o gerador, e é o único lugar que calcula `expected_floor_income`, `reroll_cost`, `exit_fee`, custos do Ferreiro e teto de juros |
| `content/factories/monsters.py` | **fonte única da população do andar** (`routine_monster_count`, `floor_role_plan`). Mapa e simulador leem daqui — é o que garante que os dois meçam o mesmo andar |
| `content/factories/features.py` | sorteio dos serviços do andar com pity (`roll_features`). Muta os contadores de seca do jogador, que pertencem à run |
| `content/floor_exit.py` | a saída: cobra a taxa (`use_exit`), mantém o `unpaid_exit_streak` e converte o roll em Essência efetiva (`effective_essence`). Não existe dívida |
| `content/forge.py` | o Ferreiro: cobra e delega. `+N`, gemas e encantamentos continuam implementados em `content/items.py` |
| `engine/map.py` | a grade do andar: casas de monstro, evento, serviço e saída, e a serialização delas no save |
| `engine/map_analysis.py` | medição da geometria do andar (Dijkstra por `(combates, passos)`). Ferramenta de auditoria, não regra de jogo |
| `sim/` | simulação headless. Roda o mesmo `mechanics/battle.py`, lê as mesmas fontes de população e de serviços, e nunca importa `engine/` nem `ui/` |

**Fonte única é regra, não estilo.** Renda do andar, população do andar, custo de
reroll, preços do Ferreiro e penalidade de Essência vivem cada um em exatamente
uma função. Copiar a fórmula para o simulador ou para a UI é o defeito que já
produziu um simulador medindo um andar que o jogo não gera.

## Onde está a verdade

| assunto | fonte |
|---|---|
| matemática fundamental | `src/shared/formulas.py` |
| valores de balanceamento | `src/shared/constants.py` e `src/data/*.json` |
| arquitetura | este arquivo |
| design do jogo | `GAME_DESIGN.md` |
| comportamento | a suíte padrão, `python -m pytest -q` |
| balanceamento | `python -m pytest -q -m balance` e `src/sim/` |

Nada além disso deve tentar ser uma segunda fonte de verdade.
