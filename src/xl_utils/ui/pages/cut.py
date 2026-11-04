"""Page wiring for the spreadsheet cut tool."""

import flet as ft

from xl_utils.controllers.cut import run_cut
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.state import ToolState

DEFAULT_ROWS = "1000"


def options(state: ToolState) -> ft.Control:
    """Build the editable rows-per-file field and keep it in the state."""
    field = ft.TextField(
        label="Linhas por arquivo",
        value=DEFAULT_ROWS,
        dense=True,
    )
    state.options["rows_per_file"] = field
    return ft.Column(
        controls=[
            field,
            ft.Text(
                "O resto final fica no último arquivo.",
                size=10,
                color=theme.MUTED,
            ),
        ],
        spacing=8,
    )


def run(state: ToolState, result: ResultPanel) -> None:
    """Cut the selected file and show the generated files."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para recortar em partes.",
        )
        return

    source = state.files[0]
    rows_per_file = _rows_per_file(state)
    result.set_log([f"Lendo {source.name}..."])

    outcome = run_cut(source, rows_per_file)
    if not outcome.outputs:
        result.set_info(
            "Nenhuma aba encontrada",
            "A planilha não tem abas para recortar.",
        )
        result.set_log(outcome.log)
        return

    state.result = outcome.preview
    state.message = f"{outcome.files} arquivo(s), {outcome.rows} linha(s)"
    result.set_success(
        outcome.outputs[0],
        outcome.preview,
        "Planilha recortada",
        f"{state.message} · {rows_per_file} linha(s) por arquivo",
    )
    result.set_log(outcome.log)


def _rows_per_file(state: ToolState) -> int:
    control = state.options.get("rows_per_file")
    raw = control.value if isinstance(control, ft.TextField) else DEFAULT_ROWS
    try:
        value = int(raw.strip())
    except AttributeError, ValueError:
        raise ValueError("Informe um número inteiro de linhas por arquivo.") from None

    if value <= 0:
        raise ValueError("O número de linhas por arquivo deve ser maior que zero.")
    return value
