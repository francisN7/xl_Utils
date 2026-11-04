"""Mescla as abas escolhidas de vários arquivos em um único livro em memória."""

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import read_headers
from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.merge import ColumnGroup, ColumnRef, merge_sheets
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog

Source = tuple[Path, Collection[str] | None]


@dataclass(frozen=True, slots=True)
class MergeOutcome:
    """Resultado de uma execução de mesclagem."""

    sources: tuple[Path, ...]
    merged: pd.DataFrame
    item: SaveItem
    sheets: int
    log: RunLog

    @property
    def suggested_name(self) -> str:
        return self.item.suggested_name

    @property
    def rows(self) -> int:
        return len(self.merged)

    @property
    def columns(self) -> int:
        return len(self.merged.columns)


def inspect_columns(sources: Sequence[Source]) -> list[ColumnRef]:
    """Devolve as colunas escolhidas de cada aba, na ordem de leitura.

    A UI usa isso para montar o quadro arrastável. Os arquivos são lidos pelo
    formato real; para Excel e CSV as linhas de dados não são carregadas.
    """
    refs: list[ColumnRef] = []
    for source, selected in sources:
        headers = filter_sheets(read_headers(source), selected)
        for sheet, names in headers.items():
            refs.extend(ColumnRef(source, sheet, name) for name in names)
    return refs


def run_merge(
    sources: Sequence[Source],
    groups: Sequence[ColumnGroup] | None = None,
) -> MergeOutcome:
    """Concatena as abas escolhidas de ``sources``, sem gravar."""
    if not sources:
        raise ValueError("Selecione ao menos um arquivo para mesclar.")

    loaded: list[tuple[Path, dict[str, pd.DataFrame]]] = []
    entries: list[tuple[Path, str, pd.DataFrame]] = []
    for source, selected in sources:
        sheets = filter_sheets(prepare_workbook(source), selected)
        loaded.append((source, sheets))
        entries.extend((source, name, frame) for name, frame in sheets.items())

    usable = sum(1 for _, _, frame in entries if not frame.empty)
    if usable == 0:
        raise ValueError("Nenhuma aba com dados para mesclar.")
    if usable < 2:
        raise ValueError(
            "Selecione ao menos duas abas — de arquivos diferentes ou do "
            "mesmo arquivo — para mesclar."
        )

    merged = merge_sheets(entries, groups)
    name = "Merge.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets={"Mesclado": merged},
        output_dir=default_output_dir(loaded[0][0]),
    )

    log = RunLog()
    for source, sheets in loaded:
        if log:
            log.info("")
        columns: dict[str, None] = {}
        for frame in sheets.values():
            for name in frame.columns:
                columns.setdefault(str(name), None)
        log.extend(
            [
                f"Arquivo: {source.name}",
                f"Abas: {len(sheets)} ({', '.join(sheets)})",
                f"Linhas: {sum(len(frame) for frame in sheets.values())}",
                f"Colunas: {len(columns)}",
            ]
        )

    log.info("")
    log.info(f"Abas mescladas: {usable}")
    log.info(f"Linhas mescladas: {len(merged)}")
    log.info(f"Colunas no resultado: {len(merged.columns)}")
    log.success(f"Pronto para salvar: {name}")

    return MergeOutcome(
        sources=tuple(source for source, _ in loaded),
        merged=merged,
        item=item,
        sheets=usable,
        log=log,
    )
