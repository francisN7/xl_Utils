"""Leitura de planilhas para plugins, pelo mesmo pipeline das nativas.

Entrada: caminho local de planilha (do computador ou do cache do Drive).
Saída: ``{nome_da_aba: DataFrame}`` com texto, sem emojis e com quebras de
linha preservadas, igual a ``prepare_workbook``.
Erros: ``ReadError`` quando nem o reparo lê o arquivo; ``ValueError`` quando a
seleção de abas é vazia ou cita aba inexistente.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd

from xl_utils.core.tools.all_str import WorkbookReadError, prepare_workbook
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog
from xl_utils.shared.progress import NullReporter


class ReadError(WorkbookReadError):
    """O plugin pediu um arquivo que não pôde ser lido nem após o reparo."""


class WorkbookReader:
    """Lê cada livro uma vez por execução e devolve as abas pedidas.

    Não olha o cancelamento: o plugin confere ``request.cancel`` entre
    arquivos. Não é thread-safe; use de uma thread só.
    """

    def __init__(
        self,
        sheets: Mapping[Path, Sequence[str]],
        *,
        log: RunLog,
        progress: NullReporter,
    ) -> None:
        self._selection = {
            Path(path).resolve(): tuple(names) for path, names in sheets.items()
        }
        self._log = log
        self._progress = progress
        self._books: dict[Path, dict[str, pd.DataFrame]] = {}

    def read(
        self,
        path: Path,
        *,
        all_sheets: bool = False,
    ) -> dict[str, pd.DataFrame]:
        """Devolve as abas marcadas de ``path``, na ordem do livro.

        ``all_sheets=True`` devolve todas. Arquivo sem seleção na tela (por
        exemplo, uma tabela em ``data_dir``) também volta inteiro. Cada
        chamada recebe um dicionário novo; alterar os DataFrames não muda a
        próxima leitura.
        """
        key = Path(path).resolve()
        book = self._books.get(key)
        if book is None:
            book = self._load(Path(path), key)
        selected = None if all_sheets else self._selection.get(key)
        chosen = filter_sheets(book, selected)
        return {name: frame.copy(deep=False) for name, frame in chosen.items()}

    def _load(self, path: Path, key: Path) -> dict[str, pd.DataFrame]:
        self._progress.stage(f"Lendo {path.name}")
        try:
            book = prepare_workbook(path)
        except WorkbookReadError as error:
            raise ReadError(str(error)) from error
        self._books[key] = book
        self._progress.note(self._log, f"{path.name}: {len(book)} aba(s)")
        return book


__all__ = ["ReadError", "WorkbookReader"]
