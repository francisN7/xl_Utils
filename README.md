# Utils

Uma série de mini scrpits python para resolução de pequenos problemas diários.

## Descrições

### all_str

Resolve o problema de números serem lidos como notação científica, convertendo todos os dados da planilha para texto simples ( ou str a nível de código).
Em paralelo, está apto a corrigir arquivos com problemas de metadados (isso anteriormente impedia a leitura via pandas).

### cnjs

Percorre todo um arquivo.xlsx em busca de numerações no formato CNJ, após retorna um novo arquivo contendo todos os CNJs únicos encontrados.

### convert

Transforma o json da api em uma planilha.

### cut

Recorta planilhas com base na quantidade de linhas desejadas por arquivo.

### merge

Unifica planilhas que possuam o mesmo cabeçalho ou várias abas da mesma planilha.

### quick_replace

Substitui nomes com base em uma lista de pares.

### remove_emoji

Rapidamente substitui emojis por strings, nesse caso, por uma string em branco: (" ").

# Futuro

## Geral

#### Idéias relacionados com todos os scripts:

- Integrar com GUI.

  - Iced;
  - Flet;
  - Tkinter;
  - Textual;
  - Slint;
  - etc.

- Distribuir com pyinstaller ou estudar possibilidade de instalação nativa.

## Específicos

Nenhuma pendência específica por hora.
