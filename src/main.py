from core import CnjProcessor
from utils import FileReader, save, set_root_dir


def xl_run() -> None:
    print("xl_run funcional!")


if __name__ == "__main__":
    set_root_dir()
    reader = FileReader()
    df = reader.run(True)
    cnj_processor = CnjProcessor(df)
    cnjs_df = cnj_processor.run()
    save(cnjs_df)
