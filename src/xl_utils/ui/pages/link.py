"""Ligação da página com a vinculação AGENDA × PROCESSOS."""

from __future__ import annotations

import flet as ft

from xl_utils.controllers.link import LinkOutcome, migration_warning, run_link
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.tool_layout import ToolLayout
from xl_utils.ui.pages.batch import append_outcomes
from xl_utils.ui.state import ToolState

LABELS = ("AGENDA", "PROCESSOS")
NOTE = (
    "Compara CNJ, PASTA e PROTOCOLO como estão na planilha. A saída preserva "
    "todas as colunas e as outras abas da AGENDA."
)


def build() -> ft.Control:
    """Monta a página com duas entradas rotuladas e o aviso de reexecução."""
    return ToolLayout(
        "Vincular Planilhas",
        "Cruza a AGENDA com PROCESSOS e marca o vínculo de cada linha.",
        note=NOTE,
        inputs=LABELS,
        pre_run=_pre_run,
        run_handler=run,
    ).control


def _pre_run(state: ToolState) -> str | None:
    """Lê só o necessário para saber se a AGENDA já foi processada."""
    agenda = state.inputs.get("AGENDA")
    if agenda is None or state.options.get("reprocess"):
        return None
    try:
        return migration_warning(agenda)
    except Exception:  # noqa: BLE001 - a execução real reporta o erro
        return None


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
) -> None:
    """Executa a vinculação e deixa o livro pronto para salvar."""
    del token  # a ferramenta termina em uma leitura; não há lote para cancelar
    agenda = state.inputs.get("AGENDA")
    processos = state.inputs.get("PROCESSOS")
    if agenda is None or processos is None:
        result.set_info(
            "Selecione as duas planilhas",
            "A AGENDA e a lista de PROCESSOS são obrigatórias.",
        )
        return

    outcome = run_link(
        agenda,
        processos,
        allow_migrated=bool(state.options.get("reprocess")),
        progress=progress,
    )
    append_outcomes(state, [outcome])
    state.save_items = [outcome.item]
    state.result = outcome.preview
    state.message = _summary(outcome)
    result.set_ready(
        outcome.preview,
        "AGENDA vinculada",
        f"{state.message} · {outcome.item.suggested_name}",
    )


def _summary(outcome: LinkOutcome) -> str:
    stats = outcome.stats
    return (
        f"{stats.rows} linha(s) · {stats.linked} vínculo(s) · "
        f"{stats.unlinked} sem vínculo"
    )
