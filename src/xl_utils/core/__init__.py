"""Pure domain logic: no UI, no file dialogs, no terminal output."""

from xl_utils.core.io import read_workbook, save_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import unique_path
from xl_utils.core.text import remove_emojis

__all__ = [
    "read_workbook",
    "remove_emojis",
    "resolve_suffix",
    "save_workbook",
    "unique_path",
]
