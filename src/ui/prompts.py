"""Único módulo autorizado para leitura de teclado (sem Enter), conforme contrato de UI."""

from __future__ import annotations

import platform


def get_key() -> str:
    """Lê um único caractere do teclado sem precisar pressionar Enter (multi-plataforma).
    
    Returns:
        - Caractere normal (a-z, 0-9, etc.)
        - "UP" para arrow up
        - "DOWN" para arrow down
        - "ENTER" para Enter/Return
        - "ESC" para Escape
        - "BACKSPACE" para Backspace
    """
    if platform.system() == "Windows":
        import msvcrt

        while True:
            key = msvcrt.getch()
            if key in [b"\xe0", b"\x00"]:
                second = msvcrt.getch()
                if second == b"H":
                    return "UP"
                elif second == b"P":
                    return "DOWN"
                elif second == b"K":
                    return "LEFT"
                elif second == b"M":
                    return "RIGHT"
                continue
            if key == b"\r":
                return "ENTER"
            if key == b"\n":
                return "ENTER"
            if key == b"\x08":
                return "BACKSPACE"
            if key == b"\x1b":
                return "ESC"
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
            next1 = sys.stdin.read(1)
            if next1 == "[":
                arrow = sys.stdin.read(1)
                if arrow == "A":
                    return "UP"
                elif arrow == "B":
                    return "DOWN"
                elif arrow == "C":
                    return "RIGHT"
                elif arrow == "D":
                    return "LEFT"
            return "ESC"
        if key == "\r" or key == "\n":
            return "ENTER"
        if key == "\x7f":
            return "BACKSPACE"
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def wait_enter_to_continue() -> None:
    """Bloqueia até Enter/Return (após o jogador ler o layout no console)."""
    while True:
        key = get_key()
        if key == "ENTER":
            return


def safe_get_key(valid_keys=None, allow_escape: bool = True) -> str | None:
    """Lê uma tecla com segurança, retornando apenas teclas válidas ou None se Escape."""
    while True:
        key = get_key()
        if not key:
            continue
        key = key.lower()
        if allow_escape and key.lower() == "esc":
            return None
        if valid_keys is None or key.lower() in [k.lower() for k in valid_keys]:
            return key
