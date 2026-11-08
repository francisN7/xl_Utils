"""Ajudantes de caminho para entrada e saída de arquivos.

Entrada: pasta, radical e sufixo desejados.
Saída: ``Path`` livre para gravação ou nome seguro para compor arquivo.
Erros: nenhum; a pasta é criada quando necessário.
"""

from collections.abc import Callable
from pathlib import Path

# O Windows recusa estes caracteres em nomes de arquivo e não aceita ponto ou
# espaço no fim. O limite de 80 evita nomes gigantes ao juntar radical + aba.
_INVALID_FILE_CHARS = frozenset('<>:"/\\|?*')
_MAX_FILE_PART = 80


def free_name(stem: str, suffix: str, exists: Callable[[str], bool]) -> str:
    """Devolve ``stem.suffix`` ou ``stem_001.suffix``... até o nome estar livre.

    ``exists`` recebe o nome completo e diz se ele já está ocupado. A mesma
    convenção vale para o disco e para o Drive, para o usuário reconhecer o
    resultado nos dois lugares.
    """
    candidate = f"{stem}{suffix}"
    counter = 1
    while exists(candidate):
        candidate = f"{stem}_{counter:03}{suffix}"
        counter += 1
    return candidate


def unique_path(directory: Path, stem: str, suffix: str = ".xlsx") -> Path:
    """Cria ``directory`` e devolve um caminho que ainda não existe.

    O primeiro nome é ``stem.suffix``; a partir da segunda gravação o sufixo
    numérico aparece como ``stem_001.suffix``.
    """
    directory.mkdir(parents=True, exist_ok=True)
    name = free_name(
        stem,
        suffix,
        lambda candidate: (directory / candidate).exists(),
    )
    return directory / name


def default_output_dir(source: Path, name: str = "output") -> Path:
    """Devolve a pasta de saída padrão ao lado do arquivo de origem."""
    return source.parent / name


def safe_file_part(value: str) -> str:
    """Torna um nome de aba seguro para compor um nome de arquivo.

    Usado pelo recorte quando uma planilha tem várias abas: o nome da aba entra
    no arquivo final. Caracteres de controle e proibidos no Windows viram ``_``.
    """
    cleaned = "".join(
        "_" if char in _INVALID_FILE_CHARS or ord(char) < 32 else char for char in value
    ).strip(" .")
    return (cleaned or "Aba")[:_MAX_FILE_PART]
