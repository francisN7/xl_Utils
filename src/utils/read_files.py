from pathlib import Path

import magic
import pandas as pd
from file_picker_py import pick_files_blocking


class FileReader:
    def __init__(self):
        self.files_paths: list[Path] = []
        self.dfs: dict[Path, dict[str, pd.DataFrame]] = {}

    def run(self) -> dict[Path, dict[str, pd.DataFrame]]:
        self.__pick_files()
        self.__corret_file_type()
        # self.__read_files()
        return self.dfs

    def __pick_files(self) -> None:
        self.files_paths.extend([Path(file) for file in pick_files_blocking()])

    def __read_files(self) -> None:
        for file in self.files_paths:
            self.dfs[file] = pd.read_excel(file, dtype=str, sheet_name=None)

    def __corret_file_type(self) -> None:
        convert = {
            "text/plain": ".csv",
            "text/html": ".html",
            "application/pdf": ".pdf",
            "application/vnd.ms-excel": ".xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        }
        for file in self.files_paths:
            file_type = magic.from_file(str(file), mime=True)
            if file_type not in convert.keys():
                raise NotImplementedError(
                    f'O tipo detectado "{file_type}" ainda não é suportado.'
                )
            elif file.suffix != convert[file_type]:
                print(
                    f'O formato real de "{file.name}" é "{convert[file_type]}".\nCorrigindo extensão..\n\n'
                )
                file.rename(file.with_suffix(convert[file_type]))
