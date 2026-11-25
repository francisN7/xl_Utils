#!/usr/bin/env python3
"""Confere a saúde da documentação, sem dependências (Python >= 3.10).

Nasceu do modelo da skill ``project-context-init``; aqui não há gêmeo ``.mjs``.

1. links relativos e ``<img src>`` entre ``.md`` (ignora http(s), mailto,
   #âncora e blocos de código);
2. orçamento de linhas: AGENTS.md, CURRENT.md e specs de sessão;
3. ``{{PLACEHOLDER}}`` esquecido em qualquer .md (exceto
   docs/sessions/_TEMPLATE.md);
4. histórico disfarçado de referência ("## Cobertura da SXX") em
   docs/reference/.

Escopo: *.md na raiz e em docs/. Sem checagem de link nos históricos:
CHANGELOG.md, docs/releases/, o corpo dos ADRs e docs/sessions/ (a spec cita
arquivos que ainda vão existir). O índice docs/adr/README.md é checado.

Uso: python3 scripts/check_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".temp",
    "backups",
    "build",
    "dist",
    "node_modules",
    "output",
    "tmp",
}
SKIP_LINKS = ["CHANGELOG.md", "docs/releases/", "docs/sessions/"]
NO_PLACEHOLDER_CHECK = {"docs/sessions/_TEMPLATE.md"}
BUDGETS = {"AGENTS.md": 100, "docs/state/CURRENT.md": 60}
SESSION_MAX = 90

PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_/]*\}\}")
LINK = re.compile(r"\]\(([^)\s]+)\)")
IMAGE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
FENCE = re.compile(r"^\s*(```|~~~)")
EXTERNAL = re.compile(r"^(https?:|mailto:|#|<)")
REF_HISTORY = re.compile(
    r"^##+\s+(Cobertura da S.+|S\d+[a-z]?\b.*)$", re.IGNORECASE | re.MULTILINE
)

errors: list[str] = []
checked_links = 0


def walk(folder: Path) -> list[Path]:
    files: list[Path] = []
    for entry in sorted(folder.iterdir()):
        if entry.is_dir():
            if entry.name not in SKIP_DIRS:
                files.extend(walk(entry))
        elif entry.name.endswith(".md"):
            files.append(entry)
    return files


def collect() -> list[Path]:
    files = sorted(p for p in ROOT.iterdir() if p.is_file() and p.name.endswith(".md"))
    docs = ROOT / "docs"
    if docs.is_dir():
        files.extend(walk(docs))
    return files


def relative(file: Path) -> str:
    return file.relative_to(ROOT).as_posix()


def read_lines(file: Path) -> list[str]:
    text = file.read_text(encoding="utf-8")
    return re.sub(r"\r?\n$", "", text).split("\n") if text else [""]


def check_links(file: Path) -> None:
    global checked_links
    rel = relative(file)
    if any(rel == skip or rel.startswith(skip) for skip in SKIP_LINKS):
        return
    if rel.startswith("docs/adr/") and rel != "docs/adr/README.md":
        return

    def check_target(target: str, line_number: int) -> None:
        global checked_links
        if EXTERNAL.match(target):
            return
        checked_links += 1
        clean = unquote(target.split("#")[0].split("?")[0])
        if not clean:
            return
        if not (file.parent / clean).exists():
            errors.append(f"{rel}:{line_number} link quebrado -> {target}")

    in_fence = False
    for index, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK.finditer(line):
            check_target(match.group(1), index)
        for match in IMAGE.finditer(line):
            check_target(match.group(1), index)


def check_budget(file: Path) -> None:
    rel = relative(file)
    if rel in BUDGETS:
        lines = len(read_lines(file))
        if lines > BUDGETS[rel]:
            errors.append(f"{rel}: {lines} linhas (máx. {BUDGETS[rel]})")
    if rel.startswith("docs/sessions/") and not rel.endswith("_TEMPLATE.md"):
        lines = len(read_lines(file))
        if lines > SESSION_MAX:
            errors.append(f"{rel}: {lines} linhas (spec máx. {SESSION_MAX})")


def check_placeholders(file: Path) -> None:
    rel = relative(file)
    if rel in NO_PLACEHOLDER_CHECK:
        return
    for index, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
        match = PLACEHOLDER.search(line)
        if match:
            errors.append(f"{rel}:{index} placeholder esquecido -> {match.group(0)}")


def check_reference_history(file: Path) -> None:
    rel = relative(file)
    if not rel.startswith("docs/reference/"):
        return
    for match in REF_HISTORY.finditer(file.read_text(encoding="utf-8")):
        errors.append(f'{rel}: heading de histórico -> "{match.group(0).strip()}"')


def main() -> int:
    files = collect()
    for file in files:
        check_links(file)
        check_budget(file)
        check_placeholders(file)
        check_reference_history(file)

    if errors:
        print(
            f"docs: {len(errors)} problema(s) em {len(files)} arquivos", file=sys.stderr
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    opening = sum(
        (ROOT / name).stat().st_size
        for name in ("AGENTS.md", "docs/state/CURRENT.md")
        if (ROOT / name).exists()
    )
    print(
        f"docs ok: {len(files)} arquivos, {checked_links} links; "
        f"abertura (AGENTS+CURRENT) ≈ {int(opening / 4 + 0.5)} tokens"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
