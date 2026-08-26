# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual

**ID:** TASK-007
**Data:** 26/08/2026
**Status:** ✅ Concluída
**Depende de:** TASK-004 concluída

---

## Objetivo

Implementar **opção "Sair da Masmorra" (extração) entre andares** — decisão EXTRAIR vs CONTINUAR no ponto de transição de andar, seguindo o padrão EventBus existente.

---

## Contexto do Game Design

Do GAME_DESING.md:
> "Entre um andar e outro, o jogador pode optar por sair da masmorra e salvar o personagem para a Arena."
> "A Essência acumulada é perdida em caso de morte no próximo andar."

---

## Especificação Técnica

### Decisão de Design: o que "preservar essência" significa

**Sem meta-progressão nova.** O jogo hoje não tem moeda persistente entre runs além do próprio save por slot. "Preservar" = `save_game(player, dungeon_level, None, slot=slot)` no andar concluído e encerrar a run, mantendo `xp_points`, `level`, `passives`, `coins`, `inventory` e `equipment` no `saves/slot_{1-10}.json`. Morrer no próximo andar continua deletando o save (`delete_save` + `add_trophy`), como já validado no protótipo vertical slice.

### Fluxo implementado

```
level_complete em start_game (loop.py:556) — após player.rest() e ANTES de UI_OPEN_SHOP:
  1. publish(UI_EXTRACTION_PROMPT, {player, dungeon_level, essence_multiplier, result: {choice}})
     -> ui_event_handlers._on_extraction_prompt -> extraction_flow.run_extraction_prompt()
        mostra: andar concluído, HP atual, essência/XP acumulada, aviso de perda
        opções: [1] EXTRAIR | [2] CONTINUAR
  2. Se choice == "extract": save_game(...) + render_extraction_success() + return
  3. Se "continue": publica UI_OPEN_SHOP e incrementa dungeon_level normalmente
```

Arquitetura: segue o padrão `UI_OPEN_SHOP` — engine publica via `_get_game_publish()`, UI decide de forma bloqueante em `ui/` e devolve a escolha por dicionário mutável no payload (publish é síncrono).

### Arquivos tocados

| Arquivo | Ação |
|---|---|
| `src/shared/combat_topics.py` | Novo tópico `UI_EXTRACTION_PROMPT` |
| `src/ui/screens.py` | `render_extraction_prompt()` + `render_extraction_success()` |
| `src/ui/extraction_flow.py` | Novo: `run_extraction_prompt()` |
| `src/ui/ui_event_handlers.py` | Handler `_on_extraction_prompt` + registro |
| `src/engine/loop.py` | Branch `level_complete`: publica extração, salva e retorna ou continua |
| `tests/auto_test.py` | Mock de `extraction_flow.safe_get_key` + bot escolhe "2" (continuar) |

---

## Critérios de Aceite

- [x] Prompt aparece exatamente entre andares, após `player.rest()` e antes de `UI_OPEN_SHOP`
- [x] Segue padrão publish/handler, sem chamada direta de UI no engine
- [x] Mostra andar, HP, essência/XP e reforça perda em caso de morte
- [x] EXTRAIR encerra a run preservando save; CONTINUAR incrementa andar e abre loja
- [x] pytest e AutoTester (vitória Lvl 20, 0 crashes) continuam passando

---

## Backlog

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-005 | Eventos aleatórios de andar (Mercador, Altar, Fonte) | TASK-004 |
| TASK-006 | Cooldowns + `damage_reduction` + `stun_chance` em combate | TASK-004 |
| TASK-007 | Opção "Sair da Masmorra" (extração) entre andares | TASK-004 — ✅ Concluída |
