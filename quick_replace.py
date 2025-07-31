import pandas as pd
from file_picker_py import pick_file_blocking
from pathlib import Path


class QuickReplace:
    def __init__(self):
        self.replacements: dict = None
        self.df_path: Path = None
        self.dataframe: pd.DataFrame = None

    def get_replacements(self) -> None:
        replacement_path = Path(pick_file_blocking()).absolute()
        df = pd.read_excel(replacement_path, dtype=str)
        original_name = df.iloc[:, 0].to_list()
        new_name = df.iloc[:, 1].to_list()
        self.replacements = dict(zip(original_name, new_name))

    def get_dataframe(self) -> None:
        self.df_path = Path(pick_file_blocking()).absolute()
        self.dataframe = pd.read_excel(self.df_path, dtype=str)

    def run_replace(self) -> None:
        columns = ["NOME DO CLIENTE", "PARTE CONTRÁRIA"]
        self.dataframe[columns] = self.dataframe[columns].replace(
            self.replacements, regex=True
        )

    def save_dataframe(self) -> None:
        new_path = self.df_path.parent.joinpath("new.xlsx")
        self.dataframe.to_excel(new_path, index=False, engine="xlsxwriter")


if __name__ == "__main__":
    quick_replace = QuickReplace()
    quick_replace.get_replacements()
    quick_replace.get_dataframe()
    quick_replace.run_replace()
    print("Substituições realizadas com sucesso!")
    quick_replace.save_dataframe()
    print(f"Arquivo salvo em: {quick_replace.df_path.parent.joinpath('new.xlsx')}")
