"""Executa o recorte e mantém cada parte em memória para salvar."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir, safe_file_part
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.cut import split_workbook, split_workbook_by_parts
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog
from xl_utils.shared.progress import NullReporter, ProgressReporter


@dataclass(frozen=True, slots=True)
class CutOutcome:
    """Resultado de uma execução de recorte."""

    source: Path
    items: list[SaveItem]
    parts: dict[str, list[pd.DataFrame]]
    preview: dict[str, pd.DataFrame]
    log: RunLog

    @property
    def files(self) -> int:
        return len(self.items)

    @property
    def suggested_names(self) -> list[str]:
        return [item.suggested_name for item in self.items]

    @property
    def rows(self) -> int:
        return sum(len(frame) for frames in self.parts.values() for frame in frames)


def run_cut(
    source: Path,
    rows_per_file: int | None = None,
    selected: Collection[str] | None = None,
    *,
    parts: int | None = None,
    progress: ProgressReporter | NullReporter | None = None,
) -> CutOutcome:
    """Recorta as abas escolhidas de ``source``, sem gravar nada.

    Use ``rows_per_file`` para blocos de N linhas ou ``parts`` para dividir cada
    aba em uma quantidade de arquivos; os dois modos não se misturam.
    """
    if parts is not None and rows_per_file is not None:
        raise ValueError("Informe só linhas por arquivo ou quantidade de arquivos.")
    if parts is None and rows_per_file is None:
        raise ValueError("Informe linhas por arquivo ou quantidade de arquivos.")

    reporter = progress or NullReporter()
    log = RunLog().info(f"Arquivo: {source.name}")
    reporter.note(log, f"{source.name}: lendo e limpando planilha")
    sheets = filter_sheets(prepare_workbook(source), selected)
    reporter.note(log, f"{source.name}: planilha carregada · {len(sheets)} aba(s)")
    log.info(f"Tipo detectado: {resolve_suffix(source)}")

    if parts is not None:
        blocks = split_workbook_by_parts(sheets, parts)
        rule = f"Arquivos por aba: {parts}"
    else:
        blocks = split_workbook(sheets, rows_per_file)
        rule = f"Linhas por arquivo: {rows_per_file}"
    reporter.note(log, f"{source.name}: recortando · {rule}")

    output_dir = default_output_dir(source)
    multiple_sheets = len(blocks) > 1
    items: list[SaveItem] = []

    for sheet_name, frames in blocks.items():
        for number, frame in enumerate(frames, start=1):
            if multiple_sheets:
                base = (
                    f"{source.stem}_{safe_file_part(sheet_name)}_Recorte_{number:03d}"
                )
            else:
                base = f"{source.stem}_Recorte_{number:03d}"
            items.append(
                SaveItem(
                    suggested_name=f"{base}.xlsx",
                    sheets={sheet_name: frame},
                    output_dir=output_dir,
                )
            )

    first_sheet = next(iter(blocks), "")
    preview = {first_sheet: blocks[first_sheet][0]} if first_sheet else {}
    total_rows = sum(len(frame) for frames in blocks.values() for frame in frames)
    reporter.note(log, f"{source.name}: {len(items)} arquivo(s) pronto(s)")

    log.info(f"Abas: {len(blocks)}")
    log.info(f"Linhas: {total_rows}")
    log.info(rule)
    log.success(f"Arquivos prontos: {len(items)}")
    log.extend(f"Pronto para salvar: {item.suggested_name}" for item in items)

    return CutOutcome(
        source=source,
        items=items,
        parts=blocks,
        preview=preview,
        log=log,
    )
