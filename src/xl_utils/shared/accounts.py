"""Contas do Google Drive: identidade, token protegido e conta ativa.

O ``refresh_token`` nunca é gravado em texto: no Windows ele passa por DPAPI
(``CryptProtectData``) e o arquivo da conta só guarda o blob em base64. O
e-mail ativo fica em ``drive/active.json``; as demais contas continuam lá.
"""

from __future__ import annotations

import base64
import ctypes
import hashlib
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from xl_utils.shared.settings import APP_DIR

DRIVE_DIR = "drive"
ACCOUNTS_DIR = "accounts"
ACTIVE_FILE = "active.json"
ENTROPY = b"xl_utils/drive/v1"
_CRYPTPROTECT_UI_FORBIDDEN = 0x1

Protector = Callable[[bytes], bytes]


class AccountsError(Exception):
    """Falha ao ler, gravar ou proteger uma conta do Drive."""


@dataclass(frozen=True, slots=True)
class Account:
    """Uma conta autorizada, sem o token visível em ``repr`` ou log."""

    email: str
    name: str = ""
    refresh_token: str = field(default="", repr=False)
    scopes: tuple[str, ...] = ()
    token_uri: str = ""
    client_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.email, str) or "@" not in self.email:
            raise AccountsError("Conta sem e-mail válido.")


class _Blob(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_ulong),
        ("data", ctypes.POINTER(ctypes.c_char)),
    ]


def protect(data: bytes) -> bytes:
    """Criptografa bytes com DPAPI, atrelados ao usuário do Windows."""
    return _dpapi(data, protect=True)


def unprotect(blob: bytes) -> bytes:
    """Descriptografa bytes gravados por :func:`protect`."""
    return _dpapi(blob, protect=False)


def _dpapi(data: bytes, *, protect: bool) -> bytes:
    if sys.platform != "win32":
        raise AccountsError("A proteção de tokens do Drive só existe no Windows.")

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    source = ctypes.create_string_buffer(data, len(data))
    entropy = ctypes.create_string_buffer(ENTROPY, len(ENTROPY))
    blob_in = _Blob(len(data), ctypes.cast(source, ctypes.POINTER(ctypes.c_char)))
    blob_entropy = _Blob(
        len(ENTROPY), ctypes.cast(entropy, ctypes.POINTER(ctypes.c_char))
    )
    blob_out = _Blob()

    call = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    call.argtypes = [
        ctypes.POINTER(_Blob),
        ctypes.c_void_p,
        ctypes.POINTER(_Blob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(_Blob),
    ]
    call.restype = ctypes.c_int
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p

    ok = call(
        ctypes.byref(blob_in),
        None,
        ctypes.byref(blob_entropy),
        None,
        None,
        _CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(blob_out),
    )
    if not ok:
        raise AccountsError(
            f"O Windows recusou a proteção do token (código {ctypes.get_last_error()})."
        )
    try:
        return ctypes.string_at(blob_out.data, blob_out.size)
    finally:
        kernel32.LocalFree(ctypes.cast(blob_out.data, ctypes.c_void_p))


def default_root() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/drive`` ou o equivalente em casa."""
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) / APP_DIR if local else Path.home() / f".{APP_DIR}"
    return base / DRIVE_DIR


class AccountStore:
    """Contas em disco, uma por e-mail, com a conta ativa à parte."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        protector: Protector | None = None,
        unprotector: Protector | None = None,
    ) -> None:
        self.root = root or default_root()
        self._protector = protector or protect
        self._unprotector = unprotector or unprotect

    @property
    def accounts_dir(self) -> Path:
        """Pasta onde cada conta é gravada."""
        return self.root / ACCOUNTS_DIR

    @property
    def active_path(self) -> Path:
        """Arquivo que guarda o e-mail ativo."""
        return self.root / ACTIVE_FILE

    def path_for(self, email: str) -> Path:
        """Caminho estável da conta, sem usar o e-mail como nome de arquivo."""
        digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
        return self.accounts_dir / f"{digest[:16]}.json"

    def list(self) -> list[Account]:
        """Devolve as contas legíveis em ordem de e-mail; ignora arquivo corrompido."""
        if not self.accounts_dir.is_dir():
            return []
        accounts: list[Account] = []
        for path in sorted(self.accounts_dir.glob("*.json")):
            try:
                accounts.append(self._read(path))
            except AccountsError, OSError, ValueError:
                continue
        return sorted(accounts, key=lambda account: account.email.lower())

    def get(self, email: str) -> Account | None:
        """Devolve a conta do e-mail, se existir e puder ser lida."""
        try:
            return self._read(self.path_for(email))
        except AccountsError, OSError, ValueError:
            return None

    def save(self, account: Account) -> None:
        """Grava a conta de forma atômica, com o token protegido."""
        token = self._protector(account.refresh_token.encode("utf-8"))
        payload = {
            "email": account.email,
            "name": account.name,
            "token": base64.b64encode(token).decode("ascii"),
            "scopes": list(account.scopes),
            "token_uri": account.token_uri,
            "client_id": account.client_id,
        }
        _write_atomic(self.path_for(account.email), payload)

    def remove(self, email: str) -> None:
        """Apaga só a conta indicada."""
        self.path_for(email).unlink(missing_ok=True)

    def active(self) -> str | None:
        """Devolve o e-mail ativo, ou ``None`` se ele não existe mais."""
        try:
            data = json.loads(self.active_path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            return None
        email = data.get("email") if isinstance(data, dict) else None
        if not isinstance(email, str) or not email.strip():
            return None
        return email if self.path_for(email).exists() else None

    def set_active(self, email: str) -> None:
        """Marca a conta ativa; a conta precisa existir."""
        if not self.path_for(email).exists():
            raise AccountsError(f"Conta desconhecida: {email}")
        _write_atomic(self.active_path, {"email": email})

    def clear_active(self) -> None:
        """Remove a marca de conta ativa, preservando as contas."""
        self.active_path.unlink(missing_ok=True)

    def _read(self, path: Path) -> Account:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise AccountsError(f"{path.name}: conta inválida.")
        token = data.get("token")
        if not isinstance(token, str) or not token:
            raise AccountsError(f"{path.name}: token ausente.")
        scopes = data.get("scopes")
        return Account(
            email=data.get("email", ""),
            name=data.get("name", ""),
            refresh_token=self._unprotector(base64.b64decode(token)).decode("utf-8"),
            scopes=tuple(str(item) for item in scopes)
            if isinstance(scopes, list)
            else (),
            token_uri=_text(data.get("token_uri")),
            client_id=_text(data.get("client_id")),
        )


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, path)
