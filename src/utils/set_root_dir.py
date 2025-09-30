import os
from pathlib import Path


def set_root_dir() -> None:
    current_file_path = Path(__file__).resolve()
    root_dir = current_file_path.parent.parent.parent
    os.chdir(root_dir)
