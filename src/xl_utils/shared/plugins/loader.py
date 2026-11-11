"""Carrega o código do plugin sob demanda, sem tocar em ``sys.path``.

A descoberta e a página declarativa usam só o manifesto. Este é o único módulo
que importa ``lib/``, e só na primeira execução da ferramenta. O plugin vira um
pacote sintético em ``sys.modules`` — imports relativos entre os arquivos do
plugin funcionam, e nenhum nome genérico como ``main`` vaza para o processo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Protocol

from xl_utils.core.plugins.errors import PluginError
from xl_utils.core.plugins.manifest import PluginManifest, entrypoint_parts
from xl_utils.shared.plugins.install import InstalledPlugin

MODULE_PREFIX = "xl_utils_plugin_"
_UNSAFE = re.compile(r"[^a-z0-9_]")


class PluginLoadError(PluginError):
    """O plugin está instalado, mas o código não pôde ser carregado."""


class PluginRunner(Protocol):
    """Assinatura aceita para a função de entrada do plugin."""

    def __call__(self, request: object, /) -> object: ...


@dataclass(frozen=True, slots=True)
class LoadedPlugin:
    """Módulo importado e a função de entrada já conferida."""

    id: str
    version: str
    path: Path
    module: ModuleType
    run: PluginRunner


class PluginLoader:
    """Importa ``lib/`` uma vez por plugin e reusa o módulo nas execuções."""

    def __init__(self) -> None:
        self._loaded: dict[tuple[str, str, str], LoadedPlugin] = {}

    def load(
        self,
        plugin: InstalledPlugin,
        manifest: PluginManifest | None = None,
    ) -> LoadedPlugin:
        """Importa o plugin agora — chamado só quando a ferramenta executa."""
        spec = manifest or plugin.manifest
        if spec is None:
            raise PluginLoadError(
                "manifest_missing",
                f"Manifesto indisponível para {plugin.id}; releia a pasta.",
            )
        key = (plugin.id, plugin.version, str(plugin.path))
        cached = self._loaded.get(key)
        if cached is not None:
            return cached
        loaded = _import_plugin(plugin.path, spec)
        self._loaded[key] = loaded
        return loaded

    def forget(self, plugin_id: str | None = None) -> None:
        """Descarta o cache e os módulos sintéticos após instalar ou remover."""
        for key in [key for key in self._loaded if plugin_id in (None, key[0])]:
            _drop_modules(_package_name(key[0]))
            del self._loaded[key]

    def loaded_ids(self) -> tuple[str, ...]:
        """Lista os plugins já importados nesta sessão."""
        return tuple(key[0] for key in self._loaded)


def _import_plugin(plugin_dir: Path, manifest: PluginManifest) -> LoadedPlugin:
    module_name, function_name = entrypoint_parts(manifest.entrypoint)
    lib = plugin_dir / "lib"
    if not lib.is_dir():
        raise PluginLoadError(
            "entrypoint_missing",
            f"{manifest.id}: pasta lib/ ausente em {plugin_dir}.",
        )
    package = _package_name(manifest.id)
    created: list[str] = []
    _drop_modules(package)
    ready = False
    try:
        _load_package(package, lib, created)
        module = _load_entry(package, module_name, lib, created)
        function = getattr(module, function_name, None)
        if not callable(function):
            raise PluginLoadError(
                "run_missing",
                f"{manifest.id}: {manifest.entrypoint} não define "
                f"{function_name}() chamável.",
            )
        _check_signature(function, manifest)
        ready = True
    except PluginLoadError:
        raise
    except Exception as error:  # noqa: BLE001 - o erro do plugin vira diagnóstico
        raise PluginLoadError(
            "plugin_import_failed",
            f"{manifest.id}: falha ao importar {manifest.entrypoint}: "
            f"{type(error).__name__}: {error}",
        ) from error
    finally:
        if not ready:
            for name in reversed(created):
                sys.modules.pop(name, None)
    return LoadedPlugin(
        id=manifest.id,
        version=manifest.version,
        path=plugin_dir,
        module=module,
        run=function,
    )


def _package_name(plugin_id: str) -> str:
    """Gera um nome de pacote estável e sem colisão entre ids parecidos."""
    digest = hashlib.sha256(plugin_id.encode("utf-8")).hexdigest()[:8]
    safe = _UNSAFE.sub("_", plugin_id.lower())
    return f"{MODULE_PREFIX}{safe}_{digest}"


def _load_package(name: str, directory: Path, created: list[str]) -> ModuleType:
    init = directory / "__init__.py"
    if init.is_file():
        return _load_source(name, init, created, search=[str(directory)])
    module = ModuleType(name)
    module.__path__ = [str(directory)]
    module.__package__ = name
    sys.modules[name] = module
    created.append(name)
    return module


def _load_entry(
    package: str,
    module_name: str,
    lib: Path,
    created: list[str],
) -> ModuleType:
    parts = module_name.split(".")
    current = package
    directory = lib
    for part in parts[:-1]:
        directory = directory / part
        if not (directory / "__init__.py").is_file() and not directory.is_dir():
            raise PluginLoadError(
                "entrypoint_missing",
                f"Pacote {current}.{part} não existe em {lib}.",
            )
        current = f"{current}.{part}"
        _load_package(current, directory, created)

    last = parts[-1]
    name = f"{current}.{last}"
    as_package = directory / last / "__init__.py"
    as_module = directory / f"{last}.py"
    if as_package.is_file():
        return _load_source(
            name,
            as_package,
            created,
            search=[str(directory / last)],
        )
    if as_module.is_file():
        return _load_source(name, as_module, created)
    raise PluginLoadError(
        "entrypoint_missing",
        f"Módulo {module_name} não encontrado em {lib}.",
    )


def _load_source(
    name: str,
    file: Path,
    created: list[str],
    *,
    search: list[str] | None = None,
) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        name,
        file,
        submodule_search_locations=search,
    )
    if spec is None or spec.loader is None:
        raise PluginLoadError(
            "plugin_import_failed",
            f"Não foi possível montar o módulo {name} a partir de {file}.",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    created.append(name)
    spec.loader.exec_module(module)
    return module


def _check_signature(function: PluginRunner, manifest: PluginManifest) -> None:
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError) as error:
        raise PluginLoadError(
            "run_signature",
            f"{manifest.id}: não foi possível ler a assinatura de "
            f"{manifest.entrypoint}: {error}",
        ) from error
    parameters = list(signature.parameters.values())
    positional = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )
    if len(parameters) != 1 or parameters[0].kind not in positional:
        raise PluginLoadError(
            "run_signature",
            f"{manifest.id}: {manifest.entrypoint} deve receber exatamente um "
            "parâmetro posicional (request).",
        )


def _drop_modules(package: str) -> None:
    prefix = f"{package}."
    for name in [
        name for name in sys.modules if name == package or name.startswith(prefix)
    ]:
        sys.modules.pop(name, None)


__all__ = [
    "MODULE_PREFIX",
    "LoadedPlugin",
    "PluginLoadError",
    "PluginLoader",
    "PluginRunner",
]
