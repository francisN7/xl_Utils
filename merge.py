import pandas as pd
from tkinter import Tk, filedialog

#Selecionar os arquivos:
def select_files():
    Tk().withdraw()  # Oculta a janela principal do Tkinter
    file_paths = filedialog.askopenfilenames(
        title="Selecione os arquivos Excel",
        filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
    )
    return file_paths

#Unificar as planilhas:
def unify_excel_files():
    file_paths = select_files()
    if not file_paths:
        print("Nenhum arquivo selecionado.")
        return
    
    dataframes = []

    for file in file_paths:
        try:
            df = pd.read_excel(file)
            dataframes.append(df)
        except Exception as e:
            print(f"Erro ao ler {file}: {e}")

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)  # Combina os DataFrames
        save_path = filedialog.asksaveasfilename(
            title="Salvar arquivo unificado",
            defaultextension=".xlsx",
            filetypes=[("Arquivo Excel", "*.xlsx")]
        )
        if save_path:
            combined_df.to_excel(save_path, index=False)
            print(f"Planilhas unificadas e salvas em: {save_path}")
        else:
            print("Operação cancelada. Nenhum arquivo foi salvo.")
    else:
        print("Nenhum dado foi combinado.")

if __name__ == "__main__":
    unify_excel_files()