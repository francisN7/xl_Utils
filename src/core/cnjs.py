import re
from pathlib import Path

import pandas as pd


class CnjProcessor:
    def __init__(self, dfs: dict[Path, dict[str, pd.DataFrame]]):
        self.dfs = dfs
        self.path: Path = None
        self.cnjs_extraidos: list[str] = []
        self.cnjs_padronizados: set[str] = set()

    # Execução principal:
    def run(self) -> dict[Path, dict[str, pd.DataFrame]]:
        self.path = list(self.dfs.keys())[0]
        for file in self.dfs.values():
            for sheet_name, df in file.items():
                n_cnjs = len(self.cnjs_extraidos)
                self.__extrair_cnjs(self.__read_colums(df))
                n_cnjs_new = len(self.cnjs_extraidos)
                print(f"{(n_cnjs_new - n_cnjs):03} CNJs extraídos de {sheet_name}.")
        for cnj in self.cnjs_extraidos:
            self.__padronizar_cnj(cnj)
        new_file = f"{self.path.stem.replace('pesquisa', '')}lista cnjs.xlsx"
        print(
            f"{len(self.cnjs_padronizados):03} CNJs únicos encontrados. {len(self.cnjs_extraidos) - len(self.cnjs_padronizados)} duplicidades removidas."
        )
        return {self.path.parent.joinpath(new_file): {"Lista CNJs": self.__create_df()}}

    # Leitura do texto de todas as colunas do DataFrame:
    def __read_colums(self, df: pd.DataFrame) -> list[str]:
        textos = []
        for coluna in df.columns:
            textos.extend(df[coluna].astype(str).tolist())
        return textos

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

    def __create_df(self) -> pd.DataFrame:
        df = pd.DataFrame({"PROCESSOS": list(self.cnjs_padronizados)})
        return df
