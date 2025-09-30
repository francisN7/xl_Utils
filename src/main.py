from utils import FileReader, set_root_dir

if __name__ == "__main__":
    set_root_dir()
    reader = FileReader()
    dfs = reader.run()
