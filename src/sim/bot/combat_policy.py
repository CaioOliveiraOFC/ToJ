"""A decisão de um turno de combate: avaliar o que existe e escolher.

Uma necessidade só — resolver esta luta vivo —, então todas as opções são
comparáveis na mesma escala e `utility` decide sozinha. A escada de `Need` é
exclusiva do mapa.

Ataque, skill, item e FUGA disputam dentro deste mesmo sistema. Antes a fuga era
decidida por uma camada ANTES de a política tática ser consultada, e por isso
buff, controle, cura e item nunca chegavam a ser comparados com ela.
"""

from __future__ import annotations

from src.sim.bot.decision import ActionOption, Decision, Score, escolher
from src.sim.bot.evaluators import avaliar_combate
from src.sim.bot.observation import CombatState


def _motivo(score: Score, state: CombatState, opcao: ActionOption) -> str:
    partes = ", ".join(f"{nome} {valor:+.1f}" for nome, valor in score.components)
    cabeca = (
        f"{opcao.label or opcao.action_id} vale {score.utility:+.2f} [{partes}]"
        if partes
        else f"{opcao.label or opcao.action_id} vale {score.utility:+.2f}"
    )
    situacao = (
        f"Turno {state.turno}, HP {state.hp_frac:.0%}, MP {state.mp_frac:.0%}; "
        f"mato em ~{state.turnos_para_matar()}, morro em ~{state.turnos_para_morrer()}."
    )
    return f"{situacao} {cabeca}" + (f" — {score.note}" if score.note else "")


def decidir(state: CombatState, opcoes: tuple[ActionOption, ...]) -> Decision:
    """A decisão do turno. `opcoes` já vem declarada legal pelo adaptador.

    O cérebro não consegue escolher fora desta tupla: é o que ele recebeu, e a
    `Decision` aponta para um `action_id` dela.
    """
    scores: list[Score] = []
    motivos: dict[str, str] = {}
    for opcao in opcoes:
        score = avaliar_combate(opcao, state)
        scores.append(score)
        motivos[opcao.action_id] = _motivo(score, state, opcao)
    return escolher(tuple(scores), motivos)
