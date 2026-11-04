"""Text cleanup shared by every spreadsheet tool."""

import emoji


def remove_emojis(value: object) -> object:
    """Remove emojis from a string cell, keeping line breaks untouched."""
    if not isinstance(value, str):
        return value
    return emoji.replace_emoji(value, replace="")
