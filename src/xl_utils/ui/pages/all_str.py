"""Page wiring for the text treatment tool."""

import flet as ft

from xl_utils.controllers.all_str import run_all_str
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState


def options(_state: ToolState) -> ft.Control:
    """Return the fixed options of the text pipeline."""
    return ft.Column(
        controls=[
            _check("Remover emojis", True),
            _check("Reparar metadados se a leitura falhar", True),
            ft.Text(
                "Sempre aplicado antes das demais ferramentas.",
                size=theme.FONT_XS,
                color=theme.MUTED,
            ),
        ],
        spacing=4,
    )


def run(state: ToolState, result: ResultPanel) -> None:
    """Run the pipeline for every selected file and show the batch outcome."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para converter para texto.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    outcomes = [run_all_str(source, selected=selected) for source, selected in pending]
    append_outcomes(state, outcomes)
    frames = prefixed_frames(outcomes, lambda outcome: outcome.sheets)
    state.result = frames

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
    result.set_success(
        outcomes[0].output,
        frames,
        title,
        f"{state.message} · emojis removidos",
    )


def _check(label: str, value: bool = True) -> ft.Checkbox:
    return ft.Checkbox(
        label=label,
        value=value,
        disabled=True,
        label_style=ft.TextStyle(size=theme.FONT_SM),
    )
