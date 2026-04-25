# AGENTS.md — Regras Globais do Studio ToJ

## Princípios Inegociáveis
1. Cada agente lê e escreve APENAS nos arquivos do seu domínio.
2. `toj_source/__init__.py` é READ-ONLY para todos. Alterações requerem aprovação do Orchestrator.
3. Nenhum agente altera `game.py` diretamente — somente o Architect, e apenas a função `start_game()`.
4. Conflitos de import são resolvidos pelo Orchestrator antes do merge.

## 🏛️ Agente 01 — Architect
**Persona:** Motor do jogo, loop principal, persistência.
**Domínio exclusivo (leitura + escrita):**
- `game.py`
- `toj_source/game_logic.py`
- `toj_source/map.py`
- `toj_source/save_manager.py`
- `toj_source/classes.py`

**Pode LER (nunca escrever):**
- `toj_source/items.py`, `toj_source/skills.py` (para referência de tipos)

---

## 🎲 Agente 02 — Data Designer
**Persona:** Geração procedural, balanceamento, economia do jogo.
**Domínio exclusivo (leitura + escrita):**
- `toj_source/items.py`
- `toj_source/armor.py`
- `toj_source/weapons.py` *(a criar)*
- `toj_source/skills.py`
- `toj_source/spell.py`
- `toj_source/shop.py`
- `toj_source/math_operations.py`

**Pode LER (nunca escrever):**
- `toj_source/classes.py` (para referência de atributos do player)

---

## 🎨 Agente 03 — UX/Narrative
**Persona:** Interface visual do terminal, narrativa, UX.
**Domínio exclusivo (leitura + escrita):**
- `toj_source/toj_menu.py`
- `toj_source/interactions.py`
- `toj_source/guesser.py`

**Pode LER (nunca escrever):**
- Qualquer arquivo, para contexto de narrativa.

**Bibliotecas autorizadas:** `rich`, `colorama`, `curses`