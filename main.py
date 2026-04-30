#!/usr/bin/env python3
"""Entry point: bootstrap e orquestração do menu principal."""

from src.engine.bootstrap import run_main_loop


def main() -> None:
    """Função principal que inicia o loop de jogo."""
    run_main_loop()


if __name__ == "__main__":
    main()