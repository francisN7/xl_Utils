"""Common page anatomy: header, input/options, result and action bar."""

import contextlib
from collections.abc import Callable
from pathlib import Path

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.components.file_input import FileInput
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.state import ToolState

RunHandler = Callable[[ToolState, ResultPanel], None]
OptionsFactory = Callable[[ToolState], ft.Control]


class ToolLayout:
    """Shared layout for every tool page."""

    def __init__(
        self,
        title: str,
        description: str,
        *,
        options: OptionsFactory | ft.Control | None = None,
        multiple_files: bool = False,
        run_handler: RunHandler | None = None,
    ) -> None:
        self.state = ToolState()
        self._run_handler = run_handler
        self.file_input = FileInput(
            self._files_changed,
            multiple=multiple_files,
        )
        self.result = ResultPanel()

        self._summary = ft.Text(
            "Nenhum arquivo selecionado.",
            size=11,
            color=theme.MUTED,
        )
        self._run_button = ft.FilledButton(
            "Executar",
            icon=ft.Icons.PLAY_ARROW,
            disabled=True,
            on_click=self._run,
        )

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                title,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                description,
                                size=12,
                                color=theme.MUTED,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Pronto",
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=theme.GREEN,
                        ),
                        bgcolor=theme.SUCCESS_BG,
                        border=ft.Border.all(1, "#2C4A38"),
                        border_radius=999,
                        padding=ft.Padding.symmetric(
                            vertical=5,
                            horizontal=10,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.only(bottom=16),
        )

        left = ft.Column(
            controls=[
                _card(
                    "1. Entrada",
                    self.file_input.control,
                ),
                _card(
                    "2. Opções",
                    _build_options(options, self.state),
                ),
            ],
            spacing=16,
            expand=1,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        right = _card(
            "3. Resultado",
            self.result.control,
            expand=1,
        )

        body = ft.Row(
            controls=[left, right],
            spacing=16,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        action_bar = ft.Column(
            controls=[
                ft.Divider(height=1, color=theme.BORDER),
                ft.Row(
                    controls=[self._summary, self._run_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
        )

        self.control = ft.Container(
            content=ft.Column(
                controls=[header, body, action_bar],
                spacing=0,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def _files_changed(self, files: list[Path]) -> None:
        self.state.select_files(files)
        if files:
            self._summary.value = f"{len(files)} arquivo(s) selecionado(s)."
            self._run_button.disabled = False
        else:
            self._summary.value = "Nenhum arquivo selecionado."
            self._run_button.disabled = True
        self.result.set_idle()
        self._refresh()

    def _run(self, _event=None) -> None:
        if self._run_handler is None:
            self.result.set_info(
                "Ferramenta em migração",
                "A lógica será conectada na sessão desta ferramenta.",
            )
            return
        self.state.running = True
        self.result.set_running()
        try:
            self._run_handler(self.state, self.result)
        except Exception as error:  # noqa: BLE001 - show any failure in the UI
            self.state.running = False
            self.state.error = str(error)
            self.result.set_error(
                "Falha ao executar",
                str(error),
            )
        else:
            self.state.running = False

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def _card(
    title: str,
    content: ft.Control,
    *,
    expand: int | None = None,
) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color="#B8BCD0",
                ),
                content,
            ],
            spacing=10,
            expand=True,
        ),
        padding=16,
        bgcolor=theme.SURFACE,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=12,
        expand=expand,
    )


def _empty_options() -> ft.Control:
    return ft.Text(
        "As opções desta ferramenta entram na sessão de migração.",
        size=11,
        color=theme.MUTED,
    )


def _build_options(
    options: OptionsFactory | ft.Control | None,
    state: ToolState,
) -> ft.Control:
    if options is None:
        return _empty_options()
    if isinstance(options, ft.Control):
        return options
    return options(state)
