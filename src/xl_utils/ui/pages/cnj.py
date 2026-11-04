"""Page wiring for the CNJ extraction tool."""

import flet as ft
import pandas as pd

from xl_utils.controllers.cnj import run_cnj
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
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
    """Extract CNJs from the selected file and show the outcome."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para extrair as numerações CNJ.",
        )
        return

    source = state.files[0]
    selected = state.selected_sheets.get(source)
    if selected is not None and not selected:
        result.set_info(
            "Selecione ao menos uma aba",
            "Marque uma aba em “1. Entrada” antes de executar.",
        )
        return

    result.set_log([f"Lendo {source.name}..."])

    outcome = run_cnj(source, selected=selected)
    frames = {"PROCESSOS": pd.DataFrame({"PROCESSOS": outcome.cnjs})}
    state.result = frames

    if outcome.cnjs:
        state.message = f"{len(outcome.cnjs)} CNJ(s) único(s)"
        result.set_success(
            outcome.output,
            frames,
            "Lista de CNJs gerada",
            f"{state.message} · {outcome.duplicates} duplicado(s)",
        )
    else:
        state.message = "Nenhum CNJ encontrado"
        result.set_success(
            outcome.output,
            frames,
            state.message,
            "A planilha não contém numeração no padrão CNJ.",
        )

    result.set_log(outcome.log)


def _check(label: str, value: bool = True) -> ft.Checkbox:
    return ft.Checkbox(
        label=label,
        value=value,
        disabled=True,
        label_style=ft.TextStyle(size=theme.FONT_SM),
    )
