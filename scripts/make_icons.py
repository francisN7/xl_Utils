"""Gera os conceitos de ícone do xl_Utils na paleta Dracula.

Uso:
    uv run python scripts/make_icons.py                          # conceitos
    uv run python scripts/make_icons.py --pick conceito_2a_x_planilha  # ícone final
"""

from __future__ import annotations

import argparse
import struct
from collections.abc import Callable
from io import BytesIO
from math import hypot
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons"
SIZE = 1024
S = 4

BG = (40, 42, 54, 255)
BG_DARK = (33, 34, 44, 255)
PANEL = (68, 71, 90, 255)
PANEL_LIGHT = (98, 114, 164, 255)
PURPLE = (189, 147, 249, 255)
PINK = (255, 121, 198, 255)
CYAN = (139, 233, 253, 255)
GREEN = (80, 250, 123, 255)
GRID = (139, 233, 253, 120)


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (SIZE * S, SIZE * S), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def scaled(values: tuple[float, ...]) -> list[float]:
    return [value * S for value in values]


def rounded(
    draw: ImageDraw.ImageDraw,
    values: tuple[float, ...],
    radius: float,
    **kwargs: object,
) -> None:
    draw.rounded_rectangle(scaled(values), radius=radius * S, **kwargs)


def line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    fill: tuple[int, int, int, int],
    width: float,
) -> None:
    flat = [(x * S, y * S) for x, y in points]
    draw.line(
        [coord for point in flat for coord in point],
        fill=fill,
        width=int(width * S),
        joint="curve",
    )
    radius = width * S / 2
    for x, y in (flat[0], flat[-1]):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def shell(draw: ImageDraw.ImageDraw) -> None:
    rounded(draw, (32, 32, 992, 992), 190, fill=BG, outline=PANEL, width=6)


def save(image: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    image.resize((SIZE, SIZE), Image.LANCZOS).save(path)
    return path


def grid_lines(
    draw: ImageDraw.ImageDraw,
    left: float,
    top: float,
    right: float,
    bottom: float,
    color: tuple[int, int, int, int] = GRID,
) -> None:
    for index in (1, 2):
        x = left + (right - left) * index / 3
        line(draw, [(x, top), (x, bottom)], color, 8)
        y = top + (bottom - top) * index / 3
        line(draw, [(left, y), (right, y)], color, 8)


def concept_grid_x() -> Image.Image:
    image, draw = new_canvas()
    shell(draw)
    left, top, right, bottom = 230, 230, 794, 794
    grid_lines(draw, left, top, right, bottom)
    cell = 188
    rounded(
        draw,
        (left + 2 * cell + 8, top + 8, right - 8, top + cell - 8),
        18,
        fill=PINK,
    )
    for width, color in ((108, BG_DARK), (78, PURPLE)):
        line(draw, [(330, 330), (694, 694)], color, width)
        line(draw, [(694, 330), (330, 694)], color, width)
    return image


def segments(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    count: int,
    gap: float,
    fill: tuple[int, int, int, int],
    width: float,
) -> None:
    x1, y1 = start
    x2, y2 = end
    length = hypot(x2 - x1, y2 - y1)
    piece = (length - gap * (count - 1)) / count
    for index in range(count):
        begin = index * (piece + gap) / length
        finish = begin + piece / length
        line(
            draw,
            [
                (x1 + (x2 - x1) * begin, y1 + (y2 - y1) * begin),
                (x1 + (x2 - x1) * finish, y1 + (y2 - y1) * finish),
            ],
            fill,
            width,
        )


def concept_x_bicolor() -> Image.Image:
    return build_x_bicolor("")


def spreadsheet(draw: ImageDraw.ImageDraw, *, solid: bool, fold: bool) -> None:
    """Mini-planilha decorativa atrás da ponta superior direita do X."""
    left, top, right, bottom = 640, 120, 880, 360
    fill = (68, 71, 90, 215)
    if fold:
        cut = 46
        points = [
            (left, top),
            (right - cut, top),
            (right, top + cut),
            (right, bottom),
            (left, bottom),
        ]
        draw.polygon([(x * S, y * S) for x, y in points], fill=fill)
        draw.polygon(
            [
                ((right - cut) * S, top * S),
                (right * S, (top + cut) * S),
                ((right - cut) * S, (top + cut) * S),
            ],
            fill=(98, 114, 164, 215),
        )
    elif solid:
        rounded(draw, (left, top, right, bottom), 20, fill=fill)
    else:
        rounded(
            draw,
            (left, top, right, bottom),
            20,
            outline=(139, 233, 253, 80),
            width=7,
        )

    inset = 22
    x0, y0 = left + inset, top + inset
    x1, y1 = right - inset, bottom - inset
    columns, rows = 4, 4
    cell_w = (x1 - x0) / columns
    cell_h = (y1 - y0) / rows
    draw.rectangle(scaled((x0, y0, x1, y0 + cell_h)), fill=(139, 233, 253, 60))
    draw.rectangle(scaled((x0, y0, x0 + cell_w, y1)), fill=(139, 233, 253, 30))

    color = (139, 233, 253, 80)
    for index in range(1, columns):
        x = x0 + cell_w * index
        line(draw, [(x, y0), (x, y1)], color, 6)
    for index in range(1, rows):
        y = y0 + cell_h * index
        line(draw, [(x0, y), (x1, y)], color, 6)


def small_sheet(draw: ImageDraw.ImageDraw) -> None:
    """Planilha simplificada e contrastada para 16–32 px."""
    left, top, right, bottom = 610, 90, 900, 390
    rounded(draw, (left, top, right, bottom), 22, fill=(68, 71, 90, 235))
    header = top + (bottom - top) * 0.38
    rounded(draw, (left, top, right, header), 22, fill=(139, 233, 253, 120))
    line(draw, [(left, header), (right, header)], (139, 233, 253, 170), 16)
    middle = left + (right - left) * 0.55
    line(draw, [(middle, header), (middle, bottom)], (139, 233, 253, 170), 14)
    row = header + (bottom - header) * 0.5
    line(draw, [(left, row), (right, row)], (139, 233, 253, 140), 12)


def build_x_bicolor(kind: str, *, small: bool = False) -> Image.Image:
    image, draw = new_canvas()
    shell(draw)
    if small:
        small_sheet(draw)
    elif kind == "sheet":
        spreadsheet(draw, solid=True, fold=False)
    elif kind == "sheet_outline":
        spreadsheet(draw, solid=False, fold=False)
    elif kind == "sheet_fold":
        spreadsheet(draw, solid=True, fold=True)
    segments(draw, (300, 300), (724, 724), 3, 34, PURPLE, 156)
    segments(draw, (724, 300), (300, 724), 3, 34, PINK, 156)
    return image


def concept_x_planilha() -> Image.Image:
    return build_x_bicolor("sheet")


def concept_x_planilha_vazada() -> Image.Image:
    return build_x_bicolor("sheet_outline")


def concept_x_planilha_dobra() -> Image.Image:
    return build_x_bicolor("sheet_fold")


def concept_sheet() -> Image.Image:
    image, draw = new_canvas()
    sheet = [(250, 170), (690, 170), (824, 304), (824, 844), (250, 844)]
    draw.polygon([(x * S, y * S) for x, y in sheet], fill=PANEL)
    fold = [(690, 170), (824, 304), (690, 304)]
    draw.polygon([(x * S, y * S) for x, y in fold], fill=PANEL_LIGHT)
    left, top, right, bottom = 330, 350, 744, 764
    grid_lines(draw, left, top, right, bottom)
    cell_w = (right - left) / 3
    cell_h = (bottom - top) / 3
    rounded(
        draw,
        (left + 8, bottom - cell_h + 8, left + cell_w - 8, bottom - 8),
        16,
        fill=GREEN,
    )
    for width, color in ((96, BG_DARK), (70, PURPLE)):
        line(draw, [(370, 400), (704, 714)], color, width)
        line(draw, [(704, 400), (370, 714)], color, width)
    return image


def concept_diamonds() -> Image.Image:
    image, draw = new_canvas()
    shell(draw)
    side = 330
    placements = (
        (-178, -178, PURPLE),
        (178, -178, CYAN),
        (-178, 178, PINK),
        (178, 178, GREEN),
    )
    for dx, dy, color in placements:
        tile = Image.new("RGBA", (side * S, side * S), (0, 0, 0, 0))
        tile_draw = ImageDraw.Draw(tile)
        tile_draw.rounded_rectangle(
            [8 * S, 8 * S, (side - 8) * S, (side - 8) * S],
            radius=64 * S,
            fill=color,
        )
        tile = tile.rotate(45, resample=Image.BICUBIC, expand=True)
        image.alpha_composite(
            tile,
            ((512 + dx) * S - tile.width // 2, (512 + dy) * S - tile.height // 2),
        )
    return image


CONCEPTS: dict[str, Callable[[], Image.Image]] = {
    "conceito_1_grade_x": concept_grid_x,
    "conceito_2_x_bicolor": concept_x_bicolor,
    "conceito_2a_x_planilha": concept_x_planilha,
    "conceito_2b_x_planilha_vazada": concept_x_planilha_vazada,
    "conceito_2c_x_planilha_dobra": concept_x_planilha_dobra,
    "conceito_3_folha_x": concept_sheet,
    "conceito_4_diamantes": concept_diamonds,
}

BASE = (
    "conceito_1_grade_x",
    "conceito_2_x_bicolor",
    "conceito_3_folha_x",
    "conceito_4_diamantes",
)
VARIANTS = (
    "conceito_2_x_bicolor",
    "conceito_2a_x_planilha",
    "conceito_2b_x_planilha_vazada",
    "conceito_2c_x_planilha_dobra",
)


def contact_sheet(paths: list[Path], name: str) -> Path:
    sheet = Image.new("RGBA", (SIZE * 2, SIZE * 2), BG_DARK)
    for index, path in enumerate(paths):
        tile = Image.open(path).convert("RGBA")
        sheet.alpha_composite(tile, ((index % 2) * SIZE, (index // 2) * SIZE))
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{name}.png"
    sheet.save(target)
    return target


def write_ico(path: Path, layers: dict[int, Image.Image]) -> None:
    """Grava um .ico com arte diferente por tamanho (16–256 px)."""
    entries: list[bytes] = []
    payloads: list[bytes] = []
    offset = 6 + 16 * len(layers)
    for size in sorted(layers):
        buffer = BytesIO()
        layers[size].resize((size, size), Image.LANCZOS).save(buffer, format="PNG")
        data = buffer.getvalue()
        dimension = 0 if size == 256 else size
        entries.append(
            struct.pack(
                "<BBBBHHII",
                dimension,
                dimension,
                0,
                0,
                1,
                32,
                len(data),
                offset,
            )
        )
        payloads.append(data)
        offset += len(data)
    with path.open("wb") as handle:
        handle.write(struct.pack("<HHH", 0, 1, len(layers)))
        for entry in entries:
            handle.write(entry)
        for data in payloads:
            handle.write(data)


def install_pick(name: str) -> None:
    build = CONCEPTS[name]
    full = build().resize((SIZE, SIZE), Image.LANCZOS)
    small = (
        build_x_bicolor("sheet_outline", small=True).resize((SIZE, SIZE), Image.LANCZOS)
        if name.startswith("conceito_2")
        else full
    )
    full.save(ROOT / "assets" / "icon.png")
    write_ico(
        ROOT / "assets" / "icon.ico",
        {
            16: small,
            24: small,
            32: small,
            48: full,
            64: full,
            128: full,
            256: full,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pick", choices=sorted(CONCEPTS))
    arguments = parser.parse_args()
    if arguments.pick:
        install_pick(arguments.pick)
        return
    paths = {name: save(build(), name) for name, build in CONCEPTS.items()}
    for path in paths.values():
        print(path)
    print(contact_sheet([paths[name] for name in BASE], "contatos"))
    print(contact_sheet([paths[name] for name in VARIANTS], "variantes_2"))


if __name__ == "__main__":
    main()
