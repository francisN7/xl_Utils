"""Page wiring for the spreadsheet merge tool."""

import contextlib
from pathlib import Path

import flet as ft

from xl_utils.controllers.merge import inspect_columns, run_merge
from xl_utils.core.tools.merge import (
    ColumnGroup,
    ColumnRef,
    group_by_name,
    move_column,
)
from xl_utils.ui import theme
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.pages.batch import append_outcomes, pending_files
from xl_utils.ui.state import ToolState

_DRAG_GROUP = "merge-columns"
_CARD_WIDTH = 196
_CHIP_WIDTH = 176


class MergeOptions:
    """Draggable board where each column holds the sources of one output."""

    def __init__(self, state: ToolState) -> None:
        self._state = state
        self._files: tuple[Path, ...] = ()
        self._refs: list[ColumnRef] = []
        self._groups: list[list[ColumnRef]] = []
        self._last_refs: tuple[ColumnRef, ...] = ()
        self._ref_by_id: dict[str, ColumnRef] = {}
        self._message = ""

        self._title = ft.Text(
            "Alinhamento de colunas",
            size=theme.FONT_SM,
            weight=ft.FontWeight.BOLD,
        )
        self._hint = ft.Text(size=theme.FONT_XS, color=theme.MUTED)
        self._error = ft.Text(
            "",
            size=theme.FONT_XS,
            color=theme.RED,
            visible=False,
        )
        self._board = ft.Row(wrap=True, spacing=10, run_spacing=10)
        self.control = ft.Column(
            controls=[self._title, self._hint, self._error, self._board],
            spacing=8,
        )
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the board from the files and sheets in the state."""
        files = tuple(self._state.files)
        if files != self._files:
            self._files = files
            self._groups = []
            self._last_refs = ()

        refs, message = self._read_refs()
        if tuple(refs) != self._last_refs:
            self._groups = [list(group.columns) for group in group_by_name(refs)]
            self._last_refs = tuple(refs)
        self._refs = refs
        self._message = message
        self._error.value = ""
        self._store()
        self._render()

    def _read_refs(self) -> tuple[list[ColumnRef], str]:
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
            refs = inspect_columns(sources)
        except Exception as error:  # noqa: BLE001 - shown in the options card
            return [], f"Não foi possível ler as colunas: {error}"

        if not refs:
            return [], "Nenhuma coluna encontrada nas abas marcadas."
        return refs, (
            "Arraste os chips para juntar ou separar colunas; o primeiro de "
            "cada coluna define o cabeçalho. Nomes repetidos recebem sufixo."
        )

    def _store(self) -> None:
        self._state.options["column_groups"] = [
            tuple(group) for group in self._groups if group
        ]

    def _render(self) -> None:
        self._ref_by_id = {
            f"{group_index}:{chip_index}": ref
            for group_index, group in enumerate(self._groups)
            for chip_index, ref in enumerate(group)
        }
        self._board.controls = [
            self._card(group_index, group)
            for group_index, group in enumerate(self._groups)
        ]
        if self._refs:
            self._board.controls.append(self._new_column_button())
        self._hint.value = self._message
        self._hint.visible = bool(self._message)
        self._error.visible = bool(self._error.value)
        self._refresh()

    def _card(self, group_index: int, group: list[ColumnRef]) -> ft.Control:
        controls: list[ft.Control] = []
        if group:
            controls.extend(
                self._chip_target(group_index, chip_index, ref)
                for chip_index, ref in enumerate(group)
            )
        else:
            controls.extend(
                [
                    ft.Text(
                        "Solte uma coluna aqui",
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=14,
                        tooltip="Remover coluna vazia",
                        on_click=lambda _event, index=group_index: self._remove_group(
                            index
                        ),
                    ),
                ]
            )

        controls.append(
            ft.Row(
                controls=[
                    self._add_button(
                        "+ esq.",
                        "Criar uma coluna vazia à esquerda",
                        group_index,
                    ),
                    self._add_button(
                        "+ dir.",
                        "Criar uma coluna vazia à direita",
                        group_index + 1,
                    ),
                ],
                spacing=0,
            )
        )

        content = ft.Container(
            content=ft.Column(controls=controls, spacing=6),
            width=_CARD_WIDTH,
            padding=10,
            bgcolor=theme.BACKGROUND_DEEP,
            border=ft.Border.all(
                1,
                theme.BORDER if group else theme.PURPLE,
            ),
            border_radius=10,
        )
        return ft.DragTarget(
            group=_DRAG_GROUP,
            on_accept=lambda event, index=group_index: self._drop_on_group(
                event,
                index,
            ),
            content=content,
        )

    def _add_button(self, label: str, tooltip: str, target: int) -> ft.Control:
        return ft.TextButton(
            label,
            tooltip=tooltip,
            on_click=lambda _event, index=target: self._add_group(index),
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=4, vertical=0),
                text_style=ft.TextStyle(
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                ),
            ),
        )

    def _chip_target(
        self,
        group_index: int,
        chip_index: int,
        ref: ColumnRef,
    ) -> ft.Control:
        draggable = ft.Draggable(
            group=_DRAG_GROUP,
            data=f"{group_index}:{chip_index}",
            max_simultaneous_drags=1,
            content=self._chip(ref, header=chip_index == 0),
        )
        return ft.DragTarget(
            group=_DRAG_GROUP,
            on_accept=lambda event, group=group_index, chip=chip_index: (
                self._drop_before(event, group, chip)
            ),
            content=draggable,
        )

    def _chip(self, ref: ColumnRef, *, header: bool) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                (
                                    ft.Icons.PUSH_PIN
                                    if header
                                    else ft.Icons.DRAG_INDICATOR
                                ),
                                size=12,
                                color=theme.PURPLE if header else theme.MUTED,
                            ),
                            ft.Text(
                                ref.column,
                                size=theme.FONT_XS,
                                weight=ft.FontWeight.BOLD,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Text(
                        f"{ref.source.name} · {ref.sheet}",
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=0,
            ),
            width=_CHIP_WIDTH,
            padding=ft.Padding.symmetric(vertical=5, horizontal=8),
            bgcolor=theme.SURFACE,
            border=ft.Border.all(
                1,
                theme.PURPLE if header else theme.BORDER,
            ),
            border_radius=8,
            tooltip=f"{ref.source}\n{ref.sheet} · {ref.column}",
        )

    def _new_column_button(self) -> ft.Control:
        return ft.OutlinedButton(
            "Nova coluna",
            icon=ft.Icons.ADD,
            on_click=lambda _event: self._add_group(len(self._groups)),
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                text_style=ft.TextStyle(size=theme.FONT_XS),
            ),
            width=120,
        )

    def _drop_before(self, event, group_index: int, chip_index: int) -> None:
        ref = self._dragged(event)
        if ref is not None:
            self._move(ref, group_index, chip_index)

    def _drop_on_group(self, event, group_index: int) -> None:
        ref = self._dragged(event)
        if ref is None or not 0 <= group_index < len(self._groups):
            return
        self._move(ref, group_index, len(self._groups[group_index]))

    def _dragged(self, event) -> ColumnRef | None:
        data = event.src.data
        if not isinstance(data, str):
            return None
        return self._ref_by_id.get(data)

    def _move(self, ref: ColumnRef, target_group: int, target_index: int) -> None:
        try:
            self._groups = move_column(
                self._groups,
                ref,
                target_group,
                target_index,
            )
        except ValueError as error:
            self._error.value = str(error)
            self._error.visible = True
            self._refresh()
            return

        self._error.value = ""
        self._store()
        self._render()

    def _add_group(self, index: int) -> None:
        self._groups.insert(min(max(index, 0), len(self._groups)), [])
        self._store()
        self._render()

    def _remove_group(self, index: int) -> None:
        if 0 <= index < len(self._groups) and not self._groups[index]:
            del self._groups[index]
            self._store()
            self._render()

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def options(state: ToolState) -> MergeOptions:
    """Build the draggable column board for this page."""
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

    outcome = run_merge(pending, _groups(state) or None)
    append_outcomes(state, [outcome])
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


def _groups(state: ToolState) -> list[ColumnGroup]:
    raw = state.options.get("column_groups")
    if not isinstance(raw, list):
        return []
    groups: list[ColumnGroup] = []
    for columns in raw:
        if not isinstance(columns, (list, tuple)) or not columns:
            continue
        if not all(isinstance(column, ColumnRef) for column in columns):
            continue
        groups.append(ColumnGroup(tuple(columns)))
    return groups
