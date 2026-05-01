# Auditoria Arquitetural — Tales of the Journey
> Staff/Principal Engineer Review — Sprint 0–2 Post-Mortem

---

## Resumo Executivo

A refatoração avançou significativamente desde a última auditoria — sete das onze violações críticas anteriores foram resolvidas. `main.py` está exemplar (9 linhas), `entities/heroes.py` foi corretamente limpo de `print()`, `render_post_battle()` agora recebe DTOs em vez de executar lógica de negócio, e o import tardio em `map.py#load_map_state` foi eliminado. O data-driven design da Sprint 2 está sólido. A arquitetura está claramente evoluindo na direção certa.

Porém, quatro problemas sérios permanecem e introduzem regressões funcionais. O mais grave: `auto_test.py` está quebrado — chamadas para `main_mod.start_game()` vão levantar `AttributeError` em runtime pois o símbolo não existe mais no namespace de `main.py`. Adicionalmente, a refatoração de `entities/heroes.py` para retornar mensagens em vez de imprimir foi implementada corretamente, mas nenhum caller captura esses retornos — a mensagem "Você obteve: X!" foi silenciada e o jogador nunca vê o feedback de loot. O débito arquitetural mais estrutural é `ui/toj_menu.py` que viola explicitamente a Regra 2 ao importar de `engine/`.

**Conformidade geral estimada: 72%**

| Categoria | Contagem |
|---|---|
| Críticos (ação imediata) | 4 |
| Avisos (débito técnico) | 5 |
| Resolvidos com sucesso | 7 |

---

## Critical Findings — Ação Imediata

### C1 — `auto_test.py` vai crashar em runtime (Regressão)

`main_mod.start_game(player)` levanta `AttributeError` porque `main.py` não importa mais `start_game`. Também: `patch("main.safe_get_key", ...)` e `patch("src.engine.game_logic.sleep", ...)` patcheiam símbolos inexistentes nesses namespaces — falham silenciosamente. O auto_test está funcionalmente morto.

```python
# ANTES (quebrado — AttributeError em runtime)
main_mod.start_game(player)
patch("main.safe_get_key", side_effect=mocked_safe_get_key),
patch("src.engine.game_logic.sleep", ...),  # game_logic não tem sleep

# DEPOIS — importar e patchear no lugar certo
from src.engine.loop import start_game
...
start_game(player)

# patches corretos:
patch("src.engine.loop.safe_get_key", side_effect=mocked_safe_get_key),
patch("src.engine.bootstrap.sleep", side_effect=mocked_sleep, create=True),
# remover: patch("src.engine.game_logic.sleep", ...)
```

---

### C2 — `ui/toj_menu.py` importa de `engine/` (Regra 2 violada)

`from src.engine.game_logic import create_player_from_data` — a regra é inequívoca: **"ui/ NUNCA importa de engine/ ou mechanics/"**. Este import cria dependência circular latente e acopla a camada de apresentação à lógica de domínio.

```python
# ANTES (ui/ importando engine/ — Regra 2 violada)
# src/ui/toj_menu.py
from src.engine.game_logic import create_player_from_data

def character_creation_flow():
    ...
    return create_player_from_data(class_key, player_name)


# DEPOIS — toj_menu.py retorna dados brutos, engine cria a entidade
# src/ui/toj_menu.py
def character_creation_flow() -> tuple[str, str] | None:
    """Coleta classe e nome via UI. Retorna (class_key, name) ou None."""
    ...
    return class_key, player_name  # dados brutos, sem criar entidade

# src/engine/bootstrap.py — a engine faz a criação
from src.engine.game_logic import create_player_from_data
from src.ui.toj_menu import character_creation_flow

def run_main_loop() -> None:
    ...
    if menu_choice == "new_game":
        result = character_creation_flow()
        if result:
            class_key, player_name = result
            player = create_player_from_data(class_key, player_name)
            if player:
                start_game(player, 1)
```

---

### C3 — `engine/loop.py` mutação direta de atributos privados (Regra 4 violada)

No bloco de criação de mini-boss: `boss._hp = boss.base_hp`, `boss._st = ...`, `boss._df = ...`, `boss._mg = ...`. A Regra 4 é explícita: **"PROIBIDO: mutações diretas como `entity._hp = x` fora da pasta `entities/`"**. O `Monster.__init__` aceita parâmetros `hp, st, df, mg` via kwargs — a factory deveria ser usada corretamente.

```python
# ANTES (Regra 4 — mutação de atributos privados fora de entities/)
# src/engine/loop.py
boss = create_monster(f"Chefe Nv.{boss_level}", boss_level)
boss.is_boss = True
boss.base_hp = calculate_mini_boss_hp(dungeon_level)
boss._hp = boss.base_hp      # PROIBIDO
boss.base_st = calculate_mini_boss_strength(dungeon_level)
boss._st = boss.base_st      # PROIBIDO
boss.base_df = calculate_mini_boss_defense(dungeon_level)
boss._df = boss.base_df      # PROIBIDO
boss.base_mg = calculate_mini_boss_magic(dungeon_level)
boss._mg = boss.base_mg      # PROIBIDO
boss.avg_damage = (boss._st + boss._mg) // 3


# DEPOIS — Monster.__init__ já aceita kwargs hp, st, df, mg
# src/content/factories/monsters.py — adicionar factory específica
def create_boss_for_level(dungeon_level: int) -> Monster:
    """Cria mini-boss com stats escalados para o nível de masmorra."""
    boss_level = dungeon_level + 2
    boss = Monster(
        nick_name=f"Chefe Nv.{boss_level}",
        mob_level=boss_level,
        hp=calculate_mini_boss_hp(dungeon_level),
        st=calculate_mini_boss_strength(dungeon_level),
        df=calculate_mini_boss_defense(dungeon_level),
        mg=calculate_mini_boss_magic(dungeon_level),
    )
    boss.is_boss = True  # atributo público, ok fora de entities/
    return boss

# src/engine/loop.py
from src.content.factories.monsters import create_boss_for_level
...
if dungeon_level % 5 == 0:
    boss = create_boss_for_level(dungeon_level)
    monsters_to_place.append(boss)
```

---

### C4 — Retornos de `entities/heroes.py` são universalmente descartados (Loot silenciado)

A refatoração que tornou `add_item_to_inventory()`, `equip()`, `unequip()`, `use_potion()` retornarem strings foi correta, mas nenhum caller captura esses retornos. Em `engine/loop.py#process_post_battle`: `player.add_item_to_inventory(dropped_item)` — a mensagem "Você obteve: X!" é silenciada. Em `ui/inventory_flow.py`: `player.use_potion(item)`, `player.equip(item)`, `player.unequip(slot)` — todos descartam o retorno. O jogador literalmente não vê feedback de ações de inventário.

```python
# ANTES — ui/inventory_flow.py (mensagens dropadas silenciosamente)
player.use_potion(item)
screens.render_inventory_item_used(item.name)

player.equip(item)
screens.render_inventory_item_equipped(item.name)

player.unequip(slot)
screens.render_inventory_item_unequipped(item.name)


# DEPOIS — capturar e passar a mensagem real da entity
msg = player.use_potion(item)
screens.render_inventory_item_used(msg or item.name)

msg = player.equip(item)
screens.render_inventory_item_equipped(msg or item.name)

msg = player.unequip(slot)
screens.render_inventory_item_unequipped(msg or item.name)


# ANTES — engine/loop.py (loot silenciado)
dropped_item = get_loot()
if dropped_item:
    player.add_item_to_inventory(dropped_item)
# "Você obteve: X!" some no ar


# DEPOIS — capturar retorno para garantir propagação
dropped_item = get_loot()
if dropped_item:
    player.add_item_to_inventory(dropped_item)
    # dropped_item_name já é passado ao render_post_battle via dropped_item.name
    # garantir que o DTO inclua o nome correto
```

---

## Warnings — Débito Técnico

### W1 — `engine/map.py` aplica lógica ANSI/cores em camada de engine

`draw_map()` evoluiu corretamente para retornar `list[str]` em vez de `print()` — melhoria real. Porém a aplicação de códigos ANSI (`COLORS` dict, `\033[91m`) ainda acontece dentro de `engine/`. A camada de mapa deveria retornar dados semânticos (tipo de tile, tipo de entidade) e a `ui/` aplicaria a coloração. Deixar para Sprint 3 junto com o "Game Feel".

---

### W2 — `engine/ui_events.py` infraestrutura sem subscribers

`emit_log()`, `emit_save_success()`, `emit_save_error()` publicam para tópicos `SYSTEM_LOG_MESSAGE`, `SYSTEM_SAVE_SUCCESS`, `SYSTEM_SAVE_ERROR`. Nenhum arquivo em `ui/` subscreve esses tópicos. Adicionalmente, `save_game()` retorna `dict` de sucesso/erro mas `engine/loop.py` ignora o retorno e sempre exibe "Jogo salvo!" — independente de falha.

---

### W3 — `mechanics/math_operations.py` sem type hints e sem docstrings

Regra 6 direta: "Toda função pública deve ter type hints completos e docstring (padrão PEP 257)." Nenhuma das 13 funções tem anotações de tipo. Adicionalmente, os números mágicos (`base_hp=70`, `scaling_per_level=20` etc.) estão inline — violam a regra de ir para `shared/constants.py`.

```python
# ANTES
def calculate_monster_hp(monster_level):
    base_hp = 70
    scaling_per_level = 20
    return base_hp + (monster_level - 1) * scaling_per_level

# DEPOIS
# shared/constants.py
MONSTER_BASE_HP = 70
MONSTER_HP_SCALING_PER_LEVEL = 20

# mechanics/math_operations.py
from src.shared.constants import MONSTER_BASE_HP, MONSTER_HP_SCALING_PER_LEVEL

def calculate_monster_hp(monster_level: int) -> int:
    """Calcula o HP total de um monstro baseado no seu nível.

    Args:
        monster_level: Nível do monstro (mínimo 1).

    Returns:
        HP total calculado.
    """
    return MONSTER_BASE_HP + (monster_level - 1) * MONSTER_HP_SCALING_PER_LEVEL
```

---

### W4 — `content/shop.py` mutação direta de estado do player

`player.coins -= price` e `player.inventory.append(item_to_buy)` em `buy_item()` violam a Regra 4. `Player` já expõe `add_item_to_inventory()` — use-o. Falta `spend_coins(amount: int) -> bool` em `entities/heroes.py` para encapsular a transação financeira.

---

### W5 — `content/armor.py` e `content/items.py` — `RARITY_MULTIPLIERS` duplicado

O dict `RARITY_MULTIPLIERS` é definido identicamente em dois arquivos. Mover para `shared/constants.py` e importar de lá nos dois lugares. Violação de DRY que pode gerar inconsistência se os valores forem alterados em apenas um lugar.

---

## O que foi resolvido com sucesso

| Arquivo | Resolução |
|---|---|
| `main.py` | 9 linhas, puro bootstrap. Exatamente o contrato da Sprint 0. |
| `ui/screens.py#render_post_battle` | Lógica de XP e loot removida. Recebe DTOs da engine. Sprint 1 principal débito resolvido. |
| `entities/heroes.py` | Zero `print()`. API de retorno de mensagens correta. A camada de estado puro está limpa. |
| `engine/map.py` | Import lazy de `create_monster` eliminado. `draw_map()` retorna `list[str]`, não chama `print()`. |
| `storage/save_manager.py` | Sem `print()`. `save_game()` retorna `dict`. `load_game()` silencioso. |
| `engine/game_logic.py` | Reconstruído como função pura `create_player_from_data()`. Sem `print()`, `input()` ou imports de `ui/`. |
| Sprint 2 — data-driven design | `monsters.json` com 100+ nomes, `items.json` com 55+ itens. Factories como injetores puros. `loader.py` centralizado. |

---

## Checklist de Correção para a Próxima Sessão

Antes de avançar para a Sprint 3, resolver nesta ordem:

- [ ] **C1** — Corrigir `auto_test.py`: substituir `main_mod.start_game()` por import direto de `src.engine.loop`; atualizar patches para os namespaces corretos
- [ ] **C2** — Remover `from src.engine.game_logic import create_player_from_data` de `ui/toj_menu.py`; `character_creation_flow()` deve retornar `tuple[str, str] | None`; criação da entidade fica em `engine/bootstrap.py`
- [ ] **C3** — Criar `create_boss_for_level(dungeon_level)` em `content/factories/monsters.py`; remover as 5 linhas de mutação direta de `_hp/_st/_df/_mg` em `engine/loop.py`
- [ ] **C4** — Capturar retorno de `player.use_potion()`, `player.equip()`, `player.unequip()` em `ui/inventory_flow.py`; verificar propagação de loot em `engine/loop.py#process_post_battle`
- [ ] **W3** — Adicionar type hints e docstrings em todas as funções de `mechanics/math_operations.py`; extrair magic numbers para `shared/constants.py`
