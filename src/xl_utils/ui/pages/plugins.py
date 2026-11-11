"""Área “Plugins”: lista, instalação, remoção e abertura da ferramenta."""

from __future__ import annotations

import asyncio
import contextlib
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import flet as ft

from xl_utils import __version__
from xl_utils.core.plugins.errors import PluginError
from xl_utils.core.plugins.package import (
    DEFAULT_LIMITS,
    PackageInfo,
    inspect_package,
    verify_sidecar,
)
from xl_utils.core.plugins.page import describe_permissions
from xl_utils.shared.plugins.install import (
    InstalledPlugin,
    ScanResult,
    install_package,
    plugins_root,
    scan_installed,
    uninstall_plugin,
)
from xl_utils.shared.plugins.loader import PluginLoader
from xl_utils.ui import theme
from xl_utils.ui.drive import DriveSession
from xl_utils.ui.pages.plugin_tool import build_plugin_page

ARCHIVE_EXTENSIONS = ["xz", "txz"]


class PluginsPage:
    """Lista os plugins instalados e abre cada ferramenta sob demanda."""

    def __init__(
        self,
        *,
        loader: PluginLoader | None = None,
        drive: DriveSession | None = None,
        root: Path | None = None,
    ) -> None:
        self._loader = loader or PluginLoader()
        self._drive = drive
        self._root = root
        self._open_id: str | None = None
        self._picker = ft.FilePicker()
        self._picker_attached = False
        self._busy = False

        self._scan: ScanResult = scan_installed(root=root)
        self._notice = ft.Text("", size=theme.FONT_SM, color=theme.GREEN)
        self._list = ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.HIDDEN)
        self._area = ft.Container(expand=True)
        self._list_view = self._build_list()
        self._area.content = self._list_view
        self.control = self._area
        self._render_list()

    # --- leitura e ações sem UI -------------------------------------------

    @property
    def scan(self) -> ScanResult:
        """Último resultado da descoberta, sem importar código."""
        return self._scan

    @property
    def opened_id(self) -> str | None:
        """ID da ferramenta aberta, ou ``None`` quando a lista está à vista."""
        return self._open_id

    def read(self) -> ScanResult:
        """Relê a pasta de plugins e atualiza a lista."""
        self._scan = scan_installed(root=self._root)
        self._render_list()
        return self._scan

    def prepare(self, archive: Path) -> PackageInfo:
        """Confere sidecar e pacote antes de mostrar a confirmação."""
        verify_sidecar(archive)
        return inspect_package(
            archive,
            limits=DEFAULT_LIMITS,
            app_version=__version__,
        )

    def install(self, archive: Path) -> InstalledPlugin:
        """Instala um pacote conferido e atualiza a lista."""
        plugin = install_package(
            archive,
            root=self._root,
            app_version=__version__,
        )
        self._loader.forget(plugin.id)
        self.read()
        return plugin

    def remove(self, plugin_id: str) -> None:
        """Remove o plugin (com ``data/``) e invalida o módulo carregado."""
        uninstall_plugin(plugin_id, root=self._root)
        self._loader.forget(plugin_id)
        if self._open_id == plugin_id:
            self.back()
        self.read()

    def open_plugin(self, plugin_id: str) -> None:
        """Abre a ferramenta de um plugin válido."""
        plugin = next(
            (item for item in self._scan.valid if item.id == plugin_id),
            None,
        )
        if plugin is None:
            self._fail("Plugin não encontrado", f"Releia a lista: {plugin_id}.")
            return
        self._open(plugin)

    def back(self) -> None:
        """Volta da ferramenta para a lista."""
        self._open_id = None
        self._area.content = self._list_view
        self._refresh()

    # --- UI: lista --------------------------------------------------------

    def _build_list(self) -> ft.Control:
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Plugins",
                                size=theme.FONT_TITLE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Ferramentas locais instaladas em "
                                f"{plugins_root()}. Instalar é confiar no "
                                "código: as permissões são avisos, não sandbox.",
                                size=theme.FONT_SM,
                                color=theme.MUTED,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "Abrir pasta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _event: self._open_folder(plugins_root()),
                    ),
                    ft.FilledButton(
                        "Instalar plugin",
                        icon=ft.Icons.ADD,
                        on_click=self._install_clicked,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(bottom=16, right=56),
        )
        return ft.Container(
            content=ft.Column(
                controls=[header, self._notice, self._list],
                spacing=12,
                expand=True,
                scroll=ft.ScrollMode.HIDDEN,
            ),
            padding=24,
            expand=True,
        )

    def _render_list(self) -> None:
        cards: list[ft.Control] = [
            self._plugin_card(plugin) for plugin in self._scan.valid
        ]
        cards.extend(
            self._invalid_card(item.path, item.code, item.message)
            for item in self._scan.invalid
        )
        if not cards:
            cards.append(
                ft.Text(
                    "Nenhum plugin instalado ainda. Use “Instalar plugin” "
                    "com um pacote .tar.xz e o sidecar .sha256.",
                    size=theme.FONT_SM,
                    color=theme.MUTED,
                )
            )
        self._list.controls = cards
        self._refresh()

    def _plugin_card(self, plugin: InstalledPlugin) -> ft.Control:
        manifest = plugin.manifest
        permissions = (
            ", ".join(describe_permissions(manifest.permissions))
            if manifest
            else "manifesto indisponível"
        )
        description = manifest.description if manifest else ""
        api = f"API {plugin.api_version}"
        return _card(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EXTENSION, color=theme.PURPLE, size=20),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        plugin.name,
                                        size=theme.FONT_MD,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{plugin.id} · v{plugin.version} · {api}",
                                        size=theme.FONT_XS,
                                        color=theme.MUTED,
                                    ),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.FilledButton(
                                "Abrir",
                                icon=ft.Icons.PLAY_ARROW,
                                on_click=lambda _event, item=plugin: self._open(item),
                            ),
                            ft.OutlinedButton(
                                "Pasta",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=lambda _event, item=plugin: self._open_folder(
                                    item.path
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                tooltip="Remover plugin",
                                on_click=lambda _event, item=plugin: (
                                    self._remove_clicked(item)
                                ),
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(description, size=theme.FONT_SM, color=theme.SUBTLE_TEXT),
                    ft.Text(permissions, size=theme.FONT_XS, color=theme.ORANGE),
                    ft.Text(
                        str(plugin.path),
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        tooltip=str(plugin.path),
                    ),
                ],
                spacing=8,
            ),
            border=theme.BORDER,
        )

    def _invalid_card(self, path: Path, code: str, message: str) -> ft.Control:
        return _card(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=theme.RED, size=20),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        path.name,
                                        size=theme.FONT_MD,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{code} · {message}",
                                        size=theme.FONT_XS,
                                        color=theme.RED,
                                    ),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "Pasta",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=lambda _event, item=path: self._open_folder(
                                    item
                                ),
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "Corrija ou remova esta pasta manualmente; ela não "
                        "aparece como ferramenta.",
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                    ),
                ],
                spacing=8,
            ),
            border=theme.ERROR_BG,
        )

    # --- UI: instalar -----------------------------------------------------

    def _install_clicked(self, _event=None) -> None:
        page = self._page()
        if page is None or self._busy:
            return
        self._attach_picker(page)
        page.run_task(self._pick_archive)

    async def _pick_archive(self) -> None:
        files = await self._picker.pick_files(
            dialog_title="Selecione o pacote do plugin",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=ARCHIVE_EXTENSIONS,
            allow_multiple=False,
        )
        path = next((Path(item.path) for item in files if item.path), None)
        if path is None:
            return
        self._set_busy(True, "Conferindo o pacote...")
        try:
            info = await asyncio.to_thread(self.prepare, path)
        except PluginError as error:
            self._fail("Pacote recusado", f"{error.code}: {error}")
            return
        except OSError as error:
            self._fail("Pacote recusado", str(error))
            return
        finally:
            self._set_busy(False, "")
        self._confirm(path, info)

    def _confirm(self, archive: Path, info: PackageInfo) -> None:
        page = self._page()
        if page is None:
            return
        manifest = info.manifest
        permissions = ", ".join(describe_permissions(manifest.permissions))

        def confirm(_event=None) -> None:
            page.pop_dialog()
            page.run_task(self._install_async, archive)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Instalar plugin?"),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{manifest.name} {manifest.version}",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{manifest.id} · API {manifest.api_version}",
                            size=theme.FONT_XS,
                            color=theme.MUTED,
                        ),
                        ft.Text(manifest.description, size=theme.FONT_SM),
                        ft.Text(
                            f"Permissões declaradas: {permissions}.",
                            size=theme.FONT_SM,
                            color=theme.ORANGE,
                        ),
                        ft.Text(
                            "O plugin roda no mesmo processo, com os direitos "
                            "do seu usuário. Instale só o que você confia.",
                            size=theme.FONT_XS,
                            color=theme.MUTED,
                        ),
                    ],
                    spacing=8,
                    tight=True,
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda _event: page.pop_dialog(),
                    ),
                    ft.FilledButton("Instalar", on_click=confirm),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    async def _install_async(self, archive: Path) -> None:
        self._set_busy(True, "Instalando...")
        try:
            plugin = await asyncio.to_thread(self.install, archive)
        except PluginError as error:
            self._fail("Não foi possível instalar", f"{error.code}: {error}")
            return
        except OSError as error:
            self._fail("Não foi possível instalar", str(error))
            return
        finally:
            self._set_busy(False, "")
        self._ok(f"{plugin.name} {plugin.version} instalado.")

    # --- UI: remover ------------------------------------------------------

    def _remove_clicked(self, plugin: InstalledPlugin) -> None:
        page = self._page()
        if page is None:
            return

        def confirm(_event=None) -> None:
            page.pop_dialog()
            page.run_task(self._remove_async, plugin)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Remover plugin?"),
                content=ft.Text(
                    f"{plugin.name} será removido, junto com a pasta data/ "
                    "dele. Essa ação não pode ser desfeita.",
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda _event: page.pop_dialog(),
                    ),
                    ft.FilledButton("Remover", on_click=confirm),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    async def _remove_async(self, plugin: InstalledPlugin) -> None:
        try:
            await asyncio.to_thread(self.remove, plugin.id)
        except PluginError as error:
            self._fail("Não foi possível remover", f"{error.code}: {error}")
            return
        except OSError as error:
            self._fail("Não foi possível remover", str(error))
            return
        self._ok(f"{plugin.name} removido.")

    # --- UI: abrir --------------------------------------------------------

    def _open(self, plugin: InstalledPlugin) -> None:
        self._notice.value = ""
        self._open_id = plugin.id
        self._area.content = build_plugin_page(
            plugin,
            loader=self._loader,
            drive=self._drive,
            on_back=self.back,
        )
        self._refresh()

    # --- utilidades -------------------------------------------------------

    def _page(self) -> ft.Page | None:
        try:
            page = self.control.page
        except RuntimeError:
            return None
        if page is None or not hasattr(page, "run_task"):
            return None
        return page

    def _attach_picker(self, page: ft.Page) -> None:
        if not self._picker_attached:
            page.services.append(self._picker)
            self._picker_attached = True

    def _open_folder(self, path: Path) -> None:
        try:
            if sys.platform == "win32":
                startfile: Callable[[str], None] | None = getattr(os, "startfile", None)
                if startfile is None:
                    raise OSError("Abrir pasta não é suportado aqui.")
                startfile(str(path))
            else:
                subprocess.Popen(["xdg-open", str(path)])  # noqa: S603
        except OSError as error:
            self._fail("Não foi possível abrir a pasta", str(error))

    def _set_busy(self, busy: bool, message: str) -> None:
        self._busy = busy
        if message:
            self._notice.value = message
            self._notice.color = theme.MUTED
        self._refresh()

    def _ok(self, message: str) -> None:
        self._notice.value = message
        self._notice.color = theme.GREEN
        self._refresh()

    def _fail(self, title: str, detail: str) -> None:
        self._notice.value = f"{title}: {detail}"
        self._notice.color = theme.RED
        self._refresh()

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def _card(content: ft.Control, *, border: str) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=theme.SURFACE,
        border=ft.Border.all(1, border),
        border_radius=12,
        padding=16,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )


def build(drive: DriveSession | None = None) -> ft.Control:
    """Fábrica da página usada pelo registro de ferramentas."""
    return PluginsPage(drive=drive).control


__all__ = ["PluginsPage", "build"]
