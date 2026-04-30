import os
import platform


def clear_screen():
    """Limpa a tela do console de forma multi-plataforma."""
    os.system("cls" if platform.system() == "Windows" else "clear")
