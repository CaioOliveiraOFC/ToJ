# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual

**ID:** TASK-006
**Data:** 26/08/2026
**Status:** ✅ Concluída
**Depende de:** TASK-004 concluída

---

## Objetivo

Implementar **cooldown de skills + damage_reduction + stun_chance** em combate, com testes determinísticos e integração via AutoTester.

---

## Contexto

COMBAT_DESIGN.md especifica `stun_chance` e `damage_reduction` como parte do sistema de combate, e o README mencionava cooldowns — nenhum dos três existia no código. Skills só tinham custo de MP.

---

## Especificação Técnica

### Cooldown

- `SkillCard.cooldown: int = 0` (src/content/skills_loader.py) — lido de `src/data/skills.json` (não hardcoded). Cada skill tem `cooldown` por raridade: Common is_initial 1-2, Common 2, Rare 3, Epic 3, Legendary 4-5 (ex: Esmagar 4, Imortal 5).
- `Player.skill_cooldowns: dict[str, int]` — mapeia skill id → turnos restantes. Setado em `apply_skill` após uso bem-sucedido, verificado antes de aplicar (se em cooldown, não consome MP nem aplica efeito, retorna `mp_spent=0`).
- Decremento em `process_turn_start_effects` a cada turno, com evento `cooldown_expired`. UI mostra recarga em `render_skill_select_panel` e bloqueia escolha com `render_skill_on_cooldown_message`. Bot do AutoTester filtra skills em cooldown.

Constantes nomeadas: `DEFAULT_SKILL_COOLDOWN`, `STUN_DURATION`, `STUN_CHANCE_DEFAULT`, `DAMAGE_REDUCTION_DURATION`, `DAMAGE_REDUCTION_DEFAULT_PERCENT` em `src/shared/constants.py`.

### Damage Reduction

- Status temporário `damage_reduction` em `active_effects` com `{"value": percent, "duration": N}`. Aplicado via skill `effect_type == "damage_reduction"` (target self/enemy) ou diretamente.
- Em `resolve_physical_attack`, após calcular dano base, aplica `damage = max(1, int(damage * (1 - pct/100)))` se o defensor tiver o efeito.
- Expira em `process_turn_start_effects` como os demais efeitos.

### Stun

- Status `stun` em `active_effects` com `{"duration": STUN_DURATION}`. Em `process_turn_start_effects`, `stun` (como `frozen`) seta `skipped_turn = True` e publica `stun`.
- Aplicado de duas formas:
  1. Via skill `effect_type == "status"` com `effect_value == "stun"` (chance do JSON).
  2. Via `stun_chance` em skills de dano: `SkillCard.stun_chance` (ex: Esmagar 30, Investida/Golpe Baixo 15). Após hit bem-sucedido em `apply_skill` (damage), rola `randrange(1,101) <= stun_chance` e aplica `stun` no alvo.

### Arquivos tocados

| Arquivo | Ação |
|---|---|
| `src/shared/constants.py` | 5 novas constantes nomeadas |
| `src/content/skills_loader.py` | Campos `cooldown` e `stun_chance` em `SkillCard` + loader tolerante |
| `src/data/skills.json` | `cooldown` e `stun_chance` por skill (41 entradas) |
| `src/entities/heroes.py` | `skill_cooldowns` dict no Player |
| `src/mechanics/combat.py` | Cooldown check/set, damage_reduction no pipeline, stun em `resolve` e `apply_skill`, tick em `process_turn_start_effects` |
| `src/ui/screens.py` | `render_skill_select_panel` mostra recarga + `render_skill_on_cooldown_message` |
| `src/engine/loop.py` | Checagem de cooldown antes de `apply_skill` no turno humano |
| `tests/test_new_systems.py` | Novo: 12 testes determinísticos (seed fixo) para os 3 sistemas |
| `tests/auto_test.py` | Bot respeita cooldowns |
| `src/content/factories/dungeons.py` | Já tinha fountain/altar; não tocado aqui além de coexistir |

---

## Critérios de Aceite

- [x] Cooldown, damage_reduction e stun funcionam ponta a ponta (AutoTester vitória 20/20, 431 lutas, 0 crashes)
- [x] Testes de `combat.py` do PROMPT 2 continuam passando (64 → 64, total 120 com os 12 novos)
- [x] Nenhum número mágico novo sem constante nomeada

---

## Backlog

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-005 | Eventos aleatórios de andar (Mercador, Altar, Fonte) | TASK-004 — ✅ Concluída |
| TASK-006 | Cooldowns + `damage_reduction` + `stun_chance` em combate | TASK-004 — ✅ Concluída |
| TASK-007 | Opção "Sair da Masmorra" (extração) entre andares | TASK-004 — ✅ Concluída |
