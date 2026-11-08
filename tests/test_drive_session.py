import asyncio
import json
from types import SimpleNamespace

import flet as ft
import pytest

from xl_utils.shared import accounts, drive_pick
from xl_utils.shared.drive import DriveApiError, DriveFile
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
    return DriveSession(
        store=store,
        authorize=lambda: _account(email),
        configured=True,
    )


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
        configured=True,
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
        configured=True,
    )

    asyncio.run(session.connect())

    assert session.error == "falta o client_id"


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
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=True,
    )
    menu = TopMenu(session)

    items = menu.control.items

    assert [item.content for item in items] == ["Entrar com Google"]


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


def test_app_shell_puts_the_drive_menu_at_the_top_right(
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
    body = shell.controls[1]
    menu = body.controls[1]
    home = body.controls[0]

    assert isinstance(body, ft.Stack)
    assert menu.right == 16
    assert menu.top == 18
    assert isinstance(menu.content, ft.PopupMenuButton)
    logo = sidebar.content.controls[0]
    assert not any(
        isinstance(control, ft.PopupMenuButton) for control in logo.content.controls
    )
    assert not any("Drive:" in text for text in _texts(home))


class _FakeImporter:
    def __init__(self, *, ok: bool = True) -> None:
        self.pages: list[object] = []
        self.ok = ok

    async def pick(self, page) -> bool:
        self.pages.append(page)
        return self.ok


def test_missing_configuration_blocks_login(store: accounts.AccountStore) -> None:
    calls: list[int] = []

    def authorize() -> accounts.Account:
        calls.append(1)
        return _account("ana@example.com")

    session = DriveSession(store=store, authorize=authorize, configured=False)

    asyncio.run(session.connect())

    assert session.error == "Configure o cliente OAuth do Drive antes de entrar."
    assert calls == []
    assert session.accounts == []


def test_import_client_enables_login(
    store: accounts.AccountStore,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from xl_utils.shared import drive_auth

    monkeypatch.setattr(
        drive_auth, "client_path", lambda: tmp_path / "drive_client.json"
    )
    source = tmp_path / "client_secret_1.json"
    source.write_text(
        json.dumps({"installed": {"client_id": "abc.apps.googleusercontent.com"}}),
        encoding="utf-8",
    )
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=False,
    )

    session.import_client(source)
    asyncio.run(session.connect())

    assert session.configured is True
    assert session.active == "ana@example.com"


def test_import_client_reports_a_bad_file(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    source = tmp_path / "client.json"
    source.write_text("{}", encoding="utf-8")
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=False,
    )

    session.import_client(source)

    assert session.configured is False
    assert session.error is not None
    assert "client_id" in session.error


def test_first_login_imports_the_client_then_connects(
    store: accounts.AccountStore,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from xl_utils.shared import drive_auth

    monkeypatch.setattr(
        drive_auth, "client_path", lambda: tmp_path / "drive_client.json"
    )
    source = tmp_path / "client_secret_1.json"
    source.write_text(
        json.dumps({"installed": {"client_id": "abc.apps.googleusercontent.com"}}),
        encoding="utf-8",
    )
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=False,
    )

    class _Importer:
        async def pick(self, _page) -> bool:
            session.import_client(source)
            return session.configured

    menu = TopMenu(session, importer=_Importer())
    asyncio.run(menu._login_with_client(object()))

    assert session.active == "ana@example.com"
    assert session.accounts[0].email == "ana@example.com"


def test_first_login_stops_when_the_picker_is_cancelled(
    store: accounts.AccountStore,
) -> None:
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=False,
    )
    menu = TopMenu(session, importer=_FakeImporter(ok=False))

    asyncio.run(menu._login_with_client(object()))

    assert session.active is None
    assert session.accounts == []
    assert session.error is None


def test_menu_offers_only_login_when_unconfigured(
    store: accounts.AccountStore,
) -> None:
    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=False,
    )
    menu = TopMenu(session, importer=_FakeImporter())

    assert [item.content for item in menu.control.items] == ["Entrar com Google"]


def test_menu_lists_profiles_and_actions(store: accounts.AccountStore) -> None:
    asyncio.run(_session(store, "ana@example.com").connect())
    session = _session(store, "zeca@example.com")
    asyncio.run(session.connect())
    menu = TopMenu(session, importer=_FakeImporter())

    contents = [item.content for item in menu.control.items]

    assert "ana@example.com" in contents
    assert "zeca@example.com" in contents
    assert "Adicionar conta" in contents
    assert "Sair desta conta" in contents
    assert all("Configurar" not in str(content) for content in contents)
    checked = [item.content for item in menu.control.items if item.checked]
    assert checked == ["zeca@example.com"]


class _FakeClient:
    """Cliente da Drive API com conteudo fixo, sem rede."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    def metadata(self, file_id: str) -> DriveFile:
        self.calls.append(file_id)
        return DriveFile(
            id=file_id,
            name="AGENDA.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def payload(self, file: DriveFile) -> tuple[bytes, str]:
        if self.fail:
            raise DriveApiError("falha fictícia")
        return b"conteudo", file.name


def _drive_session(
    store: accounts.AccountStore,
    cache_root,
    picked: drive_pick.PickedFiles,
    *,
    fail: bool = False,
) -> tuple[DriveSession, _FakeClient, list[dict[str, object]]]:
    calls: list[dict[str, object]] = []

    def picker(**kwargs: object) -> drive_pick.PickedFiles:
        calls.append(kwargs)
        return picked

    session = DriveSession(
        store=store,
        authorize=lambda: _account("ana@example.com"),
        configured=True,
        picker=picker,
        cache_root=cache_root,
    )
    asyncio.run(session.connect())
    client = _FakeClient(fail=fail)
    session._client_for_pick = lambda token: client
    return session, client, calls


def test_open_from_drive_leaves_a_local_copy_with_the_real_name(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    session, client, calls = _drive_session(
        store,
        tmp_path,
        drive_pick.PickedFiles(ids=("id-1",), access_token="curto"),
    )

    paths = asyncio.run(session.open_from_drive())

    assert [path.name for path in paths] == ["AGENDA.xlsx"]
    assert paths[0].read_bytes() == b"conteudo"
    assert paths[0].parent.parent == tmp_path
    assert client.calls == ["id-1"]
    assert calls == [{"multiple": False}]
    assert session.error is None


def test_open_from_drive_asks_for_multiple_when_the_tool_accepts_it(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    session, _, calls = _drive_session(
        store,
        tmp_path,
        drive_pick.PickedFiles(ids=("id-1",), access_token="curto"),
    )

    asyncio.run(session.open_from_drive(multiple=True))

    assert calls == [{"multiple": True}]


def test_cancelled_picker_is_silent(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    cache = tmp_path / "cache"
    session, _, _ = _drive_session(store, cache, drive_pick.PickedFiles())

    paths = asyncio.run(session.open_from_drive())

    assert paths == []
    assert session.error is None
    assert not cache.exists()


def test_download_failure_is_reported_and_cleans_the_cache(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    cache = tmp_path / "cache"
    session, _, _ = _drive_session(
        store,
        cache,
        drive_pick.PickedFiles(ids=("id-1",), access_token="curto"),
        fail=True,
    )

    paths = asyncio.run(session.open_from_drive())

    assert paths == []
    assert session.error == "falha fictícia"
    assert list(cache.iterdir()) == []


def test_open_from_drive_without_an_account_explains(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    calls: list[object] = []
    session = DriveSession(
        store=store,
        picker=lambda **kwargs: calls.append(kwargs),
        configured=True,
        cache_root=tmp_path,
    )

    paths = asyncio.run(session.open_from_drive())

    assert paths == []
    assert session.error == "Entre no Google Drive para abrir uma planilha de lá."
    assert calls == []


def test_open_from_drive_is_ignored_while_busy(
    store: accounts.AccountStore,
    tmp_path,
) -> None:
    session, _, calls = _drive_session(
        store,
        tmp_path,
        drive_pick.PickedFiles(ids=("id-1",), access_token="curto"),
    )
    session.busy = True

    paths = asyncio.run(session.open_from_drive())

    assert paths == []
    assert calls == []
