import sys

import pytest

from xl_utils.shared import accounts


def _protect(data: bytes) -> bytes:
    return b"fake:" + data[::-1]


def _unprotect(blob: bytes) -> bytes:
    assert blob.startswith(b"fake:")
    return blob[5:][::-1]


@pytest.fixture
def store(tmp_path) -> accounts.AccountStore:
    return accounts.AccountStore(
        tmp_path,
        protector=_protect,
        unprotector=_unprotect,
    )


def _account(
    email: str = "ana@example.com",
    *,
    name: str = "Ana",
    token: str = "refresh-123",
) -> accounts.Account:
    return accounts.Account(
        email=email,
        name=name,
        refresh_token=token,
        scopes=("openid", "email"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
    )


def test_account_survives_a_round_trip(store: accounts.AccountStore) -> None:
    store.save(_account())

    loaded = store.get("ana@example.com")

    assert loaded == _account()


def test_list_returns_accounts_sorted_by_email(store: accounts.AccountStore) -> None:
    store.save(_account("zeca@example.com"))
    store.save(_account("ana@example.com"))

    assert [account.email for account in store.list()] == [
        "ana@example.com",
        "zeca@example.com",
    ]


def test_token_is_not_stored_in_plain_text(store: accounts.AccountStore) -> None:
    store.save(_account(token="segredo-do-refresh"))

    raw = store.path_for("ana@example.com").read_text(encoding="utf-8")

    assert "segredo-do-refresh" not in raw
    assert "token" in raw


def test_save_leaves_no_temporary_file(store: accounts.AccountStore) -> None:
    store.save(_account())

    assert list(store.accounts_dir.glob("*.tmp")) == []


def test_saving_the_same_email_replaces_the_file(
    store: accounts.AccountStore,
) -> None:
    store.save(_account(name="Antigo"))
    store.save(_account(name="Novo"))

    assert len(store.list()) == 1
    loaded = store.get("ana@example.com")
    assert loaded is not None
    assert loaded.name == "Novo"


def test_path_ignores_case_and_spaces(store: accounts.AccountStore) -> None:
    store.save(_account("Ana@Example.com"))

    assert store.get("ana@example.com") is not None
    assert store.get(" ana@example.com ") is not None


def test_active_account_round_trip(store: accounts.AccountStore) -> None:
    store.save(_account())

    store.set_active("ana@example.com")

    assert store.active() == "ana@example.com"


def test_active_is_none_without_a_file(store: accounts.AccountStore) -> None:
    assert store.active() is None


def test_active_rejects_an_unknown_account(store: accounts.AccountStore) -> None:
    with pytest.raises(accounts.AccountsError):
        store.set_active("ninguem@example.com")


def test_active_is_ignored_after_the_account_is_removed(
    store: accounts.AccountStore,
) -> None:
    store.save(_account())
    store.set_active("ana@example.com")

    store.remove("ana@example.com")

    assert store.active() is None


def test_remove_deletes_only_the_target_account(
    store: accounts.AccountStore,
) -> None:
    store.save(_account("ana@example.com"))
    store.save(_account("zeca@example.com"))

    store.remove("ana@example.com")

    assert [account.email for account in store.list()] == ["zeca@example.com"]


def test_clear_active_keeps_the_accounts(store: accounts.AccountStore) -> None:
    store.save(_account())
    store.set_active("ana@example.com")

    store.clear_active()

    assert store.active() is None
    assert len(store.list()) == 1


def test_corrupted_account_is_skipped(store: accounts.AccountStore) -> None:
    store.save(_account())
    broken = store.accounts_dir / "quebrado.json"
    broken.write_text("{", encoding="utf-8")

    assert [account.email for account in store.list()] == ["ana@example.com"]


def test_account_repr_hides_the_refresh_token() -> None:
    text = repr(_account(token="nao-pode-aparecer"))

    assert "nao-pode-aparecer" not in text
    assert "ana@example.com" in text


def test_account_without_email_is_rejected() -> None:
    with pytest.raises(accounts.AccountsError):
        accounts.Account(email="sem-arroba")


def test_default_root_follows_local_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert accounts.default_root() == tmp_path / "xl_utils" / "drive"


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI é exclusivo do Windows")
def test_dpapi_round_trip() -> None:
    blob = accounts.protect(b"refresh-token")

    assert blob != b"refresh-token"
    assert accounts.unprotect(blob) == b"refresh-token"


@pytest.mark.skipif(sys.platform == "win32", reason="Windows tem DPAPI")
def test_dpapi_is_rejected_outside_windows() -> None:
    with pytest.raises(accounts.AccountsError):
        accounts.protect(b"x")
