"""Executa a vinculação das planilhas e mantém os livros em memória."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.link import (
    FinanceiroStats,
    LinkStats,
    column_map,
    find_target_sheet,
    has_migration,
    header_key,
    link_agenda,
    link_financeiro,
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
    stats: LinkStats | FinanceiroStats
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
    column = column_map(frame)[header_key(spec.fields["protocolo"])]
    if not has_migration(frame, column):
        return None
    return (
        "A coluna de protocolo da AGENDA já contém MIGRAÇÃO, sinal de que a "
        "planilha já foi processada. Se continuar, o VINCULA? será recalculado "
        "e o protocolo NÃO será acrescentado de novo à descrição."
    )


def run_link(
    agenda: Path | None = None,
    processos: Path | None = None,
    financeiro: Path | None = None,
    clientes: Path | None = None,
    *,
    allow_migrated: bool = False,
    name_in_description: bool = False,
    single_field_agenda: bool = False,
    single_field_financeiro: bool = False,
    progress: ProgressReporter | NullReporter | None = None,
) -> list[LinkOutcome]:
    """Vincula as planilhas dos fluxos presentes, sem gravar nada.

    A AGENDA exige PROCESSOS; o FINANCEIRO exige PROCESSOS ou CLIENTES. Cada
    fluxo presente gera uma saída, na ordem AGENDA e depois FINANCEIRO.
    """
    _validate_selection(agenda, processos, financeiro, clientes)
    reporter = progress or NullReporter()
    reader = _Reader(reporter)
    config = load_link_config()
    outcomes: list[LinkOutcome] = []

    if agenda is not None:
        assert processos is not None
        log = RunLog().info(f"AGENDA: {agenda.name}")
        agenda_sheets = reader.read(agenda, "AGENDA", log)
        processos_sheets = reader.read(processos, "PROCESSOS", log)
        reporter.note(log, "Vinculando AGENDA por CNJ, PASTA e PROTOCOLO")
        result = link_agenda(
            agenda_sheets,
            processos_sheets,
            config,
            allow_migrated=allow_migrated,
            single_field=single_field_agenda,
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
        _log_agenda(log, result.stats)
        if allow_migrated:
            log.warning(
                "Reexecução confirmada: o protocolo não foi acrescentado à descrição."
            )
        log.success(f"Pronto para salvar: {name}")
        outcomes.append(
            LinkOutcome(
                source=agenda,
                item=item,
                preview=preview,
                stats=result.stats,
                log=log,
            )
        )

    if financeiro is not None:
        log = RunLog().info(f"FINANCEIRO: {financeiro.name}")
        financeiro_sheets = reader.read(financeiro, "FINANCEIRO", log)
        processos_sheets = (
            reader.read(processos, "PROCESSOS", log) if processos is not None else None
        )
        clientes_sheets = (
            reader.read(clientes, "CLIENTES", log) if clientes is not None else None
        )
        reporter.note(log, "Vinculando FINANCEIRO por CNJ, PASTA, PROTOCOLO e NOME")
        result = link_financeiro(
            financeiro_sheets,
            processos_sheets,
            clientes_sheets,
            config,
            name_in_description=name_in_description,
            single_field=single_field_financeiro,
            financeiro_name=financeiro.name,
            processos_name=processos.name if processos is not None else "PROCESSOS",
            clientes_name=clientes.name if clientes is not None else "CLIENTES",
        )
        reporter.note(log, "FINANCEIRO: vinculação concluída")
        name = f"{financeiro.stem} - vinculado.xlsx"
        item = SaveItem(
            suggested_name=name,
            sheets=result.sheets,
            output_dir=default_output_dir(financeiro),
        )
        preview = {result.target_sheet: result.sheets[result.target_sheet]}
        _log_financeiro(log, result.stats)
        log.success(f"Pronto para salvar: {name}")
        outcomes.append(
            LinkOutcome(
                source=financeiro,
                item=item,
                preview=preview,
                stats=result.stats,
                log=log,
            )
        )

    return outcomes


class _Reader:
    """Lê cada livro uma vez só e registra o progresso por arquivo."""

    def __init__(self, reporter: ProgressReporter | NullReporter) -> None:
        self._reporter = reporter
        self._books: dict[Path, dict[str, pd.DataFrame]] = {}

    def read(
        self,
        path: Path,
        label: str,
        log: RunLog,
    ) -> dict[str, pd.DataFrame]:
        key = path.resolve()
        if key in self._books:
            log.info(f"{label}: {path.name} (já carregada)")
            return self._books[key]

        log.info(f"{label}: {path.name}")
        self._reporter.file_started(path.name)
        self._reporter.note(log, f"{label}: lendo e limpando planilha")
        sheets = prepare_workbook(path)
        self._books[key] = sheets
        self._reporter.note(log, f"{label}: planilha carregada · {len(sheets)} aba(s)")
        self._reporter.file_done(path.name)
        return sheets


def _validate_selection(
    agenda: Path | None,
    processos: Path | None,
    financeiro: Path | None,
    clientes: Path | None,
) -> None:
    """Confere as combinações de arquivos antes de ler qualquer planilha."""
    if agenda is None and financeiro is None:
        raise ValueError("Anexe a AGENDA e/ou o FINANCEIRO.")

    if agenda is not None and processos is None:
        raise ValueError("A AGENDA exige PROCESSOS.")

    if financeiro is not None and processos is None and clientes is None:
        raise ValueError("O FINANCEIRO exige PROCESSOS ou CLIENTES.")

    seen: dict[Path, str] = {}
    for label, path in (
        ("AGENDA", agenda),
        ("PROCESSOS", processos),
        ("FINANCEIRO", financeiro),
        ("CLIENTES", clientes),
    ):
        if path is None:
            continue
        key = path.resolve()
        if key in seen:
            raise ValueError(
                f"Selecione arquivos diferentes para {seen[key]} e {label}."
            )
        seen[key] = label


def _log_agenda(log: RunLog, stats: LinkStats | FinanceiroStats) -> None:
    """Registra as contagens do fluxo da AGENDA."""
    if not isinstance(stats, LinkStats):
        return
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


def _log_financeiro(log: RunLog, stats: LinkStats | FinanceiroStats) -> None:
    """Registra as contagens do fluxo do FINANCEIRO."""
    if not isinstance(stats, FinanceiroStats):
        return
    log.info(f"Linhas no FINANCEIRO: {stats.rows}")
    if stats.numbers_tested:
        log.info(
            "Vínculos: "
            f"CNJ {stats.by_cnj} · PASTA {stats.by_pasta} · "
            f"PROTOCOLO {stats.by_protocolo}"
        )
        log.info(f"Sem vínculo: {stats.unlinked}")
        log.info(
            "CNJ mascarado/cru: "
            f"FINANCEIRO {stats.financeiro_masked}/{stats.financeiro_raw} · "
            f"PROCESSOS {stats.processos_masked}/{stats.processos_raw}"
        )
    else:
        log.info("Vínculos numéricos: não testados (sem PROCESSOS)")
    log.info(f"Nome: {stats.name_yes} SIM · {stats.name_no} NÃO")
