"""Regra pura de vinculação entre AGENDA, PROCESSOS, FINANCEIRO e CLIENTES.

Entrada: abas das planilhas e o mapa de cabeçalhos padrão.
Saída: AGENDA e/ou FINANCEIRO com as colunas de vínculo.
Erros: ``InvalidCnjError`` para CNJ fora do padrão, ``MissingColumnsError``
quando falta coluna obrigatória e ``AlreadyProcessedError`` na reexecução.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

import pandas as pd

VINCULA_POR_CNJ = "VINCULA POR CNJ"
VINCULA_POR_PASTA = "VINCULA POR PASTA"
VINCULA_POR_PROTOCOLO = "VINCULA POR PROTOCOLO"
SEM_VINCULO = "NÃO vincula, apenas processo consultivo"
MIGRACAO = "MIGRAÇÃO"
SIM = "SIM"
NAO = "NÃO"

_NOME_NA_DESCRICAO = "NOME DO CLIENTE"

# A comparação é bruta; a validação aceita exatamente a máscara canônica ou os
# 20 dígitos contínuos. Qualquer outra forma é erro e interrompe a execução.
_CNJ_MASKED = re.compile(r"[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}")
_CNJ_RAW = re.compile(r"[0-9]{20}")


class ConfigError(ValueError):
    """Indica um mapa de cabeçalhos ausente ou malformado."""


class MissingColumnsError(ValueError):
    """Indica que nenhuma aba tem todas as colunas obrigatórias."""


class AlreadyProcessedError(ValueError):
    """Indica MIGRAÇÃO na AGENDA e pede confirmação antes de repetir."""

    def __init__(self) -> None:
        super().__init__(
            "A coluna de protocolo da AGENDA já contém MIGRAÇÃO, sinal de que "
            "a planilha já foi processada. Se continuar, o VINCULA? será "
            "recalculado sem acrescentar o protocolo à descrição."
        )


@dataclass(frozen=True, slots=True)
class CnjProblem:
    """Um valor de CNJ fora do padrão, com a posição para o usuário corrigir."""

    source: str
    sheet: str
    row: int
    column: str
    value: str


class InvalidCnjError(ValueError):
    """Lista os CNJs inválidos e interrompe tudo antes de qualquer gravação."""

    def __init__(self, problems: Sequence[CnjProblem], limit: int = 20) -> None:
        self.problems = tuple(problems)
        shown = self.problems[:limit]
        lines = [
            f"{problem.source} · {problem.sheet} · linha {problem.row} · "
            f"{problem.column}: {problem.value}"
            for problem in shown
        ]
        remaining = len(self.problems) - len(shown)
        if remaining > 0:
            lines.append(f"... e mais {remaining} caso(s).")
        super().__init__(
            "CNJ fora do padrão (máscara NNNNNNN-NN.NNNN.N.NN.NNNN ou 20 "
            "dígitos). Nada foi gravado; corrija e execute de novo:\n"
            + "\n".join(lines)
        )


@dataclass(frozen=True, slots=True)
class SheetSpec:
    """Cabeçalhos padrão e campos usados por uma planilha do fluxo."""

    name: str
    standard: tuple[str, ...]
    fields: Mapping[str, str]
    required: tuple[str, ...]
    description_separator: str = "\n"


@dataclass(frozen=True, slots=True)
class LinkConfig:
    """Mapa completo dos cabeçalhos padrão carregado do JSON."""

    sheets: Mapping[str, SheetSpec]
    vincula_column: str
    vincula_nome_column: str

    def sheet(self, name: str) -> SheetSpec:
        """Devolve a especificação de uma planilha ou falha com mensagem clara."""
        try:
            return self.sheets[name]
        except KeyError as error:
            raise ConfigError(f"Cabeçalho padrão ausente para {name}.") from error


@dataclass(frozen=True, slots=True)
class LinkStats:
    """Contagens da vinculação da AGENDA para o log e para o resumo."""

    rows: int
    by_cnj: int
    by_pasta: int
    by_protocolo: int
    unlinked: int
    agenda_masked: int
    agenda_raw: int
    processos_masked: int
    processos_raw: int

    @property
    def linked(self) -> int:
        """Devolve quantas linhas da AGENDA encontraram algum vínculo."""
        return self.by_cnj + self.by_pasta + self.by_protocolo


@dataclass(frozen=True, slots=True)
class FinanceiroStats:
    """Contagens da vinculação do FINANCEIRO para o log e para o resumo."""

    rows: int
    by_cnj: int
    by_pasta: int
    by_protocolo: int
    unlinked: int
    name_yes: int
    name_no: int
    numbers_tested: bool
    financeiro_masked: int
    financeiro_raw: int
    processos_masked: int
    processos_raw: int

    @property
    def linked(self) -> int:
        """Devolve quantas linhas do FINANCEIRO encontraram vínculo numérico."""
        return self.by_cnj + self.by_pasta + self.by_protocolo


@dataclass(frozen=True, slots=True)
class LinkResult:
    """Livro transformado com a aba alvo e as demais preservadas."""

    sheets: dict[str, pd.DataFrame]
    target_sheet: str
    stats: LinkStats | FinanceiroStats


def fold_header(value: object) -> str:
    """Dobra caixa, acento e espaço para comparar apenas cabeçalhos e valores."""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.casefold().split())


def header_key(value: object) -> str:
    """Dobra o cabeçalho e remove todos os espaços para casar variações."""
    return "".join(fold_header(value).split())


def cell_text(value: object) -> str:
    """Converte uma célula em texto sem tratar célula vazia como ``nan``."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        if pd.isna(value):
            return ""
    except TypeError, ValueError:
        pass
    return str(value)


def cnj_style(value: str) -> str | None:
    """Devolve ``mascarado``, ``cru`` ou ``None`` quando o valor é inválido."""
    if _CNJ_MASKED.fullmatch(value):
        return "mascarado"
    if _CNJ_RAW.fullmatch(value):
        return "cru"
    return None


def column_map(frame: pd.DataFrame) -> dict[str, str]:
    """Mapeia o cabeçalho dobrado para o rótulo real da primeira ocorrência."""
    mapping: dict[str, str] = {}
    for column in frame.columns:
        mapping.setdefault(header_key(column), str(column))
    return mapping


def find_target_sheet(
    sheets: Mapping[str, pd.DataFrame],
    spec: SheetSpec,
    label: str,
) -> tuple[str, pd.DataFrame]:
    """Acha a primeira aba com todas as colunas obrigatórias da planilha."""
    if not sheets:
        raise MissingColumnsError(f"A planilha {label} não tem abas.")

    missing: dict[str, list[str]] = {}
    for name, frame in sheets.items():
        columns = column_map(frame)
        absent = [
            spec.fields[key]
            for key in spec.required
            if header_key(spec.fields[key]) not in columns
        ]
        if not absent:
            return name, frame
        missing[name] = absent

    detail = " | ".join(
        f"{name}: {', '.join(values)}" for name, values in missing.items()
    )
    raise MissingColumnsError(
        f"Nenhuma aba de {label} tem as colunas padrão. Faltando — {detail}."
    )


def has_migration(frame: pd.DataFrame, column: str) -> bool:
    """Diz se a coluna de protocolo já tem ``MIGRAÇÃO`` em alguma linha."""
    return any(_is_migration(cell_text(value)) for value in frame[column].tolist())


def link_agenda(
    agenda_sheets: Mapping[str, pd.DataFrame],
    processos_sheets: Mapping[str, pd.DataFrame],
    config: LinkConfig,
    *,
    allow_migrated: bool = False,
    single_field: bool = False,
    agenda_name: str = "AGENDA",
    processos_name: str = "PROCESSOS",
) -> LinkResult:
    """Cria ``VINCULA?`` e trata o protocolo sem vínculo, sem gravar nada.

    A comparação usa o valor bruto das três chaves, na prioridade CNJ → PASTA →
    PROTOCOLO. ``single_field`` move os campos que não venceram para o fim da
    descrição e esvazia as colunas deles. ``allow_migrated`` só existe para a
    reexecução confirmada pelo usuário: nela o ``MIGRAÇÃO`` já está no campo,
    não entra na comparação e é limpo quando a linha vincula.
    """
    agenda_spec = config.sheet("AGENDA")
    processos_spec = config.sheet("PROCESSOS")
    agenda_sheet, agenda = find_target_sheet(agenda_sheets, agenda_spec, agenda_name)
    processos_sheet, processos = find_target_sheet(
        processos_sheets,
        processos_spec,
        processos_name,
    )

    agenda_columns = column_map(agenda)
    processos_columns = column_map(processos)
    description_col = agenda_columns[header_key(agenda_spec.fields["descricao"])]
    agenda_cnj_col = agenda_columns[header_key(agenda_spec.fields["cnj"])]
    agenda_protocol_col = agenda_columns[header_key(agenda_spec.fields["protocolo"])]
    agenda_pasta_col = agenda_columns[header_key(agenda_spec.fields["pasta"])]
    processos_cnj_col = processos_columns[header_key(processos_spec.fields["cnj"])]
    processos_protocol_col = processos_columns[
        header_key(processos_spec.fields["protocolo"])
    ]
    processos_pasta_col = processos_columns[header_key(processos_spec.fields["pasta"])]

    problems = [
        *_validate_cnj(agenda, agenda_cnj_col, agenda_name, agenda_sheet),
        *_validate_cnj(
            processos,
            processos_cnj_col,
            processos_name,
            processos_sheet,
        ),
    ]
    if problems:
        raise InvalidCnjError(problems)

    if not allow_migrated and has_migration(agenda, agenda_protocol_col):
        raise AlreadyProcessedError()

    processos_cnjs = _values(processos, processos_cnj_col)
    processos_pastas = _values(processos, processos_pasta_col)
    processos_protocolos = {
        value
        for value in _values(processos, processos_protocol_col)
        if not _is_migration(value)
    }

    descriptions = [cell_text(value) for value in agenda[description_col].tolist()]
    protocols = [cell_text(value) for value in agenda[agenda_protocol_col].tolist()]
    cnjs = [cell_text(value) for value in agenda[agenda_cnj_col].tolist()]
    pastas = [cell_text(value) for value in agenda[agenda_pasta_col].tolist()]

    new_descriptions: list[str] = []
    new_protocols = list(protocols)
    new_cnjs = list(cnjs)
    new_pastas = list(pastas)
    vincula: list[str] = []
    by_cnj = by_pasta = by_protocolo = 0

    for index, (cnj, pasta, protocol, description) in enumerate(
        zip(cnjs, pastas, protocols, descriptions, strict=True)
    ):
        via: str | None = None
        if cnj.strip() and cnj in processos_cnjs:
            via = "CNJ"
            by_cnj += 1
        elif pasta.strip() and pasta in processos_pastas:
            via = "PASTA"
            by_pasta += 1
        elif (
            protocol.strip()
            and not _is_migration(protocol)
            and protocol in processos_protocolos
        ):
            via = "PROTOCOLO"
            by_protocolo += 1

        if via is not None:
            vincula.append(f"VINCULA POR {via}")
            new_description = description
            if _is_migration(protocol):
                new_protocols[index] = ""
            if single_field:
                new_description = _move_other_fields(
                    new_description,
                    [
                        ("cnj", cnj, agenda_cnj_col),
                        ("pasta", pasta, agenda_pasta_col),
                        ("protocolo", protocol, agenda_protocol_col),
                    ],
                    winner=via.lower(),
                    separator=agenda_spec.description_separator,
                )
                if via != "CNJ":
                    new_cnjs[index] = ""
                if via != "PASTA":
                    new_pastas[index] = ""
                if via != "PROTOCOLO":
                    new_protocols[index] = ""
            new_descriptions.append(new_description)
            continue

        vincula.append(SEM_VINCULO)
        new_protocols[index] = MIGRACAO
        if allow_migrated or not protocol.strip():
            new_descriptions.append(description)
            continue

        line = f"{agenda_protocol_col}: {protocol}"
        new_descriptions.append(
            _append_line(description, line, agenda_spec.description_separator)
        )

    result = agenda.copy(deep=True)
    result[description_col] = new_descriptions
    result[agenda_cnj_col] = new_cnjs
    result[agenda_pasta_col] = new_pastas
    result[agenda_protocol_col] = new_protocols
    result = _put_columns(
        result,
        [(config.vincula_column, vincula)],
        agenda_spec.standard,
    )

    agenda_masked, agenda_raw = _styles(agenda, agenda_cnj_col)
    processos_masked, processos_raw = _styles(processos, processos_cnj_col)
    stats = LinkStats(
        rows=len(agenda),
        by_cnj=by_cnj,
        by_pasta=by_pasta,
        by_protocolo=by_protocolo,
        unlinked=len(agenda) - by_cnj - by_pasta - by_protocolo,
        agenda_masked=agenda_masked,
        agenda_raw=agenda_raw,
        processos_masked=processos_masked,
        processos_raw=processos_raw,
    )

    sheets = dict(agenda_sheets)
    sheets[agenda_sheet] = result
    return LinkResult(sheets=sheets, target_sheet=agenda_sheet, stats=stats)


def link_financeiro(
    financeiro_sheets: Mapping[str, pd.DataFrame],
    processos_sheets: Mapping[str, pd.DataFrame] | None,
    clientes_sheets: Mapping[str, pd.DataFrame] | None,
    config: LinkConfig,
    *,
    name_in_description: bool = False,
    single_field: bool = False,
    financeiro_name: str = "FINANCEIRO",
    processos_name: str = "PROCESSOS",
    clientes_name: str = "CLIENTES",
) -> LinkResult:
    """Cria ``VINCULA?`` e ``VINCULA (POR NOME)?`` no FINANCEIRO.

    Com PROCESSOS, testa CNJ → PASTA → PROTOCOLO e o nome. Só com CLIENTES,
    testa apenas o nome e não cria nem altera ``VINCULA?``. ``single_field``
    move os campos numéricos que não venceram para o fim da descrição;
    ``name_in_description`` prefixa o nome sem vínculo.
    """
    if processos_sheets is None and clientes_sheets is None:
        raise ValueError("Selecione PROCESSOS ou CLIENTES para o FINANCEIRO.")

    financeiro_spec = config.sheet("FINANCEIRO")
    numbers_tested = processos_sheets is not None
    required = financeiro_spec.required if numbers_tested else ("descricao", "nome")
    spec = replace(financeiro_spec, required=required)
    financeiro_sheet, financeiro = find_target_sheet(
        financeiro_sheets,
        spec,
        financeiro_name,
    )

    financeiro_columns = column_map(financeiro)
    description_col = financeiro_columns[
        header_key(financeiro_spec.fields["descricao"])
    ]
    nome_col = financeiro_columns[header_key(financeiro_spec.fields["nome"])]

    if numbers_tested:
        processos_spec = config.sheet("PROCESSOS")
        processos_sheet, processos = find_target_sheet(
            processos_sheets,
            processos_spec,
            processos_name,
        )
        processos_columns = column_map(processos)
        processos_cnj_col = processos_columns[header_key(processos_spec.fields["cnj"])]
        processos_protocol_col = processos_columns[
            header_key(processos_spec.fields["protocolo"])
        ]
        processos_pasta_col = processos_columns[
            header_key(processos_spec.fields["pasta"])
        ]
        financeiro_cnj_col = financeiro_columns[
            header_key(financeiro_spec.fields["cnj"])
        ]
        financeiro_protocol_col = financeiro_columns[
            header_key(financeiro_spec.fields["protocolo"])
        ]
        financeiro_pasta_col = financeiro_columns[
            header_key(financeiro_spec.fields["pasta"])
        ]

        problems = [
            *_validate_cnj(
                financeiro,
                financeiro_cnj_col,
                financeiro_name,
                financeiro_sheet,
            ),
            *_validate_cnj(
                processos,
                processos_cnj_col,
                processos_name,
                processos_sheet,
            ),
        ]
        if problems:
            raise InvalidCnjError(problems)

        processos_cnjs = _values(processos, processos_cnj_col)
        processos_pastas = _values(processos, processos_pasta_col)
        processos_protocolos = {
            value
            for value in _values(processos, processos_protocol_col)
            if not _is_migration(value)
        }
    else:
        processos_cnjs = processos_pastas = processos_protocolos = set()

    names: set[str] = set()
    if processos_sheets is not None:
        names.update(
            _names(
                processos,
                processos_columns[header_key(processos_spec.fields["nome"])],
                split=True,
            )
        )
    if clientes_sheets is not None:
        clientes_spec = config.sheet("CLIENTES")
        clientes_sheet, clientes = find_target_sheet(
            clientes_sheets,
            clientes_spec,
            clientes_name,
        )
        clientes_columns = column_map(clientes)
        names.update(
            _names(
                clientes,
                clientes_columns[header_key(clientes_spec.fields["nome"])],
                split=False,
            )
        )

    descriptions = [cell_text(value) for value in financeiro[description_col].tolist()]
    nomes = [cell_text(value) for value in financeiro[nome_col].tolist()]
    if numbers_tested:
        cnjs = [cell_text(value) for value in financeiro[financeiro_cnj_col].tolist()]
        pastas = [
            cell_text(value) for value in financeiro[financeiro_pasta_col].tolist()
        ]
        protocols = [
            cell_text(value) for value in financeiro[financeiro_protocol_col].tolist()
        ]
        new_cnjs = list(cnjs)
        new_pastas = list(pastas)
        new_protocols = list(protocols)
    else:
        cnjs = pastas = protocols = [""] * len(financeiro)
        new_cnjs = new_pastas = new_protocols = None

    new_descriptions: list[str] = []
    vincula: list[str] = []
    vincula_nome: list[str] = []
    by_cnj = by_pasta = by_protocolo = 0

    for index, (cnj, pasta, protocol, nome, description) in enumerate(
        zip(cnjs, pastas, protocols, nomes, descriptions, strict=True)
    ):
        name_ok = bool(nome.strip()) and nome in names
        vincula_nome.append(SIM if name_ok else NAO)

        via: str | None = None
        if numbers_tested:
            if cnj.strip() and cnj in processos_cnjs:
                via = "CNJ"
                by_cnj += 1
            elif pasta.strip() and pasta in processos_pastas:
                via = "PASTA"
                by_pasta += 1
            elif (
                protocol.strip()
                and not _is_migration(protocol)
                and protocol in processos_protocolos
            ):
                via = "PROTOCOLO"
                by_protocolo += 1
            vincula.append(f"VINCULA POR {via}" if via else SEM_VINCULO)

        new_description = description
        if name_in_description and not name_ok and nome:
            new_description = _prefix_line(
                new_description,
                f"{_NOME_NA_DESCRICAO}: {nome}",
                financeiro_spec.description_separator,
            )

        if numbers_tested and single_field and via is not None:
            new_description = _move_other_fields(
                new_description,
                [
                    ("cnj", cnj, financeiro_cnj_col),
                    ("pasta", pasta, financeiro_pasta_col),
                    ("protocolo", protocol, financeiro_protocol_col),
                ],
                winner=via.lower(),
                separator=financeiro_spec.description_separator,
            )
            if via != "CNJ":
                new_cnjs[index] = ""
            if via != "PASTA":
                new_pastas[index] = ""
            if via != "PROTOCOLO":
                new_protocols[index] = ""
        elif numbers_tested and via is not None and _is_migration(protocol):
            new_protocols[index] = ""

        new_descriptions.append(new_description)

    result = financeiro.copy(deep=True)
    result[description_col] = new_descriptions
    if numbers_tested:
        result[financeiro_cnj_col] = new_cnjs
        result[financeiro_pasta_col] = new_pastas
        result[financeiro_protocol_col] = new_protocols

    columns: list[tuple[str, Sequence[object]]] = []
    if numbers_tested:
        columns.append((config.vincula_column, vincula))
    columns.append((config.vincula_nome_column, vincula_nome))
    result = _put_columns(
        result,
        columns,
        financeiro_spec.standard,
        after=(config.vincula_column,),
    )

    if numbers_tested:
        financeiro_masked, financeiro_raw = _styles(financeiro, financeiro_cnj_col)
        processos_masked, processos_raw = _styles(processos, processos_cnj_col)
    else:
        financeiro_masked = financeiro_raw = 0
        processos_masked = processos_raw = 0

    linked = by_cnj + by_pasta + by_protocolo
    stats = FinanceiroStats(
        rows=len(financeiro),
        by_cnj=by_cnj,
        by_pasta=by_pasta,
        by_protocolo=by_protocolo,
        unlinked=len(financeiro) - linked if numbers_tested else len(financeiro),
        name_yes=vincula_nome.count(SIM),
        name_no=vincula_nome.count(NAO),
        numbers_tested=numbers_tested,
        financeiro_masked=financeiro_masked,
        financeiro_raw=financeiro_raw,
        processos_masked=processos_masked,
        processos_raw=processos_raw,
    )

    sheets = dict(financeiro_sheets)
    sheets[financeiro_sheet] = result
    return LinkResult(sheets=sheets, target_sheet=financeiro_sheet, stats=stats)


def _values(frame: pd.DataFrame, column: str) -> set[str]:
    """Devolve os valores brutos não vazios de uma coluna."""
    return {
        text for value in frame[column].tolist() if (text := cell_text(value)).strip()
    }


def _names(frame: pd.DataFrame, column: str, *, split: bool) -> set[str]:
    """Monta o conjunto de nomes, com split cru por ``;`` quando pedido."""
    names: set[str] = set()
    for value in frame[column].tolist():
        text = cell_text(value)
        if not text.strip():
            continue
        if split:
            names.update(piece for piece in text.split(";") if piece.strip())
        else:
            names.add(text)
    return names


def _is_migration(value: str) -> bool:
    """Diz se o valor é a sentinela ``MIGRAÇÃO``, que nunca é comparada."""
    return bool(value.strip()) and fold_header(value) == fold_header(MIGRACAO)


def _append_line(description: str, line: str, separator: str) -> str:
    """Acrescenta uma linha ao fim da descrição, sem separador sobrando."""
    return f"{description}{separator}{line}" if description else line


def _prefix_line(description: str, line: str, separator: str) -> str:
    """Prefixa uma linha na descrição, sem separador sobrando."""
    return f"{line}{separator}{description}" if description else line


def _move_other_fields(
    description: str,
    fields: Sequence[tuple[str, str, str]],
    *,
    winner: str,
    separator: str,
) -> str:
    """Move para a descrição os campos que não venceram o vínculo."""
    result = description
    for key, value, header in fields:
        if key == winner:
            continue
        if not value.strip() or _is_migration(value):
            continue
        result = _append_line(result, f"{header}: {value}", separator)
    return result


def _validate_cnj(
    frame: pd.DataFrame,
    column: str,
    source: str,
    sheet: str,
) -> list[CnjProblem]:
    """Lista todos os CNJs preenchidos que não seguem os dois padrões."""
    problems: list[CnjProblem] = []
    for position, value in enumerate(frame[column].tolist()):
        text = cell_text(value)
        if not text.strip() or cnj_style(text) is not None:
            continue
        problems.append(
            CnjProblem(
                source=source,
                sheet=sheet,
                row=position + 2,
                column=column,
                value=text,
            )
        )
    return problems


def _styles(frame: pd.DataFrame, column: str) -> tuple[int, int]:
    """Conta CNJs mascarados e crus preenchidos em uma coluna."""
    masked = raw = 0
    for value in frame[column].tolist():
        text = cell_text(value)
        style = cnj_style(text) if text.strip() else None
        if style == "mascarado":
            masked += 1
        elif style == "cru":
            raw += 1
    return masked, raw


def _put_columns(
    frame: pd.DataFrame,
    columns: Sequence[tuple[str, Sequence[object]]],
    standard: Sequence[str],
    *,
    after: Sequence[str] = (),
) -> pd.DataFrame:
    """Sobrescreve no lugar ou insere o bloco depois do bloco padrão.

    ``after`` permite ancorar a inserção depois de uma coluna existente que não
    faz parte do bloco padrão, como ``VINCULA?`` antes de ``VINCULA (POR NOME)?``.
    """
    existing = column_map(frame)
    anchors = {header_key(value) for value in standard}
    anchors.update(header_key(value) for value in after)
    positions = [
        index
        for index, column in enumerate(frame.columns)
        if header_key(column) in anchors
    ]
    last = max(positions) if positions else len(frame.columns) - 1

    for name, values in columns:
        current = existing.get(header_key(name))
        if current is not None:
            frame[current] = list(values)
            last = list(frame.columns).index(current)
            continue
        frame.insert(last + 1, name, list(values))
        last += 1

    return frame
