"""Ligação da página com a ferramenta de extração de CNJ."""

import pandas as pd

from xl_utils.controllers.cnj import run_cnj
from xl_utils.shared.progress import NullReporter, ProgressReporter
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
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
    for source, selected in pending:
        progress.file_started(source.name)
        outcomes.append(run_cnj(source, selected=selected))
        progress.file_done(source.name)
    append_outcomes(state, outcomes)
    frames = prefixed_frames(
        outcomes,
        lambda outcome: {"PROCESSOS": pd.DataFrame({"PROCESSOS": outcome.cnjs})},
    )
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
