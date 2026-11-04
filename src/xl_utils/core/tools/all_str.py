"""Pipeline compartilhado: ler tudo como texto e remover emojis.

Entrada: caminho de uma planilha.
Saída: ``{nome_da_aba: DataFrame}`` já limpo.
Erros: ``WorkbookReadError`` quando a leitura normal e o reparo falham.
"""

from pathlib import Path

import pandas as pd

from xl_utils.core.io import read_html_tables, read_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.text import remove_emojis


class WorkbookReadError(Exception):
    """Indica que o livro não pôde ser lido nem após a tentativa de reparo."""


def prepare_workbook(path: Path) -> dict[str, pd.DataFrame]:
    """Lê todas as abas como texto e remove emojis, mantendo quebras de linha.

    O arquivo original nunca é modificado. Quando a leitura normal falha, um
    leitor mais tolerante é tentado uma vez; se também falhar,
    ``WorkbookReadError`` é levantado com a causa original.
    """
    try:
        sheets = read_workbook(path, dtype=str)
    except Exception as error:  # noqa: BLE001 - qualquer falha ganha um retry
        sheets = _read_with_repair(path, error)

    return {name: frame.map(remove_emojis) for name, frame in sheets.items()}


def _read_with_repair(
    path: Path,
    original: Exception,
) -> dict[str, pd.DataFrame]:
    """Tenta o leitor alternativo ou falha com uma mensagem tipada."""
    if resolve_suffix(path) == ".xls":
        # O calamine é o único leitor de .xls do projeto; repetir a mesma
        # chamada só esconderia a causa original.
        raise WorkbookReadError(
            f"Não foi possível ler {path.name}: {original} "
            "(o formato .xls não tem leitor alternativo)."
        ) from original

    try:
        return _repair_read(path)
    except Exception as error:  # noqa: BLE001 - devolve uma falha única e clara
        raise WorkbookReadError(
            f"Não foi possível ler {path.name}: {original}"
        ) from error


def _repair_read(path: Path) -> dict[str, pd.DataFrame]:
    """Tenta um leitor mais tolerante para o formato real, sem shell."""
    suffix = resolve_suffix(path)

    match suffix:
        case ".xlsx" | ".xlsm":
            return _read_excel_openpyxl(path)
        case ".csv":
            return _read_csv_encodings(path)
        case ".html" | ".htm":
            return _read_html_flavors(path)

    raise ValueError(f"Sem leitor alternativo para {suffix or path.name!r}")


def _read_excel_openpyxl(path: Path) -> dict[str, pd.DataFrame]:
    """Lê Excel em modo somente leitura e com valores calculados."""
    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype=str,
        engine="openpyxl",
        engine_kwargs={"read_only": True, "data_only": True},
        keep_default_na=False,
    )
    return dict(sheets)


def _read_csv_encodings(path: Path) -> dict[str, pd.DataFrame]:
    """Percorre encodings e deixa o pandas inferir o separador."""
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            frame = pd.read_csv(
                path,
                dtype=str,
                encoding=encoding,
                sep=None,
                engine="python",
                keep_default_na=False,
            )
        except Exception as error:  # noqa: BLE001 - tenta o próximo encoding
            last_error = error
            continue
        return {"Planilha1": frame}

    assert last_error is not None
    raise last_error


def _read_html_flavors(path: Path) -> dict[str, pd.DataFrame]:
    """Tenta os parsers de HTML disponíveis e mantém índices de página."""
    last_error: Exception | None = None
    for flavor in ("lxml", None):
        try:
            frames = read_html_tables(path, dtype=str, flavor=flavor)
        except Exception as error:  # noqa: BLE001 - tenta o próximo parser
            last_error = error
            continue
        if frames:
            return frames

    if last_error is not None:
        raise last_error
    raise ValueError(f"Nenhuma tabela encontrada em {path.name}")
