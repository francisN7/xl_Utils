"""Chips clicáveis para escolher quais abas entram em cada execução."""

import contextlib
from collections.abc import Callable
from pathlib import Path

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.state import ToolState

Selection = dict[Path, set[str]]

_SELECTED_BG = "#2D2A47"
_CHIP_TEXT = "#B8BCD0"


class SheetSelector:
    """Chips por arquivo, além de "Todas"/"Limpar" e um contador ao vivo."""

    def __init__(
        self,
        state: ToolState,
        *,
        on_change: Callable[[Selection], None] | None = None,
    ) -> None:
        self._state = state
        self._on_change = on_change
        self._failures: list[str] = []
        self._loading = False

        self._counter = ft.Text(size=theme.FONT_XS, color=theme.MUTED)
        self._groups = ft.Column(spacing=10)
        self._empty = ft.Text(size=theme.FONT_XS, color=theme.MUTED)
        self._spinner = ft.ProgressRing(
            width=14,
            height=14,
            stroke_width=2,
            color=theme.PURPLE,
        )
        self._loading_text = ft.Text(
            "Lendo as abas...",
            size=theme.FONT_XS,
            color=theme.PURPLE,
        )
        self._loading_row = ft.Row(
            controls=[self._spinner, self._loading_text],
            spacing=8,
            visible=False,
        )
        self._all_button = ft.TextButton(
            "Todas",
            on_click=self._select_all,
            style=ft.ButtonStyle(padding=8),
        )
        self._clear_button = ft.TextButton(
            "Limpar",
            on_click=self._clear,
            style=ft.ButtonStyle(padding=8),
        )

        self.control = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Abas",
                                size=theme.FONT_XS,
                                weight=ft.FontWeight.BOLD,
                                color=_CHIP_TEXT,
                            ),
                            self._counter,
                            self._all_button,
                            self._clear_button,
                        ],
                        spacing=8,
                        wrap=True,
                        run_spacing=2,
                    ),
                    self._loading_row,
                    self._groups,
                    self._empty,
                ],
                spacing=6,
            ),
            padding=ft.Padding.only(top=4),
        )

        self.refresh()

    def set_failures(self, failures: list[str]) -> None:
        """Mostra os arquivos cujas abas não puderam ser listadas."""
        self._failures = list(failures)

    def set_loading(self, loading: bool) -> None:
        """Mostra uma linha de progresso enquanto as abas são listadas."""
        self._loading = loading
        self.refresh()

    def refresh(self) -> None:
        """Reconstrói os chips a partir do estado e atualiza o contador."""
        state = self._state
        self._loading_row.visible = self._loading
        self._groups.visible = not self._loading
        self._counter.value = (
            "lendo..."
            if self._loading
            else f"{state.selected_count} de {state.sheet_count}"
        )
        self._all_button.disabled = self._loading or state.sheet_count == 0
        self._clear_button.disabled = self._loading or state.sheet_count == 0

        if self._loading:
            self._groups.controls = []
            self._empty.visible = False
        else:
            self._render_groups()
            self._empty.value, self._empty.color = self._empty_text()
            self._empty.visible = self._empty.value != ""

        self._refresh()

    def _render_groups(self) -> None:
        state = self._state
        multiple = len(state.files) > 1
        groups: list[ft.Control] = []
        for path in state.files:
            names = state.sheet_names.get(path, [])
            if not names:
                continue
            selected = state.selected_sheets.get(path, set())
            controls: list[ft.Control] = []
            if multiple:
                controls.append(
                    ft.Text(
                        f"{path.name} · {len(names)} aba(s)",
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                    )
                )
            controls.append(
                ft.Row(
                    controls=[
                        self._chip(path, name, name in selected) for name in names
                    ],
                    spacing=6,
                    run_spacing=6,
                    wrap=True,
                )
            )
            groups.append(ft.Column(controls=controls, spacing=4))

        self._groups.controls = groups

    def _empty_text(self) -> tuple[str, str]:
        if self._state.sheet_count > 0:
            return "", theme.MUTED
        if self._failures:
            detail = "\n".join(self._failures)
            return f"Não foi possível listar as abas:\n{detail}", theme.RED
        if self._state.files:
            return "Nenhuma aba encontrada.", theme.MUTED
        return "Selecione um arquivo para escolher as abas.", theme.MUTED

    def _chip(self, path: Path, name: str, selected: bool) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK,
                        size=12,
                        color=theme.PURPLE,
                        visible=selected,
                    ),
                    ft.Text(
                        name,
                        size=theme.FONT_XS,
                        color=theme.TEXT if selected else _CHIP_TEXT,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=4,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=_SELECTED_BG if selected else theme.BACKGROUND_DEEP,
            border=ft.Border.all(1, theme.PURPLE if selected else theme.BORDER),
            border_radius=999,
            padding=ft.Padding.symmetric(vertical=6, horizontal=10),
            ink=True,
            on_click=lambda _event, item=path, sheet=name: self._toggle(item, sheet),
            tooltip=f"{name} (clique para alternar)",
        )

    def _toggle(self, path: Path, name: str) -> None:
        selected = self._state.selected_sheets.setdefault(path, set())
        if name in selected:
            selected.discard(name)
        else:
            selected.add(name)
        self._notify()

    def _select_all(self, _event=None) -> None:
        for path, names in self._state.sheet_names.items():
            self._state.selected_sheets[path] = set(names)
        self._notify()

    def _clear(self, _event=None) -> None:
        for path in self._state.sheet_names:
            self._state.selected_sheets[path] = set()
        self._notify()

    def _notify(self) -> None:
        self.refresh()
        if self._on_change is not None:
            self._on_change(
                {
                    path: set(names)
                    for path, names in self._state.selected_sheets.items()
                }
            )

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()
