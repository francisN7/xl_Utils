from file_picker_py import pick_files_blocking
from pathlib import Path
from time import sleep
import subprocess
import pandas as pd
import magic
import os


class StrConverter:
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
            self.__read_df(self.__corret_file_type(file))
            new_file = (
                file.parent.absolute()
                .joinpath("new_files")
                .joinpath(f"{file.stem}.xlsx")
            )
            self.__save_new_df(new_file)
        self.__clear()
        self.__title()
        print(
            f"Novos arquivos salvos.\
            \nLocal: {self.files_paths[0].parent.absolute().joinpath(Path('new_files'))}"
        )

    def __title(self) -> None:
        print("__________Converter para Texto Simples__________\n\n\n")

    def __pick_files(self) -> None:
        sleep(0.5)
        for file in pick_files_blocking():
            self.files_paths.append(Path(file))

    def __check_path(self) -> None:
        if (
            not self.files_paths[0]
            .parent.absolute()
            .joinpath(Path("new_files"))
            .exists()
        ):
            Path.mkdir(
                self.files_paths[0].parent.absolute().joinpath(Path("new_files"))
            )

    def __read_df(self, file: Path) -> None:
        if file.suffix.lower() == ".xls":
            self.df = pd.read_excel(file, dtype=str, engine="xlrd")
        elif file.suffix.lower() == ".html":
            self.df = pd.read_html(file)[0]
        else:
            try:
                self.df = pd.read_excel(file, dtype=str)
            except Exception as e:  # noqa: F841
                print(f"Erro ao ler {file.name}, tentando reparar...")
                self.df = pd.read_csv(
                    self.__repair_df(file),
                    dtype=str,
                    encoding="utf-8",
                    quotechar='"',
                    sep=",",
                )

    def __repair_df(self, file: Path) -> Path:
        new_file = file.parent / f"{file.stem}_repaired.csv"
        subprocess.run(f'xlsx2csv -q all "{file}" "{new_file}"', shell=True, check=True)
        return Path(new_file)

    def __save_new_df(self, new_file: Path) -> None:
        self.df.to_excel(new_file, engine="xlsxwriter", index=False)

    def __corret_file_type(self, file: Path) -> Path:
        file_type = magic.from_file(str(file), mime=True)
        new_file_name = str(file)
        if f".{file_type.split('/')[1].split('.')[-1]}" == ".sheet":
            pass
        elif f".{file_type.split('/')[1]}" != file.suffix:
            new_file_name = (
                f"{str(file).replace(file.suffix, f'.{file_type.split("/")[1]}')}"
            )
            print(
                f"Formato real detectado como: {file_type}\nRenomeando arquivo em {file}"
            )
            os.rename(file, new_file_name)
        return Path(new_file_name)

    def __clear(self) -> None:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


if __name__ == "__main__":
    converter = StrConverter()
    converter.run()
