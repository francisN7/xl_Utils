"""Registry of the tool pages shown in the navigation rail."""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from xl_utils.ui.components.tool_layout import (
    OptionsFactory,
    RunHandler,
    ToolLayout,
)
from xl_utils.ui.pages.all_str import run as run_all_str
from xl_utils.ui.pages.cnj import run as run_cnj
from xl_utils.ui.pages.cut import options as cut_options
from xl_utils.ui.pages.cut import run as run_cut
from xl_utils.ui.pages.merge import options as merge_options
from xl_utils.ui.pages.merge import run as run_merge


@dataclass(frozen=True, slots=True)
class ToolPage:
    """Metadata and factory for one tool page."""

    id: str
    label: str
    icon: ft.IconData
    description: str
    build: Callable[[], ft.Control]


def _tool(
    tool_id: str,
    label: str,
    icon: ft.IconData,
    description: str,
    options: OptionsFactory | None = None,
    *,
    note: str = "",
    multiple_files: bool = False,
    default_all_sheets: bool = False,
    run_handler: RunHandler | None = None,
) -> ToolPage:
    def build() -> ft.Control:
        return ToolLayout(
            label,
            description,
            options=options,
            note=note,
            multiple_files=multiple_files,
            default_all_sheets=default_all_sheets,
            run_handler=run_handler,
        ).control

    return ToolPage(
        id=tool_id,
        label=label,
        icon=icon,
        description=description,
        build=build,
    )


TOOLS: tuple[ToolPage, ...] = (
    _tool(
        "all_str",
        "Tratamento de Texto",
        ft.Icons.TEXT_FIELDS,
        "Converte tudo para texto, remove emojis e repara metadados.",
        note="Remove emojis, preserva quebras de linha e repara metadados "
        "automaticamente.",
        multiple_files=True,
        default_all_sheets=True,
        run_handler=run_all_str,
    ),
    _tool(
        "cnj",
        "Extrair CNJs",
        ft.Icons.SEARCH,
        "Encontra e padroniza numerações CNJ em uma ou mais planilhas.",
        note="Padroniza para o formato CNJ e remove duplicados automaticamente.",
        multiple_files=True,
        default_all_sheets=True,
        run_handler=run_cnj,
    ),
    _tool(
        "cut",
        "Recortar Planilha",
        ft.Icons.CONTENT_CUT,
        "Divide planilhas em vários arquivos por quantidade de linhas.",
        cut_options,
        multiple_files=True,
        default_all_sheets=True,
        run_handler=run_cut,
    ),
    _tool(
        "merge",
        "Mesclar Planilhas",
        ft.Icons.MERGE_TYPE,
        "Concatena as abas selecionadas em uma planilha, com a origem de cada linha.",
        merge_options,
        multiple_files=True,
        run_handler=run_merge,
    ),
)
