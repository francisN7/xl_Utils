from file_picker_py import pick_file_blocking
from pathlib import Path
import pandas as pd
import json


class JsonConverter:
    def __init__(self):
        self.json: Path = Path(pick_file_blocking()).absolute()
        self.data: dict = None
        self.df: pd.DataFrame = None

    def run(self, mode: str):
        self.__load_data()
        self.__load_df()
        if mode == "copy":
            self.__copy_df()
        elif mode == "save":
            self.__save_df()
        else:
            raise ValueError(f"{mode} não é uma opção válida!")

    def __load_data(self):
        with open(self.json, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.data = self.data["resultado"]

    def __load_df(self):
        self.df = pd.DataFrame(self.data)

    def __copy_df(self):
        self.df.to_clipboard(index=False, excel=True)
        print("Arquivos disponíveis na área de transferêcia.\nCtrl + V")

    def __save_df(self):
        new_path = Path(f"{self.json.parent}").joinpath("process.xlsx")
        self.df.to_excel(new_path, index=False)
        print(f"Planilha salva em {new_path}")


if __name__ == "__main__":
    json_converter = JsonConverter()
    json_converter.run("copy")
