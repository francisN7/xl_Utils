"""Resultados em memória e a gravação que acontece depois da escolha.

Entrada: lista de ``SaveItem`` e o destino escolhido pelo usuário.
Saída: lista de ``Path`` realmente gravados, ``None`` no cancelamento ou ``[]``
quando não há item.
Erros: ``SaveError`` quando o destino não pode receber o livro.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import save_workbook


class SaveError(Exception):
    """Indica que o destino escolhido não pôde receber o livro."""


@dataclass(frozen=True, slots=True)
class SaveItem:
    """Um livro mantido em memória até o usuário escolher onde salvar."""

    suggested_name: str
    sheets: dict[str, pd.DataFrame]
    output_dir: Path


def save_chosen(
    items: Sequence[SaveItem],
    destination: Path | None,
) -> list[Path] | None:
    """Grava um item no arquivo escolhido ou vários na pasta escolhida.

    ``None`` significa que o usuário cancelou o diálogo nativo: nada é escrito.
    Com vários itens, o destino precisa ser uma pasta; um arquivo existente é
    recusado com ``SaveError`` em vez de virar uma pasta com nome de arquivo.
    Arquivos existentes nunca são sobrescritos: os caminhos retornados são os
    reais, já com sufixo numérico quando necessário.
    """
    items = list(items)
    if destination is None:
        return None
    if not items:
        return []

    if len(items) == 1:
        targets = [destination.with_suffix(".xlsx")]
    else:
        if destination.exists() and not destination.is_dir():
            raise SaveError(
                f"Escolha uma pasta para salvar {len(items)} arquivos: "
                f"{destination.name} é um arquivo."
            )
        targets = [destination / item.suggested_name for item in items]

    return [
        save_item(item, target) for item, target in zip(items, targets, strict=True)
    ]


def save_to_output(items: Sequence[SaveItem]) -> list[Path]:
    """Grava cada item na pasta ``output/`` da própria origem."""
    return [save_item(item, item.output_dir / item.suggested_name) for item in items]


def save_item(item: SaveItem, destination: Path) -> Path:
    """Grava um item e devolve o caminho real, sem sobrescrever."""
    target = destination.with_suffix(".xlsx")
    try:
        return save_workbook(item.sheets, target)
    except Exception as error:  # noqa: BLE001 - uma falha tipada para a UI
        raise SaveError(f"Não foi possível salvar {target.name}: {error}") from error
