"""Chips for choosing which sheets enter each tool run."""

import contextlib
from collections.abc import Callable
from pathlib import Path

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.state import ToolState

Selection = dict[Path, set[str]]


class SheetSelector:
    """Chips per file, plus "Todas"/"Limpar" and a live counter."""

    def __init__(
        self,
        state: ToolState,
        *,
        on_change: Callable[[Selection], None] | None = None,
    ) -> None:
        self._state = state
        self._on_change = on_change
        self._failures: list[str] = []

        self._counter = ft.Text(size=10, color=theme.MUTED)
        self._groups = ft.Column(spacing=10)
        self._empty = ft.Text(size=10, color=theme.MUTED)
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
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color="#B8BCD0",
                            ),
                            self._counter,
                            self._all_button,
                            self._clear_button,
                        ],
                        spacing=8,
                        wrap=True,
                        run_spacing=2,
                    ),
                    self._groups,
                    self._empty,
                ],
                spacing=6,
            ),
            padding=ft.Padding.only(top=4),
        )

        self.refresh()

    def set_failures(self, failures: list[str]) -> None:
        """Show files whose sheet names could not be listed."""
        self._failures = list(failures)

    def refresh(self) -> None:
        """Rebuild the chips from the state and update the counter."""
        state = self._state
        self._counter.value = f"{state.selected_count} de {state.sheet_count}"
        self._all_button.disabled = state.sheet_count == 0
        self._clear_button.disabled = state.sheet_count == 0

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
                        size=9,
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
        self._empty.value, self._empty.color = self._empty_text()
        self._empty.visible = self._empty.value != ""
        self._refresh()

    def _empty_text(self) -> tuple[str, str]:
        if self._state.sheet_count > 0:
            return "", theme.MUTED
        if self._failures:
            detail = "\n".join(self._failures)
            return f"Não foi possível listar as abas:\n{detail}", theme.RED
        if self._state.files:
            return "Nenhuma aba encontrada.", theme.MUTED
        return "Selecione um arquivo para escolher as abas.", theme.MUTED

    def _chip(self, path: Path, name: str, selected: bool) -> ft.Chip:
        return ft.Chip(
            label=name,
            selected=selected,
            show_checkmark=True,
            on_click=lambda _event, item=path, sheet=name: self._toggle(item, sheet),
            bgcolor=theme.BACKGROUND_DEEP,
            selected_color=theme.SUCCESS_BG,
            check_color=theme.GREEN,
            color=theme.TEXT,
            label_text_style=ft.TextStyle(size=10, color=theme.TEXT),
            visual_density=ft.VisualDensity.COMPACT,
            padding=ft.Padding.symmetric(vertical=2, horizontal=6),
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
