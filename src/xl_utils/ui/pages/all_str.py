"""Ligação da página com a ferramenta de tratamento de texto."""

from xl_utils.controllers.all_str import run_all_str
from xl_utils.shared.progress import NullReporter, ProgressReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
) -> None:
    """Roda o pipeline para cada arquivo selecionado e mostra o lote."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para converter para texto.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    outcomes = []
    for source, selected in pending:
        progress.file_started(source.name)
        outcomes.append(run_all_str(source, selected=selected))
        progress.file_done(source.name)
    append_outcomes(state, outcomes)
    frames = prefixed_frames(outcomes, lambda outcome: outcome.sheets)
    state.result = frames
    state.save_items = [outcome.item for outcome in outcomes]

    total_sheets = sum(len(outcome.sheets) for outcome in outcomes)
    total_rows = sum(outcome.rows for outcome in outcomes)
    state.message = (
        f"{len(outcomes)} arquivo(s), {total_sheets} aba(s), {total_rows} linha(s)"
    )
    title = (
        "Planilhas convertidas para texto"
        if len(outcomes) > 1
        else "Planilha convertida para texto"
    )
    result.set_ready(
        frames,
        title,
        f"{state.message} · emojis removidos",
    )
