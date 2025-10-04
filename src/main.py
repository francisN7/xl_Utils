from utils import FileReader, save, set_root_dir

if __name__ == "__main__":
    set_root_dir()
    reader = FileReader()
    dfs = reader.run()
    save(dfs)
