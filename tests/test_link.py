import pandas as pd
import pytest

from xl_utils.core.tools.link import (
    MIGRACAO,
    NAO,
    SEM_VINCULO,
    SIM,
    VINCULA_POR_CNJ,
    VINCULA_POR_PASTA,
    VINCULA_POR_PROTOCOLO,
    AlreadyProcessedError,
    InvalidCnjError,
    LinkConfig,
    MissingColumnsError,
    SheetSpec,
    fold_header,
    header_key,
    link_agenda,
    link_financeiro,
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
            "FINANCEIRO": SheetSpec(
                name="FINANCEIRO",
                standard=("DESCRIÇÃO", "PROCESSO", "PROTOCOLO", "PASTA", "NOME"),
                fields={
                    "descricao": "DESCRIÇÃO",
                    "cnj": "PROCESSO",
                    "protocolo": "PROTOCOLO",
                    "pasta": "PASTA",
                    "nome": "NOME",
                },
                required=("descricao", "cnj", "protocolo", "pasta", "nome"),
                description_separator=" | ",
            ),
            "CLIENTES": SheetSpec(
                name="CLIENTES",
                standard=("NOME",),
                fields={"nome": "NOME"},
                required=("nome",),
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
    nome: str = "Cliente fictício",
) -> dict[str, str]:
    return {
        "NOME": nome,
        "CNJ": cnj,
        "PROTOCOLO": protocolo,
        "PASTA": pasta,
    }


FIN_COLUMNS = ["DESCRIÇÃO", "PROCESSO", "PROTOCOLO", "PASTA", "NOME"]


def _financeiro(rows: list[dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=FIN_COLUMNS)


def _fin_linha(
    cnj: str = "",
    protocolo: str = "",
    pasta: str = "",
    nome: str = "Cliente Alfa",
    descricao: str = "Mensalidade",
) -> dict[str, str]:
    return {
        "DESCRIÇÃO": descricao,
        "PROCESSO": cnj,
        "PROTOCOLO": protocolo,
        "PASTA": pasta,
        "NOME": nome,
    }


def _clientes(nomes: list[str]) -> dict[str, pd.DataFrame]:
    return {"Clientes": pd.DataFrame({"NOME": nomes})}


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


def test_header_key_ignores_spaces_in_the_column_name() -> None:
    assert header_key("VINCULA (POR NOME)?") == header_key("VINCULA(POR NOME)?")


def test_financeiro_priority_is_cnj_then_pasta_then_protocolo() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1", nome="Cliente Alfa")])
    financeiro = _financeiro(
        [
            _fin_linha(CNJ_A, "P1", "A1"),
            _fin_linha(CNJ_B, "P1", "A1"),
            _fin_linha(CNJ_B, "P1", "A2"),
            _fin_linha(CNJ_B, "P2", "A2"),
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    saida = result.sheets["Fin"]
    assert saida["VINCULA?"].tolist() == [
        VINCULA_POR_CNJ,
        VINCULA_POR_PASTA,
        VINCULA_POR_PROTOCOLO,
        SEM_VINCULO,
    ]
    assert saida["VINCULA (POR NOME)?"].tolist() == [SIM, SIM, SIM, SIM]
    assert result.stats.by_cnj == 1
    assert result.stats.by_pasta == 1
    assert result.stats.by_protocolo == 1
    assert result.stats.unlinked == 1


def test_financeiro_name_joins_processos_and_clientes_without_normalizing() -> None:
    processos = _processos(
        [_processo(CNJ_A, "P1", "A1", nome="Cliente Eta;\u0020Cliente Sigma")]
    )
    financeiro = _financeiro(
        [
            _fin_linha(nome="Cliente Eta"),
            _fin_linha(nome="Cliente Sigma"),
            _fin_linha(nome="Cliente Alfa"),
            _fin_linha(nome="cliente alfa"),
            _fin_linha(nome=""),
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    assert result.sheets["Fin"]["VINCULA (POR NOME)?"].tolist() == [
        SIM,
        NAO,
        SIM,
        NAO,
        NAO,
    ]


def test_financeiro_with_only_clientes_creates_only_the_name_column() -> None:
    financeiro = _financeiro(
        [_fin_linha(nome="Cliente Alfa"), _fin_linha(nome="Cliente Beta")]
    )
    financeiro["VINCULA?"] = ["antigo", "antigo"]

    result = link_financeiro(
        {"Fin": financeiro},
        None,
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    saida = result.sheets["Fin"]
    assert saida["VINCULA?"].tolist() == ["antigo", "antigo"]
    assert saida["VINCULA (POR NOME)?"].tolist() == [SIM, NAO]
    assert result.stats.numbers_tested is False
    assert list(saida.columns) == [
        "DESCRIÇÃO",
        "PROCESSO",
        "PROTOCOLO",
        "PASTA",
        "NOME",
        "VINCULA?",
        "VINCULA (POR NOME)?",
    ]


def test_financeiro_with_only_processos_tests_numbers_and_names() -> None:
    processos = _processos(
        [
            _processo(CNJ_A, "P1", "A1", nome="Cliente Alfa"),
            _processo("", "", "", nome="Cliente Beta;Cliente Gama"),
        ]
    )
    financeiro = _financeiro(
        [
            _fin_linha(CNJ_A, "", "", nome="Cliente Alfa"),
            _fin_linha("", "", "", nome="Cliente Beta"),
            _fin_linha("", "", "", nome="Cliente Gama"),
            _fin_linha("", "", "", nome="Cliente Delta"),
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        None,
        _config(),
    )

    saida = result.sheets["Fin"]
    assert saida["VINCULA?"].tolist() == [
        VINCULA_POR_CNJ,
        SEM_VINCULO,
        SEM_VINCULO,
        SEM_VINCULO,
    ]
    assert saida["VINCULA (POR NOME)?"].tolist() == [SIM, SIM, SIM, NAO]


def test_financeiro_name_in_description_prefixes_only_when_unlinked() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1", nome="Cliente Alfa")])
    financeiro = _financeiro(
        [
            _fin_linha(
                CNJ_A,
                "P1",
                "A1",
                nome="Cliente Desconhecido",
                descricao="Mensalidade",
            ),
            _fin_linha(nome="Cliente Desconhecido", descricao=""),
            _fin_linha(nome="", descricao="Mensalidade"),
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        None,
        _config(),
        name_in_description=True,
    )

    saida = result.sheets["Fin"]
    assert saida.loc[0, "DESCRIÇÃO"] == (
        "NOME DO CLIENTE: Cliente Desconhecido | Mensalidade"
    )
    assert saida.loc[1, "DESCRIÇÃO"] == "NOME DO CLIENTE: Cliente Desconhecido"
    assert saida.loc[2, "DESCRIÇÃO"] == "Mensalidade"


def test_financeiro_single_field_moves_and_clears_the_other_numbers() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1", nome="Cliente Alfa")])
    financeiro = _financeiro(
        [
            _fin_linha(CNJ_A, "P2", "A2"),
            _fin_linha(CNJ_B, "P3", "A1"),
            _fin_linha(CNJ_B, "P1", "A3"),
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        None,
        _config(),
        single_field=True,
    )

    saida = result.sheets["Fin"]
    assert saida.loc[0, "DESCRIÇÃO"] == "Mensalidade | PASTA: A2 | PROTOCOLO: P2"
    assert saida.loc[0, "PASTA"] == ""
    assert saida.loc[0, "PROTOCOLO"] == ""
    assert saida.loc[1, "DESCRIÇÃO"] == (
        f"Mensalidade | PROCESSO: {CNJ_B} | PROTOCOLO: P3"
    )
    assert saida.loc[1, "PROCESSO"] == ""
    assert saida.loc[1, "PROTOCOLO"] == ""
    assert saida.loc[2, "DESCRIÇÃO"] == f"Mensalidade | PROCESSO: {CNJ_B} | PASTA: A3"
    assert saida.loc[2, "PROCESSO"] == ""
    assert saida.loc[2, "PASTA"] == ""


def test_financeiro_combines_name_prefix_and_moved_fields() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1", nome="Cliente Alfa")])
    financeiro = _financeiro(
        [
            _fin_linha(
                CNJ_A,
                "P2",
                "A2",
                nome="Cliente Desconhecido",
                descricao="Mensalidade",
            )
        ]
    )

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": processos},
        None,
        _config(),
        name_in_description=True,
        single_field=True,
    )

    assert result.sheets["Fin"].loc[0, "DESCRIÇÃO"] == (
        "NOME DO CLIENTE: Cliente Desconhecido | Mensalidade | "
        "PASTA: A2 | PROTOCOLO: P2"
    )


def test_agenda_single_field_moves_and_clears_the_other_numbers() -> None:
    processos = _processos([_processo(CNJ_A, "P1", "A1")])
    agenda = _agenda(
        [
            _linha(CNJ_A, "P2", "A2"),
            _linha(CNJ_B, "P3", "A1"),
            _linha(CNJ_B, "P1", "A3"),
        ]
    )

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": processos},
        _config(),
        single_field=True,
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência\nPASTA: A2\nPROTOCOLO: P2"
    assert saida.loc[0, "PASTA"] == ""
    assert saida.loc[0, "PROTOCOLO"] == ""
    assert saida.loc[1, "DESCRIÇÃO"] == (f"Audiência\nCNJ: {CNJ_B}\nPROTOCOLO: P3")
    assert saida.loc[1, "CNJ"] == ""
    assert saida.loc[1, "PROTOCOLO"] == ""
    assert saida.loc[2, "DESCRIÇÃO"] == f"Audiência\nCNJ: {CNJ_B}\nPASTA: A3"
    assert saida.loc[2, "CNJ"] == ""
    assert saida.loc[2, "PASTA"] == ""


def test_linked_row_clears_the_migration_sentinel() -> None:
    agenda = _agenda([_linha(CNJ_A, MIGRACAO, "A1")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A2")])},
        _config(),
        allow_migrated=True,
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "VINCULA?"] == VINCULA_POR_CNJ
    assert saida.loc[0, "PROTOCOLO"] == ""


def test_linked_row_with_migration_is_not_moved_to_the_description() -> None:
    agenda = _agenda([_linha(CNJ_A, MIGRACAO, "A1", descricao="Audiência")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": _processos([_processo(CNJ_A, "P2", "A2")])},
        _config(),
        allow_migrated=True,
        single_field=True,
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "PROTOCOLO"] == ""
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência\nPASTA: A1"


def test_migration_in_processos_is_never_matched_as_protocol() -> None:
    agenda = _agenda([_linha("", MIGRACAO, "", descricao="Audiência")])
    processos = _processos([_processo("", MIGRACAO, "")])

    result = link_agenda(
        {"Agenda": agenda},
        {"Processos": processos},
        _config(),
        allow_migrated=True,
    )

    saida = result.sheets["Agenda"]
    assert saida.loc[0, "VINCULA?"] == SEM_VINCULO
    assert saida.loc[0, "PROTOCOLO"] == MIGRACAO
    assert saida.loc[0, "DESCRIÇÃO"] == "Audiência"


def test_financeiro_overwrites_a_name_column_without_space_in_the_header() -> None:
    financeiro = _financeiro([_fin_linha(nome="Cliente Alfa")])
    financeiro["VINCULA?"] = ["antigo"]
    financeiro["VINCULA(POR NOME)?"] = ["antigo"]

    result = link_financeiro(
        {"Fin": financeiro},
        None,
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    saida = result.sheets["Fin"]
    assert list(saida.columns).count("VINCULA (POR NOME)?") == 0
    assert list(saida.columns).count("VINCULA(POR NOME)?") == 1
    assert saida["VINCULA(POR NOME)?"].tolist() == [SIM]
    assert saida["VINCULA?"].tolist() == ["antigo"]


def test_financeiro_preserves_other_sheets_and_columns() -> None:
    financeiro = _financeiro([_fin_linha(nome="Cliente Alfa")])
    financeiro["EXTRA"] = ["livre"]
    outra = pd.DataFrame({"QUALQUER": ["x"]})

    result = link_financeiro(
        {"Fin": financeiro, "Outra": outra},
        None,
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    assert result.target_sheet == "Fin"
    assert result.sheets["Outra"].equals(outra)
    assert "EXTRA" in result.sheets["Fin"].columns


def test_financeiro_invalid_cnj_stops_everything() -> None:
    financeiro = _financeiro([_fin_linha("abc")])

    with pytest.raises(InvalidCnjError):
        link_financeiro(
            {"Fin": financeiro},
            {"Processos": _processos([_processo(CNJ_A, "P1", "A1")])},
            None,
            _config(),
        )


def test_financeiro_with_only_clientes_skips_cnj_validation() -> None:
    financeiro = _financeiro([_fin_linha("abc")])

    result = link_financeiro(
        {"Fin": financeiro},
        None,
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    assert result.sheets["Fin"]["VINCULA (POR NOME)?"].tolist() == [SIM]


def test_financeiro_requires_processos_or_clientes() -> None:
    with pytest.raises(ValueError):
        link_financeiro({"Fin": _financeiro([_fin_linha()])}, None, None, _config())


def test_financeiro_columns_go_after_the_standard_block_and_before_extras() -> None:
    financeiro = _financeiro([_fin_linha(nome="Cliente Alfa")])
    financeiro["EXTRA"] = ["livre"]

    result = link_financeiro(
        {"Fin": financeiro},
        None,
        _clientes(["Cliente Alfa"]),
        _config(),
    )

    assert list(result.sheets["Fin"].columns) == [
        "DESCRIÇÃO",
        "PROCESSO",
        "PROTOCOLO",
        "PASTA",
        "NOME",
        "VINCULA (POR NOME)?",
        "EXTRA",
    ]


def test_financeiro_both_columns_keep_the_order() -> None:
    financeiro = _financeiro([_fin_linha(nome="Cliente Alfa")])
    financeiro["EXTRA"] = ["livre"]

    result = link_financeiro(
        {"Fin": financeiro},
        {"Processos": _processos([_processo(nome="Cliente Alfa")])},
        None,
        _config(),
    )

    assert list(result.sheets["Fin"].columns) == [
        "DESCRIÇÃO",
        "PROCESSO",
        "PROTOCOLO",
        "PASTA",
        "NOME",
        "VINCULA?",
        "VINCULA (POR NOME)?",
        "EXTRA",
    ]
