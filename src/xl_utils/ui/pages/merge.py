"""Page wiring for the spreadsheet merge tool."""

import contextlib
from pathlib import Path

import flet as ft

from xl_utils.controllers.merge import inspect_columns, run_merge
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import pending_files
from xl_utils.ui.state import ToolState


class MergeOptions:
    """One dropdown per distinct column, mapping it to a canonical name."""

    def __init__(self, state: ToolState) -> None:
        self._state = state
        self._files: tuple[Path, ...] = ()
        self._column_map: dict[str, str] = {}
        self._hint = ft.Text(size=theme.FONT_XS, color=theme.MUTED)
        self._rows = ft.Column(spacing=6)
        self.control = ft.Column(
            controls=[self._hint, self._rows],
            spacing=8,
        )
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the dropdowns from the files and sheets in the state."""
        files = tuple(self._state.files)
        if files != self._files:
            self._files = files
            self._column_map = {}

        columns, message = self._columns()
        self._column_map = {
            column: self._column_map.get(column, column) for column in columns
        }
        self._state.options["column_map"] = dict(self._column_map)

        self._hint.value = message
        self._hint.visible = bool(message)
        self._rows.controls = (
            [self._dropdown(column, columns) for column in columns]
            if len(columns) > 1
            else []
        )
        self._refresh()

    def _columns(self) -> tuple[list[str], str]:
        state = self._state
        if not state.files:
            return [], "Selecione os arquivos para alinhar as colunas."
        if not state.sheet_names:
            return [], "Lendo as abas..."
        if any(not state.selected_sheets.get(path, set()) for path in state.files):
            return [], "Marque ao menos uma aba em cada arquivo."

        sources = [
            (path, state.selected_sheets.get(path, set())) for path in state.files
        ]
        try:
            columns = inspect_columns(sources)
        except Exception as error:  # noqa: BLE001 - shown in the options card
            return [], f"Não foi possível ler as colunas: {error}"

        if len(columns) <= 1:
            return columns, "Não há colunas diferentes para alinhar."
        return columns, "Colunas com o mesmo nome já ficam alinhadas."

    def _dropdown(self, column: str, columns: list[str]) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Text(
                    column,
                    size=theme.FONT_SM,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    tooltip=column,
                ),
                ft.Dropdown(
                    value=self._column_map.get(column, column),
                    options=[
                        ft.DropdownOption(key=name, text=name) for name in columns
                    ],
                    dense=True,
                    text_size=theme.FONT_XS,
                    width=170,
                    on_select=lambda event, source=column: self._mapped(
                        source,
                        event.control.value or source,
                    ),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _mapped(self, column: str, canonical: str) -> None:
        self._column_map[column] = canonical
        self._state.options["column_map"] = dict(self._column_map)

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def options(state: ToolState) -> MergeOptions:
    """Build the column alignment controls for this page."""
    return MergeOptions(state)


def run(state: ToolState, result: ResultPanel) -> None:
    """Merge every selected file and sheet into one workbook."""
    if not state.files:
        result.set_info(
            "Selecione um arquivo",
            "Escolha ao menos duas abas ou dois arquivos para mesclar.",
        )
        return

    pending = pending_files(state, result)
    if pending is None:
        return

    result.set_log([f"Lendo {len(pending)} arquivo(s)..."])
    outcome = run_merge(pending, _column_map(state))
    frames = {"Mesclado": outcome.merged}
    state.result = frames
    state.message = (
        f"{outcome.sheets} aba(s), {outcome.rows} linha(s), {outcome.columns} coluna(s)"
    )
    result.set_success(
        outcome.output,
        frames,
        "Planilhas mescladas",
        f"{state.message} · {len(pending)} arquivo(s)",
    )
    result.set_log(outcome.log)


def _column_map(state: ToolState) -> dict[str, str]:
    mapping = state.options.get("column_map")
    if not isinstance(mapping, dict):
        return {}
    return {str(column): str(canonical) for column, canonical in mapping.items()}
