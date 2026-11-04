"""Run CNJ extraction and save the unique list beside the source file."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import save_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.cnj import collect_cnjs, count_cnjs


@dataclass(frozen=True, slots=True)
class CnjOutcome:
    """Result of one CNJ extraction run."""

    source: Path
    output: Path
    cnjs: list[str]
    found: int
    log: list[str]

    @property
    def duplicates(self) -> int:
        return self.found - len(self.cnjs)


def run_cnj(source: Path) -> CnjOutcome:
    """Read, extract, deduplicate and save the CNJ list into ``output/``."""
    sheets = prepare_workbook(source)
    cnjs = collect_cnjs(sheets)
    found = count_cnjs(sheets)

    destination = default_output_dir(source) / f"{source.stem} lista cnj.xlsx"
    output = save_workbook(
        {"PROCESSOS": pd.DataFrame({"PROCESSOS": cnjs})},
        destination,
    )

    log = [
        f"Arquivo: {source.name}",
        f"Tipo detectado: {resolve_suffix(source)}",
        f"Abas lidas: {len(sheets)} ({', '.join(sheets)})",
        f"CNJs encontrados: {found}",
        f"Duplicados removidos: {found - len(cnjs)}",
        f"CNJs únicos: {len(cnjs)}",
        f"Saída: {output}",
    ]
    return CnjOutcome(
        source=source,
        output=output,
        cnjs=cnjs,
        found=found,
        log=log,
    )
