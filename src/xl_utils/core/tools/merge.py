"""Mesclagem pura: concatena abas e rotula a origem de cada linha.

Entrada: sequência ``(arquivo, aba, DataFrame)`` e, opcionalmente, os grupos de
colunas montados na UI.
Saída: um único DataFrame com ``ORIGEM`` como primeira coluna.
Erros: ``ValueError`` para coluna repetida, aba contribuindo duas vezes para a
mesma saída ou ausência de dados.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

SheetEntry = tuple[Path, str, pd.DataFrame]


@dataclass(frozen=True, slots=True)
class ColumnRef:
    """Uma coluna de uma aba de origem."""

    source: Path
    sheet: str
    column: str


@dataclass(frozen=True, slots=True)
class ColumnGroup:
    """Uma coluna de saída, alimentada pelas colunas de origem em ordem."""

    columns: tuple[ColumnRef, ...]

    @property
    def header(self) -> str:
        """Devolve o nome escolhido pelo primeiro chip."""
        return self.columns[0].column


def group_by_name(refs: Iterable[ColumnRef]) -> list[ColumnGroup]:
    """Agrupa colunas de mesmo nome, preservando a ordem da primeira aparição."""
    groups: dict[str, list[ColumnRef]] = {}
    for ref in refs:
        groups.setdefault(ref.column, []).append(ref)
    return [ColumnGroup(tuple(columns)) for columns in groups.values()]


def move_column(
    groups: Iterable[Iterable[ColumnRef]],
    ref: ColumnRef,
    target_group: int,
    target_index: int,
) -> list[list[ColumnRef]]:
    """Devolve uma cópia de ``groups`` com ``ref`` na posição de destino.

    A primeira coluna de origem de um grupo define o cabeçalho. Um grupo pode
    ter no máximo uma coluna de cada aba de origem; senão a mesclagem não saberia
    qual valor usar para aquela aba.
    """
    result = [list(group) for group in groups]
    if not 0 <= target_group < len(result):
        raise ValueError("Coluna de destino inválida.")

    source_group = next(
        (index for index, group in enumerate(result) if ref in group),
        None,
    )
    if source_group is None:
        raise ValueError("A coluna de origem não está no quadro.")

    target = result[target_group]
    if any(
        other != ref and other.source == ref.source and other.sheet == ref.sheet
        for other in target
    ):
        raise ValueError("Uma aba só pode contribuir com uma coluna por saída.")

    source_index = result[source_group].index(ref)
    result[source_group].remove(ref)
    # Ao mover dentro do mesmo grupo, remover antes desloca o destino uma
    # posição para a esquerda quando a origem vinha antes dele.
    if source_group == target_group and source_index < target_index:
        target_index -= 1
    target.insert(min(max(target_index, 0), len(target)), ref)
    return result


def merge_sheets(
    entries: Iterable[SheetEntry],
    groups: Iterable[ColumnGroup] | None = None,
) -> pd.DataFrame:
    """Concatena ``entries`` na ordem, com ``ORIGEM`` como primeira coluna.

    Cada entrada é ``(arquivo, aba, frame)``. Abas vazias (sem linhas) são
    descartadas; linhas nunca são removidas. ``groups`` decide as colunas de
    saída: cada grupo vira uma coluna, a primeira coluna de origem dá o nome e
    as demais alimentam a mesma coluna. Sem ``groups``, colunas de mesmo nome
    são agrupadas automaticamente.

    Valores ausentes viram ``pd.NA``; a saída segue a ordem dos grupos. O
    ``ORIGEM`` usa ``<arquivo> - <aba> - <linha>``, onde ``linha`` conta só as
    linhas de dados (1 é a primeira linha depois do cabeçalho), não a linha
    física da planilha.
    """
    active = [
        (source, sheet_name, frame)
        for source, sheet_name, frame in entries
        if not frame.empty
    ]
    if not active:
        raise ValueError("Nenhuma aba com dados para mesclar.")

    selected = list(groups) if groups is not None else group_by_name(_refs(active))
    active_refs = {
        _key(ColumnRef(source, sheet_name, str(column)))
        for source, sheet_name, frame in active
        for column in frame.columns
    }
    # Grupos que só apontam para abas vazias/ausentes saem do resultado.
    selected = [
        group
        for group in selected
        if any(_key(ref) in active_refs for ref in group.columns)
    ]
    if not selected:
        raise ValueError("Nenhuma coluna com dados para mesclar.")
    _validate(selected)

    headers = _unique_headers(group.header for group in selected)
    frames: list[pd.DataFrame] = []
    for source, sheet_name, frame in active:
        frame = frame.copy(deep=False)
        frame.columns = [str(column) for column in frame.columns]
        data: dict[str, object] = {
            "ORIGEM": [
                f"{source.name} - {sheet_name} - {row}"
                for row in range(1, len(frame) + 1)
            ]
        }
        for header, group in zip(headers, selected, strict=True):
            column = _column_for(group, source, sheet_name)
            data[header] = (
                frame[column].tolist() if column is not None else [pd.NA] * len(frame)
            )
        frames.append(pd.DataFrame(data))

    return pd.concat(frames, ignore_index=True, sort=False)


def _refs(entries: Iterable[SheetEntry]) -> list[ColumnRef]:
    refs: list[ColumnRef] = []
    for source, sheet_name, frame in entries:
        refs.extend(
            ColumnRef(source, sheet_name, str(column)) for column in frame.columns
        )
    return refs


def _key(ref: ColumnRef) -> tuple[Path, str, str]:
    return (ref.source, ref.sheet, ref.column)


def _column_for(
    group: ColumnGroup,
    source: Path,
    sheet_name: str,
) -> str | None:
    for ref in group.columns:
        if ref.source == source and ref.sheet == sheet_name:
            return ref.column
    return None


def _validate(groups: Iterable[ColumnGroup]) -> None:
    """Recusa coluna repetida e aba que contribui duas vezes para a saída."""
    seen: set[tuple[Path, str, str]] = set()
    for group in groups:
        sheets: set[tuple[Path, str]] = set()
        for ref in group.columns:
            key = _key(ref)
            if key in seen:
                raise ValueError(
                    f"A coluna {ref.column!r} aparece em mais de uma coluna de saída."
                )
            seen.add(key)
            sheet = (ref.source, ref.sheet)
            if sheet in sheets:
                raise ValueError(
                    f"A aba {ref.sheet!r} contribui com duas colunas para "
                    f"{group.header!r}."
                )
            sheets.add(sheet)


def _unique_headers(names: Iterable[str]) -> list[str]:
    """Desempata cabeçalhos repetidos com ``_2`` e protege o ``ORIGEM``.

    Se o usuário já tem uma coluna ``ORIGEM``, ela vira ``ORIGEM_original``
    para não disputar o rótulo com a coluna gerada pela mesclagem.
    """
    used = {"ORIGEM"}
    headers: list[str] = []
    for name in names:
        candidate = "ORIGEM_original" if name == "ORIGEM" else name
        if candidate in used:
            counter = 2
            while f"{candidate}_{counter}" in used:
                counter += 1
            candidate = f"{candidate}_{counter}"
        used.add(candidate)
        headers.append(candidate)
    return headers
