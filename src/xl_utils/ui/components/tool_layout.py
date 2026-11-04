"""Common page anatomy: header, input/options, result and action bar."""

import asyncio
import contextlib
from collections.abc import Callable
from pathlib import Path

import flet as ft

from xl_utils.core.io import list_sheets
from xl_utils.ui import theme
from xl_utils.ui.components.file_input import FileInput
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.sheet_selector import SheetSelector
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
        self._sheet_loading = False
        self.sheet_selector = SheetSelector(
            self.state,
            on_change=self._selection_changed,
        )

        self._summary = ft.Text(
            "Nenhum arquivo selecionado.",
            size=theme.FONT_SM,
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
                                size=theme.FONT_TITLE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                description,
                                size=theme.FONT_SM,
                                color=theme.MUTED,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Pronto",
                            size=theme.FONT_XS,
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

        entrada = ft.Column(
            controls=[
                self.file_input.control,
                ft.Divider(height=1, color=theme.BORDER),
                self.sheet_selector.control,
            ],
            spacing=10,
        )

        left = ft.Column(
            controls=[
                _card(
                    "1. Entrada",
                    entrada,
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
        self.sheet_selector.set_failures([])
        self.sheet_selector.refresh()
        if files:
            self._summary.value = f"{len(files)} arquivo(s) selecionado(s)."
            self._run_button.disabled = False
        else:
            self._summary.value = "Nenhum arquivo selecionado."
            self._run_button.disabled = True
        self.result.set_idle()
        self._refresh()
        self._start_sheet_load()

    def _start_sheet_load(self) -> None:
        if not self.state.files:
            self._sheet_loading = False
            self.sheet_selector.set_loading(False)
            return
        self._sheet_loading = True
        self.sheet_selector.set_loading(True)
        self._run_button.disabled = True
        page = self.control.page
        if page is None:
            names, failures = self._read_sheet_names(list(self.state.files))
            self._apply_sheet_names(names, failures)
            return
        page.run_task(self._load_sheet_names)

    async def _load_sheet_names(self) -> None:
        files = list(self.state.files)
        names, failures = await asyncio.to_thread(self._read_sheet_names, files)
        if list(self.state.files) != files:
            return
        self._apply_sheet_names(names, failures)

    @staticmethod
    def _read_sheet_names(
        files: list[Path],
    ) -> tuple[dict[Path, list[str]], list[str]]:
        names: dict[Path, list[str]] = {}
        failures: list[str] = []
        for path in files:
            try:
                names[path] = list_sheets(path)
            except Exception as error:  # noqa: BLE001 - shown in the selector
                failures.append(f"{path.name}: {error}")
        return names, failures

    def _apply_sheet_names(
        self,
        names: dict[Path, list[str]],
        failures: list[str],
    ) -> None:
        self.state.set_sheet_names(names)
        self.sheet_selector.set_failures(failures)
        self._sheet_loading = False
        self.sheet_selector.set_loading(False)
        self._run_button.disabled = not self.state.files
        self._selection_changed(self.state.selected_sheets)

    def _selection_changed(self, selection: dict[Path, set[str]]) -> None:
        if not self.state.files:
            return
        total = sum(len(names) for names in selection.values())
        self._summary.value = f"{len(self.state.files)} arquivo(s), {total} aba(s)."
        self._refresh()

    def _run(self, _event=None) -> None:
        if self._sheet_loading:
            self.result.set_info(
                "Lendo as abas...",
                "Aguarde a lista de abas terminar de carregar.",
            )
            return
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
                    size=theme.FONT_SM,
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
        size=theme.FONT_SM,
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
