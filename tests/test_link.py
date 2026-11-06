import pandas as pd
import pytest

from xl_utils.core.tools.link import (
    MIGRACAO,
    SEM_VINCULO,
    VINCULA_POR_CNJ,
    VINCULA_POR_PASTA,
    VINCULA_POR_PROTOCOLO,
    AlreadyProcessedError,
    InvalidCnjError,
    LinkConfig,
    MissingColumnsError,
    SheetSpec,
    fold_header,
    link_agenda,
)

CNJ_A = "1111111-11.1111.1.11.1111"
CNJ_B = "2222222-22.2222.2.22.2222"
CNJ_RAW = "11111111111111111111"
CNJ_OTHER_RAW = "22222222222222222222"


def _config() -> LinkConfig:
    return LinkConfig(
        sheets={
            "AGENDA": SheetSpec(
                name="AGENDA",
                standard=("DATA", "DESCRIÇÃO", "CNJ", "PROTOCOLO", "PASTA"),
                fields={
                    "descricao": "DESCRIÇÃO",
                    "cnj": "CNJ",
                    "protocolo": "PROTOCOLO",
                    "pasta": "PASTA",
                },
                required=("descricao", "cnj", "protocolo", "pasta"),
            ),
            "PROCESSOS": SheetSpec(
                name="PROCESSOS",
                standard=("NOME", "CNJ", "PROTOCOLO", "PASTA"),
                fields={
                    "nome": "NOME",
                    "cnj": "CNJ",
                    "protocolo": "PROTOCOLO",
                    "pasta": "PASTA",
                },
                required=("nome", "cnj", "protocolo", "pasta"),
            ),
        },
        vincula_column="VINCULA?",
        vincula_nome_column="VINCULA (POR NOME)?",
    )


def _agenda(rows: list[dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["DATA", "DESCRIÇÃO", "CNJ", "PROTOCOLO", "PASTA"],
    )


def _processos(rows: list[dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["NOME", "CNJ", "PROTOCOLO", "PASTA"])


def _processo(
    cnj: str = "",
    protocolo: str = "",
    pasta: str = "",
) -> dict[str, str]:
    return {
        "NOME": "Cliente fictício",
        "CNJ": cnj,
        "PROTOCOLO": protocolo,
        "PASTA": pasta,
    }


def _linha(
    cnj: str = "",
    protocolo: str = "",
    pasta: str = "",
    descricao: str = "Audiência",
) -> dict[str, str]:
    return {
        "DATA": "01/01/2026",
        "DESCRIÇÃO": descricao,
        "CNJ": cnj,
        "PROTOCOLO": protocolo,
        "PASTA": pasta,
    }


def test_priority_is_cnj_then_pasta_then_protocolo() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1")])
    agenda = _agenda(
        [
            _linha(CNJ_A, "P1", "A1"),
            _linha(CNJ_B, "P1", "A1"),
            _linha(CNJ_B, "P1", "A2"),
            _linha(CNJ_B, "P2", "A2"),
        ]
    )

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": processos},
        _config(),
    )

    saida = result.sheets["Agenda"]
    assert saida["VINCULA?"].tolist() == [
        VINCULA_POR_CNJ,
        VINCULA_POR_PASTA,
        VINCULA_POR_PROTOCOLO,
        SEM_VINCULO,
    ]
    assert result.stats.by_cnj == 1
    assert result.stats.by_pasta == 1
    assert result.stats.by_protocolo == 1
    assert result.stats.unlinked == 1


def test_masked_and_raw_cnj_are_compared_as_text() -> None:
    processos = _processos([_processo(CNJ_RAW)])
    agenda = _agenda([_linha(CNJ_A), _linha(CNJ_RAW)])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": processos},
        _config(),
    )

    saida = result.sheets["Agenda"]
    assert saida["VINCULA?"].tolist() == [SEM_VINCULO, VINCULA_POR_CNJ]
    assert result.stats.agenda_masked == 1
    assert result.stats.agenda_raw == 1


def test_invalid_cnj_stops_everything_and_lists_the_cases() -> None:
    agenda = _agenda([_linha("123"), _linha(CNJ_A)])
    processos = _processos([_processo("abc")])

    with pytest.raises(InvalidCnjError) as captured:
        link_agenda({"Agenda": agenda}, {"Processos": processos}, _config())

    problems = captured.value.problems
    assert len(problems) == 2
    assert problems[0].source == "AGENDA"
    assert problems[0].row == 2
    assert problems[1].source == "PROCESSOS"
    assert "CNJ fora do padrão" in str(captured.value)


def test_unlinked_row_keeps_protocol_in_description_and_becomes_migration() -> None:
    agenda = _agenda([_linha("", "P1", descricao="Audiência")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A1")])},
        _config(),
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência\nPROTOCOLO: P1"
    assert saida.loc[0, "PROTOCOLO"] == MIGRACAO
    assert saida.loc[0, "VINCULA?"] == SEM_VINCULO


def test_unlinked_row_without_protocol_still_becomes_migration() -> None:
    agenda = _agenda([_linha("", "", descricao="Audiência")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A1")])},
        _config(),
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência"
    assert saida.loc[0, "PROTOCOLO"] == MIGRACAO


def test_empty_description_receives_only_the_protocol_line() -> None:
    agenda = _agenda([_linha("", "P1", descricao="")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A1")])},
        _config(),
    )

    assert result.sheets["Agenda"].loc[0, "DESCRIÇÃO"] == "PROTOCOLO: P1"


def test_new_column_goes_after_the_standard_block_and_before_extras() -> None:
    agenda = _agenda([_linha(CNJ_A, "P1", "A1")])
    agenda["EXTRA"] = ["livre"]

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
        _config(),
    )

    assert list(result.sheets["Agenda"].columns) == [
        "DATA",
        "DESCRIÇÃO",
        "CNJ",
        "PROTOCOLO",
        "PASTA",
        "VINCULA?",
        "EXTRA",
    ]


def test_existing_vincula_column_is_overwritten_in_place() -> None:
    agenda = _agenda([_linha(CNJ_A, "P1", "A1")])
    agenda.insert(5, "VINCULA?", ["valor antigo"])
    agenda["EXTRA"] = ["livre"]

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
        _config(),
    )

    saida = result.sheets["Agenda"]
    assert list(saida.columns) == [
        "DATA",
        "DESCRIÇÃO",
        "CNJ",
        "PROTOCOLO",
        "PASTA",
        "VINCULA?",
        "EXTRA",
    ]
    assert saida.loc[0, "VINCULA?"] == VINCULA_POR_CNJ


def test_other_sheets_are_preserved() -> None:
    agenda = _agenda([_linha(CNJ_A, "P1", "A1")])
    outra = pd.DataFrame({"QUALQUER": ["x"]})

    result = link_agenda(
        {"Agenda": agenda, "Outra": outra},
        {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
        _config(),
    )

    assert result.target_sheet == "Agenda"
    assert result.sheets["Outra"].equals(outra)


def test_missing_columns_are_reported() -> None:
    agenda = pd.DataFrame(
        {
            "DESCRIÇÃO": ["Audiência"],
            "CNJ": [CNJ_A],
            "PROTOCOLO": ["P1"],
        }
    )

    with pytest.raises(MissingColumnsError) as captured:
        link_agenda({"Agenda": agenda}, {"Processos": _processos([])}, _config())

    assert "PASTA" in str(captured.value)


def test_reexecution_requires_confirmation() -> None:
    agenda = _agenda([_linha(CNJ_A, MIGRACAO, "A1")])

    with pytest.raises(AlreadyProcessedError):
        link_agenda(
            {"Agenda": agenda},
            {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
            _config(),
        )


def test_confirmed_reexecution_does_not_repeat_the_protocol_line() -> None:
    agenda = _agenda([_linha("", MIGRACAO, "", descricao="Audiência\nPROTOCOLO: P1")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A1")])},
        _config(),
        allow_migrated=True,
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência\nPROTOCOLO: P1"
    assert saida.loc[0, "PROTOCOLO"] == MIGRACAO
    assert saida.loc[0, "VINCULA?"] == SEM_VINCULO


def test_pasta_and_protocol_are_compared_without_normalization() -> None:
    processos = _processos([_processo("", "P1", "A1")])
    agenda = _agenda([_linha("", "P1 ", " A1")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": processos},
        _config(),
    )

    assert result.sheets["Agenda"].loc[0, "VINCULA?"] == SEM_VINCULO


def test_header_matching_ignores_case_accent_and_extra_spaces() -> None:
    assert fold_header("  NÚMERO   do Processo ") == "numero do processo"
    assert fold_header("Descrição") == fold_header("DESCRIÇÃO")
    assert fold_header("NUMERO DO PROCESSO") == fold_header("NÚMERO DO PROCESSO")


def test_header_matching_finds_the_sheet_with_the_required_columns() -> None:
    vazia = pd.DataFrame({"OUTRA": ["x"]})
    agenda = _agenda([_linha(CNJ_A, "P1", "A1")])

    result = link_agenda(
        {"Primeira": vazia, "Segunda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
        _config(),
    )

    assert result.target_sheet == "Segunda"
