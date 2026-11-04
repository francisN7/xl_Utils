"""Recorte puro de planilha por quantidade fixa de linhas.

Entrada: DataFrame e o número de linhas por arquivo.
Saída: lista de blocos sequenciais, na ordem original.
Erros: ``ValueError`` quando o número de linhas não é positivo.
"""

from collections.abc import Mapping

import pandas as pd


def split_frame(frame: pd.DataFrame, rows_per_file: int) -> list[pd.DataFrame]:
    """Divide ``frame`` em blocos sequenciais de ``rows_per_file`` linhas.

    O último bloco fica com o resto. Um frame vazio ainda gera um bloco vazio,
    para o chamador ter um arquivo a salvar. As fatias compartilham memória com
    o frame original e mantêm o índice; a gravação em Excel ignora o índice.
    """
    if rows_per_file <= 0:
        raise ValueError("O número de linhas por arquivo deve ser maior que zero.")

    if len(frame) == 0:
        return [frame]

    return [
        frame.iloc[start : start + rows_per_file]
        for start in range(0, len(frame), rows_per_file)
    ]


def split_workbook(
    sheets: Mapping[str, pd.DataFrame],
    rows_per_file: int,
) -> dict[str, list[pd.DataFrame]]:
    """Divide cada aba, preservando a ordem original das abas."""
    return {name: split_frame(frame, rows_per_file) for name, frame in sheets.items()}
