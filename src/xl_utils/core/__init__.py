"""Regra pura do domínio: sem UI, sem diálogo e sem saída no terminal."""

from xl_utils.core.io import list_sheets, read_workbook, save_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import unique_path
from xl_utils.core.text import remove_emojis

__all__ = [
    "list_sheets",
    "read_workbook",
    "remove_emojis",
    "resolve_suffix",
    "save_workbook",
    "unique_path",
]
