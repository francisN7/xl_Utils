"""Executa a extração de CNJ e mantém a lista única em memória para salvar."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.cnj import summarize_cnjs
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog
from xl_utils.shared.progress import NullReporter, ProgressReporter


@dataclass(frozen=True, slots=True)
class CnjOutcome:
    """Resultado de uma execução de extração de CNJ."""

    source: Path
    item: SaveItem
    cnjs: list[str]
    found: int
    log: RunLog

    @property
    def suggested_name(self) -> str:
        return self.item.suggested_name

    @property
    def sheets(self) -> dict[str, pd.DataFrame]:
        return self.item.sheets

    @property
    def duplicates(self) -> int:
        return self.found - len(self.cnjs)


def run_cnj(
    source: Path,
    selected: Collection[str] | None = None,
    progress: ProgressReporter | NullReporter | None = None,
) -> CnjOutcome:
    """Extrai CNJs das abas escolhidas, sem gravar nada."""
    reporter = progress or NullReporter()
    log = RunLog().info(f"Arquivo: {source.name}")
    reporter.note(log, f"{source.name}: lendo e limpando planilha")
    sheets = filter_sheets(prepare_workbook(source), selected)
    reporter.note(log, f"{source.name}: planilha carregada · {len(sheets)} aba(s)")
    log.info(f"Tipo detectado: {resolve_suffix(source)}")

    reporter.note(log, f"{source.name}: procurando CNJs em {len(sheets)} aba(s)")
    found, cnjs = summarize_cnjs(sheets)
    reporter.note(
        log,
        f"{source.name}: {found} CNJ(s) encontrado(s) · {len(cnjs)} único(s)",
    )

    name = f"{source.stem} lista cnj.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets={"PROCESSOS": pd.DataFrame({"PROCESSOS": cnjs})},
        output_dir=default_output_dir(source),
    )

    log.info(f"Abas lidas: {len(sheets)} ({', '.join(sheets)})")
    log.info(f"CNJs encontrados: {found}")
    log.info(f"Duplicados removidos: {found - len(cnjs)}")
    log.info(f"CNJs únicos: {len(cnjs)}")
    log.success(f"Pronto para salvar: {name}")
    return CnjOutcome(
        source=source,
        item=item,
        cnjs=cnjs,
        found=found,
        log=log,
    )
