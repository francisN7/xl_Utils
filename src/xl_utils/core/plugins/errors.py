"""Erros tipados do contrato de plugins."""


class PluginError(Exception):
    """Falha de plugin com um código estável para testes e diagnóstico."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ManifestError(PluginError):
    """Manifesto ausente, inválido ou incompatível."""


class PackageError(PluginError):
    """Pacote inseguro, corrompido ou fora dos limites."""


class InstallError(PluginError):
    """Falha ao instalar, listar ou remover um plugin."""
