"""Generate a local 1k-row fictitious sample; nothing here is versioned."""

import csv
from itertools import cycle
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "samples"
CSV_SAMPLE = SAMPLE_DIR / "base_ficticia_1k.csv"
XLSX_SAMPLE = SAMPLE_DIR / "base_ficticia_1k.xlsx"

ROWS = 1000
CITIES = (
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Recife",
)
FIELDS = ("id", "cnj", "nome", "observacao", "valor", "cidade", "email")


def build_rows() -> list[dict[str, str]]:
    """Return fictitious rows with zeros, CNJ-like text, emojis and breaks."""
    cities = cycle(CITIES)
    return [
        {
            "id": f"{number:06d}",
            # Ano 0000 deixa explícito que a numeração não é um CNJ real.
            "cnj": f"{number:07d}-{number % 100:02d}.0000.0.00.{number % 10000:04d}",
            "nome": f"Pessoa Fictícia {number} 🙂",
            "observacao": f"Linha {number}\nsegunda linha ✅",
            "valor": f"{number * 37 % 1_000_000:06d}",
            "cidade": next(cities),
            "email": f"pessoa{number}@exemplo.test",
        }
        for number in range(1, ROWS + 1)
    ]


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_SAMPLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(build_rows())

    frame = pd.read_csv(CSV_SAMPLE, dtype=str)
    frame.to_excel(XLSX_SAMPLE, index=False)

    print(f"{len(frame)} linhas -> {CSV_SAMPLE} (fora do Git)")
    print(f"{len(frame)} linhas -> {XLSX_SAMPLE} (fora do Git)")


if __name__ == "__main__":
    main()
