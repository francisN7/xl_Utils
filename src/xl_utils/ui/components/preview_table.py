"""Read-only spreadsheet preview limited to the first rows."""

import contextlib

import flet as ft
import pandas as pd

from xl_utils.ui import theme

MAX_ROWS = 100


class PreviewTable:
    """Shows the first rows of one result sheet."""

    def __init__(self) -> None:
        self._frames: dict[str, pd.DataFrame] = {}
        self._sheet = ft.Dropdown(
            visible=False,
            dense=True,
            width=180,
            text_size=11,
            on_select=self._sheet_changed,
        )
        self._empty = ft.Text(
            "Nenhum resultado para pré-visualizar.",
            size=11,
            color=theme.MUTED,
        )
        self._body = ft.Container(expand=True)
        self.control = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Prévia",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self._sheet,
                    ],
                    spacing=12,
                ),
                self._empty,
                self._body,
            ],
            spacing=8,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def set_frames(self, frames: dict[str, pd.DataFrame] | None) -> None:
        self._frames = dict(frames or {})
        names = list(self._frames)

        if not names:
            self._sheet.visible = False
            self._empty.visible = True
            self._body.content = None
        else:
            self._sheet.options = [
                ft.DropdownOption(key=name, text=name) for name in names
            ]
            self._sheet.value = names[0]
            self._sheet.visible = len(names) > 1
            self._empty.visible = False
            self._show(names[0])

        self._refresh()

    def set_frame(self, frame: pd.DataFrame | None, name: str = "Planilha1") -> None:
        self.set_frames({name: frame} if frame is not None else None)

    def _sheet_changed(self, _event=None) -> None:
        if self._sheet.value:
            self._show(self._sheet.value)
            self._refresh()

    def _show(self, name: str) -> None:
        self._body.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[self._build_table(self._frames[name])],
                    scroll=ft.ScrollMode.AUTO,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_table(self, frame: pd.DataFrame) -> ft.DataTable:
        columns = [
            ft.DataColumn(
                label=ft.Text(
                    str(column),
                    size=10,
                    weight=ft.FontWeight.BOLD,
                )
            )
            for column in frame.columns
        ]
        rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(_cell(value), size=10)) for value in row]
            )
            for row in frame.head(MAX_ROWS).itertuples(index=False, name=None)
        ]

        return ft.DataTable(
            columns=columns,
            rows=rows,
            heading_row_color=theme.BACKGROUND_DEEP,
            heading_text_style=ft.TextStyle(
                color=theme.MUTED,
                size=10,
                weight=ft.FontWeight.BOLD,
            ),
            data_text_style=ft.TextStyle(color=theme.TEXT, size=10),
            border=ft.Border.all(1, theme.BORDER),
            border_radius=8,
            column_spacing=18,
            horizontal_margin=10,
            data_row_min_height=32,
            data_row_max_height=36,
        )

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def _cell(value: object) -> str:
    try:
        if pd.isna(value):
            return ""
    except TypeError, ValueError:
        pass
    return str(value)
