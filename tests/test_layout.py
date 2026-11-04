import flet as ft

from xl_utils.ui.components.tool_layout import ToolLayout


def _texts(control: object) -> list[str]:
    if isinstance(control, ft.Text):
        return [str(control.value)]

    found: list[str] = []
    content = getattr(control, "content", None)
    if content is not None:
        found.extend(_texts(content))
    for child in getattr(control, "controls", None) or []:
        found.extend(_texts(child))
    return found


def test_layout_without_options_hides_the_options_card() -> None:
    layout = ToolLayout(
        "Sem opções",
        "Teste",
        note="Comportamento fixo.",
    )

    texts = _texts(layout.control)

    assert "1. Entrada" in texts
    assert "2. Resultado" in texts
    assert "2. Opções" not in texts
    assert "3. Resultado" not in texts
    assert texts.count("Comportamento fixo.") == 1


def test_layout_with_options_keeps_the_options_card() -> None:
    layout = ToolLayout(
        "Com opções",
        "Teste",
        options=ft.Text("Campo editável"),
    )
    texts = _texts(layout.control)

    assert "2. Opções" in texts
    assert "3. Resultado" in texts
