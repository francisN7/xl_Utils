from file_picker_py import pick_file_blocking
from pathlib import Path
import pandas as pd
import os
import demoji


class EmojiRemover:
    def __init__(self):
        self.__file_path: Path = None
        self.__df: pd.DataFrame = None

    def run(self) -> None:
        demoji.download_codes()
        self.__load_df()
        self.__replace_df()
        self.__save_new_df()

    def __load_df(self) -> None:
        self.__clear()
        print(f"{'_' * 10}Removedor de emoji{'_' * 10}")
        print("\n\nSelecione a planilha para a remoção:")
        self.__file_path = Path(pick_file_blocking()).absolute()
        self.__clear()
        print(f"{'_' * 10}Removedor de emoji{'_' * 10}")
        print("\n\nCarregando planilha")
        self.__df = pd.read_excel(self.__file_path, dtype=str)

    def __replace_df(self) -> None:
        self.__clear()
        print(f"{'_' * 10}Removedor de emoji{'_' * 10}")
        print("\n\nRemovendo emojis")
        for col in self.__df.columns:
            self.__df[col] = self.__df[col].apply(self.__remove_emojis)

    def __remove_emojis(self, texto) -> str:
        try:
            if isinstance(texto, str):
                return demoji.replace(texto, "")
            else:
                return texto
        except Exception as e:
            print(f"Erro ao remover emojis:\n{e}")

    def __save_new_df(self) -> None:
        self.__clear()
        print(f"{'_' * 10}Removedor de emoji{'_' * 10}")
        new_file_path = self.__file_path.parent.joinpath(
            f"{self.__file_path.stem}_new.xlsx"
        )
        self.__df.to_excel(new_file_path, engine="xlsxwriter", index=False)
        print(f"\n\nNovo arquivo salvo em:\n{new_file_path}")

    def __clear(self) -> None:  # Limpa o terminal
        # Para Windows
        if os.name == "nt":
            os.system("cls")
        # Para Mac e Linux
        else:
            os.system("clear")


if __name__ == "__main__":
    remover = EmojiRemover()
    remover.run()
