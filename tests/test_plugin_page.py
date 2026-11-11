"""Página declarativa do plugin e validação das opções."""

from __future__ import annotations

import pytest

from xl_utils.core.plugins.manifest import parse_manifest
from xl_utils.core.plugins.page import (
    OptionError,
    PageSpec,
    coerce,
    defaults,
    describe_permissions,
    validate,
)

ALL_OPTIONS = """\
[plugin]
id = "autor.opcoes"
name = "Opções de Teste"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Testa todos os tipos de opção."

[ui]
multiple_files = true
default_all_sheets = true
note = "Dica curta."

[[options]]
key = "texto"
label = "Texto"
type = "text"
default = "oi"

[[options]]
key = "limite"
label = "Limite"
type = "int"
default = 5
min = 1
max = 10

[[options]]
key = "detalhado"
label = "Detalhado"
type = "bool"

[[options]]
key = "modo"
label = "Modo"
type = "choice"
default = "a"
choices = ["a", "b"]
"""

NAMED_INPUTS = """\
[plugin]
id = "autor.entradas"
name = "Entradas"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Usa slots nomeados."

[[ui.inputs]]
key = "origem"
label = "Planilha de origem"

[[ui.inputs]]
key = "apoio"
label = "Planilha de apoio"
required = false
"""


def spec(manifest: str = ALL_OPTIONS) -> PageSpec:
    return PageSpec.from_manifest(parse_manifest(manifest))


def test_page_spec_follows_manifest() -> None:
    page = spec()

    assert page.title == "Opções de Teste"
    assert page.description.startswith("Testa todos")
    assert page.note == "Dica curta."
    assert page.multiple_files is True
    assert page.default_all_sheets is True
    assert page.uses_inputs is False
    assert [option.key for option in page.options] == [
        "texto",
        "limite",
        "detalhado",
        "modo",
    ]


def test_named_inputs_replace_the_generic_selector() -> None:
    page = spec(NAMED_INPUTS)

    assert page.uses_inputs is True
    assert [slot.key for slot in page.inputs] == ["origem", "apoio"]
    assert [slot.required for slot in page.inputs] == [True, False]
    assert page.multiple_files is False


def test_defaults_come_from_the_manifest() -> None:
    assert defaults(spec()) == {
        "texto": "oi",
        "limite": 5,
        "detalhado": False,
        "modo": "a",
    }


def test_validate_converts_every_type() -> None:
    values = validate(
        spec(),
        {"texto": "livre", "limite": "7", "detalhado": True, "modo": "b"},
    )

    assert values == {
        "texto": "livre",
        "limite": 7,
        "detalhado": True,
        "modo": "b",
    }


def test_validate_falls_back_to_defaults() -> None:
    assert validate(spec(), {}) == defaults(spec())


def test_text_is_limited_to_500_characters() -> None:
    option = spec().options[0]

    with pytest.raises(OptionError, match="500"):
        coerce(option, "x" * 501)

    assert coerce(option, "x" * 500) == "x" * 500


def test_text_requires_a_string() -> None:
    with pytest.raises(OptionError, match="informe um texto"):
        coerce(spec().options[0], 12)


@pytest.mark.parametrize("raw", ["0", "11", "abc", "", True, None])
def test_int_out_of_range_or_invalid(raw: object) -> None:
    with pytest.raises(OptionError):
        coerce(spec().options[1], raw)


@pytest.mark.parametrize(("raw", "value"), [(1, 1), ("10", 10), (" 5 ", 5)])
def test_int_accepts_numbers_and_numeric_text(raw: object, value: int) -> None:
    assert coerce(spec().options[1], raw) == value


def test_bool_requires_a_boolean() -> None:
    option = spec().options[2]

    assert coerce(option, True) is True
    with pytest.raises(OptionError):
        coerce(option, "true")


def test_choice_must_be_declared() -> None:
    option = spec().options[3]

    assert coerce(option, "b") == "b"
    with pytest.raises(OptionError):
        coerce(option, "c")


def test_permissions_are_summarized() -> None:
    replacement = (
        '[permissions]\nnetwork = true\nfilesystem = "write"\nsubprocess = true\n\n[ui]'
    )
    manifest = parse_manifest(ALL_OPTIONS.replace("[ui]", replacement))

    assert describe_permissions(manifest.permissions) == (
        "usa a rede",
        "lê e grava arquivos",
        "inicia processos",
    )


def test_empty_permissions_are_explicit() -> None:
    manifest = parse_manifest(ALL_OPTIONS)

    assert describe_permissions(manifest.permissions) == ("sem permissões extras",)
