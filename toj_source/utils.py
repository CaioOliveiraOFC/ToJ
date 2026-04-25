import os
import platform

def clear_screen():
    """Limpa a tela do console de forma multi-plataforma."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_key():
    """Lê um único caractere do teclado sem precisar pressionar Enter (multi-plataforma)."""
    if platform.system() == 'Windows':
        import msvcrt
        while True:
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                msvcrt.getch()
                continue
            return key.decode('utf-8', errors='replace')
    else:
        import tty
        import termios
        import sys
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # Ignorar teclas de seta e sequências de escape multibyte
            if key == '\x1b':
                sys.stdin.read(2)  # consome os 2 bytes restantes da sequência
                return '\x1b'
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def safe_get_key(valid_keys=None, allow_escape=True):
    """Lê uma tecla com segurança, retornando apenas teclas válidas ou None se Escape."""
    while True:
        key = get_key()
        if not key:
            continue
        key = key.lower()
        if allow_escape and key == '\x1b':
            return None
        if valid_keys is None or key in valid_keys:
            return key
