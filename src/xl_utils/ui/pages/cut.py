"""Ligação da página com a ferramenta de recorte de planilhas."""

import contextlib

import flet as ft

from xl_utils.controllers.cut import run_cut
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import (
    append_outcomes,
    pending_files,
    prefixed_frames,
    report_cancelled,
)
from xl_utils.ui.state import ToolState

DEFAULT_ROWS = "1000"
DEFAULT_PARTS = "2"
MODE_ROWS = "rows"
MODE_PARTS = "parts"


def options(state: ToolState) -> ft.Control:
    """Monta o seletor de modo e o campo numérico correspondente."""
    mode = ft.Dropdown(
        label="Modo de recorte",
        value=MODE_ROWS,
        dense=True,
        text_size=theme.FONT_SM,
        label_style=ft.TextStyle(size=theme.FONT_XS),
        options=[
            ft.DropdownOption(key=MODE_ROWS, text="Linhas por arquivo"),
            ft.DropdownOption(key=MODE_PARTS, text="Arquivos por aba"),
        ],
    )
    rows_field = _number_field("Linhas por arquivo", DEFAULT_ROWS)
    parts_field = _number_field(
        "Arquivos por aba",
        DEFAULT_PARTS,
        visible=False,
    )
    hint = ft.Text(
        "O resto final fica no último arquivo.",
        size=theme.FONT_XS,
        color=theme.MUTED,
    )
    state.options["cut_mode"] = mode
    state.options["rows_per_file"] = rows_field
    state.options["files_per_sheet"] = parts_field

    column = ft.Column(
        controls=[mode, rows_field, parts_field, hint],
        spacing=8,
    )

    def mode_changed(_event=None) -> None:
        uses_parts = mode.value == MODE_PARTS
        rows_field.visible = not uses_parts
        parts_field.visible = uses_parts
        hint.value = (
            "Divide cada aba em N arquivos; a quantidade vale por aba."
            if uses_parts
            else "O resto final fica no último arquivo."
        )
        with contextlib.suppress(RuntimeError):
            column.update()

    mode.on_select = mode_changed
    return column


def run(
    state: ToolState,
    result: ResultPanel,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
) -> None:
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

    mode, value = _split_settings(state)
    outcomes = []
    cancelled = False
    for source, selected in pending:
        if token.cancelled:
            cancelled = True
            break
        progress.file_started(source.name)
        if mode == MODE_PARTS:
            outcome = run_cut(
                source,
                parts=value,
                selected=selected,
                progress=progress,
            )
        else:
            outcome = run_cut(
                source,
                value,
                selected=selected,
                progress=progress,
            )
        outcomes.append(outcome)
        progress.file_done(source.name)
    append_outcomes(state, outcomes)

    items = [item for outcome in outcomes for item in outcome.items]
    frames = prefixed_frames(outcomes, lambda outcome: outcome.preview)
    if cancelled:
        report_cancelled(state, result, frames, len(outcomes), len(pending))
        return
    state.save_items = items
    total_outputs = len(items)
    total_rows = sum(outcome.rows for outcome in outcomes)
    if not total_outputs:
        result.set_info(
            "Nenhuma aba encontrada",
            "As planilhas não têm abas para recortar.",
        )
        return

    state.result = frames
    state.message = (
        f"{len(outcomes)} arquivo(s), {total_outputs} arquivo(s) gerado(s), "
        f"{total_rows} linha(s)"
    )
    title = "Planilhas recortadas" if len(outcomes) > 1 else "Planilha recortada"
    result.set_ready(
        frames,
        title,
        f"{state.message} · {_rule_text(mode, value)}",
    )


def _number_field(label: str, value: str, *, visible: bool = True) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        dense=True,
        text_size=theme.FONT_SM,
        label_style=ft.TextStyle(size=theme.FONT_XS),
        visible=visible,
    )


def _split_settings(state: ToolState) -> tuple[str, int]:
    mode = _mode(state)
    if mode == MODE_PARTS:
        value = _int_option(state, "files_per_sheet", DEFAULT_PARTS, "arquivos por aba")
        problem = "A quantidade de arquivos por aba deve ser maior que zero."
    else:
        value = _int_option(state, "rows_per_file", DEFAULT_ROWS, "linhas por arquivo")
        problem = "O número de linhas por arquivo deve ser maior que zero."
    if value <= 0:
        raise ValueError(problem)
    return mode, value


def _mode(state: ToolState) -> str:
    control = state.options.get("cut_mode")
    raw = control.value if isinstance(control, ft.Dropdown) else MODE_ROWS
    return MODE_PARTS if raw == MODE_PARTS else MODE_ROWS


def _int_option(state: ToolState, key: str, default: str, label: str) -> int:
    control = state.options.get(key)
    raw = control.value if isinstance(control, ft.TextField) else default
    try:
        return int(raw.strip())
    except AttributeError, ValueError:
        raise ValueError(f"Informe um número inteiro de {label}.") from None


def _rule_text(mode: str, value: int) -> str:
    if mode == MODE_PARTS:
        return f"{value} arquivo(s) por aba"
    return f"{value} linha(s) por arquivo"
