"""Carregamento sob demanda do código do plugin."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from plugin_helpers import VALID_MANIFEST, installed_plugin

from xl_utils.shared.plugins.install import InstalledPlugin
from xl_utils.shared.plugins.loader import (
    MODULE_PREFIX,
    PluginLoader,
    PluginLoadError,
)

MARKER = """\
from pathlib import Path

Path(__file__).parents[1].joinpath("data", "imported.txt").write_text("x")


def run(request):
    return "ok"
"""


@pytest.fixture(autouse=True)
def clean_synthetic_modules() -> Iterator[None]:
    """Nenhum módulo sintético sobrevive de um teste para o outro."""
    yield
    for name in [name for name in sys.modules if name.startswith(MODULE_PREFIX)]:
        sys.modules.pop(name, None)


def make_plugin(
    root: Path,
    *,
    plugin_id: str = "autor.teste",
    manifest: str = VALID_MANIFEST,
    files: dict[str, str] | None = None,
) -> InstalledPlugin:
    """Apelido local do helper compartilhado de plugin instalado."""
    return installed_plugin(
        root,
        plugin_id=plugin_id,
        manifest=manifest,
        files=files,
    )


def test_discovery_does_not_import_code(tmp_path: Path) -> None:
    plugin = make_plugin(tmp_path, files={"main.py": MARKER})
    marker = plugin.data_dir / "imported.txt"

    assert plugin.manifest is not None
    assert not marker.exists()

    loader = PluginLoader()
    loaded = loader.load(plugin)

    assert marker.read_text(encoding="utf-8") == "x"
    assert loaded.run(None) == "ok"


def test_load_is_cached_per_plugin(tmp_path: Path) -> None:
    plugin = make_plugin(
        tmp_path,
        files={
            "main.py": (
                "import_count = 1\n\n\ndef run(request):\n    return import_count\n"
            )
        },
    )
    loader = PluginLoader()

    first = loader.load(plugin)
    second = loader.load(plugin)

    assert first is second
    assert second.module.import_count == 1
    assert loader.loaded_ids() == ("autor.teste",)


def test_relative_import_between_plugin_files(tmp_path: Path) -> None:
    manifest = VALID_MANIFEST.replace(
        'entrypoint = "main:run"',
        'entrypoint = "pkg.main:run"',
    )
    plugin = make_plugin(
        tmp_path,
        manifest=manifest,
        files={
            "pkg/__init__.py": "",
            "pkg/helper.py": "VALUE = 42\n",
            "pkg/main.py": (
                "from .helper import VALUE\n\n\ndef run(request):\n    return VALUE\n"
            ),
        },
    )

    loaded = PluginLoader().load(plugin)

    assert loaded.run(None) == 42


def test_relative_import_from_namespace_package(tmp_path: Path) -> None:
    manifest = VALID_MANIFEST.replace(
        'entrypoint = "main:run"',
        'entrypoint = "pkg.main:run"',
    )
    plugin = make_plugin(
        tmp_path,
        manifest=manifest,
        files={
            "pkg/helper.py": "VALUE = 'sem init'\n",
            "pkg/main.py": (
                "from .helper import VALUE\n\n\ndef run(request):\n    return VALUE\n"
            ),
        },
    )

    loaded = PluginLoader().load(plugin)

    assert loaded.run(None) == "sem init"


def test_import_error_is_isolated(tmp_path: Path) -> None:
    plugin = make_plugin(
        tmp_path,
        files={"main.py": "raise RuntimeError('boom')\n"},
    )

    with pytest.raises(PluginLoadError) as info:
        PluginLoader().load(plugin)

    assert info.value.code == "plugin_import_failed"
    assert "boom" in str(info.value)
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]


def test_missing_run_function(tmp_path: Path) -> None:
    plugin = make_plugin(tmp_path, files={"main.py": "VALUE = 1\n"})

    with pytest.raises(PluginLoadError) as info:
        PluginLoader().load(plugin)

    assert info.value.code == "run_missing"
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]


@pytest.mark.parametrize(
    "source",
    [
        "def run():\n    return None\n",
        "def run(request, extra):\n    return None\n",
        "def run(*args):\n    return None\n",
        "def run(*, request):\n    return None\n",
        "run = 3\n",
    ],
)
def test_wrong_signature_is_refused(tmp_path: Path, source: str) -> None:
    plugin = make_plugin(tmp_path, files={"main.py": source})

    with pytest.raises(PluginLoadError) as info:
        PluginLoader().load(plugin)

    assert info.value.code in ("run_signature", "run_missing")
    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]


def test_sys_path_is_untouched(tmp_path: Path) -> None:
    plugin = make_plugin(tmp_path)
    before = list(sys.path)

    PluginLoader().load(plugin)

    assert sys.path == before


def test_two_plugins_with_same_module_name(tmp_path: Path) -> None:
    loader = PluginLoader()
    first = make_plugin(
        tmp_path,
        plugin_id="autor.um",
        files={"main.py": "def run(request):\n    return 'um'\n"},
    )
    second = make_plugin(
        tmp_path,
        plugin_id="autor.dois",
        files={"main.py": "def run(request):\n    return 'dois'\n"},
    )

    loaded_first = loader.load(first)
    loaded_second = loader.load(second)

    assert loaded_first.run(None) == "um"
    assert loaded_second.run(None) == "dois"
    assert loaded_first.module is not loaded_second.module


def test_forget_drops_modules(tmp_path: Path) -> None:
    plugin = make_plugin(tmp_path)
    loader = PluginLoader()
    first = loader.load(plugin)

    loader.forget(plugin.id)

    assert not [name for name in sys.modules if name.startswith(MODULE_PREFIX)]
    assert loader.loaded_ids() == ()
    assert loader.load(plugin) is not first
