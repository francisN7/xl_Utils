"""Page wiring for the text treatment tool."""

import flet as ft

from xl_utils.controllers.all_str import run_all_str
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.state import ToolState


def options(_state: ToolState) -> ft.Control:
    """Return the fixed options of the text pipeline."""
    return ft.Column(
        controls=[
            _check("Remover emojis", True),
            _check("Reparar metadados se a leitura falhar", True),
            ft.Text(
                "Sempre aplicado antes das demais ferramentas.",
                size=10,
            ),
        ],
        spacing=4,
    )


def run(state: ToolState, result: ResultPanel) -> None:
    """Run the pipeline for the selected file and show its outcome."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para converter para texto.",
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

    outcome = run_all_str(source, selected=selected)
    state.result = outcome.sheets
    state.message = f"{len(outcome.sheets)} aba(s), {outcome.rows} linha(s)"

    result.set_success(
        outcome.output,
        outcome.sheets,
        "Planilha convertida para texto",
        f"{state.message} · emojis removidos",
    )
    result.set_log(outcome.log)


def _check(label: str, value: bool = True) -> ft.Checkbox:
    return ft.Checkbox(label=label, value=value, disabled=True)
