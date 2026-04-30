# ROADMAP DE DESENVOLVIMENTO - TALES OF THE JOURNEY

## Regras de Execução de Sprint
- A IA NÃO deve pular Sprints.
- A IA deve executar apenas a Sprint solicitada pelo usuário.
- Ao finalizar a Sprint, a IA deve aguardar o comando explícito do usuário para avançar.
- Ao iniciar qualquer tarefa, a IA deve ler `.windsurfrules` e `ARCHITECTURE.md` antes de tocar em qualquer arquivo.

---

## [SPRINT 0] Saneamento e Contratos (PRÉ-REQUISITO)
**Foco:** `main.py`, `src/shared/`, configuração do projeto
**Objetivo:** Eliminar todas as violações arquiteturais existentes e estabelecer os contratos de tipo antes de qualquer nova feature. A Sprint 1 só pode começar com esta concluída.

### Tarefas:

**0.1 — Limpar o `main.py`**
- Remover TODOS os imports de `rich` do `main.py` (Console, Panel, Text, Table).
- Mover a função `inventory_menu()` integralmente para `src/ui/screens.py`.
- Mover a função `start_game()` integralmente para `src/engine/loop.py`.
- O `main.py` final deve ter no máximo 30 linhas e conter apenas: imports do menu, chamada de `main()` e o bloco `if __name__ == '__main__'`.

**0.2 — Eliminar imports tardios**
- Remover todos os imports declarados dentro de funções (ex: `from src.mechanics... import` dentro de `start_game()`).
- Reorganizar os imports para o topo do arquivo correto, respeitando as regras de camada do `.windsurfrules`.

**0.3 — Criar `src/shared/constants.py`**
- Extrair todos os números mágicos de `engine/loop.py` (ex: `12`, `25`, `0.05`, `0.15`, `0.01`) para constantes nomeadas.
- Exemplos de nomes: `BASE_MAP_HEIGHT`, `BASE_MAP_WIDTH`, `MIN_WALL_PERCENT`, `MAX_WALL_PERCENT`, `WALL_PERCENT_PER_LEVEL`.

**0.4 — Criar `src/shared/types.py`**
- Definir as dataclasses e TypedDicts principais para uso como DTOs entre camadas:
  - `EntityStats` (hp, mp, strength, defense, magic)
  - `CombatResult` (damage_dealt, is_critical, is_dodge, attacker_name, target_name)
  - `MapState` (height, width, grid, player_pos, exit_pos, enemies_pos)
  - `SaveData` (player_class, player_name, level, xp, coins, dungeon_level, map_state)

**0.5 — Adicionar Type Hints**
- Adicionar anotações de tipo em todas as funções públicas de `main.py`, `engine/loop.py` e `ui/screens.py`.
- Usar os tipos de `src/shared/types.py` onde aplicável.

**0.6 — Configurar ferramentas de qualidade**
- Criar `pyproject.toml` na raiz com configuração de:
  - `ruff` (linter + formatter): regras E, W, F, I (isort), N (naming conventions PEP 8)
  - `mypy`: `strict = false`, `ignore_missing_imports = true` (para começar sem dor)
- Rodar `ruff check src/` e corrigir todas as violações reportadas.

---

## [SPRINT 1] O Sistema Nervoso (Event-Driven Integration)
**Foco:** `events.py`, `loop.py`, `screens.py`, `combat.py`
**Objetivo:** Eliminar o acoplamento restante entre o motor e a UI usando Pub/Sub.
**Tarefas:**
1. Ligar os fios do `EventBus` (`events.py`). O combate não retorna textos — ele publica eventos (ex: `EventBus.publish("damage_taken", data)`).
2. A interface (`ui/`) se inscreve (`subscribe`) nesses eventos para saber quando atualizar a tela.
3. `screens.py` deve conter APENAS funções `render_*` — sem lógica de escolha ou fluxo.

---

## [SPRINT 2] O Motor de Conteúdo (Data-Driven Design)
**Foco:** `content/factories/`, `src/data/` (nova pasta)
**Objetivo:** Remover hardcodes (números mágicos e listas de itens) de dentro dos arquivos Python.
**Tarefas:**
1. Criar `src/data/monsters.json` e `src/data/items.json`.
2. Refatorar as fábricas (`monsters.py`, `loot.py`) para lerem os stats básicos a partir desses arquivos JSON. O código Python passa a ser apenas o injetor.

---

## [SPRINT 3] O "Game Feel" (UX Visual)
**Foco:** `ui/renderer.py`, `ui/prompts.py`
**Objetivo:** Trazer peso, ritmo e suspense ao jogo de terminal.
**Tarefas:**
1. Inserir pausas dramáticas (`time.sleep`) nos eventos de combate (entre o ataque e a exibição do dano).
2. Adicionar efeitos visuais do `rich` (textos que mudam de cor baseado na porcentagem de vida).

---

## [SPRINT 4] Expansão de Features
**Foco:** `mechanics/combat.py`, `entities/`
**Objetivo:** Escalar o jogo usando a nova arquitetura limpa.
**Tarefas:**
1. Implementar sistema de "Status Effects" (Veneno, Atordoamento, Sangramento) no combate, controlando a duração por turnos.
2. Iniciar a fundação do modo "Arena".