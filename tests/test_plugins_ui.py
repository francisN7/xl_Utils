"""Área “Plugins”: lista, instalação, remoção e execução declarativa."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import flet as ft
import pytest
from plugin_helpers import installed_plugin, valid_package, write_sidecar

from xl_utils.core.plugins.errors import InstallError
from xl_utils.core.plugins.page import PageSpec
from xl_utils.shared.plugins.install import scan_installed
from xl_utils.shared.plugins.loader import MODULE_PREFIX, PluginLoader
from xl_utils.ui.pages.plugin_tool import build_plugin_page
from xl_utils.ui.pages.plugins import PluginsPage

OPTIONS_MANIFEST = """\
[plugin]
id = "autor.opcoes"
name = "Opções"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Plugin com todos os tipos de opção."

[ui]
multiple_files = true
default_all_sheets = true
note = "Dica da página."

[[options]]
key = "texto"
label = "Texto livre"
type = "text"
default = "oi"

[[options]]
key = "limite"
label = "Limite"
type = "int"
default = 5
min = 1
max = 10

[[options]]
key = "detalhado"
label = "Detalhado"
type = "bool"

[[options]]
key = "modo"
label = "Modo"
type = "choice"
default = "a"
choices = ["a", "b"]
"""

FRAMES = """\
import pandas as pd

from xl_utils.shared.plugins.api import PluginResult


def run(request):
    frame = pd.DataFrame({"aba": sorted(request.sheets.values())[0]})
    return PluginResult(frames={"dados": frame}, message="Tudo certo")
"""

MARKER = """\
from pathlib import Path

Path(__file__).parents[1].joinpath("data", "imported.txt").write_text("x")


def run(request):
    return None
"""


@pytest.fixture(autouse=True)
def clean_synthetic_modules() -> Iterator[None]:
    yield
    for name in [name for name in sys.modules if name.startswith(MODULE_PREFIX)]:
        sys.modules.pop(name, None)


def _texts(control: object) -> list[str]:
    if isinstance(control, ft.Text):
        return [str(control.value)]
    found: list[str] = []
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_texts(content))
    for child in getattr(control, "controls", None) or []:
        found.extend(_texts(child))
    return found


def _find(control: object, kind: type) -> list[object]:
    found: list[object] = []
    if isinstance(control, kind):
        found.append(control)
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_find(content, kind))
    for child in getattr(control, "controls", None) or []:
        found.extend(_find(child, kind))
    return found


def test_empty_area_explains_how_to_install(tmp_path: Path) -> None:
    page = PluginsPage(root=tmp_path / "plugins")

    assert page.scan.valid == ()
    assert page.scan.invalid == ()
    assert any("Nenhum plugin instalado" in text for text in _texts(page.control))


def test_install_and_remove_through_the_page(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    package = valid_package(tmp_path / "plugin.tar.xz")
    write_sidecar(package)
    page = PluginsPage(root=root)

    info = page.prepare(package)
    assert info.manifest.name == "Plugin de Teste"
    assert page.scan.valid == ()

    plugin = page.install(package)

    assert plugin.id == "autor.teste"
    assert [item.id for item in page.scan.valid] == ["autor.teste"]
    assert any("Plugin de Teste" in text for text in _texts(page.control))

    page.remove("autor.teste")

    assert page.scan.valid == ()
    assert not plugin.path.exists()


def test_install_refuses_duplicate_without_touching_the_first(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    package = valid_package(tmp_path / "plugin.tar.xz")
    write_sidecar(package)
    page = PluginsPage(root=root)
    first = page.install(package)

    with pytest.raises(InstallError) as info:
        page.install(package)

    assert info.value.code == "plugin_duplicate"
    assert first.path.is_dir()
    assert [item.id for item in page.scan.valid] == ["autor.teste"]


def test_invalid_folder_is_listed_with_the_code(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    broken = root / "quebrado"
    broken.mkdir(parents=True)
    (broken / "plugin.toml").write_text("isto não é toml", encoding="utf-8")

    page = PluginsPage(root=root)

    assert [item.path.name for item in page.scan.invalid] == ["quebrado"]
    assert page.scan.invalid[0].code == "manifest_invalid"
    assert any("manifest_invalid" in text for text in _texts(page.control))


def test_open_builds_the_declarative_page_and_back_returns(tmp_path: Path) -> None:
    plugin = installed_plugin(
        tmp_path,
        plugin_id="autor.opcoes",
        manifest=OPTIONS_MANIFEST,
    )
    page = PluginsPage(root=tmp_path)

    page.open_plugin("autor.opcoes")

    assert page.opened_id == "autor.opcoes"
    view = page.control.content
    layout = view.data["layout"]
    spec = PageSpec.from_manifest(plugin.manifest)
    texts = _texts(layout.control)
    assert spec.title in texts
    assert "Dica da página." in texts

    fields = _find(layout.control, ft.TextField)
    assert [field.label for field in fields] == ["Texto livre", "Limite"]
    dropdowns = _find(layout.control, ft.Dropdown)
    assert [item.label for item in dropdowns if item.label] == ["Modo"]
    checkboxes = _find(layout.control, ft.Checkbox)
    assert [item.label for item in checkboxes] == ["Detalhado"]

    page.back()

    assert page.opened_id is None
    assert any("autor.opcoes" in text for text in _texts(page.control))


def test_browse_and_open_do_not_import_plugin_code(tmp_path: Path) -> None:
    plugin = installed_plugin(tmp_path, files={"main.py": MARKER})
    marker = plugin.data_dir / "imported.txt"
    page = PluginsPage(root=tmp_path)

    page.open_plugin("autor.teste")
    page.back()
    page.read()

    assert not marker.exists()
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]


def test_execute_uses_frames_and_builds_a_save_item(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    plugin = installed_plugin(tmp_path, files={"main.py": FRAMES})
    page = build_plugin_page(plugin, loader=PluginLoader())
    layout = page.data["layout"]
    layout.state.select_files([xlsx_file])
    layout.state.set_sheet_names({xlsx_file: ["Dados"]}, all_sheets=True)
    layout._run_button.disabled = False

    layout._run()

    assert layout.result.kind == "ready"
    assert layout.state.result is not None
    assert list(layout.state.result) == ["dados"]
    assert len(layout.state.save_items) == 1
    assert layout.state.save_items[0].suggested_name.endswith(".xlsx")
    assert "Tudo certo" in " ".join(_texts(layout.result.control))


def test_options_reach_the_plugin_with_the_declared_types(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    source = """\
from xl_utils.shared.plugins.api import PluginResult


def run(request):
    options = request.options
    message = "|".join(
        f"{key}={type(options[key]).__name__}:{options[key]}"
        for key in ("texto", "limite", "detalhado", "modo")
    )
    return PluginResult(message=message)
"""
    plugin = installed_plugin(
        tmp_path,
        plugin_id="autor.opcoes",
        manifest=OPTIONS_MANIFEST,
        files={"main.py": source},
    )
    page = build_plugin_page(plugin, loader=PluginLoader())
    layout = page.data["layout"]
    layout.state.select_files([xlsx_file])
    layout.state.set_sheet_names({xlsx_file: ["Dados"]}, all_sheets=True)
    layout._run_button.disabled = False

    texts = _find(layout.control, ft.TextField)
    texts[1].value = "9"
    checkboxes = _find(layout.control, ft.Checkbox)
    checkboxes[0].value = True
    dropdowns = _find(layout.control, ft.Dropdown)
    dropdowns[0].value = "b"

    layout._run()

    assert layout.result.kind == "info"
    assert layout.result.status == "Opções"
    assert "texto=str:oi" in " ".join(_texts(layout.result.control))
    assert "limite=int:9" in " ".join(_texts(layout.result.control))
    assert "detalhado=bool:True" in " ".join(_texts(layout.result.control))
    assert "modo=str:b" in " ".join(_texts(layout.result.control))


def test_invalid_option_stops_before_the_plugin(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    plugin = installed_plugin(
        tmp_path,
        plugin_id="autor.opcoes",
        manifest=OPTIONS_MANIFEST,
        files={
            "main.py": (
                "from xl_utils.shared.plugins.api import PluginResult\n\n\n"
                "def run(request):\n"
                "    return PluginResult(message='executou')\n"
            )
        },
    )
    loader = PluginLoader()
    page = build_plugin_page(plugin, loader=loader)
    layout = page.data["layout"]
    layout.state.select_files([xlsx_file])
    layout.state.set_sheet_names({xlsx_file: ["Dados"]}, all_sheets=True)
    layout._run_button.disabled = False
    fields = _find(layout.control, ft.TextField)
    fields[1].value = "0"

    layout._run()

    assert loader.loaded_ids() == ()
    assert layout.result.kind == "error"
    assert layout.result.status == "Confira a seleção"
    assert "mínimo é 1" in " ".join(_texts(layout.result.control))


def test_broken_plugin_isolates_the_import_error(
    tmp_path: Path,
    xlsx_file: Path,
) -> None:
    plugin = installed_plugin(
        tmp_path,
        files={"main.py": "raise RuntimeError('import quebrado')\n"},
    )
    page = build_plugin_page(plugin, loader=PluginLoader())
    layout = page.data["layout"]
    layout.state.select_files([xlsx_file])
    layout.state.set_sheet_names({xlsx_file: ["Dados"]}, all_sheets=True)
    layout._run_button.disabled = False

    layout._run()

    assert layout.result.kind == "error"
    assert "falha ao importar main:run" in layout.result.diagnostics
    assert "import quebrado" in layout.result.diagnostics
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]


def test_remove_drops_the_loaded_module(tmp_path: Path) -> None:
    plugin = installed_plugin(tmp_path, files={"main.py": FRAMES})
    loader = PluginLoader()
    page = PluginsPage(root=tmp_path, loader=loader)
    page.open_plugin(plugin.id)
    loader.load(plugin)

    page.remove(plugin.id)

    assert loader.loaded_ids() == ()
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]
    assert page.opened_id is None


def test_registry_has_a_single_plugins_entrance() -> None:
    from xl_utils.ui.pages.registry import TOOLS

    entries = [tool for tool in TOOLS if tool.id == "plugins"]

    assert len(entries) == 1
    assert entries[0].label == "Plugins"


def test_scan_does_not_run_plugin_code(tmp_path: Path) -> None:
    installed_plugin(tmp_path, files={"main.py": MARKER})

    result = scan_installed(root=tmp_path)

    assert [item.id for item in result.valid] == ["autor.teste"]
    assert not (tmp_path / "autor.teste" / "data" / "imported.txt").exists()
