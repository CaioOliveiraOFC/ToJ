"""Simulação headless para balanceamento.

Este pacote fala apenas com `mechanics/` e `entities/`. Ele nunca importa de
`ui/` nem de `engine/loop.py`, e é isso que o mantém rápido: sem EventBus, sem
Rich, sem espera por teclado.
"""
