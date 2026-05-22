# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual

**ID:** TASK-004
**Data:** 04/05/2026
**Status:** 🟡 Em progresso
**Depende de:** TASK-002 concluída, TASK-003 concluída

---

## Objetivo

Implementar **slots de personagem + permadeath + Troféu de Fracasso**.

---

## Contexto do Game Design

Do GAME_DESING.md:
> "Permadeath real: Morte na masmorra = personagem perdido"
> "10 slots de personagem (save/load)"
> "Troféu de Fracasso - registro de personagens que morreram"

---

## Especificação Técnica

### 1. Sistema de Slots de Personagem

Adicionar 10 slots no menu principal:
- Slot 1 a 10
- Cada slot pode ter um personagem salvo ou vazio
- Ao criar novo personagem,可以选择 slot vazio
- Ao carregar,可以选择 slot ocupado

Arquivo de saves: `saves/slot_{1-10}.json`

### 2. Permadeath

- Ao morrer na masmorra, o personagem é **deletado permanentemente**
- Não há opção de continuar com outro personagem na mesma run
- Cada tentativa é uma nova run completa

### 3. Troféu de Fracasso

Registro de personagens que morreram:
- Nome do personagem
- Classe
- Nível reached
- Andar reached
- Data/hora da morte
- Causa da morte

Arquivo: `saves/trophies.json`

### 4. Modificações no Bootstrap

```python
# Arquivos de save por slot
SAVE_DIR = "saves/"
SLOT_FILES = [f"slot_{i}.json" for i in range(1, 11)]
TROPHY_FILE = "trophies.json"

# Menu principal expandido
def main_menu() -> str:
    # Mostrar slots disponíveis
    # Opções: Novo Jogo (escolher slot), Carregar (escolher slot), Troféus, Sair
```

### 5. Modificações no SaveManager

```python
def save_game(player, dungeon_level, map_state, slot: int) -> bool:
    """Salva no slot especificado (1-10)."""
    filepath = f"{SAVE_DIR}slot_{slot}.json"
    # ... salvar

def load_game(slot: int) -> tuple[Player, int, dict] | None:
    """Carrega do slot especificado."""
    filepath = f"{SAVE_DIR}slot_{slot}.json"
    # ... carregar

def add_trophy(player: Player, floor_reached: int, cause: str) -> None:
    """Adiciona entrada ao livro de troféus."""
    # ... adicionar a trophies.json

def get_trophies() -> list[dict]:
    """Retorna lista de troféus."""
    # ... ler trophies.json
```

### 6. Modificações no Game Over

```python
def game_over_screen(player_name):
    # Após mostrar game over, adicionar:
    add_trophy(player, floor_reached, cause)
    # Perguntar se deseja ver troféus
    # Deletar o save do slot
```

---

## Arquivos que serão tocados

| Arquivo | Ação | O que muda |
|---|---|---|
| `src/storage/save_manager.py` | Modificar | save/load por slot, trophyes |
| `src/engine/bootstrap.py` | Modificar | Menu de slots |
| `src/ui/toj_menu.py` | Modificar | Mostrar slots, trophyes |
| `saves/` | Criar diretório | Armazenar saves |

---

## Critérios de Aceite

- [ ] Menu principal mostra 10 slots (vazios/ocupados)
- [ ] Criar novo personagem em slot vazio
- [ ] Carregar personagem de slot ocupado
- [ ] Ao morrer, save do slot é deletado
- [ ] Troféu de Fracasso registra personagens mortos
- [ ] UI mostra lista de troféus

---

## Backlog

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-005 | Eventos aleatórios de andar (Mercador, Altar, Fonte) | TASK-004 |
| TASK-006 | Cooldowns + `damage_reduction` + `stun_chance` em combate | TASK-004 |
| TASK-007 | Opção "Sair da Masmorra" (extração) entre andares | TASK-004 |