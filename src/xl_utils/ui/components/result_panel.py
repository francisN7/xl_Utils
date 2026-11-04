"""Cartão de resultado: status, ações de salvar, caminho de saída, log e prévia."""

import contextlib
from collections.abc import Callable, Sequence
from pathlib import Path

import flet as ft
import pandas as pd
import pyperclip

from xl_utils.shared.log import RunLog
from xl_utils.shared.system import open_folder
from xl_utils.ui import theme
from xl_utils.ui.components.preview_table import PreviewTable

_LOG_MAX_HEIGHT = 160


class ResultPanel:
    """Estado visual do resultado de uma ferramenta."""

    def __init__(
        self,
        *,
        on_save: Callable[[], None] | None = None,
        on_save_output: Callable[[], None] | None = None,
    ) -> None:
        self._on_save = on_save
        self._on_save_output = on_save_output
        self._output: Path | None = None
        self._kind = "idle"
        self._diagnostics = ""
        self.preview = PreviewTable()

        self._icon = ft.Icon(ft.Icons.INFO_OUTLINE, color=theme.MUTED, size=18)
        self._status = ft.Text(
            "Aguardando arquivo.",
            size=theme.FONT_SM,
            weight=ft.FontWeight.BOLD,
        )
        self._detail = ft.Text("", size=theme.FONT_SM, color=theme.MUTED)
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
        self._save_row = ft.Column(
            controls=[
                ft.Row(
                    controls=[self._save_button, self._save_output_button],
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
            color="#C9CBDC",
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
                self._path,
                self._save_row,
                ft.Row(
                    controls=[self._open_button],
                    alignment=ft.MainAxisAlignment.START,
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
        """Devolve o estado: idle, info, running, ready, success ou error."""
        return self._kind

    @property
    def status(self) -> str:
        """Devolve a linha de status exibida agora."""
        return str(self._status.value or "")

    @property
    def diagnostics(self) -> str:
        """Devolve o texto guardado para “Copiar diagnóstico”."""
        return self._diagnostics

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
        self._save_row.visible = False
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
        self._refresh()

    def set_running(self, message: str = "Executando...") -> None:
        self._kind = "running"
        self._icon.name = ft.Icons.HOURGLASS_EMPTY
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = ""
        self._save_row.visible = False
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
        self._save_row.visible = True
        self.preview.set_frames(frames)
        self._refresh()

    def set_saving(self, message: str = "Salvando...") -> None:
        self._kind = "running"
        self._icon.name = ft.Icons.HOURGLASS_EMPTY
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = ""
        self._save_row.visible = False
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
        self._save_row.visible = False
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
        self._save_row.visible = True
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
        self._save_row.visible = False
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
        current = self._log.value or ""
        self._log.value = f"{current}\n{line}".strip()
        self._log_section.visible = True
        self._resize_log(len(self._log.value.splitlines()))
        self._refresh()

    def _resize_log(self, lines: int) -> None:
        """Limita a altura do log para a prévia manter uma área útil."""
        self._log_box.height = min(28 + 18 * lines, _LOG_MAX_HEIGHT) if lines else 0

    def _save(self, _event=None) -> None:
        if self._on_save is not None:
            self._on_save()

    def _save_output(self, _event=None) -> None:
        if self._on_save_output is not None:
            self._on_save_output()

    def _open_folder(self, _event=None) -> None:
        if self._output is not None:
            open_folder(self._output)

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
        with contextlib.suppress(RuntimeError):
            self.control.update()
