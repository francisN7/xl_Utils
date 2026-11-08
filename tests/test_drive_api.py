"""Cliente da Drive API testado com transporte falso, sem rede."""

from __future__ import annotations

from typing import Any

import pytest

from xl_utils.shared.drive import (
    DriveApiError,
    DriveClient,
    DriveFile,
    static_token,
)
from xl_utils.shared.drive_auth import DriveAuthError

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SHEET = "application/vnd.google-apps.spreadsheet"
DOC = "application/vnd.google-apps.document"


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
    """Devolve respostas na ordem e guarda cada chamada."""

    def __init__(self, *responses: _Response) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self._responses:
            raise AssertionError(f"chamada inesperada: {method} {url}")
        return self._responses.pop(0)


class _Provider:
    def __init__(self, calls: list[bool]) -> None:
        self.calls = calls

    def __call__(self, force: bool) -> str:
        self.calls.append(force)
        return f"token-{len(self.calls)}"


def _client(*responses: _Response) -> tuple[DriveClient, _Transport, _Provider]:
    transport = _Transport(*responses)
    provider = _Provider([])
    return (
        DriveClient(provider, transport=transport),
        transport,
        provider,
    )


def test_metadata_reads_name_type_and_parents() -> None:
    client, transport, _ = _client(
        _Response(
            payload={
                "id": "abc",
                "name": "AGENDA",
                "mimeType": SHEET,
                "parents": ["pasta"],
            }
        )
    )

    metadata = client.metadata("abc")

    assert metadata == DriveFile(
        id="abc",
        name="AGENDA",
        mime_type=SHEET,
        size=None,
        parents=("pasta",),
    )
    assert transport.calls[0]["url"].endswith("/abc")
    assert transport.calls[0]["headers"] == {"Authorization": "Bearer token-1"}


def test_native_sheet_is_exported_as_xlsx() -> None:
    client, transport, _ = _client(
        _Response(payload={"id": "abc", "name": "Orçamento", "mimeType": SHEET}),
        _Response(content=b"xlsx-ficticio"),
    )
    metadata = client.metadata("abc")

    data, name = client.payload(metadata)

    assert data == b"xlsx-ficticio"
    assert name == "Orçamento.xlsx"
    assert transport.calls[1]["url"].endswith("/abc/export")
    assert transport.calls[1]["params"]["mimeType"] == XLSX


def test_binary_file_is_downloaded_with_its_own_name() -> None:
    client, transport, _ = _client(
        _Response(payload={"id": "abc", "name": "dados.xlsx", "mimeType": XLSX}),
        _Response(content=b"binario"),
    )
    metadata = client.metadata("abc")

    data, name = client.payload(metadata)

    assert (data, name) == (b"binario", "dados.xlsx")
    assert transport.calls[1]["params"]["alt"] == "media"


def test_native_document_is_refused_with_a_clear_message() -> None:
    client, _, _ = _client()
    metadata = DriveFile(id="doc", name="Contrato", mime_type=DOC)

    with pytest.raises(DriveApiError) as error:
        client.payload(metadata)

    assert "não é uma planilha" in str(error.value)


def test_expired_token_is_refreshed_once() -> None:
    client, _, provider = _client(
        _Response(401),
        _Response(payload={"id": "abc", "name": "AGENDA", "mimeType": SHEET}),
    )

    client.metadata("abc")

    assert provider.calls == [False, True]


def test_two_401s_become_a_login_error() -> None:
    client, _, provider = _client(_Response(401), _Response(401))

    with pytest.raises(DriveAuthError) as error:
        client.metadata("abc")

    assert "expirou" in str(error.value)
    assert provider.calls == [False, True]


def test_quota_error_speaks_about_space() -> None:
    client, _, _ = _client(
        _Response(
            403,
            payload={
                "error": {
                    "errors": [{"reason": "storageQuotaExceeded"}],
                    "message": "quota",
                }
            },
        )
    )

    with pytest.raises(DriveApiError) as error:
        client.metadata("abc")

    assert "sem espaço" in str(error.value)


def test_missing_file_is_reported_as_not_found() -> None:
    client, _, _ = _client(_Response(404, payload={"error": {"message": "x"}}))

    with pytest.raises(DriveApiError) as error:
        client.metadata("abc")

    assert "não encontrado" in str(error.value)


def test_busy_google_asks_to_try_again() -> None:
    client, _, _ = _client(_Response(503))

    with pytest.raises(DriveApiError) as error:
        client.metadata("abc")

    assert "ocupado" in str(error.value)


def test_connection_failure_never_leaks_the_token() -> None:
    from requests import ConnectionError as RequestsConnectionError

    class _Broken:
        def request(self, *_args: object, **_kwargs: object) -> _Response:
            raise RequestsConnectionError("sem rede")

    client = DriveClient(static_token("segredo-ficticio"), transport=_Broken())

    with pytest.raises(DriveApiError) as error:
        client.metadata("abc")

    assert "conexão" in str(error.value)
    assert "segredo-ficticio" not in str(error.value)


def test_static_token_refuses_to_refresh() -> None:
    with pytest.raises(DriveAuthError):
        static_token("curto")(True)


def test_file_without_suffix_borrows_the_mime_suffix() -> None:
    file = DriveFile(id="x", name="Base", mime_type=XLSX)

    assert file.suffix == ".xlsx"
    assert file.is_spreadsheet is True
    assert file.is_native is False
