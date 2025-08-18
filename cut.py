# ______Importações______:
from file_picker_py import pick_file_blocking
from math import ceil
from pathlib import Path
import pandas as pd
import os


# ______Cortador______:
class Cutter:
    def __init__(self):
        self.__file_path: Path = None  # Diretório do arquivo.
        self.__files: list[pd.DataFrame] = []  # Dataframes recortados.
        self.__df: pd.DataFrame = None  # Dataframe original.

    def cut(self) -> None:  # Faz os recortes
        self.__clear()  # Limpa o terminal
        print(":__________Recortar Planilhas__________:\n\n")
        self.__file_path = Path(
            pick_file_blocking()
        ).absolute()  # Define o diretório do arquivo
        self.__files = []  # Limpa a lista de arquivos
        print("Carregando a planilha selecionada...")
        self.__load_df()  # Carrega o dataframe original
        lines = self.__lines()  # Linhas por arquivo
        n = ceil(len(self.__df) / lines)  # Número de arquivos necessários
        print("Recortando...")
        for i in range(n):  # Para cada arquivo
            inicio = i * lines  # Linha inicial
            fim = (i + 1) * lines  # Linha final
            self.__files.append(
                self.__df.iloc[inicio:fim]
            )  # Adiciona a lista de Dataframes
        self.__save_files()

    def __load_df(self) -> None:  # Carrega o Dataframe original
        first_df = pd.read_excel(self.__file_path)
        for col in first_df.columns:
            first_df[col] = first_df[col].apply(
                lambda x: x.replace("_x000D__x000A_", "\n")
                .replace("_x000A__x000D_", "\n")
                .replace("_x000D_", "\n")
                .replace("_x000A_", "\n")
                if isinstance(x, str)
                else x
            )
        self.__df = first_df

    def __save_files(self) -> None:  # Salva os recortes
        n = 1  # Contador de arquivos
        output = Path(
            f"{self.__file_path.parent.as_posix()}/output/"
        )  # Diretório dos recortes
        if not Path.exists(output):  # Se a pasta não existir
            Path.mkdir(output)  # Cria a pasta
        for dataframe in self.__files:  # Para cada dataframe
            self.__clear()
            print(":__________Recortar Planilhas__________:\n\n")
            new_path = Path.joinpath(
                output, f"{self.__file_path.stem}_Recorte_{n}.xlsx"
            )  # Gera o nome do arquivo
            n += 1  # Aumenta o contador
            print(f"Salvando...\n{new_path}")
            dataframe.to_excel(new_path, index=False, engine="xlsxwriter")  # Salva

    def __clear(self) -> None:  # Limpa o terminal
        # Para Windows
        if os.name == "nt":
            os.system("cls")
        # Para Mac e Linux
        else:
            os.system("clear")

    def __lines(self) -> int:  # Retorna a quantidade de linhas
        lines = 0  # Quantidade de linhas
        while lines <= 0:  # Enquanto for menor ou igual a zero
            self.__clear()  # Limpa o terminal
            print(":__________Recortar Planilhas__________:\n\n")
            try:  # Tenta receber um inteiro
                question = "Quantas linhas por arquivo?"
                lines = int(
                    input(f"{'=' * len(question)}\n{question}\n{'=' * len(question)}\n")
                )
            except Exception as e:  # Se a entrada for errada!  # noqa: F841
                input(
                    "Por favor, informe um número válido!! \
                    \nPressione Enter para continuar..."
                )
        self.__clear()  # Limpa o terminal
        print(":__________Recortar Planilhas__________:\n\n")
        return lines  # Retorna a quantidade de linhas


if __name__ == "__main__":
    cutter = Cutter()
    cutter.cut()
