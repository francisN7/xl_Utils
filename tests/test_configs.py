import json
from importlib import resources

import pytest

from xl_utils.core.tools.link import ConfigError
from xl_utils.shared import configs


def _packaged_text() -> str:
    resource = resources.files("xl_utils.configs").joinpath("headers.json")
    return resource.read_text(encoding="utf-8")


def test_packaged_config_has_the_four_standard_sheets() -> None:
    config = configs.load_packaged_config()

    assert set(config.sheets) == {"AGENDA", "PROCESSOS", "FINANCEIRO", "CLIENTES"}
    assert config.sheets["AGENDA"].fields["cnj"] == "NUMERO DO PROCESSO"
    assert config.sheets["PROCESSOS"].fields["cnj"] == "NÚMERO DO PROCESSO"
    assert config.sheets["FINANCEIRO"].fields["cnj"] == "PROCESSO"
    assert config.sheets["CLIENTES"].fields["nome"] == "NOME"


def test_agenda_and_financeiro_use_different_join_separators() -> None:
    config = configs.load_packaged_config()

    assert config.sheets["AGENDA"].description_separator == "\n"
    assert config.sheets["FINANCEIRO"].description_separator == " | "


def test_override_is_used_when_present(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    data = json.loads(_packaged_text())
    data["columns"]["vincula"] = "VINCULA (TESTE)?"
    override = tmp_path / "xl_utils" / "headers.json"
    override.parent.mkdir(parents=True)
    override.write_text(json.dumps(data), encoding="utf-8")

    config = configs.load_link_config()

    assert config.vincula_column == "VINCULA (TESTE)?"


def test_invalid_override_raises_a_clear_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    override = tmp_path / "xl_utils" / "headers.json"
    override.parent.mkdir(parents=True)
    override.write_text("{}", encoding="utf-8")

    with pytest.raises(ConfigError):
        configs.load_link_config()


def test_packaged_config_does_not_need_the_repository(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(configs, "override_path", lambda: tmp_path / "ausente.json")

    config = configs.load_link_config()

    assert config.vincula_column == "VINCULA?"
