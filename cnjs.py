from pathlib import Path
from file_picker_py import pick_file_blocking
import pandas as pd
import re
import os


class CnjProcessor:
    def __init__(self):
        self.caminho: Path = None
        self.planilhas: list = None
        self.cnjs_extraidos: list = []
        self.cnjs_padronizados: set = set()

    def extract_cnjs(self) -> None:
        title = ":__________Extrair CNJs de Planilhas__________:\n\n"
        self.__clear()
        print(f"{title}Selecione a planilha para extrair os CNJs:")
        self.__ler_arquivo()
        for df in self.planilhas:
            self.__extrair_cnjs(self.__read_colums(df))
        for cnj in self.cnjs_extraidos:
            self.__padronizar_cnj(cnj)
        self.save_list_cnjs()

    def __ler_arquivo(self) -> None:
        self.caminho = Path(pick_file_blocking()).absolute()
        self.planilhas = list(pd.read_excel(self.caminho, sheet_name=None).values())
        print(f"\nArquivo {self.caminho.stem} carregado com sucesso.")

    def __extrair_cnjs(self, textos: list[str]) -> None:
        padrao_cnj = re.compile(
            r"\b\d{7}\-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}\b|\b\d{20}\b"
        )
        for texto in textos:
            self.cnjs_extraidos.extend(padrao_cnj.findall(texto))

    def __padronizar_cnj(self, cnj: str) -> None:
        if len(cnj) == 20:
            cnj = f"{cnj[:7]}-{cnj[7:9]}.{cnj[9:13]}.{cnj[13]}.{cnj[14:16]}.{cnj[16:]}"
        elif len(cnj) != 25:
            raise ValueError(
                f"Formato de CNJ inválido.\n A extração retornou um padrão com {len(cnj)} caracteres, mas o esperado é 20 ou 25."
            )
        self.cnjs_padronizados.add(cnj)

    def __read_colums(self, df: pd.DataFrame) -> list[str]:
        textos = []
        for coluna in df.columns:
            textos.extend(df[coluna].astype(str).tolist())
        return textos

    def save_list_cnjs(self) -> None:
        file_name = f"{self.caminho.stem.replace('pesquisa', '')} lista cnj.xlsx"
        output = Path(f"{self.caminho.parent}")
        pd.DataFrame(list(self.cnjs_padronizados), columns=["PROCESSOS"]).to_excel(
            f"{Path.joinpath(output, file_name)}", index=False, engine="xlsxwriter"
        )

    def __clear(self) -> None:  # Limpa o terminal
        # Para Windows
        if os.name == "nt":
            os.system("cls")
        # Para Mac e Linux
        else:
            os.system("clear")


if __name__ == "__main__":
    processor = CnjProcessor()
    processor.extract_cnjs()
