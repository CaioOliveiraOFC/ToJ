"""Registros de injeção de dependência entre camadas.

A regra 3 da arquitetura diz que `entities/` não importa de `content/`: as
entidades não conhecem os dados. Mas o `Player` precisa aprender as skills
iniciais da classe dele, e essas skills vivem em `content/skills_loader.py`.

Antes, `heroes.py` importava `get_initial_skills` direto de `content/`, o que
invertia a dependência e furava a regra. A correção é o padrão clássico:
`shared/` — a única camada que todo mundo pode importar — guarda o ponto de
registro; `content/` se registra ao ser carregado; `entities/` só consulta o
registro e nunca sabe quem o preencheu.

Este módulo não importa nada do projeto.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Recebe o nome da classe e devolve as skills iniciais dela.
InitialSkillProvider = Callable[[str], list[Any]]

_initial_skill_provider: InitialSkillProvider | None = None


def set_initial_skill_provider(provider: InitialSkillProvider) -> None:
    """Registra quem sabe listar as skills iniciais de uma classe.

    Chamado por `content/skills_loader.py` ao ser importado.
    """
    global _initial_skill_provider
    _initial_skill_provider = provider


def get_initial_skills_for(class_name: str) -> list[Any]:
    """Skills iniciais da classe, ou lista vazia se ninguém se registrou.

    Devolver vazio em vez de levantar erro mantém `entities/` utilizável
    isoladamente — em um teste de atributos puros, por exemplo, que não precisa
    do catálogo de skills carregado.
    """
    if _initial_skill_provider is None:
        return []
    return list(_initial_skill_provider(class_name))
