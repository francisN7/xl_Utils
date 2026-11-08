"""Auxiliares de sistema operacional que não pertencem ao core do domínio."""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def open_folder(path: Path) -> None:
    """Abre no gerenciador nativo a pasta que contém ``path``."""
    target = path if path.is_dir() else path.parent
    if sys.platform == "win32":
        os.startfile(target)  # noqa: S606  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(target)])
    else:
        subprocess.Popen(["xdg-open", str(target)])


def open_url(url: str) -> bool:
    """Abre um endereço no navegador padrão e diz se deu certo."""
    if not url:
        return False
    try:
        return webbrowser.open(url, new=2)
    except webbrowser.Error:
        return False
