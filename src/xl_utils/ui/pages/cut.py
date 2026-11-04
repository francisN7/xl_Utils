"""Ligação da página com a ferramenta de recorte de planilhas."""

import flet as ft

from xl_utils.controllers.cut import run_cut
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files, prefixed_frames
from xl_utils.ui.state import ToolState

DEFAULT_ROWS = "1000"


def options(state: ToolState) -> ft.Control:
    """Monta o campo editável de linhas por arquivo e o guarda no estado."""
    field = ft.TextField(
        label="Linhas por arquivo",
        value=DEFAULT_ROWS,
        dense=True,
        text_size=theme.FONT_SM,
        label_style=ft.TextStyle(size=theme.FONT_XS),
    )
    state.options["rows_per_file"] = field
    return ft.Column(
        controls=[
            field,
            ft.Text(
                "O resto final fica no último arquivo.",
                size=theme.FONT_XS,
                color=theme.MUTED,
            ),
        ],
        spacing=8,
    )


def run(state: ToolState, result: ResultPanel) -> None:
    """Recorta cada arquivo selecionado e mostra os arquivos gerados."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha uma planilha para recortar em partes.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    rows_per_file = _rows_per_file(state)
    outcomes = [
        run_cut(source, rows_per_file, selected=selected)
        for source, selected in pending
    ]
    append_outcomes(state, outcomes)

    items = [item for outcome in outcomes for item in outcome.items]
    state.save_items = items
    total_outputs = len(items)
    total_rows = sum(outcome.rows for outcome in outcomes)
    if not total_outputs:
        result.set_info(
            "Nenhuma aba encontrada",
            "As planilhas não têm abas para recortar.",
        )
        return

    frames = prefixed_frames(outcomes, lambda outcome: outcome.preview)
    state.result = frames
    state.message = (
        f"{len(outcomes)} arquivo(s), {total_outputs} arquivo(s) gerado(s), "
        f"{total_rows} linha(s)"
    )
    title = "Planilhas recortadas" if len(outcomes) > 1 else "Planilha recortada"
    result.set_ready(
        frames,
        title,
        f"{state.message} · {rows_per_file} linha(s) por arquivo",
    )


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
