"""Contas do Google Drive: identidade, token protegido e conta selecionada.

O ``refresh_token`` nunca é gravado em texto. No Windows ele passa por DPAPI
(``CryptProtectData``) e o arquivo da conta só guarda o blob em base64; nos
demais sistemas ele vai para o chaveiro do usuário (Secret Service/KWallet, via
``keyring``) e o arquivo só diz onde está. O e-mail selecionado fica em
``drive/active.json``; as demais contas continuam lá.
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
from typing import Any, Protocol

from xl_utils.shared.settings import APP_DIR

DRIVE_DIR = "drive"
ACCOUNTS_DIR = "accounts"
ACTIVE_FILE = "active.json"
ENTROPY = b"xl_utils/drive/v1"
KEYRING_SERVICE = "xl_utils/drive"
VAULT_KEYRING = "keyring"
_CRYPTPROTECT_UI_FORBIDDEN = 0x1

Protector = Callable[[bytes], bytes]


class AccountsError(Exception):
    """Falha ao ler, gravar ou proteger uma conta do Drive."""


class TokenVault(Protocol):
    """Guarda o token fora do arquivo da conta, por uma chave estável."""

    def put(self, key: str, token: str) -> None: ...

    def get(self, key: str) -> str | None: ...

    def delete(self, key: str) -> None: ...


class KeyringVault:
    """Chaveiro do usuário (Secret Service, KWallet ou macOS Keychain)."""

    def __init__(self, service: str = KEYRING_SERVICE) -> None:
        self._service = service

    def put(self, key: str, token: str) -> None:
        self._call("gravar", "set_password", key, token)

    def get(self, key: str) -> str | None:
        return self._call("ler", "get_password", key)

    def delete(self, key: str) -> None:
        import keyring.errors

        try:
            self._call("apagar", "delete_password", key)
        except AccountsError as error:
            if not isinstance(error.__cause__, keyring.errors.PasswordDeleteError):
                raise

    def _call(self, verb: str, name: str, *args: str) -> Any:
        try:
            import keyring
            import keyring.errors
        except ImportError as error:
            raise AccountsError(
                "O chaveiro do sistema não está disponível (pacote keyring)."
            ) from error
        try:
            return getattr(keyring, name)(self._service, *args)
        except keyring.errors.KeyringError as error:
            # Só o tipo do erro: a mensagem do backend pode citar o segredo.
            raise AccountsError(
                f"Não foi possível {verb} o token no chaveiro do sistema "
                f"({type(error).__name__}). Confira se o KWallet ou o "
                "GNOME Keyring está ativo e desbloqueado."
            ) from error


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


def account_key(email: str) -> str:
    """Hash curto e estável do e-mail: nomeia os arquivos da conta sem expô-lo."""
    digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
    return digest[:16]


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
        vault: TokenVault | None = None,
    ) -> None:
        self.root = root or default_root()
        self._protector = protector or protect
        self._unprotector = unprotector or unprotect
        # Sem protetor injetado e fora do Windows, o token vai para o chaveiro.
        if vault is None and protector is None and sys.platform != "win32":
            vault = KeyringVault()
        self._vault = vault

    @property
    def accounts_dir(self) -> Path:
        """Pasta onde cada conta é gravada."""
        return self.root / ACCOUNTS_DIR

    @property
    def active_path(self) -> Path:
        """Arquivo que guarda o e-mail selecionado."""
        return self.root / ACTIVE_FILE

    def path_for(self, email: str) -> Path:
        """Caminho estável da conta, sem usar o e-mail como nome de arquivo."""
        return self.accounts_dir / f"{account_key(email)}.json"

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
        payload: dict[str, Any] = {"email": account.email, "name": account.name}
        if self._vault is not None:
            self._vault.put(self._key(account.email), account.refresh_token)
            payload["vault"] = VAULT_KEYRING
        else:
            token = self._protector(account.refresh_token.encode("utf-8"))
            payload["token"] = base64.b64encode(token).decode("ascii")
        payload.update(
            {
                "scopes": list(account.scopes),
                "token_uri": account.token_uri,
                "client_id": account.client_id,
            }
        )
        _write_atomic(self.path_for(account.email), payload)

    def remove(self, email: str) -> None:
        """Apaga só a conta indicada e, depois, o token dela no chaveiro.

        O arquivo sai primeiro: se o chaveiro falhar, a conta já não aparece e
        o erro chega ao usuário para ele limpar o segredo à mão.
        """
        self.path_for(email).unlink(missing_ok=True)
        if self._vault is not None:
            self._vault.delete(self._key(email))

    def _key(self, email: str) -> str:
        """Chave do token no chaveiro: o mesmo hash do nome do arquivo."""
        return account_key(email)

    def active(self) -> str | None:
        """Devolve o e-mail selecionado, ou ``None`` se ele não existe mais."""
        try:
            data = json.loads(self.active_path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            return None
        email = data.get("email") if isinstance(data, dict) else None
        if not isinstance(email, str) or not email.strip():
            return None
        return email if self.path_for(email).exists() else None

    def set_active(self, email: str) -> None:
        """Marca a conta selecionada; a conta precisa existir."""
        if not self.path_for(email).exists():
            raise AccountsError(f"Conta desconhecida: {email}")
        _write_atomic(self.active_path, {"email": email})

    def clear_active(self) -> None:
        """Remove a marca de conta selecionada, preservando as contas."""
        self.active_path.unlink(missing_ok=True)

    def _read(self, path: Path) -> Account:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise AccountsError(f"{path.name}: conta inválida.")
        refresh_token = self._token(path, data)
        scopes = data.get("scopes")
        return Account(
            email=data.get("email", ""),
            name=data.get("name", ""),
            refresh_token=refresh_token,
            scopes=tuple(str(item) for item in scopes)
            if isinstance(scopes, list)
            else (),
            token_uri=_text(data.get("token_uri")),
            client_id=_text(data.get("client_id")),
        )

    def _token(self, path: Path, data: dict[str, Any]) -> str:
        """Lê o token do chaveiro ou desfaz a proteção do blob do arquivo."""
        if data.get("vault") == VAULT_KEYRING:
            if self._vault is None:
                raise AccountsError(f"{path.name}: token em chaveiro indisponível.")
            token = self._vault.get(path.stem)
            if not token:
                raise AccountsError(f"{path.name}: token ausente no chaveiro.")
            return token
        blob = data.get("token")
        if not isinstance(blob, str) or not blob:
            raise AccountsError(f"{path.name}: token ausente.")
        return self._unprotector(base64.b64decode(blob)).decode("utf-8")


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    write_atomic(path, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))


def write_atomic(path: Path, data: bytes) -> None:
    """Grava num ``.tmp`` ao lado e troca de uma vez: quem lê nunca vê metade."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)
