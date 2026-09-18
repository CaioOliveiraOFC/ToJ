"""O cérebro do BOT_PADRÃO: observar, avaliar as ações legais, escolher uma.

    ADAPTADOR  responde "o que esta ação FAZ"    -> ActionMechanicsView
    POLICY     responde "quanto isso VALE agora"  -> Score  -> Decision
    ENGINE     executa a Action                   (inalterado)

Este pacote não importa `engine/`, `entities/`, `content/` nem `mechanics/`: ele
recebe dataclasses frozen e devolve um `action_id`. Quem atravessa a fronteira é
`tools/bot_adapter.py`, e é ele que traduz a decisão em `battle.Action`.

NÃO registrado em `src/sim/policies.py::POLICIES`: aquele dicionário pertence ao
contrato legado `policy(hero, monsters, turn)`, e adaptar esta policy a ele
significaria receber objetos do jogo — exatamente a fronteira que este pacote
existe para criar. `harness` e `scout` seguem em `smart_policy`.
"""

from src.sim.bot.combat_policy import decidir as decidir_no_combate
from src.sim.bot.decision import ActionOption, Decision, Need, Score
from src.sim.bot.macro_policy import decidir as decidir_no_mapa
from src.sim.bot.observation import (
    ActionMechanicsView,
    CombatState,
    InteractionView,
    MapState,
    ProgressionState,
    ServiceView,
    StatusView,
    TargetView,
)

__all__ = [
    "ActionMechanicsView",
    "ActionOption",
    "CombatState",
    "Decision",
    "InteractionView",
    "MapState",
    "Need",
    "ProgressionState",
    "Score",
    "ServiceView",
    "StatusView",
    "TargetView",
    "decidir_no_combate",
    "decidir_no_mapa",
]
