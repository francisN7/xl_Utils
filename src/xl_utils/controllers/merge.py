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
from xl_utils.shared.progress import NullReporter, ProgressReporter

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
    progress: ProgressReporter | NullReporter | None = None,
) -> MergeOutcome:
    """Concatena as abas escolhidas de ``sources``, sem gravar."""
    if not sources:
        raise ValueError("Selecione ao menos um arquivo para mesclar.")

    reporter = progress or NullReporter()
    log = RunLog()
    loaded: list[tuple[Path, dict[str, pd.DataFrame]]] = []
    entries: list[tuple[Path, str, pd.DataFrame]] = []
    for index, (source, selected) in enumerate(sources, start=1):
        reporter.note(
            log,
            f"Lendo fonte {index}/{len(sources)}: {source.name}",
        )
        sheets = filter_sheets(prepare_workbook(source), selected)
        reporter.note(
            log,
            f"{source.name}: planilha carregada · {len(sheets)} aba(s)",
        )
        loaded.append((source, sheets))
        entries.extend((source, name, frame) for name, frame in sheets.items())

        columns: dict[str, None] = {}
        for frame in sheets.values():
            for name in frame.columns:
                columns.setdefault(str(name), None)
        log.info(f"  Abas: {len(sheets)} ({', '.join(sheets)})")
        log.info(f"  Linhas: {sum(len(frame) for frame in sheets.values())}")
        log.info(f"  Colunas: {len(columns)}")

    usable = sum(1 for _, _, frame in entries if not frame.empty)
    if usable == 0:
        raise ValueError("Nenhuma aba com dados para mesclar.")
    if usable < 2:
        raise ValueError(
            "Selecione ao menos duas abas — de arquivos diferentes ou do "
            "mesmo arquivo — para mesclar."
        )

    reporter.note(log, f"Mesclando {usable} aba(s)")
    merged = merge_sheets(entries, groups)
    reporter.note(
        log,
        f"Resultado: {len(merged)} linha(s), {len(merged.columns)} coluna(s)",
    )
    name = "Merge.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets={"Mesclado": merged},
        output_dir=default_output_dir(loaded[0][0]),
    )

    log.success(f"Pronto para salvar: {name}")

    return MergeOutcome(
        sources=tuple(source for source, _ in loaded),
        merged=merged,
        item=item,
        sheets=usable,
        log=log,
    )
