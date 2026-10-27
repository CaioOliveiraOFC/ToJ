"""A IA estratégica da Copa Arena 03 v2, como as ferramentas da Copa a importam.

O controlador vive em `src/sim/ia_estrategica.py` desde a Fase 5, porque a Arena
offline do jogo o usa contra o jogador. Este módulo mantém o nome que os
scripts, os relatórios e os testes da Copa 03 v2 importam, e acrescenta só o que
é da Copa: o registro do que a `PoliticaCopa` teria feito na mesma visão
(`politica_copa` em `last_decision`), que não influencia a escolha.
"""

from __future__ import annotations

from src.sim import ia_estrategica as _nucleo
from src.sim.ia_estrategica import *  # noqa: F403
from tools.arena_copa_teste import PoliticaCopa


class IAEstrategica(_nucleo.IAEstrategica):
    """A IA da Arena com a `PoliticaCopa` como referência de registro."""

    def __init__(self, heroi, config: _nucleo.Configuracao | None = None) -> None:
        super().__init__(heroi, config, referencia=PoliticaCopa(heroi))
