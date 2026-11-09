# 0021 — Instalador Windows com PyInstaller e Inno Setup

**Status:** Aceita · **Data:** 2026-11-09 · **Sessão:** S12

## Contexto

A 0.3.0 é a primeira versão instalável: precisa abrir numa máquina sem Python,
com menu Iniciar, atalho opcional, ícone próprio e desinstalação que remove tudo
o que o app criou. O app usa Flet 1.1.2 desktop, pandas 3, lxml, openpyxl e
OAuth do Google. Não há certificado de assinatura e o build é local.

## Alternativas consideradas

- **`flet build windows` (Flutter + MSIX):** é o caminho oficial do Flet 1.x,
  mas exige Flutter SDK e o workload Desktop C++ do Visual Studio (nenhum dos
  dois está na máquina), baixa gigabytes e o MSIX confiável exige certificado
  de assinatura. Descartado nesta versão por custo de ambiente e por SmartScreen
  continuar aparecendo sem certificado.
- **Nuitka + Inno Setup:** não há integração do Nuitka com o cliente desktop do
  Flet; seria preciso empacotar o cliente Flutter à mão e compilar pandas/lxml,
  com tempo de build e risco de incompatibilidade muito maiores. Descartado.
- **PyInstaller (`flet pack`) + Inno Setup:** escolhido. O `flet pack` já monta
  o cliente Flutter, aplica ícone e versão e roda o PyInstaller; o Inno resolve
  instalação por usuário e desinstalação.

## Decisão

1. **Empacotador:** `flet pack` em modo **onedir**, a partir do wheel em um venv
   limpo (`artifacts/venv`), com `--add-data` do `configs/`. Onedir abre mais
   rápido e sofre menos com antivírus do que onefile; a pasta vai dentro do
   instalador. `artifacts/` fica fora de `build/` porque o `flet pack` apaga a
   pasta `build/` antes de empacotar.
2. **Instalador:** Inno Setup 6, por usuário (`PrivilegesRequired=lowest`), em
   `%LOCALAPPDATA%\Programs\xl_Utils`, menu Iniciar, atalho opcional na área de
   trabalho e versão 0.3.0 nos metadados.
3. **Desinstalação destrutiva:** remove a instalação, atalhos, a chave de
   desinstalação e **toda** a pasta `%LOCALAPPDATA%\xl_utils` — contas, tokens
   DPAPI, preferências, cache do Drive e logs. Também apaga o cache do cliente
   Flet em `%USERPROFILE%\.flet`: o cliente extrai o zip empacotado na primeira
   execução para `client\flet-desktop-<flavor>-<versão>-<fingerprint>`. O
   desinstalador lê o fingerprint do sidecar `flet-windows.zip.sha256` do bundle
   (ou calcula o SHA-256 do zip) e remove só a pasta deste app, preservando o
   cache de outros apps Flet; as pastas `.flet` e `.flet\client` só saem se
   ficarem vazias. O desinstalador mostra um aviso explícito antes de continuar.
   Arquivos que o usuário exportou para pastas próprias não são tocados: são
   dados dele, não estado do app.
4. **Build local** com `scripts/build_windows.ps1`; publicar no GitHub com
   `gh release create`. Automação no Actions fica no backlog.
5. **Correção do Flet 1.1.2:** o `flet pack` no Windows quebra ao reanexar o
   overlay do `flet.exe` (`open(..., "ab", encoding="utf-8")` é inválido em modo
   binário). O build troca a linha por `open(..., "ab")` de forma idempotente no
   venv limpo e falha alto se o trecho não existir. Remover quando o Flet
   corrigir.
6. **Shim do Python 3.15:** o `_rust.pyd` do cryptography importa
   `python3t.dll`, que o Python instala em `abi3t-compat/` e só expõe no
   interpretador normal. O build copia esse DLL para `_internal/`; sem ele o
   app empacotado morre no import do google-auth.

## Medições

- Build completo da S12: **1,8 min**; pasta do app com **161 MB**, executável
  com **21,5 MB** e instalador com **85,1 MB**.
- O `headers.json` aparece em `_internal/xl_utils/configs/` e o exe abre a
  janela a partir do build.
- `flet pack` sem PyInstaller 6.22.3 e sem o patch falha antes de empacotar.
- O `.ico` tem arte própria por tamanho: completa em 48–256 px e planilha
  simplificada em 16–32 px, porque a arte completa some num ícone de 32 px.
- A limpeza do cache Flet foi testada em ambiente isolado: com dois caches no
  `client`, só o do xl_Utils saiu; com um só, `.flet` inteiro sumiu; sem o
  sidecar, o fingerprint calculado do zip também bateu.

## Consequências

- Sem assinatura, o SmartScreen avisa; a release publica SHA-256 e o guia
  explica o aviso. Certificado pago não entra nesta versão.
- A versão precisa bater em `pyproject.toml`, `uv.lock`, `__version__` e no
  diagnóstico; o build lê a versão do `pyproject.toml`.
- `pyinstaller` passa a ser dependência de desenvolvimento; o usuário final
  recebe só o instalador.
- Trocar de empacotador exige ADR novo; o patch do Flet é dívida técnica
  rastreada até o upstream corrigir.
