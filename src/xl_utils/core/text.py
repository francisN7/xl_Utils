"""Limpeza de texto compartilhada por todas as ferramentas."""

import emoji


def remove_emojis(value: object) -> object:
    """Remove emojis de uma célula de texto, preservando quebras de linha.

    Valores que não são texto (números, vazios, ``NA``) passam intactos.
    """
    if not isinstance(value, str):
        return value
    return emoji.replace_emoji(value, replace="")
