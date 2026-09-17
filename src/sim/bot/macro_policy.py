"""A decisão no mapa: avaliar tudo que existe e escolher por necessidade.

A escolha é lexicográfica — `min(need)`, depois `max(utility)`, depois o
desempate declarado. A prioridade ordena necessidades incompatíveis; a utilidade
compara alternativas dentro de uma necessidade comparável.

A prioridade NUNCA impede uma ação de ser enumerada, avaliada ou registrada. Toda
opção recebida entra em `Decision.scores`, inclusive as de necessidade menos
urgente — é o que torna a decisão auditável, e há teste para isso.

E o que saiu daqui: ter ouro para pagar a saída não é mais condição de nada.
Ouro é parcela na nota de `saida`, dentro de ENCERRAR, e nunca portão de
`lutar`, que vive em PROGREDIR.
"""

from __future__ import annotations

from src.sim.bot.decision import ActionOption, Decision, Score, escolher
from src.sim.bot.evaluators import avaliar_mapa
from src.sim.bot.observation import MapState, ProgressionState


def _motivo(score: Score, mapa: MapState, prog: ProgressionState, opcao: ActionOption) -> str:
    partes = ", ".join(f"{nome} {valor:+.2f}" for nome, valor in score.components)
    situacao = (
        f"Andar {mapa.andar}, Nv{prog.nivel}, HP {prog.hp_frac:.0%}, MP {prog.mp_frac:.0%}, "
        f"{prog.ouro} de ouro contra saída de {prog.taxa_de_saida}, "
        f"{len(mapa.alvos)} alvo(s) no mapa."
    )
    alvo = opcao.target
    onde = f" a {alvo.passos} passos" if alvo is not None else ""
    cabeca = (
        f"{opcao.label or opcao.action_id}{onde} atende {score.need.name} "
        f"e vale {score.utility:+.2f}"
    )
    if partes:
        cabeca += f" [{partes}]"
    return f"{situacao} {cabeca}" + (f" — {score.note}" if score.note else "")


def decidir(mapa: MapState, prog: ProgressionState, opcoes: tuple[ActionOption, ...]) -> Decision:
    """A próxima coisa a fazer no andar. `opcoes` já vem declarada legal."""
    scores: list[Score] = []
    motivos: dict[str, str] = {}
    for opcao in opcoes:
        score = avaliar_mapa(opcao, mapa, prog)
        scores.append(score)
        motivos[opcao.action_id] = _motivo(score, mapa, prog, opcao)
    return escolher(tuple(scores), motivos)
