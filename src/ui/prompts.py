"""Único módulo autorizado para leitura de teclado (sem Enter), conforme contrato de UI."""

from __future__ import annotations

import platform


def get_key() -> str:
    """Lê um único caractere do teclado sem precisar pressionar Enter (multi-plataforma)."""
    if platform.system() == "Windows":
        import msvcrt

        while True:
            key = msvcrt.getch()
            if key in [b"\xe0", b"\x00"]:
                msvcrt.getch()
                continue
            return key.decode("utf-8", errors="replace")
    import sys
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
            sys.stdin.read(2)
            return "\x1b"
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def wait_enter_to_continue() -> None:
    """Bloqueia até Enter/Return (após o jogador ler o layout no console)."""
    while True:
        key = get_key()
        if key in ("\r", "\n"):
            return


def safe_get_key(valid_keys=None, allow_escape: bool = True) -> str | None:
    """Lê uma tecla com segurança, retornando apenas teclas válidas ou None se Escape."""
    while True:
        key = get_key()
        if not key:
            continue
        key = key.lower()
        if allow_escape and key == "\x1b":
            return None
        if valid_keys is None or key in valid_keys:
            return key
