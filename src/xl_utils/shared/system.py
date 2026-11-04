"""Operating-system helpers that are not part of the domain core."""

import os
import subprocess
import sys
from pathlib import Path


def open_folder(path: Path) -> None:
    """Open the folder that contains ``path`` in the native file manager."""
    target = path if path.is_dir() else path.parent
    if sys.platform == "win32":
        os.startfile(target)  # noqa: S606  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(target)])
    else:
        subprocess.Popen(["xdg-open", str(target)])
