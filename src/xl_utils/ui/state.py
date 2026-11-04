"""Per-tool state kept while the user navigates between pages."""

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class ToolState:
    """State of one tool page.

    Selecting a new file resets options and result; the page itself and the
    selected tool stay in memory while the user navigates.
    """

    files: list[Path] = field(default_factory=list)
    result: dict[str, pd.DataFrame] | None = None
    message: str = ""
    error: str | None = None
    running: bool = False

    def select_files(self, files: list[Path]) -> None:
        """Replace the selection and discard any previous result."""
        self.files = list(files)
        self.result = None
        self.message = ""
        self.error = None
        self.running = False

    def reset(self) -> None:
        """Clear everything for this tool."""
        self.files.clear()
        self.result = None
        self.message = ""
        self.error = None
        self.running = False
