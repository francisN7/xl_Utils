"""Perfil local de cada conta do Drive: apelido e foto escolhidos pelo usuário.

Nada aqui vem do Google: o apelido é digitado e a foto sai do disco. A foto é
recortada no quadrado central, reduzida a 256 px e copiada para dentro de
``drive/profiles/`` como PNG; o arquivo original nunca é referenciado. Os nomes
usam o mesmo hash de :func:`~xl_utils.shared.accounts.account_key`, então nem o
nome do arquivo nem o conteúdo guardam o e-mail.

Entrada: e-mail da conta, apelido e bytes da imagem.
Saída: :class:`Profile` (vazio se não houver nada gravado).
Erros: :class:`ProfileError` para imagem inválida; gravação levanta ``OSError``.
"""

from __future__ import annotations

import io
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from xl_utils.shared.accounts import account_key, default_root, write_atomic

PROFILES_DIR = "profiles"
NICKNAME_LIMIT = 16
PHOTO_SIZE = 256
PHOTO_MAX_BYTES = 10 * 1024 * 1024
PHOTO_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
_PHOTO_FORMATS = {"PNG", "JPEG", "WEBP"}


class ProfileError(Exception):
    """Imagem que não pode virar foto da conta."""


@dataclass(frozen=True, slots=True)
class Profile:
    """Apelido e foto (PNG 256×256) de uma conta; vazio quando não há nada."""

    nickname: str = ""
    photo: bytes | None = field(default=None, repr=False)


def clean_nickname(text: str | None) -> str:
    """Apelido sem espaços nas pontas e com no máximo ``NICKNAME_LIMIT``."""
    return (text or "").strip()[:NICKNAME_LIMIT].strip()


def normalize_photo(data: bytes) -> bytes:
    """Recorta o quadrado central, reduz a ``PHOTO_SIZE`` e devolve PNG.

    Aceita PNG, JPEG e WebP de até ``PHOTO_MAX_BYTES``; respeita a orientação
    do EXIF. Qualquer outra coisa levanta :class:`ProfileError`.
    """
    if not data:
        raise ProfileError("O arquivo da foto está vazio.")
    if len(data) > PHOTO_MAX_BYTES:
        raise ProfileError(
            f"A foto passa de {PHOTO_MAX_BYTES // (1024 * 1024)} MB; "
            "escolha uma imagem menor."
        )
    try:
        # Imagem com pixels demais vira erro em vez de aviso (bomba de descompressão).
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(data))
        with image:
            if image.format not in _PHOTO_FORMATS:
                raise ProfileError("Use uma foto PNG, JPEG ou WebP.")
            # JPEG grande decodifica já reduzido: poupa memória e tempo.
            image.draft("RGB", (PHOTO_SIZE, PHOTO_SIZE))
            image.load()
            upright = ImageOps.exif_transpose(image)
            mode = "RGBA" if "A" in upright.getbands() else "RGB"
            square = ImageOps.fit(
                upright.convert(mode),
                (PHOTO_SIZE, PHOTO_SIZE),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
    except ProfileError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ProfileError("A foto tem pixels demais; use uma imagem menor.") from error
    except UnidentifiedImageError as error:
        raise ProfileError("Não deu para ler essa imagem como foto.") from error
    except (OSError, ValueError) as error:
        raise ProfileError("A imagem está corrompida ou incompleta.") from error
    output = io.BytesIO()
    square.save(output, format="PNG", optimize=True)
    return output.getvalue()


class ProfileStore:
    """Perfis em ``drive/profiles/``: ``<hash>.json`` (apelido) e ``<hash>.png``."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_root()

    @property
    def profiles_dir(self) -> Path:
        """Pasta onde ficam apelidos e fotos."""
        return self.root / PROFILES_DIR

    def nickname_path(self, email: str) -> Path:
        """Arquivo do apelido da conta."""
        return self.profiles_dir / f"{account_key(email)}.json"

    def photo_path(self, email: str) -> Path:
        """Arquivo da foto da conta."""
        return self.profiles_dir / f"{account_key(email)}.png"

    def get(self, email: str) -> Profile:
        """Devolve o perfil; arquivo ausente ou corrompido conta como vazio."""
        return Profile(nickname=self._nickname(email), photo=self._photo(email))

    def save(self, email: str, nickname: str, photo: bytes | None) -> None:
        """Grava foto e apelido de forma atômica; o vazio apaga o arquivo."""
        photo_path = self.photo_path(email)
        if photo:
            write_atomic(photo_path, photo)
        else:
            photo_path.unlink(missing_ok=True)
        nickname_path = self.nickname_path(email)
        cleaned = clean_nickname(nickname)
        if cleaned:
            payload = json.dumps({"nickname": cleaned}, ensure_ascii=False, indent=2)
            write_atomic(nickname_path, payload.encode("utf-8"))
        else:
            nickname_path.unlink(missing_ok=True)

    def remove(self, email: str) -> None:
        """Apaga apelido e foto só da conta indicada."""
        self.photo_path(email).unlink(missing_ok=True)
        self.nickname_path(email).unlink(missing_ok=True)

    def _nickname(self, email: str) -> str:
        try:
            data = json.loads(self.nickname_path(email).read_text(encoding="utf-8"))
        except OSError, ValueError:
            return ""
        value = data.get("nickname") if isinstance(data, dict) else None
        return clean_nickname(value) if isinstance(value, str) else ""

    def _photo(self, email: str) -> bytes | None:
        try:
            data = self.photo_path(email).read_bytes()
        except OSError:
            return None
        return data or None


__all__ = [
    "NICKNAME_LIMIT",
    "PHOTO_EXTENSIONS",
    "PHOTO_MAX_BYTES",
    "PHOTO_SIZE",
    "Profile",
    "ProfileError",
    "ProfileStore",
    "clean_nickname",
    "normalize_photo",
]
