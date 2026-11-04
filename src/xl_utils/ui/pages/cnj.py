"""Ligação da página com a ferramenta de extração de CNJ."""

import pandas as pd

from xl_utils.controllers.cnj import run_cnj
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import (
    append_outcomes,
    pending_files,
    prefixed_frames,
    report_cancelled,
)
from xl_utils.ui.state import ToolState


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
) -> None:
    """Extrai CNJs de cada arquivo selecionado e mostra o lote."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para extrair as numerações CNJ.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    outcomes = []
    cancelled = False
    for source, selected in pending:
        if token.cancelled:
            cancelled = True
            break
        progress.file_started(source.name)
        outcome = run_cnj(source, selected=selected)
        outcomes.append(outcome)
        progress.file_done(source.name)
        progress.log(outcome.log)
    append_outcomes(state, outcomes)
    frames = prefixed_frames(
        outcomes,
        lambda outcome: {"PROCESSOS": pd.DataFrame({"PROCESSOS": outcome.cnjs})},
    )
    if cancelled:
        report_cancelled(state, result, frames, len(outcomes), len(pending))
        return
    state.result = frames
    state.save_items = [outcome.item for outcome in outcomes]

    unique = sum(len(outcome.cnjs) for outcome in outcomes)
    duplicates = sum(outcome.duplicates for outcome in outcomes)
    if unique:
        state.message = f"{len(outcomes)} arquivo(s), {unique} CNJ(s) único(s)"
        title = (
            "Listas de CNJs geradas" if len(outcomes) > 1 else "Lista de CNJs gerada"
        )
        result.set_ready(
            frames,
            title,
            f"{state.message} · {duplicates} duplicado(s)",
        )
    else:
        state.message = "Nenhum CNJ encontrado"
        result.set_ready(
            frames,
            state.message,
            "A planilha não contém numeração no padrão CNJ."
            if len(outcomes) == 1
            else "As planilhas não contêm numeração no padrão CNJ.",
        )
