"""Página declarativa do plugin: regras puras, sem Flet.

O host converte o manifesto em ``PageSpec`` e confere os valores dos controles
antes de chamar ``run(request)``. Nada aqui importa o código do plugin.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from xl_utils.core.plugins.errors import PluginError
from xl_utils.core.plugins.manifest import (
    MAX_TEXT_LENGTH,
    InputSpec,
    OptionSpec,
    Permissions,
    PluginManifest,
)

OptionValue = str | int | bool


class OptionError(PluginError):
    """Valor de opção inválido para o tipo declarado no manifesto."""


@dataclass(frozen=True, slots=True)
class PageSpec:
    """O que a página precisa saber, já lido do manifesto."""

    title: str
    description: str
    note: str
    multiple_files: bool
    default_all_sheets: bool
    inputs: tuple[InputSpec, ...]
    options: tuple[OptionSpec, ...]

    @classmethod
    def from_manifest(cls, manifest: PluginManifest) -> PageSpec:
        """Monta a descrição da página sem tocar no código do plugin."""
        return cls(
            title=manifest.name,
            description=manifest.description,
            note=manifest.ui.note,
            multiple_files=manifest.ui.multiple_files,
            default_all_sheets=manifest.ui.default_all_sheets,
            inputs=manifest.ui.inputs,
            options=manifest.options,
        )

    @property
    def uses_inputs(self) -> bool:
        """Diz se a página usa slots nomeados em vez do seletor genérico."""
        return bool(self.inputs)


def defaults(spec: PageSpec) -> dict[str, OptionValue]:
    """Devolve o valor inicial de cada opção, na ordem do manifesto."""
    return {option.key: option.default for option in spec.options}


def coerce(option: OptionSpec, raw: object) -> OptionValue:
    """Converte o valor do controle para o tipo que ``run`` recebe."""
    if option.kind == "bool":
        if isinstance(raw, bool):
            return raw
        raise OptionError(
            "option_invalid",
            f"{option.label}: marque ou desmarque a opção.",
        )
    if option.kind == "int":
        return _integer(option, raw)
    if option.kind == "choice":
        if isinstance(raw, str) and raw in option.choices:
            return raw
        raise OptionError(
            "option_invalid",
            f"{option.label}: escolha uma das opções da lista.",
        )
    if not isinstance(raw, str):
        raise OptionError(
            "option_invalid",
            f"{option.label}: informe um texto.",
        )
    if len(raw) > MAX_TEXT_LENGTH:
        raise OptionError(
            "option_invalid",
            f"{option.label}: use no máximo {MAX_TEXT_LENGTH} caracteres.",
        )
    return raw


def validate(
    spec: PageSpec,
    values: Mapping[str, object],
) -> dict[str, OptionValue]:
    """Confere todos os campos de uma vez e devolve o mapping de ``options``."""
    return {
        option.key: coerce(option, values.get(option.key, option.default))
        for option in spec.options
    }


def describe_permissions(permissions: Permissions) -> tuple[str, ...]:
    """Resume as permissões declaradas para o aviso da tela."""
    labels: list[str] = []
    if permissions.network:
        labels.append("usa a rede")
    if permissions.filesystem == "read":
        labels.append("lê arquivos")
    elif permissions.filesystem == "write":
        labels.append("lê e grava arquivos")
    if permissions.subprocess:
        labels.append("inicia processos")
    return tuple(labels) or ("sem permissões extras",)


def _integer(option: OptionSpec, raw: object) -> int:
    if isinstance(raw, bool):
        raise OptionError(
            "option_invalid",
            f"{option.label}: informe um número inteiro.",
        )
    try:
        value = int(str(raw).strip())
    except TypeError, ValueError:
        raise OptionError(
            "option_invalid",
            f"{option.label}: informe um número inteiro.",
        ) from None
    if option.min is not None and value < option.min:
        raise OptionError(
            "option_invalid",
            f"{option.label}: o mínimo é {option.min}.",
        )
    if option.max is not None and value > option.max:
        raise OptionError(
            "option_invalid",
            f"{option.label}: o máximo é {option.max}.",
        )
    return value


__all__ = [
    "OptionError",
    "OptionValue",
    "PageSpec",
    "coerce",
    "defaults",
    "describe_permissions",
    "validate",
]
