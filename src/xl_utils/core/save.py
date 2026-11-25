"""Resultados em memória e a gravação que acontece depois da escolha.

Entrada: lista de ``SaveItem`` e o destino escolhido pelo usuário.
Saída: lista de ``Path`` realmente gravados, ``None`` no cancelamento ou ``[]``
quando não há item.
Erros: ``SaveError`` quando o destino não pode receber o livro.

Livro com aba acima de ``ROW_LIMIT`` linhas vira vários arquivos
(``Merge_parte1.xlsx``, ``Merge_parte2.xlsx``…): o Excel não aceita aba com mais
de 1.048.576 linhas e o limite redondo deixa margem.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import save_workbook

ROW_LIMIT = 1_000_000


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
        path
        for item, target in zip(items, targets, strict=True)
        for path in save_item(item, target)
    ]


def save_to_output(items: Sequence[SaveItem]) -> list[Path]:
    """Grava cada item na pasta ``output/`` da própria origem."""
    return [
        path
        for item in items
        for path in save_item(item, item.output_dir / item.suggested_name)
    ]


def save_item(item: SaveItem, destination: Path) -> list[Path]:
    """Grava um item e devolve os caminhos reais, sem sobrescrever.

    Acima de ``ROW_LIMIT`` linhas o item sai em partes, uma por arquivo.
    """
    parts = split_item(item)
    stem = destination.with_suffix("").name
    written: list[Path] = []
    for index, part in enumerate(parts):
        name = _part_stem(stem, index) if len(parts) > 1 else stem
        target = destination.with_name(f"{name}.xlsx")
        try:
            written.append(save_workbook(part.sheets, target))
        except Exception as error:  # noqa: BLE001 - uma falha tipada para a UI
            raise SaveError(
                f"Não foi possível salvar {target.name}: {error}"
            ) from error
    return written


def split_item(item: SaveItem, limit: int | None = None) -> list[SaveItem]:
    """Divide o item em partes de até ``limit`` linhas por aba.

    Sem aba acima do limite, devolve o próprio item. Cada parte leva o
    cabeçalho e o trecho correspondente de cada aba; aba que acaba antes fica
    só nas primeiras partes. Os nomes ganham ``_parte1``, ``_parte2``…
    """
    limit = limit or ROW_LIMIT
    longest = max((len(frame) for frame in item.sheets.values()), default=0)
    if longest <= limit:
        return [item]
    name = Path(item.suggested_name)
    total = math.ceil(longest / limit)
    suffix = name.suffix or ".xlsx"
    parts: list[SaveItem] = []
    for index in range(total):
        start = index * limit
        sheets = {
            sheet: frame.iloc[start : start + limit]
            for sheet, frame in item.sheets.items()
            if index == 0 or len(frame) > start
        }
        parts.append(
            SaveItem(
                suggested_name=_part_stem(name.stem, index) + suffix,
                sheets=sheets,
                output_dir=item.output_dir,
            )
        )
    return parts


def _part_stem(stem: str, index: int) -> str:
    """Nome da parte ``index`` (base 0): ``Merge`` vira ``Merge_parte1``."""
    return f"{stem}_parte{index + 1}"
