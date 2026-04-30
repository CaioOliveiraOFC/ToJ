"""Módulo de dados do jogo (Data-Driven Design).

Contém definições JSON de monstros, itens e utilitários de carregamento.
"""

from __future__ import annotations

from src.data.loader import load_items_data, load_monsters_data

__all__ = ["load_items_data", "load_monsters_data"]
