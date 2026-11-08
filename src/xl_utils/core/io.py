"""Leitura e escrita de planilhas como objetos pandas simples.

O nome do arquivo nunca decide o formato: ``resolve_suffix`` olha o conteúdo e
devolve o sufixo efetivo. Cada formato tem um leitor próprio e todos preservam
texto, zeros à esquerda e células vazias.

Entrada: caminho de um arquivo suportado.
Saída: ``{nome_da_aba: DataFrame}`` ou o ``Path`` do arquivo gravado.
Erros: ``ValueError`` com o nome do arquivo quando a leitura falha.
"""

import csv
import io
from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import unique_path

_INVALID_SHEET_CHARS = frozenset("[]:*?/\\")
_MAX_SHEET_NAME = 31

# O Excel em pt-BR exporta CSV com ``;``. Ler com a vírgula padrão não levanta
# erro: transforma a linha inteira em uma coluna e quebra os decimais. Por isso
# o separador e o encoding são detectados antes da leitura principal.
_CSV_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
_CSV_DELIMITERS = ",;\t|"
_CSV_SAMPLE_BYTES = 65_536
_CSV_HEADER_ROWS = 50


def read_workbook(
    path: Path,
    *,
    dtype: str | None = str,
) -> dict[str, pd.DataFrame]:
    """Lê todas as abas de um arquivo suportado.

    O padrão é texto: isso preserva zeros à esquerda, códigos CNJ/CPF e valores
    que o Excel transformaria em notação científica. ``keep_default_na=False``
    mantém ``NA``, ``N/A`` e ``NULL`` como texto; célula vazia vira string vazia.
    """
    suffix = resolve_suffix(path)

    match suffix:
        case ".xlsx" | ".xlsm":
            return _read_excel(path, dtype=dtype, engine="openpyxl")
        case ".xls":
            return _read_excel(path, dtype=dtype, engine="calamine")
        case ".csv":
            return {"Planilha1": _read_csv(path, dtype=dtype)}
        case ".html" | ".htm":
            return read_html_tables(path, dtype=dtype)

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def read_html_tables(
    path: Path,
    *,
    dtype: str | None,
    flavor: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Lê cada tabela HTML como uma aba ``PáginaN``.

    ``read_html`` não aceita ``dtype``; a segunda passada usa converters para
    não perder zeros à esquerda. As chaves dos converters precisam ser os
    rótulos reais (tuplas quando há cabeçalho de dois níveis), não a versão em
    texto. Depois o cabeçalho é achatado para um nome único por coluna.
    """
    frames = pd.read_html(path, flavor=flavor, keep_default_na=False)
    if dtype is str:
        columns = {column for frame in frames for column in frame.columns}
        frames = pd.read_html(
            path,
            flavor=flavor,
            converters=dict.fromkeys(columns, str),
            keep_default_na=False,
        )

    return {
        f"Página{index}": _flatten_columns(frame)
        for index, frame in enumerate(frames, start=1)
    }


def list_sheets(path: Path) -> list[str]:
    """Devolve os nomes das abas de um arquivo suportado, na ordem original.

    Excel lê apenas os metadados do livro. CSV tem uma aba sintética e HTML
    precisa ser analisado, porque cada tabela vira uma aba.
    """
    suffix = resolve_suffix(path)

    if suffix == ".csv":
        return ["Planilha1"]
    if suffix in {".html", ".htm"}:
        return _list_html_sheets(path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        engine = "calamine" if suffix == ".xls" else "openpyxl"
        return _excel_sheet_names(path, engine=engine)

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def read_headers(path: Path) -> dict[str, list[str]]:
    """Devolve os rótulos de coluna de cada aba sem carregar os dados.

    Excel lê só o cabeçalho; CSV lê uma amostra curta, suficiente para detectar
    separador e encoding; HTML é lido por inteiro, porque cada tabela vira uma
    aba. Os rótulos saem sempre como texto, no mesmo formato usado na UI.
    """
    suffix = resolve_suffix(path)

    try:
        match suffix:
            case ".xlsx" | ".xlsm" | ".xls":
                engine = "calamine" if suffix == ".xls" else "openpyxl"
                frames = pd.read_excel(
                    path,
                    sheet_name=None,
                    nrows=0,
                    engine=engine,
                    keep_default_na=False,
                )
                return {
                    str(name): [str(column) for column in frame.columns]
                    for name, frame in frames.items()
                }
            case ".csv":
                frame = _read_csv(path, dtype=str, nrows=_CSV_HEADER_ROWS)
                return {"Planilha1": [str(column) for column in frame.columns]}
            case ".html" | ".htm":
                return {
                    name: [str(column) for column in frame.columns]
                    for name, frame in read_workbook(path, dtype=str).items()
                }
    except Exception as error:  # noqa: BLE001 - devolve uma falha única e clara
        raise ValueError(
            f"Não foi possível ler as colunas de {path.name}: {error}"
        ) from error

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def dump_workbook(sheets: Mapping[str, pd.DataFrame]) -> bytes:
    """Gera o ``.xlsx`` em memória, sem gravar em disco.

    É o mesmo conteúdo de :func:`save_workbook`, usado quando o destino é o
    Google Drive: o resultado vai direto para o upload, sem passar por
    ``output/`` nem por um arquivo temporário.
    """
    buffer = io.BytesIO()
    _write_workbook(sheets, buffer)
    return buffer.getvalue()


def save_workbook(sheets: Mapping[str, pd.DataFrame], destination: Path) -> Path:
    """Grava o mapa de DataFrames em um único ``.xlsx`` e devolve o caminho real.

    O sufixo do destino é sempre normalizado para ``.xlsx``. Nomes de aba
    inválidos são saneados e nomes repetidos ganham sufixo. O arquivo nunca é
    sobrescrito: ``unique_path`` escolhe um nome livre.
    """
    destination = unique_path(destination.parent, destination.stem, ".xlsx")
    _write_workbook(sheets, destination)
    return destination


def _write_workbook(
    sheets: Mapping[str, pd.DataFrame],
    target: Path | io.BytesIO,
) -> None:
    """Escreve o livro no caminho ou no buffer informado."""
    used_names: set[str] = set()

    with pd.ExcelWriter(target, engine="xlsxwriter") as writer:
        for name, frame in sheets.items():
            frame.to_excel(
                writer,
                sheet_name=_safe_sheet_name(name, used_names),
                index=False,
            )


def _read_csv(
    path: Path,
    *,
    dtype: str | None,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Lê CSV detectando encoding e separador antes de confiar no padrão.

    A amostra evita o falso sucesso da vírgula em arquivo separado por ``;``.
    Se a leitura rápida ainda falhar, o motor Python tenta inferir o separador
    linha a linha e cada encoding alternativo é testado.
    """
    encoding, delimiter = _sniff_csv(path)
    try:
        return pd.read_csv(
            path,
            dtype=dtype,
            encoding=encoding,
            sep=delimiter,
            keep_default_na=False,
            nrows=nrows,
        )
    except UnicodeDecodeError, pd.errors.ParserError:
        return _read_csv_loose(path, dtype=dtype, nrows=nrows)


def _sniff_csv(path: Path) -> tuple[str, str]:
    """Devolve o encoding e o separador mais prováveis da primeira amostra."""
    with path.open("rb") as handle:
        raw = handle.read(_CSV_SAMPLE_BYTES)

    for encoding in _CSV_ENCODINGS:
        try:
            sample = raw.decode(encoding)
        except UnicodeDecodeError:
            continue

        try:
            delimiter = (
                csv.Sniffer()
                .sniff(
                    sample,
                    delimiters=_CSV_DELIMITERS,
                )
                .delimiter
            )
        except csv.Error:
            delimiter = _most_common_delimiter(sample)
        return encoding, delimiter

    return "latin-1", ","


def _most_common_delimiter(sample: str) -> str:
    """Fallback para uma amostra de uma linha: escolhe o separador mais comum."""
    first_line = sample.splitlines()[0] if sample else ""
    counts = {delimiter: first_line.count(delimiter) for delimiter in _CSV_DELIMITERS}
    best = max(counts, key=counts.get)
    return best if counts[best] else ","


def _read_csv_loose(
    path: Path,
    *,
    dtype: str | None,
    nrows: int | None,
) -> pd.DataFrame:
    """Tenta cada encoding deixando o pandas inferir o separador."""
    last_error: Exception | None = None
    for encoding in _CSV_ENCODINGS:
        try:
            return pd.read_csv(
                path,
                dtype=dtype,
                encoding=encoding,
                sep=None,
                engine="python",
                keep_default_na=False,
                nrows=nrows,
            )
        except Exception as error:  # noqa: BLE001 - tenta o próximo encoding
            last_error = error

    assert last_error is not None
    raise last_error


def _excel_sheet_names(path: Path, *, engine: str) -> list[str]:
    try:
        with pd.ExcelFile(path, engine=engine) as workbook:
            return [str(name) for name in workbook.sheet_names]
    except Exception as error:  # noqa: BLE001 - devolve uma falha única e clara
        raise ValueError(
            f"Não foi possível listar as abas de {path.name}: {error}"
        ) from error


def _list_html_sheets(path: Path) -> list[str]:
    try:
        return list(read_workbook(path, dtype=str))
    except Exception as error:  # noqa: BLE001 - devolve uma falha única e clara
        raise ValueError(
            f"Não foi possível listar as abas de {path.name}: {error}"
        ) from error


def _flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Troca cabeçalho de vários níveis por nomes únicos de uma linha."""
    labels = [_column_label(column) for column in frame.columns]
    frame.columns = _unique_labels(labels)
    return frame


def _column_label(column: object) -> str:
    """Converte um rótulo (simples ou tupla) em texto legível."""
    if isinstance(column, tuple):
        parts = [
            text
            for part in column
            if (text := str(part).strip()) and not text.startswith("Unnamed:")
        ]
        return " - ".join(parts) or "Coluna"
    return str(column) or "Coluna"


def _unique_labels(labels: Iterable[str]) -> list[str]:
    """Desempata rótulos repetidos com sufixo ``_2``, ``_3``..."""
    used: set[str] = set()
    result: list[str] = []
    for label in labels:
        candidate = label
        if candidate in used:
            counter = 2
            while f"{candidate}_{counter}" in used:
                counter += 1
            candidate = f"{candidate}_{counter}"
        used.add(candidate)
        result.append(candidate)
    return result


def _read_excel(
    path: Path,
    *,
    dtype: str | None,
    engine: str,
) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype=dtype,
        engine=engine,
        keep_default_na=False,
    )
    return dict(sheets)


def _safe_sheet_name(name: str, used_names: set[str]) -> str:
    """Sanea o nome da aba para os limites do Excel.

    O Excel recusa ``[]:*?/\\``, limita a 31 caracteres e compara nomes sem
    diferenciar maiúsculas; por isso o controle de repetição usa ``lower()``.
    """
    cleaned = "".join(
        "_" if char in _INVALID_SHEET_CHARS else char for char in name
    ).strip()
    cleaned = (cleaned or "Planilha")[:_MAX_SHEET_NAME]

    candidate = cleaned
    counter = 1
    while candidate.lower() in used_names:
        suffix = f"_{counter}"
        candidate = f"{cleaned[: _MAX_SHEET_NAME - len(suffix)]}{suffix}"
        counter += 1

    used_names.add(candidate.lower())
    return candidate
