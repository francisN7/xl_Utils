from file_picker_py import pick_files_blocking
import pandas as pd
from pathlib import Path
from time import sleep
import os

class StrConverter():
    def __init__(self):
        self.files_paths: list[Path] = []
        self.df: pd.DataFrame = None

    def run(self) -> None:
        self.__clear()
        self.__title()
        print("Selecione os arquivos a converter: (.xlsx)")
        self.__pick_files()
        self.__check_path()
        self.__clear()
        self.__title()
        print("Salvando novos arquivos...")
        for file in self.files_paths:
            self.__read_df(file)
            new_file = file.parent.absolute().joinpath("new_files").joinpath(f"{file.stem}.xlsx")
            self.__save_new_df(new_file)
        self.__clear()
        self.__title()
        print(
            f"Novos arquivos salvos.\
            \nLocal: {self.files_paths[0].parent.absolute().joinpath(Path("new_files"))}"
        )

    
    def __title(self) -> None:
        print("__________Converter para Texto Simples__________\n\n\n")

    def __clear(self) -> None:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def __pick_files(self) -> None:
        sleep(0.5)
        for file in pick_files_blocking():
            self.files_paths.append(Path(file))

    def __read_df(self, file: Path) -> None:
        self.df = pd.read_excel(file, dtype=str)

    def __save_new_df(self, new_file: Path) -> None:
        self.df.to_excel(new_file, engine='xlsxwriter', index=False)

    def __check_path(self) -> None:
        if not self.files_paths[0].parent.absolute().joinpath(Path("new_files")).exists():
            Path.mkdir(self.files_paths[0].parent.absolute().joinpath(Path("new_files")))

if __name__ == "__main__":
    converter = StrConverter()
    converter.run()