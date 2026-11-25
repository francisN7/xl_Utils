"""Cartões do Início e o rótulo curto de e-mail."""

import flet as ft

from xl_utils.ui.components.account_label import (
    EMAIL_LIMIT,
    email_text,
    short_email,
)
from xl_utils.ui.pages.home import build_home
from xl_utils.ui.pages.registry import FOOTER_PAGES, TOOLS

LONG_EMAIL = "francisco.almeida@escritorio-advocacia.com.br"


def _cards(control: ft.Control) -> list[ft.Container]:
    """Acha os cartões clicáveis do hub, sem depender da ordem externa."""
    found: list[ft.Container] = []
    for child in getattr(control, "controls", None) or []:
        if isinstance(child, ft.Container) and child.on_click is not None:
            found.append(child)
        found.extend(_cards(child))
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_cards(content))
    return found


def test_home_has_four_native_tools_and_plugins_only_in_footer() -> None:
    assert [tool.id for tool in TOOLS] == ["all_str", "cnj", "cut", "merge"]
    assert [page.id for page in FOOTER_PAGES] == ["plugins"]
    assert len(_cards(build_home(lambda _tool_id: None))) == 4


def test_home_cards_keep_title_description_and_shortcut_inside_narrow_width() -> None:
    home = build_home(lambda _tool_id: None)
    cards = _cards(home)

    assert len(cards) == len(TOOLS)
    assert "plugins" not in {tool.id for tool in TOOLS}
    for card in cards:
        assert card.height == 200
        assert card.clip_behavior == ft.ClipBehavior.HARD_EDGE
        assert card.width is None  # a largura vem do ResponsiveRow

        column = card.content
        assert isinstance(column, ft.Column)
        title = column.controls[0].controls[1]
        description = column.controls[1]
        shortcut = column.controls[3]

        assert title.max_lines == 1
        assert title.no_wrap is True
        assert title.overflow == ft.TextOverflow.ELLIPSIS
        assert description.max_lines == 2
        assert description.overflow == ft.TextOverflow.ELLIPSIS
        assert description.tooltip == description.value
        assert shortcut.value == "Abrir ferramenta →"


def test_short_email_keeps_addresses_that_fit() -> None:
    assert short_email("ana@example.com") == "ana@example.com"


def test_short_email_truncates_with_ellipsis() -> None:
    short = short_email(LONG_EMAIL)

    assert short.endswith("…")
    assert len(short) == EMAIL_LIMIT
    assert LONG_EMAIL.startswith(short[:-1])


def test_email_text_exposes_the_full_value_in_a_delayed_tooltip() -> None:
    text = email_text(LONG_EMAIL)

    assert text.value == short_email(LONG_EMAIL)
    assert text.max_lines == 1
    assert text.overflow == ft.TextOverflow.ELLIPSIS
    assert isinstance(text.tooltip, ft.Tooltip)
    assert text.tooltip.message == LONG_EMAIL
    assert text.tooltip.wait_duration.seconds >= 2
    assert text.tooltip.wait_duration.seconds <= 3


def test_email_text_without_truncation_has_no_tooltip() -> None:
    text = email_text("ana@example.com")

    assert text.value == "ana@example.com"
    assert text.tooltip is None


def test_home_has_no_plugins_card() -> None:
    opened: list[str] = []
    home = build_home(opened.append)

    for card in _cards(home):
        card.on_click(None)

    assert opened == [tool.id for tool in TOOLS]
    assert "plugins" not in opened
