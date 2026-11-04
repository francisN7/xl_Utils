"""Dracula dark palette and the Flet theme built from it."""

import flet as ft

BACKGROUND = "#282A36"
BACKGROUND_DEEP = "#21222C"
SURFACE = "#343746"
BORDER = "#44475A"
TEXT = "#F8F8F2"
MUTED = "#6272A4"
PURPLE = "#BD93F9"
PINK = "#FF79C6"
GREEN = "#50FA7B"
YELLOW = "#F1FA8C"
RED = "#FF5555"
CYAN = "#8BE9FD"
ORANGE = "#FFB86C"

SUCCESS_BG = "#22342A"
ERROR_BG = "#3A2428"
INFO_BG = "#1F3438"

# Smallest size used anywhere in the UI: hints, counters, logs and table cells.
FONT_XS = 12
FONT_SM = 13
FONT_MD = 15
FONT_TITLE = 24
FONT_HERO = 26


def build_theme() -> ft.Theme:
    """Return the Dracula theme used by the app."""
    return ft.Theme(
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary=PURPLE,
            on_primary=BACKGROUND_DEEP,
            secondary=PINK,
            on_secondary=BACKGROUND_DEEP,
            surface=SURFACE,
            on_surface=TEXT,
            surface_container=BACKGROUND,
            surface_container_high=SURFACE,
            surface_container_highest=BORDER,
            outline=BORDER,
            outline_variant=BORDER,
            error=RED,
            on_error=BACKGROUND_DEEP,
        ),
    )
