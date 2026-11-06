"""Preferências locais do aplicativo, persistidas em JSON."""

import json
import os
from pathlib import Path
from typing import Any

APP_DIR = "xl_utils"
SETTINGS_FILE = "settings.json"
DEFAULT_THEME = "dark"
VALID_THEMES = ("dark", "light")


def settings_path() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/settings.json`` ou ``~/.xl_utils/...``."""
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) / APP_DIR if local else Path.home() / f".{APP_DIR}"
    return base / SETTINGS_FILE


def _read(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return {}
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def load_theme(path: Path | None = None) -> str:
    """Lê o tema salvo; ausente, inválido ou desconhecido volta ao escuro."""
    value = _read(path or settings_path()).get("theme")
    return value if value in VALID_THEMES else DEFAULT_THEME


def save_theme(mode: str, path: Path | None = None) -> None:
    """Grava o tema de forma atômica, preservando as demais chaves."""
    if mode not in VALID_THEMES:
        raise ValueError(f"tema desconhecido: {mode}")
    target = path or settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    data = _read(target)
    data["theme"] = mode
    temporary = target.with_name(f"{target.name}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, target)
