"""Cartão de resultado: status, ações de salvar, caminho de saída, log e prévia."""

import contextlib
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd
import pyperclip

from xl_utils.shared.log import LogEvent, RunLog
from xl_utils.shared.progress import ProgressEvent
from xl_utils.shared.system import open_folder, open_url
from xl_utils.ui import theme
from xl_utils.ui.components.preview_table import PreviewTable

if TYPE_CHECKING:
    from xl_utils.ui.drive import DriveSaved

_LOG_MAX_HEIGHT = 160

Dispatcher = Callable[[Callable[[], None]], None]


class ResultPanel:
    """Estado visual do resultado de uma ferramenta."""

    def __init__(
        self,
        *,
        on_save: Callable[[], None] | None = None,
        on_save_output: Callable[[], None] | None = None,
        on_save_drive: Callable[[], None] | None = None,
    ) -> None:
        self._on_save = on_save
        self._on_save_output = on_save_output
        self._on_save_drive = on_save_drive
        self._output: Path | None = None
        self._drive_link = ""
        self._kind = "idle"
        self._diagnostics = ""
        self._dispatch: Dispatcher | None = None
        self.preview = PreviewTable()

        self._icon = ft.Icon(ft.Icons.INFO_OUTLINE, color=theme.MUTED, size=18)
        self._status = ft.Text(
            "Aguardando arquivo.",
            size=theme.FONT_SM,
            weight=ft.FontWeight.BOLD,
        )
        self._detail = ft.Text("", size=theme.FONT_SM, color=theme.MUTED)
        self._progress_text = ft.Text(
            "",
            size=theme.FONT_XS,
            color=theme.MUTED,
            visible=False,
        )
        self._progress_bar = ft.ProgressBar(
            value=0,
            bar_height=4,
            color=theme.PURPLE,
            bgcolor=theme.BORDER,
            visible=False,
        )
        self._path = ft.Text(
            "",
            size=theme.FONT_XS,
            font_family="Consolas",
            color=theme.CYAN,
            selectable=True,
            visible=False,
        )
        self._open_button = ft.OutlinedButton(
            "Abrir pasta",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._open_folder,
            visible=False,
        )
        self._save_button = ft.FilledButton(
            "Salvar",
            icon=ft.Icons.SAVE,
            on_click=self._save,
        )
        self._save_output_button = ft.OutlinedButton(
            "Salvar em output/",
            icon=ft.Icons.FOLDER,
            on_click=self._save_output,
        )
        self._save_drive_button = ft.OutlinedButton(
            "Salvar no Drive",
            icon=ft.Icons.CLOUD_UPLOAD,
            on_click=self._save_drive,
            visible=False,
        )
        self._drive_link_button = ft.OutlinedButton(
            "Abrir no Drive",
            icon=ft.Icons.OPEN_IN_NEW,
            on_click=self._open_drive_link,
            visible=False,
        )
        self._save_row = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._save_button,
                        self._save_drive_button,
                        self._save_output_button,
                    ],
                    spacing=8,
                    wrap=True,
                ),
                ft.Text(
                    "Nada é gravado até você escolher o destino.",
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                ),
            ],
            spacing=4,
            visible=False,
        )
        self._copy_button = ft.IconButton(
            icon=ft.Icons.CONTENT_COPY,
            icon_size=16,
            tooltip="Copiar log",
            on_click=self._copy_log,
        )
        self._copy_diagnostics_button = ft.TextButton(
            "Copiar diagnóstico",
            icon=ft.Icons.BUG_REPORT,
            tooltip="Copiar versões, arquivos, opções e traceback",
            on_click=self._copy_diagnostics,
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=6, vertical=0),
                text_style=ft.TextStyle(size=theme.FONT_XS),
            ),
        )
        self._log = ft.Text(
            "",
            size=theme.FONT_XS,
            font_family="Consolas",
            color=theme.SUBTLE_TEXT,
            selectable=True,
        )
        self._log_box = ft.Container(
            content=ft.Column(
                controls=[self._log],
                scroll=ft.ScrollMode.HIDDEN,
                expand=True,
            ),
            height=0,
            bgcolor=theme.BACKGROUND_DEEP,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=8,
            padding=10,
        )
        self._log_section = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Log",
                            size=theme.FONT_SM,
                            weight=ft.FontWeight.BOLD,
                            color=theme.MUTED,
                        ),
                        ft.Row(
                            controls=[
                                self._copy_diagnostics_button,
                                self._copy_button,
                            ],
                            spacing=0,
                            tight=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self._log_box,
            ],
            spacing=4,
            visible=False,
        )

        self.control = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._icon,
                        ft.Column(
                            controls=[self._status, self._detail],
                            spacing=0,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Column(
                    controls=[self._progress_text, self._progress_bar],
                    spacing=4,
                ),
                self._path,
                self._save_row,
                ft.Row(
                    controls=[self._open_button, self._drive_link_button],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=8,
                ),
                self._log_section,
                ft.Divider(height=1, color=theme.BORDER),
                self.preview.control,
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    @property
    def kind(self) -> str:
        """Devolve o estado: idle, info, running, ready, success, cancelled ou error."""
        return self._kind

    @property
    def status(self) -> str:
        """Devolve a linha de status exibida agora."""
        return str(self._status.value or "")

    @property
    def diagnostics(self) -> str:
        """Devolve o texto guardado para “Copiar diagnóstico”."""
        return self._diagnostics

    def set_dispatcher(self, dispatch: Dispatcher | None) -> None:
        """Agenda as atualizações no loop da página, fora da thread de trabalho."""
        self._dispatch = dispatch
        self.preview.set_dispatcher(dispatch)

    def start_progress(self, total: int) -> None:
        """Mostra a barra indeterminada antes do primeiro arquivo."""
        self._progress_bar.value = None
        self._progress_bar.visible = True
        self._progress_text.value = f"Arquivo 0 de {total}"
        self._progress_text.visible = True
        self._refresh()

    def apply_progress(self, event: ProgressEvent) -> None:
        """Atualiza barra, texto e log sempre no loop da página."""
        if event.kind == "log":
            self._append_log_line(event.text)
            self._update_now()
            return
        if event.kind == "stage":
            self._progress_text.value = event.text
            self._progress_text.visible = self._kind == "running"
            self._append_log_line(LogEvent("info", event.text).to_line())
            self._update_now()
            return
        visible = self._kind == "running"
        if event.kind in ("start", "file_started"):
            self._progress_bar.value = None
        else:
            self._progress_bar.value = event.value
        self._progress_bar.visible = visible
        self._progress_text.value = event.text
        self._progress_text.visible = visible
        self._update_now()

    def _hide_progress(self) -> None:
        self._progress_bar.visible = False
        self._progress_text.visible = False

    def set_idle(self, message: str = "Selecione um arquivo para começar.") -> None:
        self._output = None
        self._kind = "idle"
        self._diagnostics = ""
        self._icon.name = ft.Icons.INFO_OUTLINE
        self._icon.color = theme.MUTED
        self._status.value = message
        self._detail.value = ""
        self._path.value = ""
        self._path.visible = False
        self._open_button.visible = False
        self._drive_link_button.visible = False
        self._drive_link = ""
        self._save_row.visible = False
        self._hide_progress()
        self.set_log([])
        self.preview.set_frames(None)
        self._refresh()

    def set_info(self, message: str, detail: str = "") -> None:
        self._kind = "info"
        self._icon.name = ft.Icons.INFO_OUTLINE
        self._icon.color = theme.CYAN
        self._status.value = message
        self._detail.value = detail
        self._save_row.visible = False
        self._drive_link_button.visible = False
        self._hide_progress()
        self._refresh()

    def set_running(self, message: str = "Executando...") -> None:
        self._kind = "running"
        self._icon.name = ft.Icons.HOURGLASS_EMPTY
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = ""
        self._save_row.visible = False
        self._drive_link_button.visible = False
        self._refresh()

    def set_cancelling(self) -> None:
        """Avisa que a parada só acontece quando o item atual terminar."""
        self._detail.value = "Cancelando após o item atual..."
        self._refresh()

    def set_ready(
        self,
        frames: dict[str, pd.DataFrame],
        message: str,
        detail: str = "",
    ) -> None:
        """Mostra a prévia e as ações de salvar, antes de existir arquivo."""
        self._output = None
        self._kind = "ready"
        self._icon.name = ft.Icons.SAVE
        self._icon.color = theme.PURPLE
        self._status.value = message
        self._detail.value = detail
        self._path.value = ""
        self._path.visible = False
        self._open_button.visible = False
        self._drive_link_button.visible = False
        self._drive_link = ""
        self._save_row.visible = True
        self._hide_progress()
        self.preview.set_frames(frames)
        self._refresh()

    def set_drive_mode(self, enabled: bool, available: bool = True) -> None:
        """Troca “Salvar em output/” por “Salvar no Drive” para origens do Drive.

        ``available`` diz se há conta conectada; sem ela o botão do Drive fica
        visível, mas desabilitado, em vez de voltar ao atalho de ``output/``.
        """
        self._save_drive_button.visible = enabled
        self._save_drive_button.disabled = enabled and not available
        self._save_output_button.visible = not enabled
        self._refresh()

    def set_saving(self, message: str = "Salvando...") -> None:
        self._kind = "running"
        self._icon.name = ft.Icons.HOURGLASS_EMPTY
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = ""
        self._save_row.visible = False
        self._drive_link_button.visible = False
        self._hide_progress()
        self._refresh()

    def set_success(
        self,
        output_path: Path,
        frames: dict[str, pd.DataFrame],
        message: str,
        detail: str = "",
    ) -> None:
        self._output = Path(output_path)
        self._kind = "success"
        self._icon.name = ft.Icons.CHECK_CIRCLE
        self._icon.color = theme.GREEN
        self._status.value = message
        self._detail.value = detail
        self._path.value = str(self._output)
        self._path.visible = True
        self._open_button.visible = True
        self._drive_link_button.visible = False
        self._drive_link = ""
        self._save_row.visible = False
        self._hide_progress()
        self.preview.set_frames(frames)
        self._refresh()

    def set_drive_success(
        self,
        saved: Sequence[DriveSaved],
        frames: dict[str, pd.DataFrame],
        account: str = "",
        note: str = "",
    ) -> None:
        """Mostra os arquivos recém-gravados no Drive, com link para abrir."""
        self._output = None
        self._kind = "success"
        self._icon.name = ft.Icons.CLOUD_DONE
        self._icon.color = theme.GREEN
        folder = saved[0].folder_name if saved else "Meu Drive"
        if len(saved) == 1:
            self._status.value = "Salvo no Drive"
            parts = [folder, saved[0].name]
            self._path.value = f"{folder}/{saved[0].name}"
            self._drive_link = saved[0].web_link
        else:
            self._status.value = f"{len(saved)} arquivos salvos no Drive"
            parts = [folder, f"{len(saved)} arquivos"]
            self._path.value = folder
            self._drive_link = ""
        if account:
            parts.append(account)
        if note:
            parts.append(note)
        self._detail.value = " · ".join(parts)
        self._path.visible = True
        self._open_button.visible = False
        self._drive_link_button.visible = bool(self._drive_link)
        self._save_row.visible = False
        self._hide_progress()
        self.preview.set_frames(frames)
        self._refresh()

    def set_save_error(self, message: str, detail: str = "") -> None:
        """Relata falha de escrita mantendo a prévia e as ações de salvar."""
        self._kind = "ready"
        self._icon.name = ft.Icons.ERROR_OUTLINE
        self._icon.color = theme.RED
        self._status.value = message
        self._detail.value = detail
        self._path.value = ""
        self._path.visible = False
        self._open_button.visible = False
        self._drive_link_button.visible = False
        self._save_row.visible = True
        self._hide_progress()
        self._refresh()

    def set_cancelled(
        self,
        frames: dict[str, pd.DataFrame] | None = None,
        message: str = "Execução cancelada",
        detail: str = "",
    ) -> None:
        """Mostra o que já foi calculado, sem liberar a gravação incompleta."""
        self._output = None
        self._kind = "cancelled"
        self._icon.name = ft.Icons.CANCEL
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = detail
        self._path.value = ""
        self._path.visible = False
        self._open_button.visible = False
        self._drive_link_button.visible = False
        self._save_row.visible = False
        self._hide_progress()
        self.preview.set_frames(frames)
        self._refresh()

    def set_error(
        self,
        message: str,
        detail: str = "",
        *,
        keep_preview: bool = False,
    ) -> None:
        self._output = None
        self._kind = "error"
        self._icon.name = ft.Icons.ERROR_OUTLINE
        self._icon.color = theme.RED
        self._status.value = message
        self._detail.value = detail
        self._path.visible = False
        self._open_button.visible = False
        self._drive_link_button.visible = False
        self._save_row.visible = False
        self._hide_progress()
        if not keep_preview:
            self.preview.set_frames(None)
        self._refresh()

    def set_log(self, log: RunLog | Sequence[str]) -> None:
        if isinstance(log, RunLog):
            text = log.to_text()
        else:
            text = "\n".join(str(line) for line in log)
        self._log.value = text
        lines = text.splitlines() if text else []
        self._log_section.visible = bool(lines)
        self._resize_log(len(lines))
        self._refresh()

    def set_diagnostics(self, text: str) -> None:
        """Guarda o texto usado por “Copiar diagnóstico”."""
        self._diagnostics = text

    def append_log(self, line: str) -> None:
        self._append_log_line(line)
        self._refresh()

    def _append_log_line(self, line: str) -> None:
        current = self._log.value or ""
        self._log.value = f"{current}\n{line}".strip()
        self._log_section.visible = True
        self._resize_log(len(self._log.value.splitlines()))

    def _resize_log(self, lines: int) -> None:
        """Limita a altura do log para a prévia manter uma área útil."""
        self._log_box.height = min(28 + 18 * lines, _LOG_MAX_HEIGHT) if lines else 0

    def _save(self, _event=None) -> None:
        if self._on_save is not None:
            self._on_save()

    def _save_output(self, _event=None) -> None:
        if self._on_save_output is not None:
            self._on_save_output()

    def _save_drive(self, _event=None) -> None:
        if self._on_save_drive is not None:
            self._on_save_drive()

    def _open_folder(self, _event=None) -> None:
        if self._output is not None:
            open_folder(self._output)

    def _open_drive_link(self, _event=None) -> None:
        open_url(self._drive_link)

    def _copy_log(self, _event=None) -> None:
        if not self._log.value:
            return
        with contextlib.suppress(Exception):
            pyperclip.copy(self._log.value)

    def _copy_diagnostics(self, _event=None) -> None:
        if not self._diagnostics:
            return
        with contextlib.suppress(Exception):
            pyperclip.copy(self._diagnostics)

    def _refresh(self) -> None:
        if self._dispatch is not None:
            self._dispatch(self._update_now)
            return
        self._update_now()

    def _update_now(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()
