import base64
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import WSGITimeoutError

from xl_utils.shared import drive_auth


def _client() -> drive_auth.ClientConfig:
    return drive_auth.ClientConfig(
        client_id="123.apps.googleusercontent.com",
        client_secret="segredo-de-app-desktop",
    )


def _id_token(email: str = "ana@example.com", name: str = "Ana") -> str:
    header = _encode({"alg": "RS256"})
    payload = _encode({"email": email, "name": name})
    return f"{header}.{payload}.assinatura"


def _encode(data: dict[str, str]) -> str:
    raw = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _credentials(*, refresh: str | None = "refresh-123") -> Credentials:
    credentials = Credentials(
        token="access-123",
        refresh_token=refresh,
        id_token=_id_token(),
        token_uri=drive_auth.TOKEN_URI,
        client_id="123.apps.googleusercontent.com",
        scopes=["openid", "email"],
    )
    return credentials


def test_installed_block_is_accepted(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "abc",
                    "client_secret": "xyz",
                    "token_uri": drive_auth.TOKEN_URI,
                }
            }
        ),
        encoding="utf-8",
    )

    client = drive_auth.load_client(path)

    assert client.client_id == "abc"
    assert client.client_secret == "xyz"
    assert client.token_uri == drive_auth.TOKEN_URI


def test_flat_client_is_accepted(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(json.dumps({"client_id": "abc"}), encoding="utf-8")

    assert drive_auth.load_client(path).client_id == "abc"


def test_missing_client_id_explains_how_to_fix(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(json.dumps({"installed": {"client_secret": "x"}}), encoding="utf-8")

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.load_client(path)

    assert "client_id" in str(error.value)


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(drive_auth.DriveConfigError):
        drive_auth.load_client(path)


def test_override_wins_over_the_packaged_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    override = tmp_path / "xl_utils" / "drive_client.json"
    override.parent.mkdir(parents=True)
    override.write_text(json.dumps({"client_id": "do-usuario"}), encoding="utf-8")

    assert drive_auth.load_client().client_id == "do-usuario"


def test_packaged_placeholder_asks_for_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        drive_auth,
        "client_path",
        lambda: tmp_path / "drive_client.json",
    )

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.load_client()

    assert "drive_client.json" in str(error.value)


def test_authorization_url_carries_pkce_state_and_scopes() -> None:
    url, state = drive_auth.authorization_url(_client())

    query = parse_qs(urlparse(url).query)

    assert state
    assert query["state"] == [state]
    assert query["code_challenge_method"] == ["S256"]
    assert len(query["code_challenge"][0]) >= 43
    assert query["access_type"] == ["offline"]
    assert "https://www.googleapis.com/auth/drive.file" in query["scope"][0]
    assert query["redirect_uri"] == ["http://127.0.0.1:0/"]


def test_identity_reads_email_and_name() -> None:
    assert drive_auth.identity(_id_token("zeca@example.com", "Zeca")) == (
        "zeca@example.com",
        "Zeca",
    )


def test_identity_requires_a_token() -> None:
    with pytest.raises(drive_auth.DriveAuthError):
        drive_auth.identity(None)


def test_identity_rejects_a_malformed_token() -> None:
    with pytest.raises(drive_auth.DriveAuthError):
        drive_auth.identity("sem-pontos")


class _FakeFlow:
    def __init__(self, *, credentials=None, error=None) -> None:
        self.credentials = credentials
        self.error = error
        self.kwargs: dict[str, object] = {}

    def run_local_server(self, **kwargs):
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.credentials


def test_authorize_returns_a_protected_account(monkeypatch) -> None:
    flow = _FakeFlow(credentials=_credentials())
    monkeypatch.setattr(drive_auth, "build_flow", lambda _client: flow)

    account = drive_auth.authorize(_client())

    assert account.email == "ana@example.com"
    assert account.name == "Ana"
    assert account.refresh_token == "refresh-123"
    assert account.client_id == "123.apps.googleusercontent.com"
    assert flow.kwargs["host"] == "127.0.0.1"
    assert flow.kwargs["port"] == 0
    assert flow.kwargs["timeout_seconds"] == drive_auth.LOGIN_TIMEOUT
    assert flow.kwargs["authorization_prompt_message"] is None


def test_authorize_reports_a_timeout(monkeypatch) -> None:
    flow = _FakeFlow(error=WSGITimeoutError("sem resposta"))
    monkeypatch.setattr(drive_auth, "build_flow", lambda _client: flow)

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client())

    assert "Tempo esgotado" in str(error.value)


def test_authorize_reports_a_cancelled_login(monkeypatch) -> None:
    denied = type("Denied", (Exception,), {"error": "access_denied"})("negado")
    flow = _FakeFlow(error=denied)
    monkeypatch.setattr(drive_auth, "build_flow", lambda _client: flow)

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client())

    assert "cancelada" in str(error.value)


def test_authorize_never_leaks_the_client_secret(monkeypatch) -> None:
    flow = _FakeFlow(error=RuntimeError("segredo-de-app-desktop vazou"))
    monkeypatch.setattr(drive_auth, "build_flow", lambda _client: flow)

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client())

    assert "segredo-de-app-desktop" not in str(error.value)


def test_authorize_requires_a_refresh_token(monkeypatch) -> None:
    flow = _FakeFlow(credentials=_credentials(refresh=None))
    monkeypatch.setattr(drive_auth, "build_flow", lambda _client: flow)

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client())

    assert "token de atualização" in str(error.value)


def _payload(client_id: str = "123-abc.apps.googleusercontent.com") -> dict:
    return {"installed": {"client_id": client_id, "client_secret": "xyz"}}


def test_save_client_normalizes_and_round_trips(tmp_path: Path) -> None:
    target = tmp_path / "drive_client.json"

    client = drive_auth.save_client(json.dumps(_payload()), target)

    assert drive_auth.load_client(target) == client
    saved = json.loads(target.read_text(encoding="utf-8"))
    assert saved["installed"]["redirect_uris"] == ["http://127.0.0.1"]
    assert not target.with_name("drive_client.json.tmp").exists()


def test_save_client_drops_fields_it_does_not_use(tmp_path: Path) -> None:
    target = tmp_path / "drive_client.json"
    payload = _payload()
    payload["installed"]["project_id"] = "nao-deve-ficar"

    drive_auth.save_client(json.dumps(payload), target)

    assert "nao-deve-ficar" not in target.read_text(encoding="utf-8")


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI só existe no Windows")
def test_saved_client_secret_is_encrypted_at_rest(tmp_path: Path) -> None:
    target = tmp_path / "drive_client.json"

    drive_auth.save_client(json.dumps(_payload()), target)

    raw = target.read_text(encoding="utf-8")
    saved = json.loads(raw)["installed"]
    assert "xyz" not in raw
    assert saved["client_secret"] == ""
    assert saved[drive_auth.SECRET_FIELD]
    assert drive_auth.load_client(target).client_secret == "xyz"


def test_client_config_repr_hides_the_secret() -> None:
    client = drive_auth.ClientConfig(
        client_id="abc",
        client_secret="segredo-que-nao-pode-aparecer",
    )

    assert "segredo-que-nao-pode-aparecer" not in repr(client)


def test_protected_secret_that_cannot_be_opened_is_a_config_error(
    tmp_path: Path,
) -> None:
    path = tmp_path / "drive_client.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "abc",
                    "client_secret_dpapi": "lixo",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.load_client(path)

    assert "segredo protegido" in str(error.value)


def test_import_client_keeps_the_downloaded_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        drive_auth, "client_path", lambda: tmp_path / "drive_client.json"
    )
    source = tmp_path / "client_secret_1.json"
    source.write_text(json.dumps(_payload()), encoding="utf-8")

    drive_auth.import_client(source)

    assert source.exists()
    assert drive_auth.load_client().client_id == _payload()["installed"]["client_id"]


def test_import_client_rejects_a_huge_file(tmp_path: Path) -> None:
    source = tmp_path / "client.json"
    source.write_text("x" * (drive_auth.MAX_CLIENT_BYTES + 1), encoding="utf-8")

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.import_client(source)

    assert "grande demais" in str(error.value)


def test_import_client_rejects_a_file_that_is_not_utf8(tmp_path: Path) -> None:
    source = tmp_path / "client.json"
    source.write_bytes(b"\xff\xfe{")

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.import_client(source)

    assert "UTF-8" in str(error.value)


def test_import_client_never_echoes_the_file_content(tmp_path: Path) -> None:
    source = tmp_path / "client.json"
    source.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "conteudo-sensivel",
                    "token_uri": "https://exemplo.invalido/token",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.import_client(source)

    assert "conteudo-sensivel" not in str(error.value)


def test_client_with_a_foreign_token_endpoint_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "abc",
                    "token_uri": "https://exemplo.invalido/token",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(drive_auth.DriveConfigError) as error:
        drive_auth.load_client(path)

    assert "não é do Google" in str(error.value)


def test_client_with_plain_http_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "abc",
                    "auth_uri": "http://accounts.google.com/o/oauth2/auth",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(drive_auth.DriveConfigError):
        drive_auth.load_client(path)


def test_client_id_with_spaces_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(json.dumps(_payload("id com espaco")), encoding="utf-8")

    with pytest.raises(drive_auth.DriveConfigError):
        drive_auth.load_client(path)


def test_is_configured_follows_the_local_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        drive_auth, "client_path", lambda: tmp_path / "drive_client.json"
    )

    assert drive_auth.is_configured() is False

    drive_auth.save_client(json.dumps(_payload()))

    assert drive_auth.is_configured() is True


def test_packaged_client_has_no_credentials() -> None:
    from importlib import resources

    raw = (
        resources.files("xl_utils.configs")
        .joinpath(drive_auth.CLIENT_FILE)
        .read_text(encoding="utf-8")
    )
    installed = json.loads(raw)["installed"]

    assert installed["client_id"] == ""
    assert installed["client_secret"] == ""
