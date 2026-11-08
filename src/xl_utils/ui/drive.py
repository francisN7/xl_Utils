"""Estado do Drive compartilhado pelo menu do topo e pela tela inicial."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from xl_utils.shared import accounts, drive_auth
from xl_utils.shared.accounts import Account, AccountStore


class DriveSession:
    """Contas, conta ativa e o login em andamento.

    O login roda fora da thread da UI; quem escuta recebe um aviso quando o
    estado muda e só então redesenha os controles.
    """

    def __init__(
        self,
        store: AccountStore | None = None,
        authorize: Callable[[], Account] | None = None,
    ) -> None:
        self._store = store or AccountStore()
        self._authorize = authorize or drive_auth.authorize
        self._listeners: list[Callable[[], None]] = []
        self.accounts: list[Account] = []
        self.active: str | None = None
        self.busy = False
        self.error: str | None = None
        self.reload()

    @property
    def active_account(self) -> Account | None:
        """Devolve o registro da conta ativa, se houver."""
        for account in self.accounts:
            if account.email == self.active:
                return account
        return None

    @property
    def status(self) -> str:
        """Resume o estado do Drive para a tela inicial."""
        if self.busy:
            return "Conectando ao Google Drive…"
        if self.active:
            return f"Drive: {self.active}"
        if self.accounts:
            return "Drive: escolha uma conta"
        return "Drive: nenhuma conta conectada"

    def subscribe(self, listener: Callable[[], None]) -> None:
        """Registra um redesenho para quando o estado mudar."""
        self._listeners.append(listener)

    def reload(self) -> None:
        """Relê as contas e a conta ativa do disco."""
        self.accounts = self._store.list()
        self.active = self._store.active()

    def notify(self) -> None:
        """Avisa todos os controles inscritos."""
        for listener in self._listeners:
            listener()

    async def connect(self) -> None:
        """Abre o navegador e guarda a conta autorizada, fora da UI thread."""
        if self.busy:
            return
        self.busy = True
        self.error = None
        self.notify()
        try:
            account = await asyncio.to_thread(self._authorize)
            self._store.save(account)
            self._store.set_active(account.email)
        except (drive_auth.DriveError, accounts.AccountsError) as error:
            self.error = str(error)
        except Exception:  # noqa: BLE001 - nunca vazar token ou traceback
            self.error = "Falha inesperada ao entrar no Google Drive."
        finally:
            self.busy = False
            self.reload()
            self.notify()

    def switch(self, email: str) -> None:
        """Troca a conta ativa sem apagar nenhuma outra."""
        try:
            self._store.set_active(email)
            self.error = None
        except accounts.AccountsError as error:
            self.error = str(error)
        self.reload()
        self.notify()

    def next_account(self) -> str | None:
        """Devolve o próximo e-mail da lista, para o botão “Trocar”."""
        if len(self.accounts) < 2:
            return None
        emails = [account.email for account in self.accounts]
        if self.active not in emails:
            return emails[0]
        return emails[(emails.index(self.active) + 1) % len(emails)]

    def logout(self) -> None:
        """Remove só a conta ativa; as demais continuam guardadas."""
        if self.active is None:
            return
        self._store.remove(self.active)
        self._store.clear_active()
        self.error = None
        self.reload()
        self.notify()
