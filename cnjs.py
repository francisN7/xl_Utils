from pathlib import Path
from file_picker_py import pick_file_blocking
import pandas as pd
import re
import os
from time import sleep


class CnjProcessor:
    def __init__(self):
        # Caminho do arquivo Excel:
        self.caminho: Path = None
        # Planilhas do arquivo Excel:
        self.planilhas: dict = None
        # CNJs extraídos e padronizados:
        self.cnjs_extraidos: list = []
        self.cnjs_padronizados: set = set()

    # Execução principal:
    def extract_cnjs(self) -> None:
        # Título
        title = ":__________Extrair CNJs de Planilhas__________:\n\n"
        self.__clear()
        # Instrução inicial:
        print(f"{title}Selecione a planilha para extrair os CNJs:")
        sleep(2)
        self.__clear()
        self.__ler_arquivo()
        # Iterar sobre as planilhas e extrair os CNJs:
        for name, df in self.planilhas.items():
            # Quantidade de CNJs antes da extração:
            x = len(self.cnjs_extraidos)
            self.__extrair_cnjs(self.__read_colums(df))
            # Exibindo a quantidade de CNJs extraídos:
            print(f'{len(self.cnjs_extraidos) - x} CNJs extraídos da aba "{name}"')
        # Padronizando e removendo duplicados:
        for cnj in self.cnjs_extraidos:
            self.__padronizar_cnj(cnj)
        # Resultados finais:
        print("-" * 50)
        print(
            f"{len(self.cnjs_extraidos) - len(self.cnjs_padronizados)} CNJs duplicados removidos.\n\nTotal de CNJs únicos extraídos: {len(self.cnjs_padronizados)}\n"
        )
        self.save_list_cnjs()

    # Leitura do arquivo Excel:
    def __ler_arquivo(self) -> None:
        self.caminho = Path(pick_file_blocking()).absolute()
        self.planilhas = pd.read_excel(self.caminho, sheet_name=None)
        print(f'\nArquivo "{self.caminho.stem}" carregado com sucesso.\n\n')

    # Extração dos cnjs:
    def __extrair_cnjs(self, textos: list[str]) -> None:
        padrao_cnj = re.compile(
            r"\b\d{7}\-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}\b|\b\d{20}\b"
        )
        for texto in textos:
            self.cnjs_extraidos.extend(padrao_cnj.findall(texto))

    # Padronização dos cnjs extraídos:
    def __padronizar_cnj(self, cnj: str) -> None:
        if len(cnj) == 20:
            cnj = f"{cnj[:7]}-{cnj[7:9]}.{cnj[9:13]}.{cnj[13]}.{cnj[14:16]}.{cnj[16:]}"
        elif len(cnj) != 25:
            raise ValueError(
                f"Formato de CNJ inválido.\n A extração retornou um padrão com {len(cnj)} caracteres, mas o esperado é 20 ou 25."
            )
        # Adicionando a um set para evitar duplicatas:
        self.cnjs_padronizados.add(cnj)

    # Leitura do texto de todas as colunas do DataFrame:
    def __read_colums(self, df: pd.DataFrame) -> list[str]:
        textos = []
        for coluna in df.columns:
            textos.extend(df[coluna].astype(str).tolist())
        return textos

    # Salvando a lista de CNJs em um arquivo Excel:
    def save_list_cnjs(self) -> None:
        file_name = f"{self.caminho.stem.replace(' pesquisa', '')} lista cnj.xlsx"
        output = Path(f"{self.caminho.parent}")
        pd.DataFrame(list(self.cnjs_padronizados), columns=["PROCESSOS"]).to_excel(
            f"{Path.joinpath(output, file_name)}", index=False, engine="xlsxwriter"
        )
        print(f'Lista salva como "{file_name}" em "{output}".\n')

    # Limpa o terminal:
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
