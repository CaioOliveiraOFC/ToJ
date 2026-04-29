"""Utilitários para carregar dados JSON do jogo."""

from __future__ import annotations

import json
import os
from typing import Any


def _get_data_dir() -> str:
    """Retorna o caminho absoluto do diretório de dados."""
    return os.path.dirname(os.path.abspath(__file__))


def _load_json(filename: str) -> dict[str, Any]:
    """Carrega um arquivo JSON do diretório de dados."""
    filepath = os.path.join(_get_data_dir(), filename)
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def load_monsters_data() -> dict[str, Any]:
    """Carrega os dados de definição de monstros."""
    return _load_json("monsters.json")


def load_items_data() -> dict[str, Any]:
    """Carrega os dados de definição de itens."""
    return _load_json("items.json")
