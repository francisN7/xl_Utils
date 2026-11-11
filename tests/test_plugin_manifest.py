"""Validação pura do plugin.toml."""

import pytest
from plugin_helpers import VALID_MANIFEST

from xl_utils.core.plugins.errors import ManifestError
from xl_utils.core.plugins.manifest import (
    MAX_MANIFEST_BYTES,
    entrypoint_parts,
    parse_manifest,
    validate_id,
)


def manifest_with(**replacements: str) -> str:
    text = VALID_MANIFEST
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def test_valid_manifest_is_parsed() -> None:
    manifest = parse_manifest(VALID_MANIFEST, app_version="0.3.0")
    assert manifest.id == "autor.teste"
    assert manifest.name == "Plugin de Teste"
    assert manifest.version == "1.0.0"
    assert manifest.api_version == 1
    assert manifest.entrypoint == "main:run"
    assert manifest.permissions.filesystem == "read"
    assert manifest.ui.multiple_files is True
    assert manifest.options[0].kind == "choice"
    assert manifest.options[0].default == "a"


def test_named_inputs_are_parsed() -> None:
    text = VALID_MANIFEST.replace(
        "multiple_files = true\ndefault_all_sheets = true",
        "multiple_files = false\ndefault_all_sheets = true\n\n"
        '[[ui.inputs]]\nkey = "origem"\nlabel = "Origem"\nrequired = true',
    )
    manifest = parse_manifest(text)
    assert manifest.ui.inputs[0].key == "origem"
    assert manifest.ui.inputs[0].required is True


def test_missing_plugin_table_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest("[permissions]\nnetwork = false\n")
    assert error.value.code == "manifest_invalid"


def test_missing_required_field_fails() -> None:
    text = manifest_with(**{'description = "Plugin usado nos testes."': ""})
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_invalid_id_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{"autor.teste": "Autor.Teste"}))
    assert error.value.code == "invalid_id"


def test_reserved_windows_id_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{"autor.teste": "con.teste"}))
    assert error.value.code == "invalid_id"


def test_validate_id_accepts_and_rejects() -> None:
    assert validate_id("autor.ferramenta") == "autor.ferramenta"
    with pytest.raises(ManifestError):
        validate_id("..")


def test_invalid_version_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{'version = "1.0.0"': 'version = "1.0"'}))
    assert error.value.code == "manifest_invalid"


def test_unsupported_api_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{"api_version = 1": "api_version = 2"}))
    assert error.value.code == "unsupported_api"


def test_min_app_version_is_checked() -> None:
    text = manifest_with(
        **{
            'authors = ["Teste"]': 'authors = ["Teste"]\nmin_app_version = "0.4.0"',
        }
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text, app_version="0.3.0")
    assert error.value.code == "app_too_old"


def test_invalid_entrypoint_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{"main:run": "main"}))
    assert error.value.code == "manifest_invalid"


def test_unknown_key_fails() -> None:
    text = manifest_with(
        **{
            "[permissions]": "[plugin.extra]\nvalue = true\n\n[permissions]",
        }
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_unknown_ui_key_fails() -> None:
    text = manifest_with(
        **{
            "multiple_files = true": "multiple_files = true\nextra = true",
        }
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_duplicate_option_fails() -> None:
    text = (
        VALID_MANIFEST
        + """
[[options]]
key = "modo"
label = "Outro"
type = "text"
"""
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "duplicate_option"


def test_choice_default_must_be_in_choices() -> None:
    text = manifest_with(**{'default = "a"': 'default = "z"'})
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_int_default_must_fit_bounds() -> None:
    text = (
        VALID_MANIFEST
        + """
[[options]]
key = "limite"
label = "Limite"
type = "int"
default = 20
min = 1
max = 10
"""
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_inputs_and_multiple_files_conflict() -> None:
    text = (
        VALID_MANIFEST
        + """
[[ui.inputs]]
key = "origem"
label = "Origem"
"""
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_too_many_options_fails() -> None:
    text = VALID_MANIFEST
    for index in range(20):
        text += f"""
[[options]]
key = "opcao_{index}"
label = "Opção"
type = "text"
"""
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_broken_toml_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest("[plugin")
    assert error.value.code == "manifest_invalid"


def test_large_manifest_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest("x" * (MAX_MANIFEST_BYTES + 1))
    assert error.value.code == "manifest_too_large"


def test_invalid_dependency_fails() -> None:
    text = manifest_with(
        **{
            'authors = ["Teste"]': 'authors = ["Teste"]\ndependencies = ["pandas>=3"]',
        }
    )
    with pytest.raises(ManifestError) as error:
        parse_manifest(text)
    assert error.value.code == "manifest_invalid"


def test_invalid_filesystem_permission_fails() -> None:
    with pytest.raises(ManifestError) as error:
        parse_manifest(manifest_with(**{'filesystem = "read"': 'filesystem = "all"'}))
    assert error.value.code == "manifest_invalid"


def test_entrypoint_parts() -> None:
    assert entrypoint_parts("pkg.mod:run") == ("pkg.mod", "run")
