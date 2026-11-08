"""Fluxo de navegador testado de ponta a ponta, sem tocar na internet.

Um servidor falso em ``127.0.0.1`` faz o papel do Google: recebe a URL de
consentimento, devolve o redirecionamento com ``code``, confere PKCE e
``state`` e responde ao pedido de token. O navegador é substituído por uma
função que busca a URL. Nenhum pacote sai da máquina e nenhuma credencial real
é usada.
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

from xl_utils.shared import drive_auth


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _id_token(email: str = "ana@example.com", name: str = "Ana") -> str:
    header = _b64(json.dumps({"alg": "RS256"}).encode("utf-8"))
    payload = _b64(json.dumps({"email": email, "name": name}).encode("utf-8"))
    return f"{header}.{payload}.assinatura"


class _FakeGoogle:
    """Estado compartilhado entre o teste e o servidor falso."""

    def __init__(self) -> None:
        self.state: str | None = None
        self.redirect_uri: str | None = None
        self.challenge: str | None = None
        self.challenge_method: str | None = None
        self.verifier_ok = False
        self.deny = False
        self.wrong_state = False
        self.code = "codigo-ficticio"
        self.refresh_token = "atualizacao-ficticia"
        self.port = 0

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
                query = parse_qs(parsed.query)
                fake.state = query.get("state", [None])[0]
                fake.redirect_uri = query.get("redirect_uri", [None])[0]
                fake.challenge = query.get("code_challenge", [None])[0]
                fake.challenge_method = query.get("code_challenge_method", [None])[0]
                if fake.deny:
                    location = _redirect(
                        fake.redirect_uri,
                        {"error": "access_denied", "state": fake.state},
                    )
                else:
                    state = "estado-de-outro-app" if fake.wrong_state else fake.state
                    location = _redirect(
                        fake.redirect_uri,
                        {"code": fake.code, "state": state},
                    )
                self.send_response(302)
                self.send_header("Location", location)
                self.end_headers()

            def do_POST(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path != "/token":
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", 0))
                body = parse_qs(self.rfile.read(length).decode("utf-8"))
                verifier = body.get("code_verifier", [""])[0]
                digest = hashlib.sha256(verifier.encode("utf-8")).digest()
                fake.verifier_ok = _b64(digest) == fake.challenge
                if body.get("code", [""])[0] != fake.code or not fake.verifier_ok:
                    self._json(400, {"error": "invalid_grant"})
                    return
                self._json(
                    200,
                    {
                        "access_token": "acesso-ficticio",
                        "refresh_token": fake.refresh_token,
                        "expires_in": 3600,
                        "token_type": "Bearer",
                        "scope": " ".join(drive_auth.SCOPES),
                        "id_token": _id_token(),
                    },
                )

            def _json(self, status: int, payload: dict[str, object]) -> None:
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        return Handler


def _redirect(target: str | None, params: dict[str, object]) -> str:
    base = target or "http://127.0.0.1:1/"
    return f"{base}?{urlencode(params)}"


@pytest.fixture(autouse=True)
def _local_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """Libera HTTP só dentro do teste e impede que um proxy intercepte."""
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
    """Navegador falso: registra a URL e, se pedido, busca sozinho."""

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


def _client(fake: _FakeGoogle) -> drive_auth.ClientConfig:
    return drive_auth.ClientConfig(
        client_id="ficticio.apps.googleusercontent.com",
        client_secret="segredo-ficticio",
        auth_uri=f"http://127.0.0.1:{fake.port}/auth",
        token_uri=f"http://127.0.0.1:{fake.port}/token",
    )


def test_login_completes_with_pkce_state_and_ephemeral_port(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    account = drive_auth.authorize(_client(google), timeout=10)

    assert account.email == "ana@example.com"
    assert account.name == "Ana"
    assert account.refresh_token == "atualizacao-ficticia"
    assert account.client_id == "ficticio.apps.googleusercontent.com"
    assert google.verifier_ok is True
    assert google.challenge_method == "S256"
    assert google.redirect_uri is not None
    redirect = urlparse(google.redirect_uri)
    assert redirect.hostname == "127.0.0.1"
    assert redirect.port is not None and redirect.port > 0
    assert browser.urls and "code_challenge=" in browser.urls[0]
    assert "state=" in browser.urls[0]
    assert "access_type=offline" in browser.urls[0]


def test_login_denied_is_reported_without_hanging(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.deny = True

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client(google), timeout=10)

    assert "cancelada" in str(error.value)


def test_login_rejects_a_state_from_another_request(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.wrong_state = True

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client(google), timeout=10)

    assert "Não foi possível concluir" in str(error.value)
    assert google.verifier_ok is False


def test_login_times_out_when_the_browser_never_returns(
    google: _FakeGoogle,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = _Browser(follow=False)
    monkeypatch.setattr(webbrowser, "get", lambda name=None: controller)

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client(google), timeout=1)

    assert "Tempo esgotado" in str(error.value)


def test_login_never_leaks_the_token_in_the_error(
    google: _FakeGoogle,
    browser: _Browser,
) -> None:
    google.deny = True

    with pytest.raises(drive_auth.DriveAuthError) as error:
        drive_auth.authorize(_client(google), timeout=10)

    message = str(error.value)
    assert "atualizacao-ficticia" not in message
    assert "segredo-ficticio" not in message
