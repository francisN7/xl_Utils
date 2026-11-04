"""Registry of the tool pages shown in the navigation rail."""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from xl_utils.ui.components.tool_layout import RunHandler, ToolLayout
from xl_utils.ui.pages.all_str import options as all_str_options
from xl_utils.ui.pages.all_str import run as run_all_str
from xl_utils.ui.pages.cnj import options as cnj_options
from xl_utils.ui.pages.cnj import run as run_cnj
from xl_utils.ui.pages.cut import options as cut_options
from xl_utils.ui.pages.cut import run as run_cut
from xl_utils.ui.state import ToolState


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
    options: Callable[[ToolState], ft.Control],
    *,
    multiple_files: bool = False,
    run_handler: RunHandler | None = None,
) -> ToolPage:
    def build() -> ft.Control:
        return ToolLayout(
            label,
            description,
            options=options,
            multiple_files=multiple_files,
            run_handler=run_handler,
        ).control

    return ToolPage(
        id=tool_id,
        label=label,
        icon=icon,
        description=description,
        build=build,
    )


def _merge_options(_state: ToolState) -> ft.Control:
    return ft.Column(
        controls=[
            ft.Dropdown(
                label="Modo de mesclagem",
                value="files",
                dense=True,
                disabled=True,
                options=[
                    ft.DropdownOption(
                        key="files",
                        text="Primeira aba de cada arquivo",
                    ),
                    ft.DropdownOption(
                        key="sheets",
                        text="Todas as abas de uma planilha",
                    ),
                ],
            ),
        ],
        spacing=8,
    )


TOOLS: tuple[ToolPage, ...] = (
    _tool(
        "all_str",
        "Tratamento de Texto",
        ft.Icons.TEXT_FIELDS,
        "Converte tudo para texto, remove emojis e repara metadados.",
        all_str_options,
        run_handler=run_all_str,
    ),
    _tool(
        "cnj",
        "Extrair CNJs",
        ft.Icons.SEARCH,
        "Encontra e padroniza numerações CNJ em uma planilha.",
        cnj_options,
        run_handler=run_cnj,
    ),
    _tool(
        "cut",
        "Recortar Planilha",
        ft.Icons.CONTENT_CUT,
        "Divide uma planilha em vários arquivos por quantidade de linhas.",
        cut_options,
        run_handler=run_cut,
    ),
    _tool(
        "merge",
        "Mesclar Planilhas",
        ft.Icons.MERGE_TYPE,
        "Unifica planilhas com o mesmo cabeçalho ou as abas de uma planilha.",
        _merge_options,
        multiple_files=True,
    ),
)
