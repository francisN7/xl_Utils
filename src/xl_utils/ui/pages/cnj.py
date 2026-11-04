"""Page wiring for the CNJ extraction tool."""

import flet as ft
import pandas as pd

from xl_utils.controllers.cnj import run_cnj
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import join_logs, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState


def options(_state: ToolState) -> ft.Control:
    """Return the fixed options of the CNJ extraction."""
    return ft.Column(
        controls=[
            _check("Padronizar para o formato CNJ", True),
            _check("Remover duplicados", True),
        ],
        spacing=4,
    )


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

    result.set_log([f"Lendo {len(pending)} arquivo(s)..."])
    outcomes = [run_cnj(source, selected=selected) for source, selected in pending]
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

    result.set_log(join_logs(outcomes))


def _check(label: str, value: bool = True) -> ft.Checkbox:
    return ft.Checkbox(
        label=label,
        value=value,
        disabled=True,
        label_style=ft.TextStyle(size=theme.FONT_SM),
    )
