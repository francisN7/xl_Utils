"""Common page anatomy: header, input/options, result and action bar."""

import asyncio
import contextlib
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

import flet as ft

from xl_utils.core.io import list_sheets
from xl_utils.core.mime import FormatCheck, check_format
from xl_utils.core.tools.all_str import WorkbookReadError
from xl_utils.shared.log import RunLog, build_diagnostics
from xl_utils.ui import theme
from xl_utils.ui.components.file_input import FileInput
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.sheet_selector import SheetSelector
from xl_utils.ui.state import ToolState

RunHandler = Callable[[ToolState, ResultPanel], None]


class OptionsPanel(Protocol):
    """Options control that rebuilds itself when the input changes."""

    control: ft.Control

    def refresh(self) -> None: ...


OptionsFactory = Callable[[ToolState], ft.Control | OptionsPanel]


class ToolLayout:
    """Shared layout for every tool page."""

    def __init__(
        self,
        title: str,
        description: str,
        *,
        options: OptionsFactory | ft.Control | None = None,
        note: str = "",
        multiple_files: bool = False,
        default_all_sheets: bool = False,
        run_handler: RunHandler | None = None,
    ) -> None:
        self.state = ToolState()
        self._title = title
        self._run_handler = run_handler
        self._default_all_sheets = default_all_sheets
        self.file_input = FileInput(
            self._files_changed,
            multiple=multiple_files,
        )
        self.result = ResultPanel()
        self._formats: dict[Path, FormatCheck] = {}
        self._sheet_loading = False
        self.sheet_selector = SheetSelector(
            self.state,
            on_change=self._selection_changed,
        )

        self._summary = ft.Text(
            "Nenhum arquivo selecionado.",
            size=theme.FONT_SM,
            color=theme.MUTED,
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
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

        entrada_controls: list[ft.Control] = [
            self.file_input.control,
            ft.Divider(height=1, color=theme.BORDER),
            self.sheet_selector.control,
        ]
        if note:
            entrada_controls.append(
                ft.Text(
                    note,
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                )
            )
        entrada = ft.Column(
            controls=entrada_controls,
            spacing=10,
        )

        options_control, self._options_refresh = _build_options(
            options,
            self.state,
        )
        left_controls: list[ft.Control] = [_card("1. Entrada", entrada)]
        if options_control is not None:
            left_controls.append(_card("2. Opções", options_control))
        left = ft.Column(
            controls=left_controls,
            spacing=16,
            expand=1,
            scroll=ft.ScrollMode.HIDDEN,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        result_step = "3" if options_control is not None else "2"
        right = ft.Column(
            controls=[
                _card(
                    f"{result_step}. Resultado",
                    self.result.control,
                )
            ],
            spacing=16,
            expand=1,
            scroll=ft.ScrollMode.HIDDEN,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        body = ft.Row(
            controls=[left, right],
            spacing=16,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        action_bar = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Divider(height=1, color=theme.BORDER),
                    ft.Row(
                        controls=[self._summary, self._run_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.only(top=16),
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
        self._check_formats()
        self.sheet_selector.set_failures([])
        self.sheet_selector.refresh()
        if files:
            self._summary.value = f"{len(files)} arquivo(s) selecionado(s)."
            self._run_button.disabled = False
        else:
            self._summary.value = "Nenhum arquivo selecionado."
            self._run_button.disabled = True
        self.result.set_idle()
        self._refresh_options()
        self._refresh()
        self._start_sheet_load()

    def _check_formats(self) -> list[FormatCheck]:
        """Detect the real format of every file and show it in the entry."""
        checks = [check_format(path) for path in self.state.files]
        self._formats = {check.path: check for check in checks}
        self.file_input.set_formats(checks)
        return checks

    def _start_sheet_load(self) -> None:
        if not self.state.files:
            self._sheet_loading = False
            self.sheet_selector.set_loading(False)
            return
        self._sheet_loading = True
        self.sheet_selector.set_loading(True)
        self._run_button.disabled = True
        try:
            page = self.control.page
        except RuntimeError:
            page = None
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
        self.state.set_sheet_names(
            names,
            all_sheets=self._default_all_sheets,
        )
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
        self._refresh_options()
        self._refresh()

    def _refresh_options(self) -> None:
        if self._options_refresh is not None:
            self._options_refresh()

    def _run(self, _event=None) -> None:
        if self._sheet_loading:
            self.result.set_info(
                "Lendo as abas...",
                "Aguarde a lista de abas terminar de carregar.",
            )
            return
        checks = self._check_formats()
        blocked = [check for check in checks if not check.identified]
        if blocked:
            self._block_formats(blocked)
            return
        if self._run_handler is None:
            self.result.set_info(
                "Ferramenta em migração",
                "A lógica será conectada na sessão desta ferramenta.",
            )
            return
        self.state.running = True
        self.state.message = ""
        self.state.error = None
        self.state.error_detail = None
        log = RunLog()
        for check in checks:
            if check.diverges:
                log.warning(
                    f"{check.path.name}: conteúdo {check.detected} · "
                    f"nome {check.declared}; lido como {check.effective}"
                )
            else:
                log.info(f"{check.path.name}: lido como {check.effective}")
        log.info(f"Lendo {len(self.state.files)} arquivo(s)...")
        self.state.log = log
        self.result.set_running()
        failure: BaseException | None = None
        try:
            self._run_handler(self.state, self.result)
        except WorkbookReadError as error:
            failure = error
            self._fail(error, "Não foi possível ler a planilha")
        except ValueError as error:
            failure = error
            self._fail(error, "Confira a seleção")
        except Exception as error:  # noqa: BLE001 - show any failure in the UI
            failure = error
            self._fail(error, "Falha inesperada", include_type=True)
        else:
            if self.result.kind == "success":
                log.success(f"Concluído: {self.result.status}")
            elif self.result.kind == "info":
                log.warning(self.result.status)
        finally:
            self.state.running = False
            self.result.set_log(log)
            self.result.set_diagnostics(self._diagnostics(failure))

    def _block_formats(self, failures: list[FormatCheck]) -> None:
        """Stop the run before reading when no format can be identified."""
        detail = "; ".join(f"{check.path.name}: {check.reason}" for check in failures)
        log = RunLog().error(f"Formato não identificado: {detail}")
        self.state.running = False
        self.state.message = ""
        self.state.error = detail
        self.state.error_detail = None
        self.state.log = log
        self.result.set_error("Não foi possível identificar o formato", detail)
        self.result.set_log(log)
        self.result.set_diagnostics(self._diagnostics(None))

    def _fail(
        self,
        error: BaseException,
        title: str,
        *,
        include_type: bool = False,
    ) -> None:
        """Show the friendly title, keep the original message and the trace."""
        self.state.error = str(error)
        self.state.error_detail = traceback.format_exc()
        detail = f"{type(error).__name__}: {error}" if include_type else str(error)
        self.result.set_error(title, detail or type(error).__name__)
        if self.state.log is not None:
            self.state.log.error(f"{type(error).__name__}: {error}")

    def _diagnostics(self, error: BaseException | None) -> str:
        return build_diagnostics(
            tool=self._title,
            files=self.state.files,
            sheets=self.state.selected_sheets,
            formats=self._formats,
            options=self.state.diagnostic_options(),
            message=self.state.message,
            error=error,
            traceback_text=self.state.error_detail,
        )

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
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        expand=expand,
    )


def _build_options(
    options: OptionsFactory | ft.Control | None,
    state: ToolState,
) -> tuple[ft.Control | None, Callable[[], None] | None]:
    if options is None:
        return None, None
    if isinstance(options, ft.Control):
        return options, None

    panel = options(state)
    if isinstance(panel, ft.Control):
        return panel, None
    return panel.control, panel.refresh
