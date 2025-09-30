import pandas as pd
from file_picker_py import pick_files_blocking
from pathlib import Path
import os


class Merger:
    def __init__(self):
        self.__file_paths: list[Path] = []
        self.__dataframes: list[pd.DataFrame] = []
        self.__combined_df: pd.DataFrame = None

    def run(self) -> None:
        try:
            self.__select_files()
        except Exception as e:
            print(f"Erro ao selecionar arquivos: {e}")

        ## Modos de mesclagem:
        mode = ""
        n = 0
        while mode not in ["1", "2"]:
            self.__clear()
            if n == 0:
                mode = input(
                    "Selecione o modo de mesclagem:"
                    "\n1. Mesclar primeira aba de cada planilha."
                    "\n2. Mesclar todas as abas de uma planilha.\n"
                )
                n = 1
            else:
                mode = input(
                    "Opção inválida. Por favor, selecione novamente:"
                    "\n1. Mesclar primeira aba de cada planilha."
                    "\n2. Mesclar todas as abas de uma planilha.\n"
                )

        ## Considerando vários arquivos:
        try:
            if mode == "1":
                self.__extract_dataframes()
            ## Considerando várias abas de uma planilha:
            elif mode == "2":
                self.__extract_dataframes_one_sheet()
        except Exception as e:
            print(f"Erro ao ler planilhas: {e}")

        try:
            self.__treat_dataframes()
        except Exception as e:
            print(f"Erro ao tratar dataframes extraídos: {e}")

        try:
            self.__merge_dataframes()
        except Exception as e:
            print(f"Erro ao mesclar planilhas: {e}")

        try:
            self.__save()
        except Exception as e:
            print(f"Erro ao salvar planilha: {e}")

    def __select_files(self) -> None:
        for path in pick_files_blocking():
            self.__file_paths.append(Path(path).absolute())

        filen_n = len(self.__file_paths)
        if filen_n == 1:
            print("1 arquivo selecionado.")
        else:
            print(f"{filen_n} arquivos selecionados.")

    def __extract_dataframes(self) -> None:
        for file in self.__file_paths:
            df = pd.read_excel(file)
            self.__dataframes.append(df)

    def __extract_dataframes_one_sheet(self) -> None:
        sheets_dict = pd.read_excel(self.__file_paths[0], sheet_name=None)
        for df in sheets_dict.values():
            self.__dataframes.append(df)

    def __treat_dataframes(self) -> None:
        self.__dataframes = [
            df for df in self.__dataframes if not df.empty and not df.isna().all().all()
        ]

    def __merge_dataframes(self) -> None:
        self.__combined_df = pd.concat(self.__dataframes, ignore_index=True, sort=False)

    def __save(self) -> None:
        save_path = self.__file_paths[0].parent.joinpath("Merge.xlsx")
        self.__combined_df.to_excel(save_path, index=False)
        print(f"Planilhas unificadas e salvas em: {save_path}")

    def __clear(self) -> None:  # Limpa o terminal
        # Para Windows
        if os.name == "nt":
            os.system("cls")
        # Para Mac e Linux
        else:
            os.system("clear")


if __name__ == "__main__":
    merger = Merger()
    merger.run()
