"""Picker de desktop testado de ponta a ponta, sem tocar na internet.

O servidor falso faz o papel do Google: guarda a URL de consentimento e devolve
o redirecionamento com ``picked_file_ids``, ``code`` e ``state``. O navegador é
substituído por uma função que busca a URL sozinha.
"""

from __future__ import annotations

import base64
import hashlib
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

import pytest

from xl_utils.shared import drive_pick
from xl_utils.shared.drive_auth import ClientConfig, DriveAuthError
from xl_utils.shared.drive_pick import pick_files


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


class _FakeGoogle:
    def __init__(self) -> None:
        self.query: dict[str, list[str]] = {}
        self.challenge = ""
        self.verifier_ok = False
        self.redirect_uri = ""
        self.state = ""
        self.picked: str | None = "id-1,id-2"
        self.error: str | None = None
        self.wrong_state = False
        self.refuse_token = False
        self.cancelled_before_pick = False
        self.token_calls = 0

    def handler(self) -> type[BaseHTTPRequestHandler]:
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:
                return

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path != "/auth":
                    self.send_error(404)
                    return
                fake.query = parse_qs(parsed.query)
                fake.redirect_uri = fake.query.get("redirect_uri", [""])[0]
                fake.challenge = fake.query.get("code_challenge", [""])[0]
                fake.state = fake.query.get("state", [""])[0]
                if fake.error:
                    params: dict[str, object] = {
                        "error": fake.error,
                        "state": fake.state,
                    }
                else:
                    state = "estado-de-outro-app" if fake.wrong_state else fake.state
                    params = {"code": "codigo-ficticio", "state": state}
                    if fake.picked is not None:
                        params["picked_file_ids"] = fake.picked
                    if fake.cancelled_before_pick:
                        params = {"code": "codigo-ficticio", "state": state}
                self.send_response(302)
                self.send_header(
                    "Location",
                    f"{fake.redirect_uri}?{urlencode(params)}",
                )
                self.end_headers()

            def do_POST(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path != "/token":
                    self.send_error(404)
                    return
                fake.token_calls += 1
                length = int(self.headers.get("Content-Length", 0))
                body = parse_qs(self.rfile.read(length).decode("utf-8"))
                verifier = body.get("code_verifier", [""])[0]
                digest = hashlib.sha256(verifier.encode("utf-8")).digest()
                fake.verifier_ok = _b64(digest) == fake.challenge
                if fake.refuse_token or not fake.verifier_ok:
                    self._json(400, {"error": "invalid_grant"})
                    return
                self._json(
                    200,
                    {
                        "access_token": "acesso-curto",
                        "expires_in": 3600,
                        "token_type": "Bearer",
                        "scope": drive_pick.PICK_SCOPE,
                    },
                )

            def _json(self, status: int, payload: dict[str, object]) -> None:
                raw = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        return Handler


@pytest.fixture(autouse=True)
def _local_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OAUTHLIB_INSECURE_TRANSPORT", "1")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")


@pytest.fixture
def google():
    fake = _FakeGoogle()
    server = ThreadingHTTPServer(("127.0.0.1", 0), fake.handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    fake.port = server.server_port
    try:
        yield fake
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class _Browser:
    def __init__(self, *, follow: bool = True) -> None:
        self.urls: list[str] = []
        self._follow = follow

    def open(self, url: str, new: int = 0, autoraise: bool = True) -> bool:
        self.urls.append(url)
        if self._follow:
            threading.Thread(target=self._fetch, args=(url,), daemon=True).start()
        return True

    def _fetch(self, url: str) -> None:
        try:
            urlopen(url, timeout=10).read()
        except OSError:
            return


@pytest.fixture
def browser(monkeypatch: pytest.MonkeyPatch) -> _Browser:
    controller = _Browser()
    monkeypatch.setattr(webbrowser, "get", lambda name=None: controller)
    return controller


def _client(fake: _FakeGoogle) -> ClientConfig:
    return ClientConfig(
        client_id="ficticio.apps.googleusercontent.com",
        client_secret="segredo-ficticio",
        auth_uri=f"http://127.0.0.1:{fake.port}/auth",
        token_uri=f"http://127.0.0.1:{fake.port}/token",
    )


def test_picker_asks_only_for_drive_file_and_online_access(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    pick_files(_client(google), timeout=10)

    url = browser.urls[0]
    assert "trigger_onepick=true" in url
    assert "prompt=consent" in url
    assert "access_type=online" in url
    assert "access_type=offline" not in url
    assert google.query["scope"] == [drive_pick.PICK_SCOPE]
    assert "allow_multiple" not in google.query


def test_picker_returns_the_chosen_ids_and_the_short_token(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    picked = pick_files(_client(google), timeout=10)

    assert picked.ids == ("id-1", "id-2")
    assert picked.access_token == "acesso-curto"
    assert picked.cancelled is False
    assert google.verifier_ok is True
    assert google.token_calls == 1


def test_multiple_is_requested_when_the_tool_accepts_several_files(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    pick_files(_client(google), multiple=True, timeout=10)

    assert google.query["allow_multiple"] == ["true"]


def test_login_hint_preselects_the_account_chosen_in_the_app(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    pick_files(_client(google), login_hint="ana@example.com", timeout=10)

    assert google.query["login_hint"] == ["ana@example.com"]


def test_cancelled_picker_is_not_an_error(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.error = "access_denied"

    picked = pick_files(_client(google), timeout=10)

    assert picked.cancelled is True
    assert picked.access_token == ""


def test_closing_the_picker_after_consent_is_a_cancel(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.cancelled_before_pick = True

    picked = pick_files(_client(google), timeout=10)

    assert picked.cancelled is True
    assert google.token_calls == 0


def test_a_state_from_another_request_is_rejected(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.wrong_state = True

    with pytest.raises(DriveAuthError) as error:
        pick_files(_client(google), timeout=10)

    assert "outra sessão" in str(error.value)


def test_no_redirect_times_out(google: _FakeGoogle) -> None:
    with pytest.raises(DriveAuthError) as error:
        pick_files(_client(google), timeout=1, open_browser=False)

    assert "Tempo esgotado" in str(error.value)


def test_refused_token_never_leaks_the_secret(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.refuse_token = True

    with pytest.raises(DriveAuthError) as error:
        pick_files(_client(google), timeout=10)

    message = str(error.value)
    assert "segredo-ficticio" not in message
    assert "codigo-ficticio" not in message
