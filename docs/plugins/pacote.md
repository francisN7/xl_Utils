# O pacote de plugin

O pacote é um arquivo **`.tar.xz`**: um tar com LZMA2 sólido, lido pela
biblioteca padrão do Python (`tarfile` + `lzma`). Não é um `.7z` e não exige
7-Zip instalado. O ADR 0023 registra a comparação: no código do app, o `.tar.xz`
fica a 2,9% do `.7z` e 65% menor que o `.zip` deflate.

## O que vai dentro

```text
plugin.toml          obrigatório, na raiz do tar
lib/                 obrigatório; só código .py
  main.py            exemplo: entrypoint "main:run"
assets/              opcional; imagens, modelos, textos
LICENSE              opcional
README.md            opcional
```

O host cria `data/` e `install.json` depois da extração. Eles **não** podem vir
no pacote:

- `data/` guarda os dados do plugin e é apagado na desinstalação.
- `install.json` é o registro do host (hash, tamanho, data, origem).

O código de `lib/` vira um pacote sintético em memória na primeira execução:
imports entre arquivos do plugin são relativos (`from .helper import x`) e
`lib/` não entra no `sys.path` do app.

## Regras de caminho

O validador recusa, antes de escrever qualquer byte:

- caminho absoluto, `..`, `\`, letra de unidade (`C:`) e `:`;
- caractere inválido do Windows (`<`, `>`, `"`, `|`, `?`, `*`);
- nome reservado do Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1`…, `LPT1`…),
  inclusive com extensão;
- ponto ou espaço no fim do nome;
- caractere de controle, nome fora de NFC e colisão de caixa
  (`A.txt` × `a.txt`);
- nome duplicado e nome com mais de 180 caracteres;
- caminho final (raiz + id + nome) com mais de 250 caracteres;
- symlink, hardlink, FIFO, dispositivo e arquivo sparse.

Só entram **arquivo regular** e **diretório**. Diretórios podem ser implícitos;
o host cria os pais. O modo e o dono gravados no tar são ignorados.

## Regras de conteúdo

- `.py` só dentro de `lib/`; o resto é dado ou asset.
- Sem `.pyc` e sem `__pycache__`.
- Sem `.pyd`, `.dll`, `.exe`, `.so`, `.dylib`, `.com`, `.bat`, `.cmd`, `.ps1`,
  `.vbs`, `.js`, `.jse`, `.wsf`, `.scr`, `.msi`, `.cpl`, `.jar`, `.lnk`,
  `.pyw`, `.pyz`, `.reg` ou `.sh`.
- Sem `plugin.toml` aninhado; o manifesto é único e fica na raiz.
- Sem `data/` e sem `install.json`.
- Sem instalação de dependências: o plugin deve trazer o código Python puro de
  que precisa, ou declarar no manifesto pacotes que o host já oferece.

## Limites

| Item | Limite |
|---|---:|
| Arquivo `.tar.xz` | 100 MB |
| Conteúdo extraído | 500 MB |
| Entradas no tar | 10.000 |
| Arquivo individual | 200 MB |
| Razão extraído/pacote | 500:1 |
| Nome de entrada | 180 caracteres |
| Caminho final | 250 caracteres |
| `plugin.toml` | 256 KB |
| Memória do xz | 256 MB |

Os limites são generosos de propósito, mas continuam sendo uma barreira contra
zip bomb. A soma dos tamanhos declarados é conferida **antes** da extração; a
contagem de bytes é conferida de novo durante a extração, e o processo aborta
se passar do teto. Também é conferido o espaço livre em disco.

## Sidecar SHA-256

Ao lado do pacote deve existir `<nome>.tar.xz.sha256`, no formato:

```text
3f7c...e91  meu-plugin.tar.xz
```

O hash é conferido na cópia que será extraída. O sidecar é **integridade**, não
autoria: ele detecta corrupção e arquivo trocado por engano, mas não impede
alguém de substituir o pacote e o sidecar juntos. Assinatura de código não faz
parte desta versão.

## Layout depois de instalar

```text
%LOCALAPPDATA%\xl_utils\plugins\
  autor.ferramenta\
    plugin.toml
    install.json
    lib\
    assets\
    data\
  .staging\             # temporário; limpo depois da promoção
```

`install.json` guarda `id`, `version`, `api_version`, `sha256`, `archive_size`,
`installed_at` e o nome do arquivo de origem. Ele não substitui o manifesto: a
descoberta lê `plugin.toml`.

## Instalação atômica

1. O pacote é copiado para `plugins/.staging/<id>-<uuid>/`.
2. O hash da cópia é conferido; o tar é inspecionado e o manifesto é validado.
3. Se o id já existe, a instalação é recusada sem tocar na pasta existente.
4. O conteúdo é extraído no staging; `install.json` é gravado; a cópia do
   pacote é apagada.
5. `os.replace(staging, plugins/<id>)` promove a pasta de uma vez. Falha em
   qualquer passo limpa o staging e deixa o estado anterior intacto.

## Desinstalação

Remove `plugins/<id>/` inteiro, incluindo `data/`. O host não segue symlink ou
junction no lugar da pasta do plugin e trata arquivos somente leitura. Não
existe lixeira de plugins nesta versão.
