"""Anatomia comum das páginas: cabeçalho, entrada/opções, resultado e barra."""

import asyncio
import contextlib
import traceback
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Protocol

import flet as ft

from xl_utils.core.io import list_sheets
from xl_utils.core.mime import FormatCheck, check_format
from xl_utils.core.save import SaveError, SaveItem, save_chosen, save_to_output
from xl_utils.core.tools.all_str import WorkbookReadError
from xl_utils.core.tools.link import (
    AlreadyProcessedError,
    ConfigError,
    InvalidCnjError,
    MissingColumnsError,
)
from xl_utils.shared import drive_auth, drive_cache
from xl_utils.shared.accounts import Account
from xl_utils.shared.drive import FolderPermissionError
from xl_utils.shared.drive_store import FolderGrant
from xl_utils.shared.log import RunLog, build_diagnostics
from xl_utils.shared.progress import (
    CancelToken,
    NullReporter,
    ProgressEvent,
    ProgressReporter,
)
from xl_utils.ui import theme
from xl_utils.ui.components.file_input import FileInput
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.sheet_selector import SheetSelector
from xl_utils.ui.drive import DriveSaved, DriveSession
from xl_utils.ui.state import ToolState

RunHandler = Callable[
    [ToolState, ResultPanel, ProgressReporter | NullReporter, CancelToken],
    None,
]

PreRun = Callable[[ToolState], str | None]

ReadyCheck = Callable[[ToolState, Mapping[str, Path | None]], bool]

Hint = Callable[[ToolState, Mapping[str, Path | None]], str | None]


class OverlayHost:
    """Área que cobre o conteúdo da página e hospeda um painel temporário."""

    def __init__(self) -> None:
        self._slot = ft.Container(expand=True)
        self.control = ft.Container(
            content=self._slot,
            visible=False,
            bgcolor=theme.BACKGROUND,
            expand=True,
            on_click=lambda _event: None,
        )

    def mount(self, content: ft.Control) -> None:
        """Deixa o painel na árvore para acompanhar a troca de tema."""
        self._slot.content = content

    def show(self) -> None:
        """Exibe o painel sobre o restante da página."""
        self.control.visible = True
        self._refresh()

    def hide(self) -> None:
        """Devolve a página ao estado normal."""
        self.control.visible = False
        self._refresh()

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


class OptionsPanel(Protocol):
    """Controle de opções que se reconstrói quando a entrada muda."""

    control: ft.Control

    def refresh(self) -> None: ...


OptionsFactory = Callable[[ToolState, OverlayHost], ft.Control | OptionsPanel]


class ToolLayout:
    """Layout compartilhado por todas as páginas de ferramenta."""

    def __init__(
        self,
        title: str,
        description: str,
        *,
        options: OptionsFactory | ft.Control | None = None,
        note: str = "",
        multiple_files: bool = False,
        default_all_sheets: bool = False,
        inputs: Sequence[str] | None = None,
        ready: ReadyCheck | None = None,
        hint: Hint | None = None,
        pre_run: PreRun | None = None,
        run_handler: RunHandler | None = None,
        drive: DriveSession | None = None,
    ) -> None:
        self.state = ToolState()
        self._title = title
        self._run_handler = run_handler
        self._pre_run = pre_run
        self._ready_check = ready
        self._hint = hint
        self._drive = drive
        self._default_all_sheets = default_all_sheets
        self._input_labels = tuple(inputs or ())
        self._pre_checking = False
        self._input_files: dict[str, Path | None] = {
            label: None for label in self._input_labels
        }
        self._file_inputs: dict[str, FileInput] = {}
        if self._input_labels:
            for label in self._input_labels:
                self._file_inputs[label] = FileInput(
                    lambda files, name=label: self._labeled_changed(name, files),
                    multiple=False,
                    drive=drive,
                )
            self.file_input = next(iter(self._file_inputs.values()))
        else:
            self.file_input = FileInput(
                self._files_changed,
                multiple=multiple_files,
                drive=drive,
            )
        self.result = ResultPanel(
            on_save=self._save_clicked,
            on_save_output=self._save_output_clicked,
            on_save_drive=self._save_drive_clicked,
        )
        if drive is not None:
            drive.subscribe(self._drive_changed)
        self._formats: dict[Path, FormatCheck] = {}
        self._sheet_loading = False
        self._running = False
        self._token: CancelToken | None = None
        self._save_picker = ft.FilePicker()
        self._save_picker_attached = False
        self.sheet_selector = SheetSelector(
            self.state,
            on_change=self._selection_changed,
        )

        initial_summary = (
            " · ".join(f"{label}: —" for label in self._input_labels)
            if self._input_labels
            else "Nenhum arquivo selecionado."
        )
        self._summary = ft.Text(
            initial_summary,
            size=theme.FONT_SM,
            color=theme.MUTED,
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        if self._hint is not None:
            self._update_summary()

        self._run_button = ft.FilledButton(
            "Executar",
            icon=ft.Icons.PLAY_ARROW,
            disabled=True,
            on_click=self._run,
        )
        self._cancel_button = ft.OutlinedButton(
            "Cancelar",
            icon=ft.Icons.CANCEL,
            visible=False,
            on_click=self._cancel_clicked,
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
                        border=ft.Border.all(1, theme.SUCCESS_BORDER),
                        border_radius=999,
                        padding=ft.Padding.symmetric(
                            vertical=5,
                            horizontal=10,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.only(bottom=16, right=64),
        )

        if self._input_labels:
            entrada_controls: list[ft.Control] = [
                ft.Column(
                    controls=[
                        ft.Text(
                            label,
                            size=theme.FONT_XS,
                            weight=ft.FontWeight.BOLD,
                            color=theme.CHIP_TEXT,
                        ),
                        self._file_inputs[label].control,
                    ],
                    spacing=6,
                )
                for label in self._input_labels
            ]
        else:
            entrada_controls = [
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

        self._overlay = OverlayHost()
        options_control, self._options_refresh = _build_options(
            options,
            self.state,
            self._overlay,
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
                        controls=[self._summary, self._cancel_button, self._run_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.only(top=16),
        )

        page = ft.Container(
            content=ft.Column(
                controls=[header, body, action_bar],
                spacing=0,
                expand=True,
            ),
            padding=24,
            expand=True,
        )
        self.control = ft.Stack(
            controls=[page, self._overlay.control],
            fit=ft.StackFit.EXPAND,
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
        self._update_drive_mode()
        self._refresh()
        self._start_sheet_load()

    def _labeled_changed(self, label: str, files: list[Path]) -> None:
        """Guarda a planilha de uma entrada rotulada e atualiza o botão."""
        self._input_files[label] = files[-1] if files else None
        selected = [path for path in self._input_files.values() if path is not None]
        self.state.select_files(selected)
        self.state.inputs = {
            name: path for name, path in self._input_files.items() if path is not None
        }
        self.state.options.pop("reprocess", None)
        self._check_formats()
        self.result.set_idle()
        self._update_summary()
        self._update_drive_mode()
        self._run_button.disabled = not self._ready()
        self._refresh_options()
        self._refresh()
        self._start_sheet_load()

    def _ready(self) -> bool:
        """Diz se as entradas exigidas pelo fluxo atual estão prontas."""
        if not self._input_labels:
            return bool(self.state.files)
        if self._ready_check is not None:
            return self._ready_check(self.state, self._input_files)
        return all(
            self._input_files.get(label) is not None for label in self._input_labels
        )

    def _update_summary(self) -> None:
        if self._hint is not None:
            text = self._hint(self.state, self._input_files)
            if text:
                self._summary.value = text
                return
        if self._input_labels:
            parts = [
                f"{label}: {path.name}" if path is not None else f"{label}: —"
                for label, path in self._input_files.items()
            ]
            self._summary.value = " · ".join(parts)
        elif self.state.files:
            self._summary.value = (
                f"{len(self.state.files)} arquivo(s), "
                f"{self.state.selected_count} aba(s)."
            )
        else:
            self._summary.value = "Nenhum arquivo selecionado."

    def _file_input_controls(self) -> list[FileInput]:
        return (
            list(self._file_inputs.values()) if self._file_inputs else [self.file_input]
        )

    def _check_formats(self) -> list[FormatCheck]:
        """Detecta o formato real de cada arquivo e o mostra na entrada."""
        checks = [check_format(path) for path in self.state.files]
        self._formats = {check.path: check for check in checks}
        for control in self._file_input_controls():
            control.set_formats(checks)
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
            except Exception as error:  # noqa: BLE001 - erro exibido no seletor
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
        self._run_button.disabled = not self._ready()
        self._selection_changed(self.state.selected_sheets)

    def _selection_changed(self, selection: dict[Path, set[str]]) -> None:
        if not self.state.files:
            return
        self._update_summary()
        self._refresh_options()
        self._refresh()

    def _refresh_options(self) -> None:
        if self._options_refresh is not None:
            self._options_refresh()

    def _run(self, _event=None) -> None:
        if self._running or self._pre_checking:
            return
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
        if self._pre_run is not None and not self.state.options.get("reprocess"):
            page = self._page()
            if page is not None and hasattr(page, "run_task"):
                self._start_preflight(checks)
                return
        self._start_run(checks)

    def _start_run(self, checks: list[FormatCheck]) -> None:
        """Começa a execução, seja logo após o formato, seja após confirmar."""
        self._update_summary()
        self._begin(checks)
        page = self._page()
        if page is None or not hasattr(page, "run_task"):
            self._execute_sync()
        else:
            page.run_task(self._execute_async)

    def _start_preflight(self, checks: list[FormatCheck]) -> None:
        """Confere a planilha fora do loop antes de perguntar qualquer coisa."""
        files = tuple(self.state.files)
        self._pre_checking = True
        self._run_button.disabled = True
        self._summary.value = "Conferindo a planilha..."
        self._refresh()
        page = self._page()
        if page is None:
            self._pre_checking = False
            self._start_run(checks)
            return
        page.run_task(self._preflight_async, checks, files)

    async def _preflight_async(
        self,
        checks: list[FormatCheck],
        files: tuple[Path, ...],
    ) -> None:
        try:
            warning = await asyncio.to_thread(self._pre_run, self.state)
        except Exception:  # noqa: BLE001 - a execução real mostra o erro
            warning = None
        self._pre_checking = False
        if tuple(self.state.files) != files:
            self._update_summary()
            self._run_button.disabled = not self._ready()
            self._refresh()
            return
        if warning:
            self._ask_confirmation(warning, checks)
        else:
            self._start_run(checks)

    def _ask_confirmation(self, message: str, checks: list[FormatCheck]) -> None:
        """Mostra o aviso de reexecução e só continua depois do aceite."""
        page = self._page()
        if page is None:
            self._start_run(checks)
            return

        def close(_event=None) -> None:
            page.pop_dialog()
            self._update_summary()
            self._run_button.disabled = not self._ready()
            self._refresh()

        def confirm(_event=None) -> None:
            page.pop_dialog()
            self.state.options["reprocess"] = True
            self._start_run(checks)

        def dismissed(_event=None) -> None:
            if self.state.running:
                return
            self._update_summary()
            self._run_button.disabled = not self._ready()
            self._refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Planilha já processada"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("Cancelar", on_click=close),
                    ft.FilledButton("Continuar mesmo assim", on_click=confirm),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=dismissed,
            )
        )

    def _begin(self, checks: list[FormatCheck]) -> None:
        """Prepara o estado e o painel antes de entregar o trabalho à thread."""
        self._running = True
        self._token = CancelToken()
        self.state.running = True
        self.state.message = ""
        self.state.error = None
        self.state.error_detail = None
        self.state.save_items.clear()
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
        self.result.set_log(log)
        self.result.set_running(f"Executando {len(self.state.files)} arquivo(s)...")
        self.result.start_progress(len(self.state.files))
        self._set_busy(True)

    def _cancel_clicked(self, _event=None) -> None:
        """Pede a parada cooperativa; o item em curso termina antes."""
        if not self._running or self._token is None:
            return
        self._token.cancel()
        self._cancel_button.disabled = True
        self._summary.value = "Cancelando após o item atual..."
        self.result.set_cancelling()
        self._refresh()

    def _execute_sync(self) -> None:
        """Executa no próprio loop quando não há página (testes headless)."""
        reporter = ProgressReporter(self.result.apply_progress)
        try:
            self._execute(reporter)
        finally:
            self._finish()

    async def _execute_async(self) -> None:
        """Roda o handler em uma thread e consome os eventos no loop da página."""
        loop = asyncio.get_running_loop()
        events: asyncio.Queue[ProgressEvent] = asyncio.Queue()

        def emit(event: ProgressEvent) -> None:
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(events.put_nowait, event)

        def warn(message: str) -> None:
            if self.state.log is not None:
                self.state.log.warning(message)

        reporter = ProgressReporter(emit, on_error=warn)
        self.result.set_dispatcher(loop.call_soon_threadsafe)

        async def execute_and_finish() -> None:
            try:
                await asyncio.to_thread(self._execute, reporter)
            finally:
                reporter.finish()
                events.put_nowait(
                    ProgressEvent(
                        kind="finish",
                        total=reporter.total,
                        completed=reporter.completed,
                    )
                )

        worker = asyncio.create_task(execute_and_finish())
        try:
            while True:
                event = await events.get()
                self.result.apply_progress(event)
                if event.kind == "finish":
                    break
                # Deixa o loop processar a atualização enviada pelo painel antes
                # de consumir o próximo evento; sem isso, lotes rápidos acumulam
                # todos os eventos e a tela só muda no fim.
                await asyncio.sleep(0)
            await worker
        finally:
            self.result.set_dispatcher(None)
            self._finish()

    def _execute(self, progress: ProgressReporter | NullReporter) -> None:
        """Chama o handler e registra o resultado da execução."""
        progress.start(len(self.state.files))
        log = self.state.log or RunLog()
        token = self._token or CancelToken()
        failure: BaseException | None = None
        try:
            self._run_handler(self.state, self.result, progress, token)
        except WorkbookReadError as error:
            failure = error
            self._fail(error, "Não foi possível ler a planilha")
        except AlreadyProcessedError as error:
            failure = error
            self._fail(error, "Planilha já processada")
        except ConfigError as error:
            failure = error
            self._fail(error, "Configuração de cabeçalhos inválida")
        except InvalidCnjError as error:
            failure = error
            self._fail(error, "CNJ fora do padrão")
        except MissingColumnsError as error:
            failure = error
            self._fail(error, "Colunas padrão ausentes")
        except ValueError as error:
            failure = error
            self._fail(error, "Confira a seleção")
        except Exception as error:  # noqa: BLE001 - mostra qualquer falha na UI
            failure = error
            self._fail(error, "Falha inesperada", include_type=True)
        else:
            if self.result.kind == "success":
                log.success(f"Concluído: {self.result.status}")
            elif self.result.kind == "ready":
                log.success("Pronto para salvar")
            elif self.result.kind == "info":
                log.warning(self.result.status)
        finally:
            self.result.set_log(log)
            self.result.set_diagnostics(self._diagnostics(failure))

    def _finish(self) -> None:
        """Devolve o controle à janela depois da execução."""
        self._running = False
        self.state.running = False
        self._update_summary()
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._run_button.visible = not busy
        self._run_button.disabled = busy or self._sheet_loading or not self._ready()
        self._cancel_button.visible = busy
        self._cancel_button.disabled = not busy
        for control in self._file_input_controls():
            control.set_busy(busy)
        self.sheet_selector.set_busy(busy)
        self._refresh()

    def _block_formats(self, failures: list[FormatCheck]) -> None:
        """Para a execução antes da leitura se nenhum formato for identificado."""
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
        """Mostra o título amigável e mantém a mensagem original e o trace."""
        self.state.error = str(error)
        self.state.error_detail = traceback.format_exc()
        detail = f"{type(error).__name__}: {error}" if include_type else str(error)
        self.result.set_error(title, detail or type(error).__name__)
        if self.state.log is not None:
            self.state.log.error(f"{type(error).__name__}: {error}")

    def _save_clicked(self, _event=None) -> None:
        """Abre o seletor nativo: arquivo para uma saída, pasta para várias."""
        items = list(self.state.save_items)
        if not items:
            return
        page = self._attach_save_picker()
        if page is None:
            self._save_failed(
                SaveError("A janela ainda não está pronta para abrir o seletor.")
            )
            return
        page.run_task(self._pick_and_save, items)

    async def _pick_and_save(self, items: list[SaveItem]) -> None:
        try:
            if len(items) == 1:
                destination = await self._save_picker.save_file(
                    dialog_title="Salvar planilha",
                    file_name=items[0].suggested_name,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["xlsx"],
                )
            else:
                destination = await self._save_picker.get_directory_path(
                    dialog_title="Selecione a pasta de destino",
                )
        except Exception as error:  # noqa: BLE001 - mantém a prévia utilizável
            self._save_failed(SaveError(f"Não foi possível abrir o seletor: {error}"))
            return
        if not destination:
            return
        chosen = Path(destination)
        await self._write(lambda: save_chosen(items, chosen))

    def _save_output_clicked(self, _event=None) -> None:
        """Grava na pasta ``output/`` da origem sem abrir diálogo."""
        items = list(self.state.save_items)
        if not items:
            return
        if any(drive_cache.is_cached(path) for path in self.state.files):
            self._save_failed(
                SaveError(
                    "Esta planilha veio do Drive. Use “Salvar” e escolha o "
                    "destino — ela não tem pasta local de origem."
                )
            )
            return
        page = self._page()
        if page is None:
            self._save_failed(SaveError("A janela ainda não está pronta para gravar."))
            return
        page.run_task(self._write, lambda: save_to_output(items))

    def _drive_changed(self) -> None:
        """Reavalia o botão do Drive quando contas entram ou saem."""
        self._update_drive_mode()
        self._refresh()

    def _update_drive_mode(self) -> None:
        """Mostra “Salvar no Drive” só quando a entrada veio do Drive."""
        has_origin = any(drive_cache.is_cached(path) for path in self.state.files)
        available = self._drive is not None and bool(self._drive.accounts)
        self.result.set_drive_mode(has_origin, available)

    def _save_drive_clicked(self, _event=None) -> None:
        """Leva o resultado para a pasta do Drive, pedindo a pasta se preciso."""
        items = list(self.state.save_items)
        if not items or self._drive is None:
            return
        page = self._page()
        if page is None:
            self._save_failed(
                SaveError("A janela ainda não está pronta para gravar no Drive.")
            )
            return
        origins = drive_cache.origins(self.state.files)
        account = self._drive.account_for(origins)
        if account is None:
            self._save_failed(
                SaveError("Entre no Google Drive para salvar o resultado lá.")
            )
            return
        folders = drive_cache.parents(self.state.files)
        if not folders:
            page.run_task(self._drive_upload, account, items, None, True)
            return
        if len(folders) > 1:
            self._ask_drive_folder(page, account, items, "")
            return
        grant = self._drive.folder_grant(account, folders[0])
        if grant is None:
            self._ask_drive_folder(page, account, items, folders[0])
            return
        page.run_task(self._drive_upload, account, items, grant, False)

    def _ask_drive_folder(
        self,
        page: ft.Page,
        account: Account,
        items: list[SaveItem],
        folder_id: str,
    ) -> None:
        """Explica a concessão de pasta e oferece a raiz como saída."""
        know_folder = bool(folder_id)
        title = (
            "Autorizar a pasta no Drive" if know_folder else "Escolher a pasta no Drive"
        )
        content = (
            "O Google só permite gravar na pasta do arquivo original depois "
            "que você a escolhe uma vez no seletor do Drive. Escolha a pasta "
            "de origem para liberar a gravação."
            if know_folder
            else "As planilhas vieram de pastas diferentes. Escolha uma pasta "
            "de destino no Drive; a escolha fica lembrada para as próximas "
            "gravações."
        )
        content = f"{content} Use a conta {account.email}."

        def to_root(_event=None) -> None:
            page.pop_dialog()
            note = (
                "A pasta de origem não foi autorizada; o resultado foi para a "
                "raiz do Meu Drive."
                if know_folder
                else "A pasta não foi escolhida; o resultado foi para a raiz "
                "do Meu Drive."
            )
            page.run_task(self._drive_upload, account, items, None, True, note)

        def choose(_event=None) -> None:
            page.pop_dialog()
            page.run_task(self._drive_pick_folder, account, items)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(content),
                actions=[
                    ft.TextButton("Salvar na raiz", on_click=to_root),
                    ft.FilledButton(
                        "Autorizar pasta" if know_folder else "Escolher pasta",
                        on_click=choose,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    async def _drive_pick_folder(
        self,
        account: Account,
        items: list[SaveItem],
    ) -> None:
        """Abre o seletor de pasta e tenta gravar de novo com a concessão."""
        if self._drive is None:
            return
        self.result.set_saving("Autorizando a pasta no Drive...")
        try:
            grant = await self._drive.authorize_folder(account)
        except drive_auth.DriveError as error:
            self._save_failed(error)
            return
        except Exception as error:  # noqa: BLE001 - falha de autorização
            self._save_failed(SaveError(f"Falha ao autorizar a pasta: {error}"))
            return
        if grant is None:
            await self._drive_upload(
                account,
                items,
                None,
                True,
                "A pasta não foi autorizada; o resultado foi para a raiz do Meu Drive.",
            )
            return
        await self._drive_upload(account, items, grant, True)

    async def _drive_upload(
        self,
        account: Account,
        items: list[SaveItem],
        folder: FolderGrant | None,
        retry: bool,
        note: str = "",
    ) -> None:
        """Grava os itens no Drive, fora da UI thread."""
        if self._drive is None:
            return
        self.result.set_saving("Salvando no Drive...")
        try:
            saved = await self._drive.save_to_drive(account, items, folder)
        except FolderPermissionError as error:
            if retry:
                self._save_failed(error)
                return
            if folder is not None:
                self._drive.forget_folder(account, folder.folder_id)
            page = self._page()
            if page is None:
                self._save_failed(error)
                return
            self._ask_drive_folder(
                page,
                account,
                items,
                folder.folder_id if folder else "",
            )
            return
        except (drive_auth.DriveError, SaveError) as error:
            self._save_failed(error)
            return
        except Exception as error:  # noqa: BLE001 - falha de gravação
            self._save_failed(SaveError(f"Falha ao salvar no Drive: {error}"))
            return
        self._drive_saved(saved, account, note)

    def _drive_saved(
        self,
        saved: Sequence[DriveSaved],
        account: Account,
        note: str = "",
    ) -> None:
        """Atualiza o painel e o log depois de gravar no Drive."""
        if not saved:
            self._save_failed(
                SaveError("O Google não confirmou nenhum arquivo gravado.")
            )
            return
        log = self.state.log or RunLog()
        for item in saved:
            log.success(f"Salvo no Drive: {item.name}")
        if note:
            log.warning(note)
        self.state.log = log
        self.result.set_drive_success(
            saved,
            self.state.result or {},
            account.email,
            note,
        )
        self.result.set_log(log)
        self.result.set_diagnostics(self._diagnostics(None))
        self._refresh()

    async def _write(self, work: Callable[[], list[Path] | None]) -> None:
        self.result.set_saving()
        try:
            paths = await asyncio.to_thread(work)
        except SaveError as error:
            self._save_failed(error)
            return
        except Exception as error:  # noqa: BLE001 - falha de escrita tipada aqui
            self._save_failed(SaveError(f"Falha ao salvar: {error}"))
            return
        if paths:
            self._saved(paths)

    def _saved(self, paths: list[Path]) -> None:
        log = self.state.log or RunLog()
        for path in paths:
            log.success(f"Salvo: {path}")
        self.state.log = log
        detail = (
            f"{len(paths)} arquivo(s) gravado(s) no destino escolhido."
            if len(paths) > 1
            else "Arquivo gravado no destino escolhido."
        )
        self.result.set_success(
            paths[0],
            self.state.result or {},
            "Salvo com sucesso",
            detail,
        )
        self.result.set_log(log)
        self.result.set_diagnostics(self._diagnostics(None))
        self._refresh()

    def _save_failed(self, error: BaseException) -> None:
        """Mantém a prévia e as ações de salvar quando a escrita falha."""
        self.state.error = str(error)
        trace = traceback.format_exc()
        self.state.error_detail = (
            trace if trace and not trace.startswith("NoneType") else None
        )
        log = self.state.log or RunLog()
        log.error(f"{type(error).__name__}: {error}")
        self.state.log = log
        self.result.set_save_error("Não foi possível salvar", str(error))
        self.result.set_log(log)
        self.result.set_diagnostics(self._diagnostics(error))
        self._refresh()

    def _attach_save_picker(self) -> ft.Page | None:
        page = self._page()
        if page is None:
            return None
        if not self._save_picker_attached:
            page.services.append(self._save_picker)
            self._save_picker_attached = True
        return page

    def _page(self) -> ft.Page | None:
        try:
            return self.control.page
        except RuntimeError:
            return None

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

    def refresh(self) -> None:
        """Reavalia o resumo e o botão depois de mudar uma opção."""
        self._update_summary()
        self._run_button.disabled = (
            self._running or self._sheet_loading or not self._ready()
        )
        self._refresh()

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
                    color=theme.CHIP_TEXT,
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
    overlay: OverlayHost,
) -> tuple[ft.Control | None, Callable[[], None] | None]:
    if options is None:
        return None, None
    if isinstance(options, ft.Control):
        return options, None

    panel = options(state, overlay)
    if isinstance(panel, ft.Control):
        return panel, None
    return panel.control, panel.refresh
