# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual

**ID:** TASK-003
**Data:** 03/05/2026
**Status:** 🟡 Em progresso
**Depende de:** TASK-002 concluída

---

## Objetivo

Corrigir bugs críticos na UI e navegação do jogo.

---

## Bugs a corrigir

### 1. Bug da loja - markup não renderizado
- **Arquivo:** `src/ui/screens.py` linha 254
- **Problema:** `Text(...)` não processa markup Rich
- **Solução:** Mudar para `Text.from_markup(...)`

### 2. Bug em toj_menu.py - markup não renderizado
- **Arquivos:** `src/ui/toj_menu.py` linhas 59 e 120
- **Problema:** Mesmo que acima
- **Solução:** Mudar para `Text.from_markup(...)`

### 3. STATUS não mostra bônus de stats corretamente
- **Arquivo:** `src/ui/navigation_menu.py`
- **Problema:** Não subtrai o valor do item atualmente equipado no mesmo slot
- **Solução:** `bonus = novo_item.damage_bonus - item_equipado.damage_bonus`

### 4. Q como tecla para sair (substitui ESC)
- **Arquivos:** Todos os menus em `src/ui/`
- **Problema:** ESC usado como sair, mas Q é a regra do jogo
- **Solução:** Substituir `key.lower() == "esc"` por `key.lower() == "q"`

### 5. Loja com terceiro quadro de melhoria de stats
- **Arquivo:** `src/ui/navigation_menu.py` - `navigate_shop_buy`
- **Problema:** Só tem 2 painéis (lista + detalhes), sem mostrar melhoria de stats
- **Solução:** Adicionar 3º painel estilo inventário (player status com bônus do item)

### 6. Mapa sem cores
- **Arquivo:** `src/ui/screens.py` - `render_map()`
- **Problema:** Renderiza apenas texto puro sem cores
- **Solução:** Colorir cada caractere baseado no tipo (@, &, B, X, D)

---

## Arquivos que serão tocados

| Arquivo | Ação | O que muda |
|---|---|---|
| `src/ui/screens.py` | Modificar | render_map() com cores, render_shop_purchase_success() |
| `src/ui/toj_menu.py` | Modificar | Linhas 59, 88, 120 - Text() → Text.from_markup() |
| `src/ui/navigation_menu.py` | Modificar | build_player_status(), navegar menus (Q), loja (3 painéis) |
| `src/ui/shop_flow.py` | Modificar | Substituir ESC por Q |

---

## Critérios de Aceite

- [ ] screens.py - render_map() exibe cores corretas para cada elemento
- [ ] screens.py - render_shop_purchase_success() exibe cores corretamente
- [ ] toj_menu.py - todas as mensagens com markup são renderizadas corretamente
- [ ] navigation_menu.py - STATUS mostra (+X) quando item selecionado
- [ ] navigation_menu.py - navegação usa Q para sair, não ESC
- [ ] navigation_menu.py - navigate_shop_buy() tem 3 painéis como inventário
- [ ] shop_flow.py - usa Q para sair da loja
- [ ] ruff check src/ passa sem erros novos

---

# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Anterior (TASK-002)

**ID:** TASK-002
**Data:** 02/05/2026
**Status:** ✅ Concluída
**Depende de:** TASK-001 concluída (Multiplicador de Essência implementado)

---

**EM MANUTENÇÃO** — Tarefas seguintes (TASK-003+) suspensas por prioridade urgente. Retomar quando instruído.

---

## Objetivo (TASK-002)

Implementar o **Sistema de Cartas de Passivas de Nível** — o coração da diferenciação de builds no TOJ. Ao subir de nível, o jogador escolhe **1 entre 3 passivas permanentes** exibidas em formato de cartas. Passivas se acumulam sem limite e persistem na run inteira (e na Arena, no futuro).

---

## Contexto do Game Design (TASK-002)

Do `GAME_DESIGN.md`:

> "Ao acumular Essência suficiente: Stats base aumentam automaticamente, pontos de atributo são concedidos, e o jogador escolhe **1 entre 3 Passivas Permanentes** exibidas em formato de cartas."

> **Taxonomia de Passivas:**
> - **[Stats]:** Ex: "+15 HP", "+10 MP".
> - **[Recursos]:** Ex: "+20% ouro dropado", "Poções curam +15%".
> - **[Combate]:** Ex: "10% chance de atordoar", "+5% esquiva".

> **Regras:** Raridades (Comum, Raro, Épico, Lendário). Acúmulo permitido sem limite.

---

## Grafo de Dependências (leia antes de tocar em qualquer arquivo)

```
shared/          → sem dependências
entities/        → shared/
mechanics/       → entities/, shared/
content/         → entities/, mechanics/, shared/   ← PassiveCard mora aqui
storage/         → content/, entities/, shared/
engine/          → content/, mechanics/, entities/, storage/, shared/
ui/              → content/, shared/  (NUNCA engine/ ou mechanics/ diretamente)
```

**Regra crítica desta task:** `mechanics/combat.py` **não importa** `PassiveCard`. Recebe bônus já calculados como parâmetros. `content/passives.py` é a única fonte da verdade sobre passivas.

---

## Arquivos que serão tocados (TASK-002)

| Arquivo | Ação | O que muda |
|---|---|---|
| `src/data/passives.json` | **CRIAR** | Catálogo de passivas em JSON |
| `src/content/passives.py` | **CRIAR** | `PassiveCard` + loader + gerador de escolhas |
| `src/ui/passive_flow.py` | **CRIAR** | Fluxo de interação de seleção de cartas |
| `src/shared/constants.py` | Modificar | Pesos de raridade de passivas |
| `src/entities/heroes.py` | Modificar | `self.passives`, `add_passive()`, `_apply_passive_stats()` |
| `src/engine/loop.py` | Modificar | Integrar escolha de passivas após render de pós-batalha |
| `src/mechanics/combat.py` | Modificar | Consultar bônus de passivas via helpers sem importar PassiveCard |
| `src/storage/save_manager.py` | Modificar | Salvar/carregar passivas por ID |
| `src/ui/screens.py` | Modificar | `render_passive_selection()` |

**Arquivos que NÃO devem ser tocados:**
- `src/entities/base.py`
- `src/engine/map.py`
- `src/ui/renderer.py`
- `src/content/items.py`, `src/content/armor.py`, `src/content/skills.py`
- `src/content/factories/` (nenhum arquivo)

---

## Especificação Técnica (TASK-002)

### 1. `src/data/passives.json`

```json
{
  "description": "Catálogo de passivas permanentes para escolhas de nível",
  "version": "1.0",
  "rarity_weights": {
    "Common": 60,
    "Rare": 28,
    "Epic": 10,
    "Legendary": 2
  },
  "passives": [
    {
      "id": "coracao_ferro",
      "name": "Coração de Ferro",
      "category": "Stats",
      "rarity": "Common",
      "description": "+15 HP máximo",
      "effect_type": "max_hp",
      "effect_value": 15
    }
  ]
}
```

Criar com as seguintes passivas (mínimo 5 por raridade, cobrindo todos os `effect_type`):

| ID | Nome | Categoria | Raridade | effect_type | effect_value |
|---|---|---|---|---|---|
| `coracao_ferro` | Coração de Ferro | Stats | Common | `max_hp` | 15 |
| `mente_serena` | Mente Serena | Stats | Common | `max_mp` | 10 |
| `musculos_aco` | Músculos de Aço | Stats | Common | `strength` | 3 |
| `pele_grossa` | Pele Grossa | Stats | Common | `defense` | 3 |
| `passos_leves` | Passos Leves | Stats | Common | `agility` | 2 |
| `sorte_iniciante` | Sorte de Principiante | Recursos | Common | `essence_bonus` | 10 |
| `olho_aguia` | Olho de Águia | Combate | Common | `crit_chance` | 5 |
| `sangue_guerreiro` | Sangue de Guerreiro | Stats | Common | `max_hp` | 25 |
| `reserva_arcana` | Reserva Arcana | Stats | Common | `max_mp` | 20 |
| `essencia_fluida` | Essência Fluída | Stats | Rare | `max_hp` | 40 |
| `furia_berserker` | Fúria Berserker | Stats | Rare | `strength` | 8 |
| `maos_midas` | Mãos de Midas | Recursos | Rare | `gold_drop_bonus` | 20 |
| `bebida_deuses` | Bebida dos Deuses | Recursos | Rare | `potion_heal_bonus` | 15 |
| `reflexos_rapidos` | Reflexos Rápidos | Combate | Rare | `dodge_chance` | 8 |
| `escudo_fé` | Escudo da Fé | Combate | Rare | `damage_reduction` | 5 |
| `essencia_viva` | Essência Viva | Recursos | Rare | `essence_bonus` | 20 |
| `lamina_afiada` | Lâmina Afiada | Combate | Rare | `crit_chance` | 10 |
| `bencao_divina` | Bênção Divina | Stats | Epic | `max_hp` | 70 |
| `toque_dragao` | Toque do Dragão | Stats | Epic | `strength` | 15 |
| `fome_batalha` | Fome de Batalha | Recursos | Epic | `essence_bonus` | 35 |
| `punho_atordoante` | Punho Atordoante | Combate | Epic | `stun_chance` | 12 |
| `sede_sangue` | Sede de Sangue | Combate | Epic | `crit_chance` | 18 |
| `pele_adamantio` | Pele de Adamântio | Combate | Epic | `damage_reduction` | 15 |
| `alma_eterna` | Alma Eterna | Stats | Epic | `max_hp` | 100 |
| `lamina_lendaria` | Lâmina Lendária | Combate | Legendary | `crit_chance` | 30 |
| `imortalidade` | Imortalidade Momentânea | Combate | Legendary | `death_ignore` | 1 |
| `essencia_pura` | Essência Pura | Recursos | Legendary | `essence_bonus` | 60 |
| `fortuna_absoluta` | Fortuna Absoluta | Recursos | Legendary | `gold_drop_bonus` | 50 |
| `coracao_tita` | Coração de Titã | Stats | Legendary | `max_hp` | 200 |

---

### 2. `src/content/passives.py`

Este arquivo concentra: classe de dados, loader do JSON, e gerador de escolhas aleatórias. **Não há lógica de passivas em nenhum outro arquivo além deste.**

```python
"""Passivas permanentes de nível — loader, modelo e gerador de escolhas."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from src.data.loader import _load_json  # reusar o utilitário existente
from src.shared.constants import (
    PASSIVE_COMMON_WEIGHT,
    PASSIVE_EPIC_WEIGHT,
    PASSIVE_LEGENDARY_WEIGHT,
    PASSIVE_RARE_WEIGHT,
)


@dataclass(frozen=True)
class PassiveCard:
    """Carta de passiva permanente carregada do JSON."""

    id: str
    name: str
    category: str
    rarity: str
    description: str
    effect_type: str
    effect_value: float


_PASSIVE_REGISTRY: dict[str, PassiveCard] | None = None


def _get_registry() -> dict[str, PassiveCard]:
    """Carrega e cacheia o registro de passivas. Chave: id."""
    global _PASSIVE_REGISTRY
    if _PASSIVE_REGISTRY is None:
        data = _load_json("passives.json")
        _PASSIVE_REGISTRY = {
            p["id"]: PassiveCard(**{k: p[k] for k in PassiveCard.__dataclass_fields__})
            for p in data["passives"]
        }
    return _PASSIVE_REGISTRY


def load_passives() -> list[PassiveCard]:
    """Retorna lista de todas as passivas disponíveis."""
    return list(_get_registry().values())


def get_passive_by_id(passive_id: str) -> PassiveCard | None:
    """Busca passiva pelo ID. Retorna None se não encontrada."""
    return _get_registry().get(passive_id)


def generate_passive_choices(count: int = 3) -> list[PassiveCard]:
    """Gera N cartas únicas com distribuição ponderada por raridade.

    Args:
        count: Número de cartas a gerar (padrão: 3).

    Returns:
        Lista de PassiveCard únicas para o jogador escolher.
    """
    all_passives = load_passives()
    weights_map = {
        "Common": PASSIVE_COMMON_WEIGHT,
        "Rare": PASSIVE_RARE_WEIGHT,
        "Epic": PASSIVE_EPIC_WEIGHT,
        "Legendary": PASSIVE_LEGENDARY_WEIGHT,
    }
    weights = [weights_map.get(p.rarity, 1) for p in all_passives]

    chosen: list[PassiveCard] = []
    pool = list(all_passives)
    pool_weights = list(weights)

    while len(chosen) < count and pool:
        [pick] = random.choices(pool, weights=pool_weights, k=1)
        idx = pool.index(pick)
        chosen.append(pick)
        pool.pop(idx)
        pool_weights.pop(idx)

    return chosen
```

---

### 3. `src/shared/constants.py` — Adicionar ao final

```python
# Pesos de raridade para sorteio de passivas
PASSIVE_COMMON_WEIGHT = 60
PASSIVE_RARE_WEIGHT = 28
PASSIVE_EPIC_WEIGHT = 10
PASSIVE_LEGENDARY_WEIGHT = 2
```

---

### 4. `src/entities/heroes.py` — Modificações em `Player`

**Adicionar ao `__init__`:**
```python
self.passives: list = []  # list[PassiveCard] — tipagem via TYPE_CHECKING
```

**Adicionar métodos:**
```python
def add_passive(self, passive: object) -> str:
    """Adiciona passiva e aplica efeitos de Stats imediatamente.

    Efeitos de Stats (max_hp, max_mp, strength, defense, agility) são
    aplicados sobre os atributos base. HP e MP atuais NÃO são alterados —
    o jogador não cura ao escolher uma passiva.

    Returns:
        Mensagem de confirmação para exibição pela UI.
    """
    self.passives.append(passive)
    self._apply_passive_stats(passive)
    return f"Passiva adquirida: {getattr(passive, 'name', '?')}!"

def _apply_passive_stats(self, passive: object) -> None:
    """Aplica efeitos imediatos de passivas do tipo Stats.

    NUNCA chama self.rest(). HP/MP atuais ficam intocados.
    """
    effect_type = getattr(passive, "effect_type", None)
    value = int(getattr(passive, "effect_value", 0))

    if effect_type == "max_hp":
        self.base_hp += value
    elif effect_type == "max_mp":
        self.base_mp += value
    elif effect_type == "strength":
        self.base_st += value
        self.avg_damage = (self.base_st + self.base_mg) // 3
    elif effect_type == "defense":
        self.base_df += value
    elif effect_type == "agility":
        self.base_ag = min(self.base_ag + value, 95)

def get_passive_bonus(self, effect_type: str) -> float:
    """Soma o bônus total de todas as passivas para um effect_type.

    Usado por engine/ e combat helpers — evita que mechanics/ importe PassiveCard.

    Args:
        effect_type: Tipo de efeito (ex: 'crit_chance', 'gold_drop_bonus').

    Returns:
        Soma de effect_value de todas as passivas com o tipo solicitado.
    """
    return sum(
        float(getattr(p, "effect_value", 0))
        for p in self.passives
        if getattr(p, "effect_type", None) == effect_type
    )
```

---

### 5. `src/mechanics/combat.py` — Integrar bônus sem importar PassiveCard

`combat.py` **não importa nada de `content/`**. Usa `get_passive_bonus()` do próprio `Player`.

Modificar `resolve_physical_attack()`:

```python
# Antes (crit_chance fixo):
crit_chance = 25 if rogue_sneak_attack else 10

# Depois (+ bônus de passivas via método do Player):
base_crit = 25 if rogue_sneak_attack else 10
passive_crit_bonus = int(attacker.get_passive_bonus("crit_chance")) \
    if hasattr(attacker, "get_passive_bonus") else 0
crit_chance = base_crit + passive_crit_bonus
```

Modificar chance de acerto (dodge):

```python
# Adicionar bônus de esquiva do defensor:
passive_dodge_bonus = int(defender.get_passive_bonus("dodge_chance")) \
    if hasattr(defender, "get_passive_bonus") else 0
hit_chance = 85 + (attacker.get_ag() - defender.get_ag()) - passive_dodge_bonus
```

`damage_reduction` e `stun_chance` ficam para TASK-005 (cooldowns e mecânicas avançadas de combate). **Não implementar agora.**

---

### 6. `src/ui/passive_flow.py` — Seguir padrão de `inventory_flow.py`

```python
"""Fluxo de interação de seleção de passivas (orquestração UI → player)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.content.passives import PassiveCard
    from src.entities.heroes import Player


def run_passive_selection_flow(player: "Player", choices: list["PassiveCard"]) -> None:
    """Exibe 3 cartas de passivas e aplica a escolha do jogador.

    Segue o padrão de inventory_flow.py:
    - A UI renderiza, o fluxo orquestra, a entidade aplica.
    - Não retorna nada; muta o estado do player via player.add_passive().
    """
    while True:
        screens.render_passive_selection(choices)
        choice = safe_get_key(valid_keys=["1", "2", "3"])
        if choice and choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(choices):
                msg = player.add_passive(choices[index])
                screens.render_passive_acquired(msg)
                return
```

---

### 7. `src/ui/screens.py` — Novas funções de renderização

```python
def render_passive_selection(choices: list) -> None:
    """Renderiza as 3 cartas de passivas para escolha."""
    RARITY_COLORS = {
        "Common": "white",
        "Rare": "blue",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("✨ Escolha uma Passiva Permanente ✨", justify="center", style="bold cyan"),
            border_style="cyan",
        )
    )
    for i, card in enumerate(choices, 1):
        color = RARITY_COLORS.get(getattr(card, "rarity", "Common"), "white")
        category = getattr(card, "category", "")
        rarity = getattr(card, "rarity", "")
        name = getattr(card, "name", "?")
        description = getattr(card, "description", "")
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"[bold {color}]{name}[/bold {color}]\n"
                    f"[dim]{description}[/dim]"
                ),
                title=f"[bold]{i}. [{rarity}] [{category}][/bold]",
                border_style=color,
            )
        )


def render_passive_acquired(message: str) -> None:
    """Renderiza confirmação de passiva adquirida."""
    from time import sleep
    renderer.console.print(
        Panel(Text(message, justify="center", style="bold green"), border_style="green")
    )
    sleep(1.5)
```

---

### 8. `src/engine/loop.py` — Sequência correta pós-batalha

**A seleção de passiva acontece APÓS o render de pós-batalha, não dentro dele.**

```python
# Importar no topo do arquivo:
from src.content.passives import generate_passive_choices
from src.ui.passive_flow import run_passive_selection_flow

# Em run_fight(), substituir o bloco final por:

# 1. Processar lógica (engine)
xp_gained, player_won, dropped_item, level_up_msgs, levels_gained = process_post_battle(
    player, monster, essence_multiplier
)

# 2. Renderizar resultado (UI)
screens.render_post_battle(
    player_name=player.get_nick_name(),
    monster_name=monster.get_nick_name(),
    xp_gained=xp_gained,
    player_won=player_won,
    dropped_item_name=getattr(dropped_item, "name", None) if dropped_item else None,
    level_up_messages=level_up_msgs,
)

# 3. Uma carta por nível ganho (após o render, não dentro dele)
if player_won and levels_gained > 0:
    for _ in range(levels_gained):
        choices = generate_passive_choices(count=3)
        run_passive_selection_flow(player, choices)
```

**`process_post_battle()` precisa retornar `levels_gained: int`:**

```python
def process_post_battle(
    player: "Player",
    monster: "Monster",
    essence_multiplier: float = 1.0,
) -> tuple[int, bool, object | None, list[str], int]:
    """
    Retorna: (xp_gained, player_won, dropped_item, level_up_messages, levels_gained)
    """
    level_before = player.get_level()
    # ... lógica existente ...
    level_up_messages = player.level_up(show=True)
    levels_gained = player.get_level() - level_before
    # ...
    return xp_gained, player_won, dropped_item, level_up_messages, levels_gained
```

---

### 9. `src/storage/save_manager.py`

**Save:**
```python
# Adicionar ao save_data:
save_data["passives"] = [
    getattr(p, "id", "") for p in player.passives
]
```

**Load (após definir nível do jogador):**
```python
from src.content.passives import get_passive_by_id

passive_ids = save_data.get("passives", [])
for pid in passive_ids:
    passive = get_passive_by_id(pid)
    if passive:
        player.passives.append(passive)
        player._apply_passive_stats(passive)  # Reaplicar stats — SEM rest()
```

---

## Decisões Confirmadas (TASK-002)

1. **Passivas são globais** — todas as classes podem receber qualquer passiva
2. **Passivas em JSON** — permite geração externa, não hardcoded em Python
3. **Identificador por `id`** — não por nome, para robustez no save/load
4. **Sem limite de acúmulo** — mesma passiva pode ser escolhida múltiplas vezes
5. **Stats aplicam imediatamente, sem `rest()`** — HP/MP atuais ficam intocados
6. **`mechanics/combat.py` não importa `PassiveCard`** — usa `player.get_passive_bonus()`
7. **Seleção de passiva é etapa após `render_post_battle()`** — nunca dentro dele
8. **`damage_reduction` e `stun_chance` não são integrados agora** — ficam para TASK-005
9. **O auto-test (bot) já lida com `["1","2","3"]`** — sempre escolhe carta 1, sem crash

---

## Critérios de Aceite (TASK-002)

- [x] `passives.json` criado com mínimo 28 passivas (todas as 4 raridades cobertas)
- [x] `generate_passive_choices()` está em `src/content/passives.py`, não em `math_operations.py`
- [x] Ao subir de nível, 3 cartas são exibidas **após** a tela de pós-batalha
- [x] Um nível = uma seleção de carta (dois níveis de uma vez = duasSeleções sequenciais)
- [x] Passivas de Stats alteram `base_hp`/`base_mp`/etc. sem chamar `rest()`
- [x] `combat.py` não contém nenhum import de `content/passives`
- [x] Passivas salvas como lista de IDs no `savegame.json`
- [x] Passivas carregadas e reaplicadas corretamente ao carregar save
- [x] `render_passive_selection()` exibe cor diferente por raridade
- [x] `ruff check src/` passa sem erros novos
- [ ] Auto-test conclui run sem crash (sempre escolhe carta 1)

---

## O Que NÃO Fazer Nesta Sessão

- ❌ Não integrar `damage_reduction` e `stun_chance` em `combat.py` (TASK-005)
- ❌ Não criar passivas exclusivas de classe
- ❌ Não implementar reroll de cartas ou reset de passivas
- ❌ Não modificar `src/entities/base.py`
- ❌ Não alterar lógica de spawn de monstros
- ❌ Não introduzir dependências pip novas
- ❌ Não implementar Arena, permadeath ou slots de personagem (TASK-003)
- ❌ Não chamar `self.rest()` dentro de `_apply_passive_stats()`

---

## Entrega Esperada

Ao finalizar, o Windsurf deve:
1. Listar todos os arquivos criados e modificados
2. Mostrar as assinaturas de função que mudaram (especialmente `process_post_battle`)
3. Confirmar que `ruff check src/` passou sem erros novos
4. **Aguardar aprovação antes de qualquer passo adicional**

---

## Backlog

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-004 | 10 slots de personagem + permadeath + Troféu de Fracasso | TASK-002 |
| TASK-005 | Eventos aleatórios de andar (Mercador, Altar, Fonte) | TASK-002 |
| TASK-006 | Cooldowns + `damage_reduction` + `stun_chance` em combate | TASK-002 |
| TASK-007 | Opção "Sair da Masmorra" (extração) entre andares | TASK-004 |