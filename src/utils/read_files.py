from pathlib import Path

import pandas as pd
from file_picker_py import pick_files_blocking


class FileReader:
    def __init__(self):
        self.files_paths: list[Path] = []
        self.dfs: dict[Path, dict[str, pd.DataFrame]] = {}

    def run(self) -> dict[Path, dict[str, pd.DataFrame]]:
        self.__pick_files()
        self.__read_files()
        return self.dfs

    def __pick_files(self) -> None:
        self.files_paths.extend([Path(file) for file in pick_files_blocking()])

    def __read_files(self) -> None:
        for file in self.files_paths:
            self.dfs[file] = pd.read_excel(file, dtype=str, sheet_name=None)
