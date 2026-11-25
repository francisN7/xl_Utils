"""Localiza os ícones de `assets/` no dev e no executável empacotado."""

import sys
from pathlib import Path


def assets_dir() -> Path:
    """Pasta `assets/`: dentro do bundle no exe, na raiz do repo no dev."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "assets"
    return Path(__file__).resolve().parents[3] / "assets"


def asset_path(name: str) -> Path | None:
    """Caminho do asset `name`, ou `None` se o arquivo não existir."""
    path = assets_dir() / name
    return path if path.is_file() else None


def window_icon() -> Path | None:
    """Ícone da janela: `.ico` no Windows, `.png` nos demais sistemas."""
    return asset_path("icon.ico" if sys.platform == "win32" else "icon.png")
