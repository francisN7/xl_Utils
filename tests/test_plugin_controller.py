"""Execução de plugin: request montado pelo host e saída validada."""

from __future__ import annotations

from pathlib import Path

import pytest
from plugin_helpers import installed_plugin

from xl_utils.controllers.plugins import execute_plugin
from xl_utils.core.plugins.errors import PluginError
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins.loader import PluginLoader
from xl_utils.shared.progress import CancelToken, NullReporter

DETAILS = """\
import pandas as pd

from xl_utils.shared.plugins.api import PluginResult


def run(request):
    names = [name for names in request.sheets.values() for name in names]
    frame = pd.DataFrame(
        {
            "aba": names,
            "arquivo": [path.name for path in request.files] * len(names),
        }
    )
    message = (
        f"{request.options['modo']}|{request.app_version}|"
        f"{request.data_dir == request.plugin_dir / 'data'}"
    )
    return PluginResult(frames={"dados": frame}, message=message)
"""


def execute(plugin, tmp_path: Path, *, options=None):
    return execute_plugin(
        plugin,
        loader=PluginLoader(),
        files=(tmp_path / "entrada.xlsx",),
        inputs={},
        sheets={tmp_path / "entrada.xlsx": ("A", "B")},
        options={"modo": "b"} if options is None else options,
        log=RunLog(),
        progress=NullReporter(),
        token=CancelToken(),
        app_version="0.3.0",
    )


def test_execute_builds_the_request_and_reads_the_result(tmp_path: Path) -> None:
    plugin = installed_plugin(tmp_path, files={"main.py": DETAILS})

    outcome = execute(plugin, tmp_path)

    frame = outcome.frames["dados"]
    assert list(frame["arquivo"]) == ["entrada.xlsx", "entrada.xlsx"]
    assert list(frame["aba"]) == ["A", "B"]
    assert outcome.message == "b|0.3.0|True"
    assert outcome.save_items == ()


def test_execute_reuses_the_imported_module(tmp_path: Path) -> None:
    source = (
        "from xl_utils.shared.plugins.api import PluginResult\n\n"
        "import_count = 1\n\n\n"
        "def run(request):\n"
        "    return PluginResult(message=str(import_count))\n"
    )
    plugin = installed_plugin(tmp_path, files={"main.py": source})
    loader = PluginLoader()

    first = execute_plugin(
        plugin,
        loader=loader,
        files=(),
        inputs={},
        sheets={},
        options={},
        log=RunLog(),
        progress=NullReporter(),
        token=CancelToken(),
        app_version="0.3.0",
    )
    second = execute_plugin(
        plugin,
        loader=loader,
        files=(),
        inputs={},
        sheets={},
        options={},
        log=RunLog(),
        progress=NullReporter(),
        token=CancelToken(),
        app_version="0.3.0",
    )

    assert first.message == "1"
    assert second.message == "1"
    assert loader.loaded_ids() == (plugin.id,)


@pytest.mark.parametrize(
    "source",
    [
        "def run(request):\n    return {'x': 1}\n",
        "def run(request):\n    return None\n",
    ],
)
def test_result_must_be_a_plugin_result(tmp_path: Path, source: str) -> None:
    plugin = installed_plugin(tmp_path, files={"main.py": source})

    with pytest.raises(PluginError) as info:
        execute(plugin, tmp_path)

    assert info.value.code == "result_invalid"


def test_frames_must_map_names_to_dataframes(tmp_path: Path) -> None:
    plugin = installed_plugin(
        tmp_path,
        files={
            "main.py": (
                "from xl_utils.shared.plugins.api import PluginResult\n\n\n"
                "def run(request):\n"
                "    return PluginResult(frames={'a': [1, 2]})\n"
            )
        },
    )

    with pytest.raises(PluginError) as info:
        execute(plugin, tmp_path)

    assert info.value.code == "result_invalid"


def test_message_must_be_text(tmp_path: Path) -> None:
    plugin = installed_plugin(
        tmp_path,
        files={
            "main.py": (
                "from xl_utils.shared.plugins.api import PluginResult\n\n\n"
                "def run(request):\n"
                "    frame = __import__('pandas').DataFrame()\n"
                "    return PluginResult(frames={'a': frame}, message=3)\n"
            )
        },
    )

    with pytest.raises(PluginError) as info:
        execute(plugin, tmp_path)

    assert info.value.code == "result_invalid"


def test_plugin_exception_keeps_the_original_type(tmp_path: Path) -> None:
    plugin = installed_plugin(
        tmp_path,
        files={"main.py": "def run(request):\n    raise RuntimeError('boom')\n"},
    )

    with pytest.raises(RuntimeError, match="boom"):
        execute(plugin, tmp_path)


def test_save_items_are_validated(tmp_path: Path) -> None:
    plugin = installed_plugin(
        tmp_path,
        files={
            "main.py": (
                "from xl_utils.shared.plugins.api import PluginResult\n\n\n"
                "def run(request):\n"
                "    return PluginResult(save_items=('nao-e-item',))\n"
            )
        },
    )

    with pytest.raises(PluginError) as info:
        execute(plugin, tmp_path)

    assert info.value.code == "result_invalid"


def test_default_options_are_not_invented(tmp_path: Path) -> None:
    """O controller repassa o mapping já validado pela página."""
    plugin = installed_plugin(
        tmp_path,
        files={
            "main.py": (
                "from xl_utils.shared.plugins.api import PluginResult\n\n\n"
                "def run(request):\n"
                "    return PluginResult(message=','.join(sorted(request.options)))\n"
            )
        },
    )

    outcome = execute(plugin, tmp_path, options={})

    assert outcome.message == ""
