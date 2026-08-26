# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual

**ID:** TASK-005
**Data:** 26/08/2026
**Status:** ✅ Concluída
**Depende de:** TASK-004 concluída

---

## Objetivo

Implementar **eventos aleatórios de masmorra**: Mercador Errante, Altar e Fonte — sistema simples sorteado ao entrar num andar, antes da decisão de extração.

---

## Contexto do Game Design

Do GAME_DESING.md (TASK-005):
> Mercador Errante, Altar de Sacrifício, Fonte de Cura — eventos que quebram a rotina da masmorra com risco/recompensa.

Antes só existiam strings soltas "mercador" na loja normal (screens.py:226,337), sem lógica.

---

## Especificação Técnica

### Probabilidade

`RANDOM_EVENT_CHANCE = 0.25` (25%) em `src/shared/constants.py` — configurável via constante nomeada, não número mágico. Documentada como equilíbrio entre surpresa e previsibilidade. Sorteio via `roll_random_event()` em `src/content/factories/dungeons.py`.

### Tipos implementados

| Tipo | Lógica real |
|---|---|
| **Mercador Errante** | 1-3 itens aleatórios (pool da loja com peso favorecendo Rare/Epic, desconto 10%), compra opcional via ouro |
| **Altar** | Escolha binária: sacrificar 30% da vida máxima por buff `Benção do Altar` (+15 por 5 turnos) ou recusar; morte por sacrifício gera troféu e deleta save |
| **Fonte** | Cura 50% da vida máxima + tenta recuperar 1 poção (`Poção de Cura Pequena`), sem custo |

### Arquitetura

Segue o padrão `UI_OPEN_SHOP`/`UI_EXTRACTION_PROMPT`: `loop.py` publica `UI_RANDOM_EVENT` via `_get_game_publish()` no branch `level_complete` (após `rest()`, antes da loja e extração); `ui_event_handlers._on_random_event` delega para `random_event_flow.run_random_event()` que é bloqueante em `ui/` e não acopla o engine.

### Arquivos tocados

| Arquivo | Ação |
|---|---|
| `src/shared/constants.py` | Constantes `RANDOM_EVENT_*` |
| `src/content/factories/dungeons.py` | Lógica de sorteio e helpers dos 3 eventos |
| `src/shared/combat_topics.py` | Novo tópico `UI_RANDOM_EVENT` |
| `src/ui/screens.py` | `render_*` para mercador/altar/fonte |
| `src/ui/random_event_flow.py` | Novo: 3 fluxos + dispatcher |
| `src/ui/ui_event_handlers.py` | Handler `_on_random_event` + registro |
| `src/engine/loop.py` | Sorteio e publish antes da extração; trata morte no altar |
| `tests/auto_test.py` | Mock de `random_event_flow.safe_get_key` + bot escolhe continuar/recusar |

---

## Critérios de Aceite

- [x] 3 tipos têm lógica real, não só texto decorativo
- [x] Probabilidade configurável via `RANDOM_EVENT_CHANCE` (25%)
- [x] Segue publish/handler via EventBus, sem acoplamento direto ao loop
- [x] pytest e AutoTester (vitória Lvl 20, 0 crashes) continuam passando

---

## Backlog

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-005 | Eventos aleatórios de andar (Mercador, Altar, Fonte) | TASK-004 — ✅ Concluída |
| TASK-006 | Cooldowns + `damage_reduction` + `stun_chance` em combate | TASK-004 |
| TASK-007 | Opção "Sair da Masmorra" (extração) entre andares | TASK-004 — ✅ Concluída |
