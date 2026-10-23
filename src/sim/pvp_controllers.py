"""Controladores de referência para o duelo da Arena.

Não são o bot de PvP. Existem para provar a interface `DuelController` e para
conduzir testes e demonstrações de forma reproduzível: decidem só pelo que a
`DuelView` mostra, e nenhum deles sabe o que o adversário escolheu.
"""

from __future__ import annotations

from collections.abc import Iterable

from src.mechanics.pvp_duel import DuelAction, DuelView


class ScriptedController:
    """Joga uma sequência fixa de ações e, esgotada, o ataque básico.

    Guarda as visões que recebeu: é assim que um teste confere o que chegou ao
    controlador, e o que NÃO chegou.
    """

    def __init__(self, actions: Iterable[DuelAction] = ()) -> None:
        self._fila = list(actions)
        self.views: list[DuelView] = []

    def choose(self, view: DuelView) -> DuelAction:
        self.views.append(view)
        if self._fila:
            return self._fila.pop(0)
        return DuelAction.attack()


class FirstLegalSkillController:
    """A primeira skill legal na ordem do deck; sem nenhuma, o ataque básico.

    Política deliberadamente ingênua e determinística. Nunca se rende.
    """

    def choose(self, view: DuelView) -> DuelAction:
        for acao in view.legal_actions:
            if acao.kind == "skill":
                return acao
        return DuelAction.attack()
