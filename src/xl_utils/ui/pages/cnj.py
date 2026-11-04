"""Page wiring for the CNJ extraction tool."""

import pandas as pd

from xl_utils.controllers.cnj import run_cnj
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState


def run(state: ToolState, result: ResultPanel) -> None:
    """Extract CNJs from every selected file and show the batch outcome."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para extrair as numerações CNJ.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    outcomes = [run_cnj(source, selected=selected) for source, selected in pending]
    append_outcomes(state, outcomes)
    frames = prefixed_frames(
        outcomes,
        lambda outcome: {"PROCESSOS": pd.DataFrame({"PROCESSOS": outcome.cnjs})},
    )
    state.result = frames

    unique = sum(len(outcome.cnjs) for outcome in outcomes)
    duplicates = sum(outcome.duplicates for outcome in outcomes)
    if unique:
        state.message = f"{len(outcomes)} arquivo(s), {unique} CNJ(s) único(s)"
        title = (
            "Listas de CNJs geradas" if len(outcomes) > 1 else "Lista de CNJs gerada"
        )
        result.set_success(
            outcomes[0].output,
            frames,
            title,
            f"{state.message} · {duplicates} duplicado(s)",
        )
    else:
        state.message = "Nenhum CNJ encontrado"
        result.set_success(
            outcomes[0].output,
            frames,
            state.message,
            "A planilha não contém numeração no padrão CNJ."
            if len(outcomes) == 1
            else "As planilhas não contêm numeração no padrão CNJ.",
        )
