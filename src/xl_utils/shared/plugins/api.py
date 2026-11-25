"""API pública que o plugin recebe em ``run(request)``.

Não importa Flet: o plugin devolve dados e o host monta a UI. Planilhas são
lidas por ``request.reader``, com o mesmo pipeline das ferramentas nativas.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from xl_utils.core.save import SaveItem
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins.reader import ReadError, WorkbookReader
from xl_utils.shared.progress import CancelToken, ProgressReporter


@dataclass(frozen=True, slots=True)
class PluginRequest:
    """Entrada de uma execução de plugin, fora da UI thread."""

    files: tuple[Path, ...]
    inputs: Mapping[str, Path]
    sheets: Mapping[Path, tuple[str, ...]]
    reader: WorkbookReader
    options: Mapping[str, object]
    log: RunLog
    progress: ProgressReporter
    cancel: CancelToken
    data_dir: Path
    plugin_dir: Path
    app_version: str


@dataclass(frozen=True, slots=True)
class PluginResult:
    """Saída de uma execução de plugin."""

    frames: Mapping[str, pd.DataFrame] = field(default_factory=dict)
    message: str = ""
    save_items: tuple[SaveItem, ...] = ()


__all__ = ["PluginRequest", "PluginResult", "ReadError", "WorkbookReader"]
