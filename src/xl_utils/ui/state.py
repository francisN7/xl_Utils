"""Per-tool state kept while the user navigates between pages."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from xl_utils.core.tools.sheets import default_selection


@dataclass
class ToolState:
    """State of one tool page.

    Selecting a new file discards the previous result; the page, its options
    and the selected tool stay in memory while the user navigates.
    """

    files: list[Path] = field(default_factory=list)
    result: dict[str, pd.DataFrame] | None = None
    options: dict[str, object] = field(default_factory=dict)
    sheet_names: dict[Path, list[str]] = field(default_factory=dict)
    selected_sheets: dict[Path, set[str]] = field(default_factory=dict)
    message: str = ""
    error: str | None = None
    running: bool = False

    @property
    def sheet_count(self) -> int:
        """Return how many sheets the current files expose."""
        return sum(len(names) for names in self.sheet_names.values())

    @property
    def selected_count(self) -> int:
        """Return how many sheets are currently marked."""
        return sum(len(names) for names in self.selected_sheets.values())

    def select_files(self, files: list[Path]) -> None:
        """Replace the selection and discard any previous result."""
        self.files = list(files)
        self.result = None
        self.sheet_names = {}
        self.selected_sheets = {}
        self.message = ""
        self.error = None
        self.running = False

    def set_sheet_names(self, sheets: Mapping[Path, Sequence[str]]) -> None:
        """Store the sheets of the current files and apply the default rule."""
        names = {path: list(values) for path, values in sheets.items()}
        self.sheet_names = names
        self.selected_sheets = default_selection(names)

    def reset(self) -> None:
        """Clear everything for this tool."""
        self.files.clear()
        self.result = None
        self.options.clear()
        self.sheet_names.clear()
        self.selected_sheets.clear()
        self.message = ""
        self.error = None
        self.running = False
