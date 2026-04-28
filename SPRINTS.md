# ROADMAP DE DESENVOLVIMENTO - TALES OF THE JOURNEY

## Regras de Execução de Sprint
- A IA NÃO deve pular Sprints.
- A IA deve executar apenas a Sprint solicitada pelo usuário.
- Ao finalizar a Sprint, a IA deve aguardar o comando explícito do usuário para avançar.

## [SPRINT 1] O Sistema Nervoso (Event-Driven Integration)
**Foco:** `events.py`, `loop.py`, `screens.py`, `combat.py`
**Objetivo:** Eliminar o acoplamento restante entre o motor e a UI usando Pub/Sub.
**Tarefas:**
1. Aceitar a sugestão prévia: mover o "motor de escolhas" de `screens.py` para `engine/loop.py`, deixando `screens.py` apenas com funções `render_*`.
2. Ligar os fios do `EventBus` (`events.py`). O combate não retorna textos, ele publica eventos (ex: `EventBus.publish("damage_taken", data)`).
3. A interface (`ui/`) se inscreve (`subscribe`) nesses eventos para saber quando atualizar a tela.

## [SPRINT 2] O Motor de Conteúdo (Data-Driven Design)
**Foco:** `content/factories/`, `data/` (nova pasta)
**Objetivo:** Remover *hardcodes* (números mágicos e listas de itens) de dentro dos arquivos Python.
**Tarefas:**
1. Criar `src/data/monsters.json` e `src/data/items.json`.
2. Refatorar as fábricas (`monsters.py`, `loot.py`) para lerem os status básicos a partir desses arquivos JSON. O código Python passa a ser apenas o injetor.

## [SPRINT 3] O "Game Feel" (UX Visual)
**Foco:** `ui/renderer.py`, `ui/prompts.py`
**Objetivo:** Trazer peso, ritmo e suspense ao jogo de terminal.
**Tarefas:**
1. Inserir pausas dramáticas (`time.sleep`) nos eventos de combate (entre o ataque e a exibição do dano).
2. Adicionar efeitos visuais do `rich` (textos que mudam de cor baseado na porcentagem de vida).

## [SPRINT 4] Expansão de Features
**Foco:** `mechanics/combat.py`, `entities/`
**Objetivo:** Escalar o jogo usando a nova arquitetura limpa.
**Tarefas:**
1. Implementar sistema de "Status Effects" (Veneno, Atordoamento, Sangramento) no combate, controlando a duração por turnos.
2. Iniciar a fundação do modo "Arena".