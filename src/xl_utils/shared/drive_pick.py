"""Escolha de planilhas no Drive pelo Picker de apps desktop.

O Picker para desktop não é o Picker JavaScript: é a mesma autorização OAuth do
login, com ``trigger_onepick=true``. O Google abre o seletor no navegador e
devolve ``picked_file_ids`` e ``code`` no redirecionamento para ``127.0.0.1``.

A autorização daqui pede **só** ``drive.file`` e **não** pede acesso offline:
cada escolha geraria um refresh token novo, e o Google invalida os mais antigos.
O token devolvido serve apenas para baixar o arquivo recém-escolhido.
"""

from __future__ import annotations

import threading
import time
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from google_auth_oauthlib.flow import InstalledAppFlow
from requests import RequestException

from xl_utils.shared.drive_auth import (
    ClientConfig,
    DriveAuthError,
    load_client,
)

PICK_SCOPE = "https://www.googleapis.com/auth/drive.file"
PICK_TIMEOUT = 180
SUCCESS_MESSAGE = "Arquivo escolhido. Volte ao xl_Utils e feche esta aba."
CANCELLED_MESSAGE = "Nenhum arquivo escolhido. Volte ao xl_Utils e feche esta aba."


@dataclass(frozen=True, slots=True)
class PickedFiles:
    """IDs escolhidos e o token curto que o próprio Picker devolveu."""

    ids: tuple[str, ...] = ()
    access_token: str = field(default="", repr=False)

    @property
    def cancelled(self) -> bool:
        """Diz se o usuário fechou o seletor sem escolher nada."""
        return not self.ids


def pick_files(
    client: ClientConfig | None = None,
    *,
    multiple: bool = False,
    timeout: int = PICK_TIMEOUT,
    open_browser: bool = True,
) -> PickedFiles:
    """Abre o seletor do Drive e devolve os arquivos escolhidos.

    A página de retorno é servida por um servidor local efêmero em
    ``127.0.0.1``; nada é gravado em disco e o código de autorização morre
    depois da troca pelo token.
    """
    client = client or load_client()
    server = _PickerServer()
    flow = InstalledAppFlow.from_client_config(
        client.as_installed(),
        [PICK_SCOPE],
        autogenerate_code_verifier=True,
    )
    flow.redirect_uri = server.redirect_uri
    extra = {
        "access_type": "online",
        "prompt": "consent",
        "trigger_onepick": "true",
    }
    if multiple:
        extra["allow_multiple"] = "true"
    url, state = flow.authorization_url(**extra)

    if open_browser:
        try:
            _open(url)
        except DriveAuthError:
            server.close()
            raise
    query = server.wait(timeout)
    if query is None:
        raise DriveAuthError(
            "Tempo esgotado esperando o seletor do Drive. Tente de novo."
        )
    if _first(query, "error"):
        if _first(query, "error") == "access_denied":
            return PickedFiles()
        raise DriveAuthError("O Google recusou a escolha do arquivo.")
    if _first(query, "state") != state:
        raise DriveAuthError(
            "O seletor do Drive devolveu uma resposta de outra sessão."
        )

    ids = tuple(item for item in _first(query, "picked_file_ids").split(",") if item)
    if not ids:
        return PickedFiles()
    code = _first(query, "code")
    if not code:
        raise DriveAuthError(
            "O Google não devolveu a autorização do seletor. Tente de novo."
        )
    token = _exchange(flow, code)
    return PickedFiles(ids=ids, access_token=token)


def _exchange(flow: InstalledAppFlow, code: str) -> str:
    try:
        payload = flow.fetch_token(code=code)
    except Exception as error:  # noqa: BLE001 - vira mensagem segura
        raise DriveAuthError(_friendly(error)) from error
    access = payload.get("access_token") if isinstance(payload, dict) else None
    return access if isinstance(access, str) else ""


def _open(url: str) -> None:
    try:
        browser = webbrowser.get()
        opened = browser.open(url, new=2)
    except webbrowser.Error as error:
        raise DriveAuthError("Não foi possível abrir o navegador padrão.") from error
    if not opened:
        raise DriveAuthError("Não foi possível abrir o navegador padrão.")


def _friendly(error: BaseException) -> str:
    if getattr(error, "error", None) == "access_denied":
        return "A escolha do arquivo foi cancelada no navegador."
    if isinstance(error, RequestException):
        return "Não foi possível falar com o Google. Verifique a conexão."
    return "O Google recusou a autorização do seletor. Tente de novo."


def _first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key)
    return values[0] if values else ""


class _PickerServer:
    """Escuta um único redirecionamento e encerra."""

    def __init__(self) -> None:
        self.query: dict[str, list[str]] | None = None
        self._done = threading.Event()
        self._server = HTTPServer(("127.0.0.1", 0), self._handler())
        self._server.timeout = 1

    @property
    def port(self) -> int:
        """Porta efêmera reservada pelo sistema."""
        return int(self._server.server_port)

    @property
    def redirect_uri(self) -> str:
        """Endereço de retorno registrado na autorização."""
        return f"http://127.0.0.1:{self.port}/"

    def close(self) -> None:
        """Fecha a porta sem esperar um redirecionamento."""
        self._server.server_close()

    def wait(self, timeout: int) -> dict[str, list[str]] | None:
        """Serve o redirecionamento até ele chegar ou o tempo acabar."""
        deadline = time.monotonic() + timeout
        try:
            while not self._done.is_set() and time.monotonic() < deadline:
                self._server.handle_request()
        finally:
            self._server.server_close()
        return self.query

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:
                return

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path not in {"", "/"}:
                    self.send_error(404)
                    return
                outer.query = parse_qs(parsed.query, keep_blank_values=True)
                message = (
                    SUCCESS_MESSAGE
                    if _first(outer.query, "picked_file_ids")
                    else CANCELLED_MESSAGE
                )
                self._page(message)
                outer._done.set()

            def _page(self, message: str) -> None:
                body = (
                    "<!doctype html><html lang='pt-BR'><head>"
                    "<meta charset='utf-8'><title>xl_Utils</title></head>"
                    "<body style='font-family:sans-serif;padding:2rem'>"
                    f"<h1>{message}</h1></body></html>"
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        return Handler


__all__ = ["PickedFiles", "pick_files"]
