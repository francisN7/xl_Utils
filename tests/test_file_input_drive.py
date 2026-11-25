"""Botão do Drive ao lado da dropzone, sem tocar na UI real."""

from __future__ import annotations

import asyncio
from pathlib import Path

import flet as ft

from xl_utils.shared.accounts import Account
from xl_utils.shared.profiles import Profile
from xl_utils.ui.components.file_input import FileInput


class _FakeSession:
    def __init__(
        self,
        accounts: list[Account],
        *,
        paths: list[Path] | None = None,
        error: str | None = None,
        active: str | None = None,
    ) -> None:
        self.accounts = accounts
        self.active = active or (accounts[0].email if accounts else None)
        self.busy = False
        self.error = error
        self.paths = paths or []
        self.calls: list[tuple[str, bool]] = []
        self.nicknames: dict[str, str] = {}
        self._listeners: list[object] = []

    @property
    def active_account(self) -> Account | None:
        return next((item for item in self.accounts if item.email == self.active), None)

    def profile_for(self, email: str) -> Profile:
        return Profile(nickname=self.nicknames.get(email, ""))

    def subscribe(self, listener: object) -> None:
        self._listeners.append(listener)

    def notify(self) -> None:
        for listener in self._listeners:
            listener()  # type: ignore[operator]

    async def open_from_drive(
        self,
        account: Account,
        *,
        multiple: bool = False,
    ) -> list[Path]:
        self.calls.append((account.email, multiple))
        return list(self.paths)


class _FakePage:
    def __init__(self) -> None:
        self.tasks: list[tuple[object, tuple[object, ...]]] = []
        self.dialog: ft.AlertDialog | None = None
        self.popped = 0
        self.services: list[object] = []

    def run_task(self, handler: object, *args: object) -> None:
        self.tasks.append((handler, args))

    def show_dialog(self, dialog: ft.AlertDialog) -> None:
        self.dialog = dialog

    def pop_dialog(self) -> None:
        self.popped += 1
        self.dialog = None


def _account(email: str, name: str = "") -> Account:
    return Account(email=email, name=name, refresh_token="token")


def _input(drive: _FakeSession) -> tuple[FileInput, _FakePage]:
    control = FileInput(lambda _files: None, drive=drive)  # type: ignore[arg-type]
    page = _FakePage()
    control._page = lambda: page  # type: ignore[method-assign]
    return control, page


def test_button_hides_without_accounts() -> None:
    control, _ = _input(_FakeSession([]))

    assert control._drive_button.visible is False


def test_button_appears_with_one_account() -> None:
    control, _ = _input(_FakeSession([_account("ana@example.com")]))

    assert control._drive_button.visible is True
    assert control._drive_button.content.icon == ft.Icons.ADD_TO_DRIVE


def test_dropzone_and_drive_button_share_the_same_row() -> None:
    control, _ = _input(_FakeSession([_account("ana@example.com")]))

    assert control._entry_row.controls == [control._dropzone, control._drive_button]
    assert control._dropzone.expand is True
    assert control._entry_row.spacing == 10
    assert control._entry_row.vertical_alignment == ft.CrossAxisAlignment.START
    assert control._drive_button.width == 44
    assert control._drive_button.height == 44


def test_dropzone_stays_visible_after_choosing_a_file(tmp_path: Path) -> None:
    source = tmp_path / "AGENDA.xlsx"
    source.write_bytes(b"x")
    control, _ = _input(_FakeSession([_account("ana@example.com")]))

    control.set_files([source])

    assert control._dropzone.visible is not False
    assert control._dropzone_text.value == "Trocar a planilha"


def test_single_account_opens_the_picker_without_asking(tmp_path: Path) -> None:
    source = tmp_path / "AGENDA.xlsx"
    source.write_bytes(b"x")
    session = _FakeSession([_account("ana@example.com")], paths=[source])
    control, page = _input(session)

    control._open_drive()

    assert page.dialog is None
    assert len(page.tasks) == 1
    handler, args = page.tasks[0]
    asyncio.run(handler(*args))  # type: ignore[operator]
    assert session.calls == [("ana@example.com", False)]
    assert control._files == [source]


def test_two_accounts_open_with_the_selected_one_without_a_dialog(
    tmp_path: Path,
) -> None:
    source = tmp_path / "AGENDA.xlsx"
    source.write_bytes(b"x")
    session = _FakeSession(
        [_account("ana@example.com", "Ana"), _account("zeca@example.com", "Zeca")],
        paths=[source],
        active="zeca@example.com",
    )
    control, page = _input(session)

    control._open_drive()

    assert page.dialog is None
    handler, args = page.tasks[0]
    asyncio.run(handler(*args))  # type: ignore[operator]
    assert session.calls == [("zeca@example.com", False)]


def test_tooltip_names_the_selected_account() -> None:
    session = _FakeSession(
        [_account("ana@example.com", "Ana"), _account("zeca@example.com", "Zeca")],
        active="ana@example.com",
    )
    control, _ = _input(session)
    assert control._drive_button.tooltip == "Abrir do Drive — Ana"

    session.active = "zeca@example.com"
    session.notify()

    assert control._drive_button.tooltip == "Abrir do Drive — Zeca"


def test_tooltip_uses_the_nickname_when_there_is_one() -> None:
    session = _FakeSession([_account("ana@example.com", "Ana Souza")])
    session.nicknames["ana@example.com"] = "Trabalho"
    control, _ = _input(session)

    assert control._drive_button.tooltip == "Abrir do Drive — Trabalho"


def test_drive_error_lands_in_the_hint() -> None:
    session = _FakeSession([_account("ana@example.com")], error="falha fictícia")
    control, page = _input(session)

    control._open_drive()
    handler, args = page.tasks[0]
    asyncio.run(handler(*args))  # type: ignore[operator]

    assert control._hint.value == "falha fictícia"


def test_button_disappears_after_the_last_logout() -> None:
    session = _FakeSession([_account("ana@example.com")])
    control, _ = _input(session)

    session.accounts = []
    session.notify()

    assert control._drive_button.visible is False


def test_busy_run_disables_the_drive_button() -> None:
    control, _ = _input(_FakeSession([_account("ana@example.com")]))

    control.set_busy(True)

    assert control._drive_button.disabled is True


def test_tool_layout_hands_the_session_to_the_single_input() -> None:
    from xl_utils.ui.components.tool_layout import ToolLayout

    drive = _FakeSession([_account("ana@example.com")])

    layout = ToolLayout("Teste", "Teste", drive=drive)  # type: ignore[arg-type]

    assert layout.file_input._drive is drive


def test_tool_layout_hands_the_session_to_every_labeled_input() -> None:
    from xl_utils.ui.components.tool_layout import ToolLayout

    drive = _FakeSession([_account("ana@example.com")])

    layout = ToolLayout(
        "Teste",
        "Teste",
        inputs=("AGENDA", "PROCESSOS"),
        drive=drive,  # type: ignore[arg-type]
    )

    assert all(input_._drive is drive for input_ in layout._file_inputs.values())
