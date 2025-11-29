import subprocess
from pathlib import Path

import pandas as pd
import puremagic
from file_picker_py import pick_file_blocking, pick_files_blocking


class FileReader:
    def __init__(self):
        self.files_paths: list[Path] = []
        self.dfs: dict[Path, dict[str, pd.DataFrame]] = {}

    def run(self, one_file: bool = False) -> dict[Path, dict[str, pd.DataFrame]]:
        self.__pick_files(one_file)
        self.__corret_file_type()
        self.__read_files()
        return self.dfs

    def __pick_files(self, one_file: bool = False) -> None:
        if one_file:
            self.files_paths.append(Path(pick_file_blocking()))
        else:
            self.files_paths.extend([Path(file) for file in pick_files_blocking()])

    def __read_files(self) -> None:
        for file in self.files_paths:
            try:
                if file.suffix.lower() == ".html":
                    for n, df in enumerate(pd.read_html(file), start=1):
                        self.dfs[file] = {f"Página{n}": df}
                elif file.suffix.lower() == ".xls":
                    self.dfs[file] = pd.read_excel(
                        file, dtype=str, engine="xlrd", sheet_name=None
                    )
                elif file.suffix.lower() == ".csv":
                    self.dfs[file] = {"Página1": pd.read_csv(file, dtype=str)}
                elif file.suffix.lower() == ".xlsx":
                    self.dfs[file] = pd.read_excel(file, dtype=str, sheet_name=None)
                else:
                    print(
                        f'O arquivo "{file}" não foi processado, pois o tipo "{file.suffix}" ainda não é suportado.'
                    )
            except (ValueError, TypeError) as e:
                if "No tables found" in str(e):
                    print(f"Ignorando o arquivo {file}, nenhuma planilha encontrada.")
                else:
                    new_file = self.__repair_df(file)
                    self.dfs[file] = {"Página1": pd.read_csv(new_file, dtype=str)}
                    new_file.unlink()

    def __corret_file_type(self) -> None:
        supported_formats = [".csv", ".html", ".xls", ".xlsx", ".json"]
        for n, file in enumerate(self.files_paths):
            file_type = f".{puremagic.what(file)}"
            print(f"\n\n\n\n{file_type}\n\n\n\n")
            if file_type == ".":
                print(
                    "\nNão foi possível detectar o real tipo de arquivo.\nSeguindo com a extensão original.\n"
                )
            elif file_type not in supported_formats:
                raise NotImplementedError(
                    f'O tipo detectado "{file_type}" ainda não é suportado.'
                )
            elif file.suffix != file_type:
                print(
                    f'O formato real de "{file.name}" é "{file_type}".\nCorrigindo extensão..\n\n'
                )
                new_file = file.with_suffix(file_type)
                file.rename(new_file)
                self.files_paths[n] = new_file

    def __repair_df(self, file: Path) -> Path:
        new_file = f"{file.with_suffix('')}_repaired.csv"
        subprocess.run(f'xlsx2csv -q all "{file}" "{new_file}"', shell=True, check=True)
        return Path(new_file)
