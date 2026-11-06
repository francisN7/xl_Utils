"""Estado por ferramenta mantido enquanto o usuário navega entre as páginas."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from xl_utils.core.save import SaveItem
from xl_utils.core.tools.sheets import default_selection
from xl_utils.shared.log import RunLog


@dataclass
class ToolState:
    """Estado de uma página de ferramenta.

    Selecionar um novo arquivo descarta o resultado anterior; a página, as
    opções e a ferramenta selecionada permanecem em memória durante a navegação.
    """

    files: list[Path] = field(default_factory=list)
    inputs: dict[str, Path] = field(default_factory=dict)
    result: dict[str, pd.DataFrame] | None = None
    save_items: list[SaveItem] = field(default_factory=list)
    options: dict[str, object] = field(default_factory=dict)
    sheet_names: dict[Path, list[str]] = field(default_factory=dict)
    selected_sheets: dict[Path, set[str]] = field(default_factory=dict)
    message: str = ""
    error: str | None = None
    error_detail: str | None = None
    log: RunLog | None = None
    running: bool = False

    @property
    def sheet_count(self) -> int:
        """Devolve quantas abas os arquivos atuais expõem."""
        return sum(len(names) for names in self.sheet_names.values())

    @property
    def selected_count(self) -> int:
        """Devolve quantas abas estão marcadas agora."""
        return sum(len(names) for names in self.selected_sheets.values())

    def select_files(self, files: list[Path]) -> None:
        """Substitui a seleção e descarta qualquer resultado anterior."""
        self.files = list(files)
        self.inputs = {}
        self.result = None
        self.save_items.clear()
        self.sheet_names = {}
        self.selected_sheets = {}
        self.message = ""
        self.error = None
        self.error_detail = None
        self.log = None
        self.running = False

    def diagnostic_options(self) -> dict[str, object]:
        """Devolve os valores atuais das opções como dados simples e legíveis."""
        values: dict[str, object] = {}
        for name, raw in self.options.items():
            value = getattr(raw, "value", raw)
            if value is None or value == "":
                continue
            values[name] = value
        return values

    def set_sheet_names(
        self,
        sheets: Mapping[Path, Sequence[str]],
        *,
        all_sheets: bool = False,
    ) -> None:
        """Guarda as abas dos arquivos atuais e aplica a regra padrão."""
        names = {path: list(values) for path, values in sheets.items()}
        self.sheet_names = names
        self.selected_sheets = default_selection(names, all_sheets=all_sheets)

    def reset(self) -> None:
        """Limpa tudo desta ferramenta."""
        self.files.clear()
        self.inputs.clear()
        self.result = None
        self.save_items.clear()
        self.options.clear()
        self.sheet_names.clear()
        self.selected_sheets.clear()
        self.message = ""
        self.error = None
        self.error_detail = None
        self.log = None
        self.running = False
