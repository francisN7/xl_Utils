"""Painel de perfis do Drive no canto superior direito (headless)."""

import asyncio

import flet as ft
import pytest

from xl_utils.shared import accounts, drive_cache
from xl_utils.ui import theme
from xl_utils.ui.components.top_menu import TopMenu
from xl_utils.ui.drive import DriveSession


def _protect(data: bytes) -> bytes:
    return b"fake:" + data[::-1]


def _unprotect(blob: bytes) -> bytes:
    return blob[5:][::-1]


@pytest.fixture
def store(tmp_path) -> accounts.AccountStore:
    return accounts.AccountStore(
        tmp_path,
        protector=_protect,
        unprotector=_unprotect,
    )


def _account(email: str, name: str | None = None) -> accounts.Account:
    return accounts.Account(
        email=email,
        name=email.split("@")[0].title() if name is None else name,
        refresh_token=f"refresh-{email}",
        scopes=("openid", "email"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
    )


def _login(
    store: accounts.AccountStore, *emails: str, name: str | None = None
) -> DriveSession:
    """Entra com cada e-mail em ordem; o último fica selecionado."""
    session = DriveSession(store=store, configured=True)
    for email in emails:
        session._authorize = lambda email=email: _account(email, name)
        asyncio.run(session.connect())
    return session


def _texts(control: object) -> list[str]:
    if isinstance(control, str):
        return [control]
    if isinstance(control, ft.Text):
        return [str(control.value)]
    found: list[str] = []
    for field in ("title", "leading", "content"):
        child = getattr(control, field, None)
        if child is not None:
            found.extend(_texts(child))
    for child in getattr(control, "controls", None) or []:
        found.extend(_texts(child))
    return found


def _action(menu: TopMenu, label: str) -> ft.MenuItemButton:
    return next(
        control
        for control in menu.panel
        if isinstance(control, ft.MenuItemButton) and _texts(control) == [label]
    )


def _others(menu: TopMenu) -> ft.ExpansionTile | None:
    return next(
        (control for control in menu.panel if isinstance(control, ft.ExpansionTile)),
        None,
    )


class _FakePage:
    def __init__(self) -> None:
        self.tasks: list[tuple[object, tuple[object, ...]]] = []

    def run_task(self, handler: object, *args: object) -> None:
        self.tasks.append((handler, args))


class _FakeImporter:
    async def pick(self, _page) -> bool:
        return True


def test_without_account_the_trigger_and_panel_offer_login(
    store: accounts.AccountStore,
) -> None:
    menu = TopMenu(DriveSession(store=store, configured=True))

    assert "Entrar com Google" in _texts(menu.trigger)
    assert [_texts(control) for control in menu.panel] == [["Entrar com Google"]]


def test_unconfigured_client_still_offers_only_login(
    store: accounts.AccountStore,
) -> None:
    session = DriveSession(store=store, configured=False)
    menu = TopMenu(session, importer=_FakeImporter())

    assert [_texts(control) for control in menu.panel] == [["Entrar com Google"]]


def test_trigger_shows_the_selected_initials_and_name(
    store: accounts.AccountStore,
) -> None:
    menu = TopMenu(_login(store, "ana@example.com", "zeca@example.com"))

    assert _texts(menu.trigger) == ["Z", "Zeca"]
    assert isinstance(menu.control, ft.MenuBar)


def test_panel_has_header_other_accounts_and_fixed_actions(
    store: accounts.AccountStore,
) -> None:
    menu = TopMenu(_login(store, "ana@example.com", "zeca@example.com"))

    header, others, divider, add, leave = menu.panel

    assert _texts(header) == ["Z", "Zeca", "zeca@example.com"]
    assert isinstance(others, ft.ExpansionTile)
    assert others.expanded is False
    assert _texts(others) == ["Outras contas", "A", "ana@example.com"]
    assert isinstance(divider, ft.Divider)
    assert _texts(add) == ["Adicionar conta"]
    assert _texts(leave) == ["Sair"]


def test_single_account_hides_other_accounts(store: accounts.AccountStore) -> None:
    menu = TopMenu(_login(store, "ana@example.com"))

    assert _others(menu) is None
    assert ["Adicionar conta"] in [_texts(control) for control in menu.panel]


def test_choosing_another_account_selects_it(store: accounts.AccountStore) -> None:
    session = _login(store, "ana@example.com", "zeca@example.com")
    menu = TopMenu(session)
    tile = _others(menu)
    assert tile is not None

    tile.controls[0].on_click(None)

    assert session.active == "ana@example.com"
    assert store.active() == "ana@example.com"
    assert _texts(menu.trigger) == ["A", "Ana"]
    assert _texts(_others(menu)) == ["Outras contas", "Z", "zeca@example.com"]


def test_leave_removes_only_the_selected_and_selects_the_next(
    store: accounts.AccountStore,
) -> None:
    session = _login(store, "bia@example.com", "ana@example.com", "zeca@example.com")
    menu = TopMenu(session)

    _action(menu, "Sair").on_click(None)

    assert [account.email for account in session.accounts] == [
        "ana@example.com",
        "bia@example.com",
    ]
    assert _texts(menu.trigger) == ["A", "Ana"]


def test_leaving_keeps_the_drive_copies_already_open(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    session = _login(store, "ana@example.com", "zeca@example.com")
    directory = drive_cache.new_session(tmp_path / "cache")
    origin = drive_cache.DriveOrigin(
        file_id="id",
        name="planilha.xlsx",
        parent="pasta",
        account="zeca@example.com",
    )
    copy = drive_cache.store(directory, "planilha.xlsx", b"planilha", origin=origin)
    menu = TopMenu(session)

    _action(menu, "Sair").on_click(None)

    assert store.get("zeca@example.com") is None
    assert store.get("ana@example.com") is not None
    assert copy.read_bytes() == b"planilha"
    assert drive_cache.origins([copy]) == [origin]
    assert session.account_for([origin]) is None


def test_add_account_opens_the_login(store: accounts.AccountStore) -> None:
    session = _login(store, "ana@example.com")
    menu = TopMenu(session)
    page = _FakePage()
    menu._page = lambda: page  # type: ignore[method-assign]

    _action(menu, "Adicionar conta").on_click(None)

    assert page.tasks == [(session.connect, ())]


def test_add_account_asks_for_the_client_when_unconfigured(
    store: accounts.AccountStore,
) -> None:
    session = DriveSession(store=store, configured=False)
    menu = TopMenu(session, importer=_FakeImporter())
    page = _FakePage()
    menu._page = lambda: page  # type: ignore[method-assign]

    _action(menu, "Entrar com Google").on_click(None)

    assert page.tasks == [(menu._login_with_client, (page,))]


def test_busy_session_shows_only_the_connecting_note(
    store: accounts.AccountStore,
) -> None:
    session = _login(store, "ana@example.com")
    menu = TopMenu(session)

    session.busy = True
    session.notify()

    assert _texts(menu.trigger) == ["Conectando ao Google…"]
    assert [_texts(control) for control in menu.panel] == [["Conectando ao Google…"]]


def test_error_appears_on_top_of_the_panel(store: accounts.AccountStore) -> None:
    session = _login(store, "ana@example.com")
    menu = TopMenu(session)

    session.error = "Acesso negado."
    session.notify()

    note = menu.panel[0]
    assert _texts(note) == ["Acesso negado."]
    assert note.content.color == theme.RED


def test_long_email_is_truncated_with_the_full_value_in_tooltip(
    store: accounts.AccountStore,
) -> None:
    long_email = "francisco.almeida@escritorio-advocacia.com.br"
    menu = TopMenu(_login(store, long_email, name=""))

    name = _texts(menu.trigger)[1]
    email = menu.panel[0].content.controls[1].controls[1]

    assert name.endswith("…")
    assert long_email.startswith(name[:-1])
    assert isinstance(email.tooltip, ft.Tooltip)
    assert email.tooltip.message == long_email


def test_refresh_follows_the_current_theme(store: accounts.AccountStore) -> None:
    menu = TopMenu(_login(store, "ana@example.com"))
    try:
        theme.apply("light")
        menu.refresh()
        assert menu.control.controls[0].menu_style.bgcolor == theme.LIGHT["SURFACE"]
    finally:
        theme.apply("dark")
        menu.refresh()
    assert menu.control.controls[0].menu_style.bgcolor == theme.DARK["SURFACE"]
