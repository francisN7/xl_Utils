"""Cliente REST mínimo da Drive API v3.

Cobre o que a S9b precisa para ler uma planilha escolhida no Picker: metadados,
download de binários e exportação de planilha nativa do Google. O transporte é
injetável para que nenhum teste toque na rede, e o token nunca entra em URL,
log ou mensagem de erro.

Entrada: um provedor de token e um arquivo do Drive.
Saída: ``DriveFile`` e os bytes prontos para o pipeline local.
Erros: ``DriveError`` em PT-BR, com a causa resumida.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote

import requests
from google.auth.exceptions import GoogleAuthError, RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from requests import RequestException, Response

from xl_utils.shared.accounts import Account
from xl_utils.shared.drive_auth import (
    ClientConfig,
    DriveAuthError,
    DriveConfigError,
    DriveError,
)

API = "https://www.googleapis.com/drive/v3/files"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"
NATIVE_PREFIX = "application/vnd.google-apps."
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
METADATA_FIELDS = "id,name,mimeType,size,parents"
REQUEST_TIMEOUT = (10, 60)
EXPORT_LIMIT = 10 * 1024 * 1024

_MIME_SUFFIXES = {
    XLSX_MIME: ".xlsx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.ms-excel.sheet.macroenabled.12": ".xlsm",
    "text/csv": ".csv",
    "text/html": ".html",
    "application/xhtml+xml": ".html",
}

#: Recebe ``force`` e devolve um token de acesso válido.
TokenProvider = Callable[[bool], str]


class Transport(Protocol):
    """O pedaço de ``requests.Session`` que o cliente usa."""

    def request(self, method: str, url: str, **kwargs: Any) -> Response: ...


class DriveApiError(DriveError):
    """O Google recusou ou não completou uma chamada da Drive API."""


@dataclass(frozen=True, slots=True)
class DriveFile:
    """Metadados do arquivo escolhido, sem nada de credencial."""

    id: str
    name: str
    mime_type: str
    size: int | None = None
    parents: tuple[str, ...] = ()

    @property
    def is_native(self) -> bool:
        """Diz se é um documento nativo do Google (não binário)."""
        return self.mime_type.startswith(NATIVE_PREFIX)

    @property
    def is_spreadsheet(self) -> bool:
        """Diz se o arquivo é uma planilha (nativa ou binária)."""
        return self.mime_type == SHEET_MIME or self.suffix in {
            ".xlsx",
            ".xlsm",
            ".xls",
            ".csv",
            ".html",
            ".htm",
        }

    @property
    def suffix(self) -> str:
        """Sufixo provável, tirado do nome e, se preciso, do MIME."""
        suffix = Path(self.name).suffix.lower()
        if suffix in _MIME_SUFFIXES.values():
            return suffix
        return _MIME_SUFFIXES.get(self.mime_type, suffix)


class DriveClient:
    """Três chamadas da Drive API, com renovação única em caso de 401."""

    def __init__(
        self,
        token: TokenProvider,
        *,
        transport: Transport | None = None,
        timeout: tuple[float, float] = REQUEST_TIMEOUT,
    ) -> None:
        self._token = token
        self._transport = transport or requests.Session()
        self._timeout = timeout

    def metadata(self, file_id: str) -> DriveFile:
        """Lê nome, tipo, tamanho e pasta do arquivo."""
        response = self._get(
            f"{API}/{_quoted(file_id)}",
            params={"fields": METADATA_FIELDS, "supportsAllDrives": "true"},
        )
        data = _json(response)
        if not isinstance(data, dict):
            raise DriveApiError("O Google devolveu metadados inesperados.")
        return _file(data)

    def payload(self, file: DriveFile) -> tuple[bytes, str]:
        """Devolve o conteúdo e o nome local do arquivo escolhido."""
        if file.mime_type == SHEET_MIME:
            return self._export(file), _export_name(file.name)
        if file.is_native:
            raise DriveApiError(
                f"“{file.name}” não é uma planilha. Escolha um arquivo "
                "do Sheets, Excel ou CSV."
            )
        response = self._get(
            f"{API}/{_quoted(file.id)}",
            params={"alt": "media", "supportsAllDrives": "true"},
        )
        return response.content, _local_name(file)

    def _export(self, file: DriveFile) -> bytes:
        response = self._get(
            f"{API}/{_quoted(file.id)}/export",
            params={"mimeType": XLSX_MIME},
        )
        return response.content

    def _get(self, url: str, *, params: dict[str, str]) -> Response:
        for attempt in range(2):
            token = self._token(attempt > 0)
            try:
                response = self._transport.request(
                    "GET",
                    url,
                    params=params,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self._timeout,
                )
            except RequestException as error:
                raise DriveApiError(
                    "Não foi possível falar com o Google. Verifique a conexão."
                ) from error
            if response.status_code == 401:
                continue
            if response.status_code >= 400:
                raise _error(response)
            return response
        raise DriveAuthError(
            "A autorização do Google Drive expirou. Saia e entre de novo."
        )


def token_provider(
    account: Account,
    client: ClientConfig,
) -> TokenProvider:
    """Monta um provedor que renova o token da conta quando preciso.

    A renovação acontece no primeiro uso e de novo, uma única vez, quando a API
    responde 401. Refresh recusado vira mensagem clara, nunca laço de login.
    """
    credentials = _credentials(account, client)
    request = Request()
    lock = threading.Lock()

    def provider(force: bool) -> str:
        with lock:
            if force or not credentials.valid:
                try:
                    credentials.refresh(request)
                except RefreshError as error:
                    raise DriveAuthError(
                        "O Google recusou a renovação desta conta. Saia e "
                        "entre de novo no Google Drive."
                    ) from error
                except (RequestException, GoogleAuthError) as error:
                    raise DriveApiError(
                        "Não foi possível renovar o acesso ao Google. "
                        "Verifique a conexão."
                    ) from error
            if not credentials.token:
                raise DriveAuthError(
                    "A conta não devolveu um token de acesso. Saia e entre "
                    "de novo no Google Drive."
                )
            return credentials.token

    return provider


def static_token(token: str) -> TokenProvider:
    """Usa o token curto devolvido pelo próprio Picker."""

    def provider(force: bool) -> str:
        if force:
            raise DriveAuthError(
                "A autorização do seletor expirou. Abra o Drive de novo."
            )
        return token

    return provider


def _credentials(account: Account, client: ClientConfig) -> Credentials:
    if not account.refresh_token:
        raise DriveAuthError(
            "A conta não tem token de atualização. Saia e entre de novo."
        )
    token_uri = account.token_uri or client.token_uri
    if not token_uri:
        raise DriveConfigError("O cliente OAuth não tem endereço de token.")
    scopes = account.scopes or ("https://www.googleapis.com/auth/drive.file",)
    return Credentials(
        token=None,
        refresh_token=account.refresh_token,
        token_uri=token_uri,
        client_id=account.client_id or client.client_id,
        client_secret=client.client_secret,
        scopes=list(scopes),
    )


def _file(data: dict[str, Any]) -> DriveFile:
    size = data.get("size")
    parents = data.get("parents")
    return DriveFile(
        id=str(data.get("id", "")),
        name=str(data.get("name", "")),
        mime_type=str(data.get("mimeType", "")),
        size=int(size) if isinstance(size, int) else _size(size),
        parents=tuple(str(item) for item in parents)
        if isinstance(parents, list)
        else (),
    )


def _size(value: Any) -> int | None:
    text = str(value) if value is not None else ""
    return int(text) if text.isdigit() else None


def _json(response: Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _error(response: Response) -> DriveError:
    reason = _reason(response)
    if response.status_code == 404:
        return DriveApiError(
            "Arquivo não encontrado no Drive. Ele pode ter sido movido ou excluído."
        )
    if response.status_code == 403 and reason == "storageQuotaExceeded":
        return DriveApiError("O Google Drive está sem espaço para gravar.")
    if response.status_code == 403 and reason == "exportSizeLimitExceeded":
        return DriveApiError(
            "A planilha é grande demais para exportar pelo Google (limite de "
            "10 MB). Baixe-a no Drive e abra pelo seletor local."
        )
    if response.status_code == 403:
        return DriveApiError(
            "O Google negou o acesso a este arquivo. Ele pode ter sido "
            "movido ou o acesso removido."
        )
    if response.status_code in {429, 500, 502, 503, 504}:
        return DriveApiError(
            "O Google está ocupado agora. Tente de novo em alguns instantes."
        )
    return DriveApiError(
        f"O Google Drive não concluiu o pedido (código {response.status_code})."
    )


def _reason(response: Response) -> str:
    data = _json(response)
    if not isinstance(data, dict):
        return ""
    error = data.get("error")
    if not isinstance(error, dict):
        return ""
    errors = error.get("errors")
    if isinstance(errors, list):
        for item in errors:
            if isinstance(item, dict) and item.get("reason"):
                return str(item["reason"])
    return str(error.get("status") or "")


def _quoted(file_id: str) -> str:
    """Escapa o ID para o caminho da URL sem montar consulta."""

    return quote(file_id, safe="")


def _export_name(name: str) -> str:
    return f"{Path(name).stem or 'Planilha'}.xlsx"


def _local_name(file: DriveFile) -> str:
    name = file.name or f"Drive-{file.id[:8]}"
    if Path(name).suffix:
        return name
    return f"{name}{file.suffix or '.xlsx'}"
