import os
import sys
from pathlib import Path


# Garante que o root dos arquivos e imports
# seja o mesmo independemente do ponto de  entrada do código:
def set_root_dir() -> None:
    current_file_path = Path(__file__).resolve()
    root_dir = current_file_path.parent.parent.parent
    os.chdir(root_dir)
    if str(root_dir) not in sys.path:
        sys.path.insert(0, f"{str(root_dir)}/src")
    print(root_dir)
