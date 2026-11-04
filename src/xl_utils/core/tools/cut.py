"""Recorte puro de planilha por linhas ou por quantidade de arquivos.

Entrada: DataFrame e o número de linhas por arquivo ou de arquivos por aba.
Saída: lista de blocos sequenciais, na ordem original.
Erros: ``ValueError`` quando o número informado não é positivo.
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


def split_frame_by_parts(frame: pd.DataFrame, parts: int) -> list[pd.DataFrame]:
    """Divide ``frame`` em até ``parts`` blocos sequenciais equilibrados.

    A diferença entre os blocos é de no máximo uma linha. Quando há menos
    linhas que ``parts``, reduz a quantidade ao número de linhas para não gerar
    arquivo vazio; um frame vazio continua gerando um bloco vazio.
    """
    if parts <= 0:
        raise ValueError("A quantidade de arquivos deve ser maior que zero.")

    if len(frame) == 0:
        return [frame]

    parts = min(parts, len(frame))
    base, remainder = divmod(len(frame), parts)
    blocks: list[pd.DataFrame] = []
    start = 0
    for index in range(parts):
        size = base + (1 if index < remainder else 0)
        blocks.append(frame.iloc[start : start + size])
        start += size
    return blocks


def split_workbook(
    sheets: Mapping[str, pd.DataFrame],
    rows_per_file: int,
) -> dict[str, list[pd.DataFrame]]:
    """Divide cada aba, preservando a ordem original das abas."""
    return {name: split_frame(frame, rows_per_file) for name, frame in sheets.items()}


def split_workbook_by_parts(
    sheets: Mapping[str, pd.DataFrame],
    parts: int,
) -> dict[str, list[pd.DataFrame]]:
    """Divide cada aba em partes, aplicando a quantidade **por aba**."""
    return {name: split_frame_by_parts(frame, parts) for name, frame in sheets.items()}
