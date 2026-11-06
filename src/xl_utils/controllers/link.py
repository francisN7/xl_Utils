"""Executa a vinculação AGENDA × PROCESSOS e mantém o livro em memória."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.link import (
    LinkStats,
    column_map,
    find_target_sheet,
    fold_header,
    has_migration,
    link_agenda,
)
from xl_utils.shared.configs import load_link_config
from xl_utils.shared.log import RunLog
from xl_utils.shared.progress import NullReporter, ProgressReporter


@dataclass(frozen=True, slots=True)
class LinkOutcome:
    """Resultado de uma execução de vinculação."""

    source: Path
    item: SaveItem
    preview: dict[str, pd.DataFrame]
    stats: LinkStats
    log: RunLog

    @property
    def suggested_name(self) -> str:
        return self.item.suggested_name


def migration_warning(agenda: Path) -> str | None:
    """Devolve o aviso de reexecução quando a AGENDA já tem ``MIGRAÇÃO``."""
    config = load_link_config()
    spec = config.sheet("AGENDA")
    sheets = prepare_workbook(agenda)
    _, frame = find_target_sheet(sheets, spec, "AGENDA")
    column = column_map(frame)[fold_header(spec.fields["protocolo"])]
    if not has_migration(frame, column):
        return None
    return (
        "A coluna de protocolo da AGENDA já contém MIGRAÇÃO, sinal de que a "
        "planilha já foi processada. Se continuar, o VINCULA? será recalculado "
        "e o protocolo NÃO será acrescentado de novo à descrição."
    )


def run_link(
    agenda: Path,
    processos: Path,
    *,
    allow_migrated: bool = False,
    progress: ProgressReporter | NullReporter | None = None,
) -> LinkOutcome:
    """Vincula as duas planilhas, sem gravar nada.

    ``allow_migrated`` é ligado pela página depois que o usuário confirma o
    aviso de planilha já processada. A leitura continua pelo ``prepare_workbook``
    e o original nunca é alterado.
    """
    if agenda.resolve() == processos.resolve():
        raise ValueError("Selecione arquivos diferentes para AGENDA e PROCESSOS.")

    reporter = progress or NullReporter()
    log = RunLog().info(f"AGENDA: {agenda.name}")
    reporter.file_started(agenda.name)
    reporter.note(log, "AGENDA: lendo e limpando planilha")
    agenda_sheets = prepare_workbook(agenda)
    reporter.note(
        log,
        f"AGENDA: planilha carregada · {len(agenda_sheets)} aba(s)",
    )
    reporter.file_done(agenda.name)

    log.info(f"PROCESSOS: {processos.name}")
    reporter.file_started(processos.name)
    reporter.note(log, "PROCESSOS: lendo e limpando planilha")
    processos_sheets = prepare_workbook(processos)
    reporter.note(
        log,
        f"PROCESSOS: planilha carregada · {len(processos_sheets)} aba(s)",
    )
    reporter.file_done(processos.name)

    config = load_link_config()
    reporter.note(log, "Vinculando por CNJ, PASTA e PROTOCOLO")
    result = link_agenda(
        agenda_sheets,
        processos_sheets,
        config,
        allow_migrated=allow_migrated,
        agenda_name=agenda.name,
        processos_name=processos.name,
    )
    reporter.note(log, "AGENDA: vinculação concluída")

    name = f"{agenda.stem} - vinculado.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets=result.sheets,
        output_dir=default_output_dir(agenda),
    )
    preview = {result.target_sheet: result.sheets[result.target_sheet]}
    _log_stats(log, result.stats)
    if allow_migrated:
        log.warning(
            "Reexecução confirmada: o protocolo não foi acrescentado à descrição."
        )
    log.success(f"Pronto para salvar: {name}")
    return LinkOutcome(
        source=agenda,
        item=item,
        preview=preview,
        stats=result.stats,
        log=log,
    )


def _log_stats(log: RunLog, stats: LinkStats) -> None:
    log.info(f"Linhas na AGENDA: {stats.rows}")
    log.info(
        "Vínculos: "
        f"CNJ {stats.by_cnj} · PASTA {stats.by_pasta} · "
        f"PROTOCOLO {stats.by_protocolo}"
    )
    log.info(f"Sem vínculo: {stats.unlinked} (MIGRAÇÃO)")
    log.info(
        "CNJ mascarado/cru: "
        f"AGENDA {stats.agenda_masked}/{stats.agenda_raw} · "
        f"PROCESSOS {stats.processos_masked}/{stats.processos_raw}"
    )
