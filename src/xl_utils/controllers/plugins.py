"""Executa um plugin instalado a partir dos dados da página."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.plugins.errors import PluginError
from xl_utils.core.save import SaveItem
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins.api import PluginRequest, PluginResult
from xl_utils.shared.plugins.install import InstalledPlugin
from xl_utils.shared.plugins.loader import PluginLoader
from xl_utils.shared.progress import CancelToken, NullReporter, ProgressReporter


@dataclass(frozen=True, slots=True)
class PluginOutcome:
    """Saída já validada, no formato que a página sabe exibir."""

    frames: dict[str, pd.DataFrame]
    message: str
    save_items: tuple[SaveItem, ...]


def execute_plugin(
    plugin: InstalledPlugin,
    *,
    loader: PluginLoader,
    files: Sequence[Path],
    inputs: Mapping[str, Path],
    sheets: Mapping[Path, Sequence[str]],
    options: Mapping[str, object],
    log: RunLog,
    progress: ProgressReporter | NullReporter,
    token: CancelToken,
    app_version: str,
) -> PluginOutcome:
    """Importa o plugin (uma vez) e chama ``run`` fora da UI thread."""
    loaded = loader.load(plugin)
    request = PluginRequest(
        files=tuple(files),
        inputs=dict(inputs),
        sheets={path: tuple(names) for path, names in sheets.items()},
        options=dict(options),
        log=log,
        progress=progress,
        cancel=token,
        data_dir=plugin.data_dir,
        plugin_dir=plugin.path,
        app_version=app_version,
    )
    return _outcome(loaded.run(request))


def _outcome(result: object) -> PluginOutcome:
    if not isinstance(result, PluginResult):
        raise PluginError(
            "result_invalid",
            f"run() deve devolver PluginResult; recebeu {type(result).__name__}.",
        )
    frames: dict[str, pd.DataFrame] = {}
    for name, frame in result.frames.items():
        if not isinstance(name, str) or not isinstance(frame, pd.DataFrame):
            raise PluginError(
                "result_invalid",
                "frames deve mapear nome de aba para DataFrame.",
            )
        frames[name] = frame
    if not isinstance(result.message, str):
        raise PluginError("result_invalid", "message deve ser texto.")
    items: list[SaveItem] = []
    for item in result.save_items:
        if not isinstance(item, SaveItem):
            raise PluginError("result_invalid", "save_items deve conter SaveItem.")
        items.append(item)
    return PluginOutcome(
        frames=frames,
        message=result.message,
        save_items=tuple(items),
    )


__all__ = ["PluginOutcome", "execute_plugin"]
