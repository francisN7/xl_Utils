import asyncio
from types import SimpleNamespace

import flet as ft
import pytest

from xl_utils.shared import accounts
from xl_utils.ui.components.drive_status import DriveStatus
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


def _account(email: str) -> accounts.Account:
    return accounts.Account(
        email=email,
        name=email.split("@")[0].title(),
        refresh_token=f"refresh-{email}",
        scopes=("openid", "email"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
    )


def _session(store: accounts.AccountStore, email: str) -> DriveSession:
    return DriveSession(store=store, authorize=lambda: _account(email))


def test_connect_saves_and_activates_the_account(
    store: accounts.AccountStore,
) -> None:
    session = _session(store, "ana@example.com")

    asyncio.run(session.connect())

    assert session.active == "ana@example.com"
    assert [account.email for account in session.accounts] == ["ana@example.com"]
    assert session.error is None
    assert session.busy is False


def test_second_login_keeps_both_accounts(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())

    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())

    assert [account.email for account in session.accounts] == [
        "ana@example.com",
        "zeca@example.com",
    ]
    assert session.active == "zeca@example.com"


def test_switch_changes_the_active_account(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())

    session.switch("ana@example.com")

    assert session.active == "ana@example.com"
    assert len(session.accounts) == 2


def test_logout_removes_only_the_active_account(
    store: accounts.AccountStore,
) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())

    session.logout()

    assert session.active is None
    assert [account.email for account in session.accounts] == ["ana@example.com"]


def test_next_account_cycles_between_two(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())

    assert session.next_account() == "ana@example.com"
    session.switch("ana@example.com")
    assert session.next_account() == "zeca@example.com"


def test_next_account_is_none_with_a_single_account(
    store: accounts.AccountStore,
) -> None:
    session = _session(store, "ana@example.com")
    asyncio.run(session.connect())

    assert session.next_account() is None


def test_failure_keeps_the_previous_accounts(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    failing = DriveSession(
        store=store,
        authorize=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    asyncio.run(failing.connect())

    assert failing.error == "Falha inesperada ao entrar no Google Drive."
    assert failing.active == "ana@example.com"
    assert failing.busy is False


def test_configuration_error_reaches_the_user(store: accounts.AccountStore) -> None:
    from xl_utils.shared.drive_auth import DriveConfigError

    session = DriveSession(
        store=store,
        authorize=lambda: (_ for _ in ()).throw(DriveConfigError("falta o client_id")),
    )

    asyncio.run(session.connect())

    assert session.error == "falta o client_id"


def test_status_describes_each_state(store: accounts.AccountStore) -> None:
    session = DriveSession(store=store, authorize=lambda: _account("ana@example.com"))
    assert session.status == "Drive: nenhuma conta conectada"

    asyncio.run(session.connect())

    assert session.status == "Drive: ana@example.com"


def test_listeners_are_notified_on_change(store: accounts.AccountStore) -> None:
    session = _session(store, "ana@example.com")
    calls: list[int] = []
    session.subscribe(lambda: calls.append(1))

    asyncio.run(session.connect())
    session.logout()

    assert len(calls) == 3


def test_menu_offers_login_when_there_is_no_account(
    store: accounts.AccountStore,
) -> None:
    session = DriveSession(store=store, authorize=lambda: _account("ana@example.com"))
    menu = TopMenu(session)

    items = menu.control.items

    assert [item.content for item in items] == ["Entrar no Google Drive"]


def test_menu_lists_accounts_and_checks_the_active_one(
    store: accounts.AccountStore,
) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())
    menu = TopMenu(session)

    checked = [item for item in menu.control.items if item.checked]

    assert [item.content for item in checked] == ["zeca@example.com"]


def test_menu_switches_the_account(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())
    menu = TopMenu(session)
    target = next(
        item for item in menu.control.items if item.content == "ana@example.com"
    )

    target.on_click(None)

    assert session.active == "ana@example.com"


def test_status_card_shows_the_active_account(
    store: accounts.AccountStore,
) -> None:
    session = _session(store, "ana@example.com")
    card = DriveStatus(session)
    assert card._title.value == "Drive: nenhuma conta conectada"

    asyncio.run(session.connect())

    assert card._title.value == "Drive: ana@example.com"
    assert card._logout.visible is True
    assert card._switch.visible is False
    assert isinstance(card.control, ft.Container)


def test_status_card_offers_the_switch_with_two_accounts(
    store: accounts.AccountStore,
) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())
    card = DriveStatus(session)

    assert card._switch.visible is True

    card._switch_clicked()

    assert session.active == "ana@example.com"


def _texts(control: object) -> list[str]:
    if isinstance(control, ft.Text):
        return [str(control.value)]
    found: list[str] = []
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_texts(content))
    for child in getattr(control, "controls", None) or []:
        found.extend(_texts(child))
    return found


class _FakeWindow(SimpleNamespace):
    width = 0
    height = 0
    min_width = 0
    min_height = 0


class _FakePage:
    def __init__(self) -> None:
        self.window = _FakeWindow()
        self.added: list[ft.Control] = []

    def add(self, *controls: ft.Control) -> None:
        self.added.extend(controls)

    def update(self, *_args: object) -> None:
        return None


def test_app_shell_carries_the_drive_menu_and_card(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from xl_utils import app
    from xl_utils.shared import settings

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(settings, "load_theme", lambda: "dark")
    monkeypatch.setattr(ft.Container, "update", lambda _self: None)

    page = _FakePage()
    app.main(page)

    shell = page.added[0]
    sidebar = shell.controls[0]
    content = shell.controls[1]
    assert any(
        isinstance(item, ft.PopupMenuButton)
        for item in sidebar.content.controls[0].content.controls
    )
    assert "Drive: nenhuma conta conectada" in _texts(content)
