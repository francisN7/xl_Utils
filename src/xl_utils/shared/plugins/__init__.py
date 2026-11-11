"""Instalação e API de plugins do xl_Utils."""

from xl_utils.shared.plugins.api import PluginRequest, PluginResult
from xl_utils.shared.plugins.install import (
    InstalledPlugin,
    InvalidPlugin,
    ScanResult,
    install_package,
    list_installed,
    plugins_root,
    scan_installed,
    uninstall_plugin,
)

__all__ = [
    "InstalledPlugin",
    "InvalidPlugin",
    "PluginRequest",
    "PluginResult",
    "ScanResult",
    "install_package",
    "list_installed",
    "plugins_root",
    "scan_installed",
    "uninstall_plugin",
]
