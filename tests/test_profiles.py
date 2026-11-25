"""Perfil local da conta: apelido e foto em ``drive/profiles/``."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from xl_utils.shared import profiles
from xl_utils.shared.accounts import account_key
from xl_utils.shared.profiles import (
    PHOTO_MAX_BYTES,
    PHOTO_SIZE,
    Profile,
    ProfileError,
    ProfileStore,
    clean_nickname,
    normalize_photo,
)

EMAIL = "ana@example.com"


def _image(
    size: tuple[int, int],
    image_format: str = "PNG",
    mode: str = "RGB",
) -> bytes:
    """Imagem com a metade esquerda vermelha e a direita azul."""
    image = Image.new(mode, size, "red")
    image.paste("blue", (size[0] // 2, 0, size[0], size[1]))
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def _open(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_photo_is_cropped_at_the_center_and_reduced_to_png() -> None:
    # 600×300: o quadrado central vai de x=150 a x=450, metade de cada cor.
    photo = _open(normalize_photo(_image((600, 300))))

    assert photo.format == "PNG"
    assert photo.size == (PHOTO_SIZE, PHOTO_SIZE)
    assert photo.getpixel((10, PHOTO_SIZE // 2))[:3] == (255, 0, 0)
    assert photo.getpixel((PHOTO_SIZE - 10, PHOTO_SIZE // 2))[:3] == (0, 0, 255)


@pytest.mark.parametrize("image_format", ["JPEG", "WEBP"])
def test_jpeg_and_webp_are_accepted(image_format: str) -> None:
    photo = _open(normalize_photo(_image((400, 500), image_format)))

    assert photo.size == (PHOTO_SIZE, PHOTO_SIZE)


def test_transparency_survives() -> None:
    photo = _open(normalize_photo(_image((300, 300), mode="RGBA")))

    assert photo.mode == "RGBA"


def test_exif_orientation_is_respected() -> None:
    # Imagem deitada (600×300) com EXIF “girar 90°”: em pé, a esquerda vira o topo.
    image = Image.new("RGB", (600, 300), "red")
    image.paste("blue", (300, 0, 600, 300))
    exif = Image.Exif()
    exif[0x0112] = 6
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)

    photo = _open(normalize_photo(buffer.getvalue())).convert("RGB")

    top = photo.getpixel((PHOTO_SIZE // 2, 10))
    bottom = photo.getpixel((PHOTO_SIZE // 2, PHOTO_SIZE - 10))
    assert top[0] > top[2]
    assert bottom[2] > bottom[0]


@pytest.mark.parametrize(
    "data",
    [b"", b"isto nao e imagem", _image((50, 50), "GIF")],
    ids=["vazio", "texto", "gif"],
)
def test_invalid_photo_is_refused(data: bytes) -> None:
    with pytest.raises(ProfileError):
        normalize_photo(data)


def test_photo_over_the_limit_is_refused() -> None:
    with pytest.raises(ProfileError, match="MB"):
        normalize_photo(b"\x89PNG" + b"0" * PHOTO_MAX_BYTES)


def test_truncated_photo_is_refused() -> None:
    data = _image((400, 400), "JPEG")

    with pytest.raises(ProfileError):
        normalize_photo(data[: len(data) // 3])


def test_too_many_pixels_is_refused(monkeypatch) -> None:
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)

    with pytest.raises(ProfileError, match="pixels"):
        normalize_photo(_image((20, 20)))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("  Trabalho  ", "Trabalho"),
        ("", ""),
        (None, ""),
        ("a" * 30, "a" * profiles.NICKNAME_LIMIT),
    ],
)
def test_nickname_is_trimmed_and_limited(text: str | None, expected: str) -> None:
    assert clean_nickname(text) == expected


def test_store_round_trip_uses_the_account_hash(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    photo = normalize_photo(_image((300, 300)))

    store.save(EMAIL, "Trabalho", photo)

    assert store.get(EMAIL) == Profile(nickname="Trabalho", photo=photo)
    names = sorted(path.name for path in store.profiles_dir.iterdir())
    key = account_key(EMAIL)
    assert names == [f"{key}.json", f"{key}.png"]
    assert store.profiles_dir == tmp_path / "profiles"
    assert EMAIL.encode() not in store.nickname_path(EMAIL).read_bytes()


def test_store_without_anything_returns_an_empty_profile(tmp_path) -> None:
    assert ProfileStore(tmp_path).get(EMAIL) == Profile()


def test_corrupted_nickname_counts_as_empty(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    store.nickname_path(EMAIL).parent.mkdir(parents=True)
    store.nickname_path(EMAIL).write_text("{quebrado", encoding="utf-8")

    assert store.get(EMAIL) == Profile()


def test_empty_nickname_and_no_photo_leave_no_file(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    store.save(EMAIL, "Trabalho", normalize_photo(_image((300, 300))))

    store.save(EMAIL, "   ", None)

    assert store.get(EMAIL) == Profile()
    assert list(store.profiles_dir.iterdir()) == []


def test_saving_twice_leaves_no_temporary_file(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    photo = normalize_photo(_image((300, 300)))

    store.save(EMAIL, "Um", photo)
    store.save(EMAIL, "Dois", photo)

    assert not list(store.profiles_dir.glob("*.tmp"))
    assert store.get(EMAIL).nickname == "Dois"


def test_remove_touches_only_the_given_account(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    photo = normalize_photo(_image((300, 300)))
    store.save(EMAIL, "Ana", photo)
    store.save("zeca@example.com", "Zeca", photo)

    store.remove(EMAIL)
    store.remove(EMAIL)

    assert store.get(EMAIL) == Profile()
    assert store.get("zeca@example.com") == Profile(nickname="Zeca", photo=photo)
