"""Gravação no Drive sem rede: multipart, pasta, nomes livres e UI."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from xl_utils.core.io import dump_workbook, read_workbook
from xl_utils.core.save import SaveItem
from xl_utils.shared import accounts, drive_cache, drive_pick
from xl_utils.shared.drive import (
    FOLDER_MIME,
    XLSX_MIME,
    DriveApiError,
    DriveClient,
    DriveFile,
    FolderPermissionError,
)
from xl_utils.shared.drive_store import FolderGrant, FolderStore
from xl_utils.ui.components.result_panel import ResultPanel
from xl_utils.ui.components.tool_layout import ToolLayout
from xl_utils.ui.drive import DriveSaved, DriveSession

NOME = "saida.xlsx"


class _Response:
    def __init__(
        self,
        status: int = 200,
        payload: dict[str, Any] | None = None,
        content: bytes = b"",
    ) -> None:
        self.status_code = status
        self._payload = payload
        self.content = content

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("sem JSON")
        return self._payload


class _Transport:
    def __init__(self, *responses: _Response) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self._responses:
            raise AssertionError(f"chamada inesperada: {method} {url}")
        return self._responses.pop(0)


def _client(*responses: _Response) -> tuple[DriveClient, _Transport]:
    transport = _Transport(*responses)
    client = DriveClient(lambda force: "token-ficticio", transport=transport)
    return client, transport


def _frame() -> pd.DataFrame:
    return pd.DataFrame({"nome": ["Ana"], "codigo": ["000123"]})


def _item(name: str = NOME) -> SaveItem:
    return SaveItem(
        suggested_name=name,
        sheets={"Dados": _frame()},
        output_dir=Path("output"),
    )


def _account(email: str = "ana@example.com") -> accounts.Account:
    return accounts.Account(email=email, refresh_token="token")


def test_upload_posts_multipart_with_metadata_and_bytes() -> None:
    client, transport = _client(
        _Response(
            payload={
                "id": "novo",
                "name": NOME,
                "mimeType": XLSX_MIME,
                "parents": ["pasta"],
                "webViewLink": "https://drive.google.com/file/d/novo/view",
            }
        )
    )

    uploaded = client.upload(NOME, b"PK\x03\x04", parent="pasta")

    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/upload/drive/v3/files")
    assert call["params"]["uploadType"] == "multipart"
    assert call["headers"]["Content-Type"].startswith("multipart/related; boundary=")
    body = call["data"]
    assert f'"name": "{NOME}"'.encode() in body
    assert b'"parents": ["pasta"]' in body
    assert b"PK\x03\x04" in body
    assert uploaded.name == NOME
    assert uploaded.parents == ("pasta",)
    assert uploaded.web_view_link.endswith("/novo/view")


def test_upload_in_an_unknown_folder_is_a_folder_permission_error() -> None:
    client, _ = _client(_Response(status=404))

    with pytest.raises(FolderPermissionError, match="mesma conta"):
        client.upload(NOME, b"PK", parent="pasta")


def test_exists_queries_the_folder_and_the_root() -> None:
    client, transport = _client(
        _Response(payload={"files": []}),
        _Response(payload={"files": [{"id": "x", "name": NOME}]}),
    )

    assert client.exists("pasta", NOME) is False
    assert client.exists(None, NOME) is True

    assert "'pasta' in parents" in transport.calls[0]["params"]["q"]
    assert f"name = '{NOME}'" in transport.calls[0]["params"]["q"]
    assert "'root' in parents" in transport.calls[1]["params"]["q"]


def _save_session(tmp_path: Path, client: Any) -> DriveSession:
    store = accounts.AccountStore(
        tmp_path / "drive", protector=lambda data: data, unprotector=lambda data: data
    )
    return DriveSession(
        store=store,
        configured=True,
        client_factory=lambda account: client,
        folders=FolderStore(tmp_path / "drive"),
    )


class _SaveClient:
    def __init__(self) -> None:
        self.names: set[str] = set()
        self.created: list[tuple[str, bytes, str | None]] = []
        self.folder_error = False

    def metadata(self, folder_id: str) -> DriveFile:
        if self.folder_error:
            raise DriveApiError("Arquivo não encontrado no Drive.", status=404)
        return DriveFile(id=folder_id, name="Teste", mime_type=FOLDER_MIME)

    def exists(self, parent: str | None, name: str) -> bool:
        return name in self.names

    def upload(
        self,
        name: str,
        data: bytes,
        *,
        parent: str | None = None,
        mime_type: str = XLSX_MIME,
    ) -> DriveFile:
        self.names.add(name)
        self.created.append((name, data, parent))
        return DriveFile(
            id=f"id-{len(self.created)}",
            name=name,
            mime_type=mime_type,
            parents=(parent,) if parent else (),
            web_view_link=f"https://drive.google.com/file/d/id-{len(self.created)}/view",
        )


def test_save_to_drive_never_overwrites_and_uses_the_origin_folder(
    tmp_path: Path,
) -> None:
    client = _SaveClient()
    client.names.add(NOME)
    session = _save_session(tmp_path, client)

    saved = asyncio.run(
        session.save_to_drive(
            _account(),
            [_item(), _item()],
            FolderGrant("pasta", "Teste"),
        )
    )

    assert [item.name for item in saved] == ["saida_001.xlsx", "saida_002.xlsx"]
    assert [parent for _, _, parent in client.created] == ["pasta", "pasta"]
    assert all(data.startswith(b"PK") for _, data, _ in client.created)
    assert saved[0].folder_name == "Teste"
    assert saved[0].web_link.endswith("/id-1/view")


def test_save_to_drive_without_folder_goes_to_the_root(tmp_path: Path) -> None:
    client = _SaveClient()
    session = _save_session(tmp_path, client)

    saved = asyncio.run(session.save_to_drive(_account(), [_item()], None))

    assert saved[0].folder_name == "Meu Drive"
    assert client.created[0][2] is None


def test_folder_hidden_from_the_account_is_typed(tmp_path: Path) -> None:
    client = _SaveClient()
    client.folder_error = True
    session = _save_session(tmp_path, client)

    with pytest.raises(FolderPermissionError, match="não vê a pasta"):
        asyncio.run(
            session.save_to_drive(
                _account(),
                [_item()],
                FolderGrant("pasta", "Teste"),
            )
        )


class _PickClient:
    def __init__(self, mime: str = FOLDER_MIME) -> None:
        self.mime = mime

    def metadata(self, folder_id: str) -> DriveFile:
        return DriveFile(id=folder_id, name="Teste", mime_type=self.mime)


def _folder_session(
    tmp_path: Path,
    picked: drive_pick.PickedFiles,
) -> tuple[DriveSession, list]:
    calls: list[dict[str, object]] = []
    store = accounts.AccountStore(
        tmp_path / "drive",
        protector=lambda data: data,
        unprotector=lambda data: data,
    )

    def picker(**kwargs: object) -> drive_pick.PickedFiles:
        calls.append(kwargs)
        return picked

    session = DriveSession(
        store=store,
        configured=True,
        picker=picker,
        folders=FolderStore(tmp_path / "drive"),
    )
    return session, calls


def test_authorize_folder_stores_the_grant(tmp_path: Path) -> None:
    session, calls = _folder_session(
        tmp_path,
        drive_pick.PickedFiles(ids=("pasta",), access_token="curto"),
    )
    session._client_for_pick = lambda token: _PickClient()  # type: ignore[method-assign]

    grant = asyncio.run(session.authorize_folder(_account()))

    assert grant == FolderGrant("pasta", "Teste")
    assert session.folder_grant(_account(), "pasta") == grant
    assert calls == [{"folders": True, "login_hint": "ana@example.com"}]


def test_authorize_folder_rejects_a_file_and_cancel_returns_none(
    tmp_path: Path,
) -> None:
    session, _ = _folder_session(
        tmp_path,
        drive_pick.PickedFiles(ids=("arquivo",), access_token="curto"),
    )
    session._client_for_pick = lambda token: _PickClient(XLSX_MIME)  # type: ignore[method-assign]

    with pytest.raises(DriveApiError, match="não é uma pasta"):
        asyncio.run(session.authorize_folder(_account()))

    cancelled, _ = _folder_session(tmp_path, drive_pick.PickedFiles())
    assert asyncio.run(cancelled.authorize_folder(_account())) is None


def test_folder_store_saves_forgets_and_ignores_corruption(tmp_path: Path) -> None:
    store = FolderStore(tmp_path)

    grant = store.save("Ana@Example.com", "pasta", "Teste")

    assert grant.name == "Teste"
    assert store.get("ana@example.com", "pasta") == grant
    assert list(store.grants("ANA@example.com")) == ["pasta"]

    store.forget("ana@example.com", "pasta")
    assert store.get("ana@example.com", "pasta") is None

    store.save("ana@example.com", "outra", "Outra")
    store.clear("ana@example.com")
    assert store.grants("ana@example.com") == {}

    store.path.write_text("{quebrado", encoding="utf-8")
    assert store.grants("ana@example.com") == {}


def test_cache_manifest_records_the_origin(tmp_path: Path) -> None:
    directory = tmp_path / "sessao"
    origin = drive_cache.DriveOrigin(
        file_id="arquivo-1",
        name="AGENDA.xlsx",
        mime_type=XLSX_MIME,
        parent="pasta",
        account="ana@example.com",
    )

    path = drive_cache.store(directory, "AGENDA.xlsx", b"dados", origin=origin)

    assert drive_cache.origin(path) == origin
    assert drive_cache.parents([path]) == ("pasta",)
    assert drive_cache.origins([path, path]) == [origin]


def test_dump_workbook_round_trips_without_touching_disk(tmp_path: Path) -> None:
    data = dump_workbook({"Dados": _frame()})

    target = tmp_path / "resultado.xlsx"
    target.write_bytes(data)
    sheets = read_workbook(target, dtype=str)

    assert data.startswith(b"PK")
    assert sheets["Dados"]["codigo"].tolist() == ["000123"]


class _FakePage:
    def __init__(self) -> None:
        self.tasks: list[tuple[object, tuple[object, ...]]] = []
        self.dialog: Any = None

    def run_task(self, handler: object, *args: object) -> None:
        self.tasks.append((handler, args))

    def show_dialog(self, dialog: Any) -> None:
        self.dialog = dialog

    def pop_dialog(self) -> None:
        self.dialog = None


class _FakeDrive:
    def __init__(
        self,
        *,
        grant: FolderGrant | None = None,
        error: BaseException | None = None,
    ) -> None:
        self.accounts = [_account()]
        self.active = self.accounts[0].email
        self.busy = False
        self.error: str | None = None
        self.grant = grant
        self.saved_error = error
        self.forgotten: list[tuple[str, str]] = []
        self.authorized = 0
        self._listeners: list[object] = []

    def subscribe(self, listener: object) -> None:
        self._listeners.append(listener)

    def notify(self) -> None:
        for listener in self._listeners:
            listener()  # type: ignore[operator]

    def account_for(self, origins: object) -> accounts.Account:
        return self.accounts[0]

    def folder_grant(self, account: accounts.Account, folder_id: str):
        return self.grant

    def forget_folder(self, account: accounts.Account, folder_id: str) -> None:
        self.forgotten.append((account.email, folder_id))
        self.grant = None

    async def authorize_folder(self, account: accounts.Account):
        self.authorized += 1
        return self.grant

    async def save_to_drive(self, account, items, folder):
        if self.saved_error is not None:
            raise self.saved_error
        return [
            DriveSaved(
                name=item.suggested_name,
                web_link="https://drive.google.com/file/d/novo/view",
                folder_id=folder.folder_id if folder else "",
                folder_name=folder.name if folder else "Meu Drive",
            )
            for item in items
        ]


def _layout(tmp_path: Path, drive: _FakeDrive) -> tuple[ToolLayout, _FakePage]:
    layout = ToolLayout("Teste", "Descrição", drive=drive)  # type: ignore[arg-type]
    page = _FakePage()
    layout._page = lambda: page  # type: ignore[method-assign]
    return layout, page


def _cached_layout(
    tmp_path: Path,
    drive: _FakeDrive,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[ToolLayout, _FakePage]:
    layout, page = _layout(tmp_path, drive)
    monkeypatch.setattr(drive_cache, "is_cached", lambda path: True)
    monkeypatch.setattr(
        drive_cache,
        "origins",
        lambda paths: [
            drive_cache.DriveOrigin(
                file_id="id",
                name=NOME,
                parent="pasta",
                account="ana@example.com",
            )
        ],
    )
    monkeypatch.setattr(drive_cache, "parents", lambda paths: ("pasta",))
    layout.state.save_items = [_item()]
    return layout, page


def test_drive_mode_without_account_keeps_the_button_disabled() -> None:
    panel = ResultPanel()

    panel.set_drive_mode(True, False)

    assert panel._save_drive_button.visible is True
    assert panel._save_drive_button.disabled is True
    assert panel._save_output_button.visible is False


def test_drive_mode_shows_the_drive_button_instead_of_output(
    tmp_path: Path,
    xlsx_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout, _ = _layout(tmp_path, _FakeDrive())
    monkeypatch.setattr(drive_cache, "is_cached", lambda path: True)

    layout._files_changed([xlsx_file])

    assert layout.result._save_drive_button.visible is True
    assert layout.result._save_output_button.visible is False


def test_drive_save_shows_success_and_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    drive = _FakeDrive(grant=FolderGrant("pasta", "Teste"))
    layout, page = _cached_layout(tmp_path, drive, monkeypatch)

    layout._save_drive_clicked()
    handler, args = page.tasks[0]
    asyncio.run(handler(*args))  # type: ignore[operator]

    assert layout.result.kind == "success"
    assert layout.result.status == "Salvo no Drive"
    assert layout.result._drive_link_button.visible is True


def test_missing_grant_opens_the_folder_dialog(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    drive = _FakeDrive(grant=None)
    layout, page = _cached_layout(tmp_path, drive, monkeypatch)

    layout._save_drive_clicked()

    assert page.dialog is not None
    assert page.dialog.title.value == "Autorizar a pasta no Drive"
    assert [action.content for action in page.dialog.actions] == [
        "Salvar na raiz",
        "Autorizar pasta",
    ]


def test_expired_grant_forgets_the_folder_and_asks_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    drive = _FakeDrive(error=FolderPermissionError("perdeu a pasta"))
    layout, page = _cached_layout(tmp_path, drive, monkeypatch)
    drive.grant = FolderGrant("pasta", "Teste")

    asyncio.run(
        layout._drive_upload(
            drive.accounts[0],
            list(layout.state.save_items),
            drive.grant,
            False,
        )
    )

    assert drive.forgotten == [("ana@example.com", "pasta")]
    assert page.dialog is not None
