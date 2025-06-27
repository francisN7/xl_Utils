import pandas as pd
from file_picker_py import pick_files_blocking
from pathlib import Path

class Merger():
    def __init__(self):
        self.__file_paths: list[Path] = []
        self.__dataframes: list[pd.DataFrame] = []
        self.__combined_df: pd.DataFrame = None

    def run(self) -> None:
        try:
            self.__select_files()
        except Exception as e:
            print(f"Erro ao selecionar arquivos: {e}")

        try:
            self.__extract_dataframes()
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

    def __treat_dataframes(self) -> None:
        self.__dataframes = [
            df for df in self.__dataframes
            if not df.empty and not df.isna().all().all()
        ]

    def __merge_dataframes(self) -> None:
        self.__combined_df = pd.concat(self.__dataframes, ignore_index=True, sort=False)

    def __save(self) -> None:
        save_path = self.__file_paths[0].parent.joinpath("Merge.xlsx")
        self.__combined_df.to_excel(save_path, index=False)
        print(f"Planilhas unificadas e salvas em: {save_path}")


if __name__ == "__main__":
    merger = Merger()
    merger.run()