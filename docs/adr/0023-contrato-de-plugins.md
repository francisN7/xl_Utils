# ADR 0023 — Contrato de plugins e pacote `.tar.xz`

**Status:** Aceita · **Data:** 2026-11-11 · **Sessão:** S13

## Contexto

O xl_Utils tem cinco ferramentas fixas e quer abrir espaço para plugins locais:
um pacote com manifesto, código e assets que adiciona uma página de ferramenta
sem mudar o núcleo. O plugin é instalado em
`%LOCALAPPDATA%/xl_utils/plugins/<id>/`, nunca no repositório, e nada é baixado
automaticamente. A S13 define o contrato e a instalação segura antes de existir
UI ou carregamento de código.

O app roda em Python 3.15 no Windows, é empacotado com PyInstaller onedir e é
distribuído como instalador por usuário. O contrato precisa caber nesse ambiente
e não pode transformar o instalador numa dependência pesada.

A spec original falava em `.7z` e `py7zr`. A medição mudou a decisão: com o
código-fonte do app (340 KB, sem `__pycache__`), o `.7z` LZMA2 ficou em 66,4 KB,
o `.tar.xz` em 68,3 KB (+2,9%), o `.zip` deflate em 109,7 KB (+65%). O
`.tar.xz` entrega praticamente a compactação máxima do `.7z` usando só a
stdlib.

## Alternativas consideradas

- **`.7z` + `py7zr`:** API Python madura e metadados por entrada, mas o
  `py7zr` 1.1.4 ainda não tem wheels cp315 para `pyppmd`, `pybcj` e
  `inflate64`; o `uv` cai no sdist e exige compilar C em todo ambiente. As
  wheels somam cerca de 5 MB, estimativa que não foi levada ao build porque a
  alternativa caiu antes; `py7zr`, `pyppmd` e `pybcj` são LGPL-2.1. Descartada
  nesta sessão.
- **`.7z` + `7zr.exe`:** mantém o formato e os 66 KB, mas embute um binário de
  terceiro (~1 MB, LGPL) e extrai por subprocesso; a listagem e a detecção de
  symlink ficam por conta de parsing. Descartada.
- **`.7z` + `tar.exe` do Windows:** não adiciona binário, mas depende da versão
  do `bsdtar` do sistema, tem flags limitadas e a listagem é frágil. Testado
  contra `..` e symlink; funciona, mas não é contrato estável. Descartada.
- **`.zip` + stdlib:** zero dependência e universal, porém 65% maior que o
  `.7z` no material testado. Descartada porque a compactação era requisito.
- **`.tar.xz` + stdlib:** tar sólido com LZMA2 via `tarfile` + `lzma`; 97% da
  compactação do `.7z`, zero dependência, zero licença nova e validação manual
  dos membros. Escolhida.
- **Execução em subprocesso ou sandbox:** isola falhas e permitiria aplicar
  permissões, mas exige protocolo IPC, UI declarativa e, para isolamento real,
  AppContainer/Job Object. Fica como decisão futura; a v1 roda no mesmo
  processo.
- **UI em controle Flet pelo plugin:** flexível, mas acopla o plugin à versão do
  Flet e fura o layout comum. A UI declarativa no manifesto foi escolhida.
- **ID reverse-DNS ou nome simples:** reverse-DNS evita colisão, mas é verboso;
  nome simples colide. O slug `autor.ferramenta` foi escolhido.
- **Permissões aplicadas vs declaradas:** aplicar exige sandbox; na v1 as
  permissões são declarativas e a UI avisa. Sem sandbox, não há promessa de
  isolamento.
- **Hash no manifesto vs sidecar:** hash dentro do pacote não protege contra
  troca do arquivo. O sidecar externo SHA-256 é obrigatório.
- **Manifesto JSON vs TOML:** JSON já é usado em `headers.json` e
  `settings.json`, mas o dono preferiu TOML; `tomllib` é stdlib no 3.15.

## Decisão

1. **Pacote:** `.tar.xz` com `tarfile` + `lzma` da stdlib, gerado de forma
   determinística. O `plugin.toml` fica na raiz do tar; o sidecar
   `<pacote>.tar.xz.sha256` é obrigatório. A instalação vai para
   `%LOCALAPPDATA%/xl_utils/plugins/<id>/` (fallback `~/.xl_utils/plugins/`).
2. **Manifesto:** `plugin.toml` com `[plugin]` (`id`, `name`, `version`,
   `api_version`, `entrypoint`, `description`, `authors`, `min_app_version`,
   `dependencies`, `license`, `homepage`), `[permissions]` (`network`,
   `filesystem`, `subprocess`), `[ui]` (`multiple_files`, `default_all_sheets`,
   `inputs`, `note`) e `[[options]]` (`key`, `label`, `type`, `default`,
   `choices`, `help`, `min`, `max`). Chaves desconhecidas são recusadas; campos
   novos exigem `api_version` novo.
3. **Pacote:** `plugin.toml` na raiz, código só em `lib/` (`.py`), `assets/`
   opcional, `LICENSE`/`README` opcionais. `data/` é criado pelo host e não
   pode vir no pacote; `install.json` é do host. Sem `.pyd`, `.dll`, `.exe`,
   `.so`, `.dylib`, `.com`, `.bat`, `.cmd`, `.ps1`, `.vbs`, `.js`, sem
   `.pyc`/`__pycache__`, sem symlink/hardlink/dispositivo e sem pip.
4. **API:** `run(request: PluginRequest) -> PluginResult`, com `files`,
   `inputs`, `sheets`, `options`, `log`, `progress`, `cancel`, `data_dir`,
   `plugin_dir` e `app_version` na entrada; `frames`, `message` e `save_items`
   na saída. Roda fora da UI thread, não importa Flet, não imprime e devolve
   dados; a UI é montada pelo host a partir do manifesto.
5. **Ciclo de vida:** descoberta lê `plugin.toml` sem importar código;
   instalação valida, extrai em staging, grava `install.json` e promove com
   `os.replace`; id duplicado é recusado sem sobrescrever; desinstalação remove
   a pasta e os dados do plugin; falha de plugin é isolada na S14.
6. **Segurança:** recusar caminho absoluto, `..`, `\`, `:`, controle, nomes
   reservados do Windows, ponto/espaço no fim, NFC divergente, colisão de caixa
   e duplicatas; só arquivo regular e diretório; limites de 100 MB de pacote,
   500 MB extraídos, 10.000 entradas, 200 MB por arquivo, razão 500:1, nome
   ≤180, caminho final ≤250, manifesto ≤256 KB e memória do xz ≤256 MB; copiar
   o pacote para o staging, conferir o hash da cópia e extrair da cópia.
7. **Versionamento:** SemVer `X.Y.Z` para o plugin; `api_version` inteiro
   suportado (`1` nesta versão); `min_app_version` opcional; qualquer mudança
   incompatível no manifesto, na request/result ou no schema de UI sobe a API.
8. **Documentação e autoria:** o contrato fica em `docs/plugins/`; o guia
   prático, os exemplos e o carregamento ficam na S14. O CLI
   `scripts/plugin_cli.py` (`pack`, `check`, `install`, `list`, `uninstall`) é a
   ferramenta canônica de desenvolvimento no repo do app, sem executar código
   do plugin e sem entry point no instalador. O repo privado de plugins consome
   esse CLI ou a biblioteca.

## Consequências

- A compactação fica a 2,9% do `.7z` sem dependência nova, sem licença nova e
  sem crescimento do instalador.
- A validação do tar é nossa: nada de `extractall`, nomes e tamanhos são
  conferidos antes e durante a extração.
- O `.tar.xz` é menos familiar que `.7z`; o CLI e a S14 documentam o fluxo.
- Plugins rodam no mesmo processo e têm os direitos do usuário. As permissões
  são avisos, não sandbox; a UI da S14 precisa dizer isso com clareza.
- O PyInstaller só embute o módulo quando a S14 ligar a UI; nessa sessão é
  preciso confirmar `_lzma` no bundle.
- O contrato é estrito: qualquer campo novo relevante exige `api_version` novo.

## Riscos

- Casos de borda do `tarfile` (PAX, nomes longos, sparse, duplicatas e colisões
  de caixa no Windows) podem escapar da validação; testes usam arquivos reais.
- `lzma` pode consumir memória demais; o leitor precisa de `memlimit` e corte
  por bytes descomprimidos.
- A promoção de diretório no Windows depende de staging no mesmo volume; falha
  injetada no teste cobre o caminho.
- Sem sandbox, um plugin malicioso executa com os direitos do usuário. O
  instalador só reduz a superfície do pacote; a confiança é explícita.
- O sidecar protege contra corrupção e arquivo errado, não contra substituição
  maliciosa dos dois arquivos; assinatura de código fica para depois.
- O repo privado de plugins depende do CLI/API do app; versões incompatíveis
  precisam ser tratadas por `api_version` e `min_app_version`.
