"""Entrada no Google Drive pelo navegador (OAuth de app instalado).

O fluxo usa PKCE e ``state`` automáticos da ``google-auth-oauthlib``, escuta
``127.0.0.1`` numa porta efêmera e devolve uma :class:`Account` já pronta para
o store. Nenhuma mensagem de erro carrega token ou segredo.
"""

from __future__ import annotations

import base64
import json
import os
import webbrowser
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, WSGITimeoutError
from requests import RequestException

from xl_utils.shared.accounts import Account
from xl_utils.shared.settings import APP_DIR

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = (
    "openid",
    "email",
    "https://www.googleapis.com/auth/drive.file",
)
CLIENT_FILE = "drive_client.json"
LOGIN_TIMEOUT = 180
SUCCESS_MESSAGE = "Autorização concluída. Volte ao xl_Utils e feche esta aba."


class DriveError(Exception):
    """Falha de configuração ou de autorização do Drive."""


class DriveConfigError(DriveError):
    """Falta o cliente OAuth ou ele está incompleto."""


class DriveAuthError(DriveError):
    """O Google não concluiu a autorização."""


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Cliente OAuth do tipo “App para computador”."""

    client_id: str
    client_secret: str = ""
    auth_uri: str = AUTH_URI
    token_uri: str = TOKEN_URI

    def as_installed(self) -> dict[str, Any]:
        """Devolve o dicionário no formato que a biblioteca espera."""
        return {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": self.auth_uri,
                "token_uri": self.token_uri,
                "redirect_uris": ["http://127.0.0.1"],
            }
        }


def client_path() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/drive_client.json`` ou o equivalente."""
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) / APP_DIR if local else Path.home() / f".{APP_DIR}"
    return base / CLIENT_FILE


def load_client(path: Path | None = None) -> ClientConfig:
    """Carrega o cliente explícito, o override local ou o JSON empacotado."""
    if path is not None:
        return _parse(_read(path), path.name)
    override = client_path()
    if override.exists():
        return _parse(_read(override), override.name)
    resource = resources.files("xl_utils.configs").joinpath(CLIENT_FILE)
    try:
        raw = resource.read_text(encoding="utf-8")
    except OSError as error:
        raise DriveConfigError(
            f"Não foi possível ler {CLIENT_FILE} empacotado: {error}"
        ) from error
    return _parse(raw, CLIENT_FILE)


def build_flow(client: ClientConfig) -> InstalledAppFlow:
    """Monta o fluxo de app instalado com PKCE ligado explicitamente."""
    return InstalledAppFlow.from_client_config(
        client.as_installed(),
        list(SCOPES),
        autogenerate_code_verifier=True,
    )


def authorization_url(
    client: ClientConfig,
    redirect_uri: str = "http://127.0.0.1:0/",
    *,
    state: str | None = None,
) -> tuple[str, str]:
    """Monta a URL de consentimento sem abrir navegador nem tocar na rede."""
    flow = build_flow(client)
    flow.redirect_uri = redirect_uri
    return flow.authorization_url(state=state)


def authorize(
    client: ClientConfig | None = None,
    *,
    timeout: int = LOGIN_TIMEOUT,
    open_browser: bool = True,
) -> Account:
    """Abre o navegador, espera o retorno e devolve a conta autorizada."""
    client = client or load_client()
    flow = build_flow(client)
    try:
        credentials = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=open_browser,
            timeout_seconds=timeout,
            authorization_prompt_message=None,
            success_message=SUCCESS_MESSAGE,
        )
    except WSGITimeoutError as error:
        raise DriveAuthError(
            "Tempo esgotado esperando o navegador. Tente entrar de novo."
        ) from error
    except Exception as error:  # noqa: BLE001 - toda falha vira mensagem segura
        raise DriveAuthError(_friendly(error)) from error

    if not credentials.refresh_token:
        raise DriveAuthError(
            "O Google não devolveu um token de atualização. Remova o acesso do "
            "app na conta Google e tente de novo."
        )
    email, name = identity(credentials.id_token)
    return account_from(credentials, client, email=email, name=name)


def identity(id_token: str | None) -> tuple[str, str]:
    """Lê e-mail e nome do ``id_token`` recebido por TLS do próprio Google."""
    if not id_token:
        raise DriveAuthError("O Google não devolveu a identidade da conta.")
    try:
        payload = id_token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    except (IndexError, TypeError, ValueError) as error:
        raise DriveAuthError(
            "A identidade devolvida pelo Google não pôde ser lida."
        ) from error
    email = data.get("email") if isinstance(data, dict) else None
    if not isinstance(email, str) or "@" not in email:
        raise DriveAuthError("O Google não devolveu um e-mail para a conta.")
    name = data.get("name")
    return email, name if isinstance(name, str) else ""


def account_from(
    credentials: Credentials,
    client: ClientConfig,
    *,
    email: str,
    name: str = "",
) -> Account:
    """Converte as credenciais do fluxo no registro que vai para o disco."""
    scopes = tuple(credentials.scopes or SCOPES)
    return Account(
        email=email,
        name=name,
        refresh_token=credentials.refresh_token or "",
        scopes=scopes,
        token_uri=credentials.token_uri or client.token_uri,
        client_id=client.client_id,
    )


def _friendly(error: BaseException) -> str:
    if getattr(error, "error", None) == "access_denied":
        return "A autorização foi cancelada no navegador."
    if isinstance(error, webbrowser.Error):
        return "Não foi possível abrir o navegador padrão."
    if isinstance(error, RequestException):
        return "Não foi possível falar com o Google. Verifique a conexão."
    if isinstance(error, GoogleAuthError):
        return "O Google recusou a autorização. Tente de novo."
    return "Não foi possível concluir a entrada no Google."


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise DriveConfigError(f"Não foi possível ler {path}: {error}") from error


def _parse(raw: str, source: str) -> ClientConfig:
    try:
        data = json.loads(raw)
    except ValueError as error:
        raise DriveConfigError(f"{source}: JSON inválido: {error}") from error
    if not isinstance(data, dict):
        raise DriveConfigError(f"{source}: esperado um objeto JSON.")
    entry = data.get("installed", data)
    if not isinstance(entry, dict):
        raise DriveConfigError(f"{source}: bloco 'installed' inválido.")
    client_id = entry.get("client_id")
    if not isinstance(client_id, str) or not client_id.strip():
        raise DriveConfigError(
            f"{source}: falta o client_id. Crie um cliente OAuth do tipo "
            "“App para computador” no Google Cloud Console e salve o JSON em "
            f"{client_path()}."
        )
    secret = entry.get("client_secret")
    auth_uri = entry.get("auth_uri")
    token_uri = entry.get("token_uri")
    return ClientConfig(
        client_id=client_id.strip(),
        client_secret=secret if isinstance(secret, str) else "",
        auth_uri=auth_uri if isinstance(auth_uri, str) else AUTH_URI,
        token_uri=token_uri if isinstance(token_uri, str) else TOKEN_URI,
    )
