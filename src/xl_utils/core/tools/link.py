"""Regra pura de vinculação entre AGENDA e PROCESSOS.

Entrada: abas das duas planilhas e o mapa de cabeçalhos padrão.
Saída: AGENDA com ``VINCULA?`` e o protocolo preservado na descrição.
Erros: ``InvalidCnjError`` para CNJ fora do padrão, ``MissingColumnsError``
quando falta coluna obrigatória e ``AlreadyProcessedError`` na reexecução.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import pandas as pd

VINCULA_POR_CNJ = "VINCULA POR CNJ"
VINCULA_POR_PASTA = "VINCULA POR PASTA"
VINCULA_POR_PROTOCOLO = "VINCULA POR PROTOCOLO"
SEM_VINCULO = "NÃO vincula, apenas processo consultivo"
MIGRACAO = "MIGRAÇÃO"

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
    """Contagens da vinculação para o log e para o resumo da página."""

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
class LinkResult:
    """Livro da AGENDA com a aba alvo transformada e as demais preservadas."""

    sheets: dict[str, pd.DataFrame]
    target_sheet: str
    stats: LinkStats


def fold_header(value: object) -> str:
    """Dobra caixa, acento e espaço para comparar apenas cabeçalhos."""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.casefold().split())


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
        mapping.setdefault(fold_header(column), str(column))
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
            if fold_header(spec.fields[key]) not in columns
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
    target = fold_header(MIGRACAO)
    return any(
        fold_header(cell_text(value)) == target for value in frame[column].tolist()
    )


def link_agenda(
    agenda_sheets: Mapping[str, pd.DataFrame],
    processos_sheets: Mapping[str, pd.DataFrame],
    config: LinkConfig,
    *,
    allow_migrated: bool = False,
    agenda_name: str = "AGENDA",
    processos_name: str = "PROCESSOS",
) -> LinkResult:
    """Cria ``VINCULA?`` e trata o protocolo sem vínculo, sem gravar nada.

    A comparação usa o valor bruto das três chaves, na prioridade CNJ → PASTA →
    PROTOCOLO. ``allow_migrated`` só existe para a reexecução confirmada pelo
    usuário: nela o ``MIGRAÇÃO`` já está no campo e não entra na descrição.
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
    description_col = agenda_columns[fold_header(agenda_spec.fields["descricao"])]
    agenda_cnj_col = agenda_columns[fold_header(agenda_spec.fields["cnj"])]
    agenda_protocol_col = agenda_columns[fold_header(agenda_spec.fields["protocolo"])]
    agenda_pasta_col = agenda_columns[fold_header(agenda_spec.fields["pasta"])]
    processos_cnj_col = processos_columns[fold_header(processos_spec.fields["cnj"])]
    processos_protocol_col = processos_columns[
        fold_header(processos_spec.fields["protocolo"])
    ]
    processos_pasta_col = processos_columns[fold_header(processos_spec.fields["pasta"])]

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
    processos_protocolos = _values(processos, processos_protocol_col)

    descriptions = [cell_text(value) for value in agenda[description_col].tolist()]
    protocols = [cell_text(value) for value in agenda[agenda_protocol_col].tolist()]
    cnjs = [cell_text(value) for value in agenda[agenda_cnj_col].tolist()]
    pastas = [cell_text(value) for value in agenda[agenda_pasta_col].tolist()]

    new_descriptions: list[str] = []
    new_protocols: list[str] = []
    vincula: list[str] = []
    by_cnj = by_pasta = by_protocolo = 0

    for cnj, pasta, protocol, description in zip(
        cnjs,
        pastas,
        protocols,
        descriptions,
        strict=True,
    ):
        via: str | None = None
        if cnj.strip() and cnj in processos_cnjs:
            via = "CNJ"
            by_cnj += 1
        elif pasta.strip() and pasta in processos_pastas:
            via = "PASTA"
            by_pasta += 1
        elif protocol.strip() and protocol in processos_protocolos:
            via = "PROTOCOLO"
            by_protocolo += 1

        if via is not None:
            vincula.append(f"VINCULA POR {via}")
            new_descriptions.append(description)
            new_protocols.append(protocol)
            continue

        vincula.append(SEM_VINCULO)
        new_protocols.append(MIGRACAO)
        if allow_migrated or not protocol.strip():
            new_descriptions.append(description)
            continue

        line = f"{agenda_protocol_col}: {protocol}"
        new_descriptions.append(
            f"{description}{agenda_spec.description_separator}{line}"
            if description
            else line
        )

    result = agenda.copy(deep=True)
    result[description_col] = new_descriptions
    result[agenda_protocol_col] = new_protocols
    result = _put_column(
        result,
        config.vincula_column,
        vincula,
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


def _values(frame: pd.DataFrame, column: str) -> set[str]:
    """Devolve os valores brutos não vazios de uma coluna."""
    return {
        text for value in frame[column].tolist() if (text := cell_text(value)).strip()
    }


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


def _put_column(
    frame: pd.DataFrame,
    name: str,
    values: Sequence[object],
    standard: Sequence[str],
) -> pd.DataFrame:
    """Sobrescreve a coluna no lugar ou insere após o bloco padrão."""
    existing = column_map(frame).get(fold_header(name))
    if existing is not None:
        frame[existing] = list(values)
        return frame

    standard_keys = {fold_header(value) for value in standard}
    positions = [
        index
        for index, column in enumerate(frame.columns)
        if fold_header(column) in standard_keys
    ]
    position = max(positions) + 1 if positions else len(frame.columns)
    frame.insert(position, name, list(values))
    return frame
