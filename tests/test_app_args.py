"""Opções de linha de comando do app."""

from xl_utils.app import WEB_PORT, parse_args


def test_default_is_desktop() -> None:
    args = parse_args([])
    assert args.web is False
    assert args.port == WEB_PORT


def test_web_flag_and_port() -> None:
    args = parse_args(["--web", "--port", "9000"])
    assert args.web is True
    assert args.port == 9000
