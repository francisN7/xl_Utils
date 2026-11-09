# Versão e distribuição — o que foi entregue (2026-11-09)

Ciclo 0007 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.
O ciclo anterior está em [`0006-backlog.md`](0006-backlog.md); o próximo começa
em [`main.md`](../roadmap/main.md).

| Sessão | Entrega | Estado |
|---|---|---|
| S11 | Versão 0.2.0 e polimento de UI | [x] |
| S12 | Empacotar a primeira versão, 0.3.0 | [x] |

Ordem definida pelo dono em 2026-11-08: **versão e polimento → primeira
release → plugins → investigações pesadas**.

## S11 — entregue

App marcado como **0.2.0** (`pyproject.toml`, lock, `__version__`, diagnóstico).
Cartões do Início com título em uma linha (reticências, sem quebra no meio da
palavra), descrição em até duas linhas com `…` e tooltip, e recorte do conteúdo
— o atalho não sai do cartão. E-mails longos no menu de perfis e no seletor de
conta ficam com `…` e valor completo em tooltip de 3 s. Testes headless cobrem o
cartão e o rótulo de e-mail. Sem mudança de regra de negócio.

## S12 — entregue

A 0.3.0 virou instalador Windows x64 por usuário, sem Python nem `uv` na máquina
de destino. A decisão está no [ADR 0021](../adr/0021-instalador-windows.md):
`flet pack` (PyInstaller onedir, a partir do wheel) + Inno Setup 6. Nuitka sem
integração com o cliente desktop e MSIX/Flutter com custo de Flutter SDK +
Visual Studio foram descartados.

`scripts/build_windows.ps1` roda o pipeline inteiro — `uv build`, venv limpo em
`artifacts/venv`, `flet pack`, Inno Setup e SHA-256 — em ~2 min, gerando
`xl_Utils-0.3.0-setup.exe` com 85,1 MB (pasta do app com 161 MB). O instalador
cria menu Iniciar, atalho opcional na área de trabalho, ícone próprio e versão
0.3.0 nos metadados; instala em `%LOCALAPPDATA%\Programs\xl_Utils`.

A desinstalação é destrutiva por decisão do dono e avisa antes: apaga a
instalação, atalhos, `%LOCALAPPDATA%\xl_utils` (contas, tokens DPAPI,
preferências, cache do Drive e logs) e o cache do cliente Flet em
`%USERPROFILE%\.flet`. A pasta do `.flet` é identificada pelo fingerprint do zip
empacotado, então cache de outros apps Flet fica; `client` e `.flet` só saem se
ficarem vazios. Planilhas exportadas para pastas do usuário não são tocadas.

Três correções de empacotamento ficaram registradas no ADR: o patch idempotente
no `flet-cli` 1.1.2 (`open(..., "ab", encoding=...)` em modo binário), a cópia do
shim `python3t.dll` que o Python 3.15 guarda em `abi3t-compat/` (sem ele o
google-auth morria no import) e o `.ico` com arte própria por tamanho — completa
de 48 a 256 px e planilha simplificada em 16–32 px, porque a arte completa some
num ícone de 32 px. O conceito escolhido foi o 2b: X bicolor com mini-planilha
vazada atrás da ponta superior direita.

A validação foi feita no Windows Sandbox com planilha fictícia: instalação,
abertura pelo menu Iniciar, execução de ferramenta, troca de tema, desinstalação
e conferência de que `%LOCALAPPDATA%\xl_utils` e `%USERPROFILE%\.flet` sumiram.
O roteiro ficou em [`guide/release-windows.md`](../guide/release-windows.md).

Os acentos do instalador quebraram por uma regravação do `.iss` em ANSI; o
arquivo voltou a ser UTF-8 com BOM e a janela do desinstalador foi conferida por
captura de tela antes da release. A `v0.3.0` foi publicada no GitHub com
instalador, `SHA256SUMS.txt` e notas.

## Backlog do ciclo

Revisado pelo dono em 2026-11-08 (S10) e mantido em 2026-11-09: primeira release
→ **plugins** → investigações pesadas. A lista viva está em
[`../roadmap/main.md`](../roadmap/main.md) e abriu o ciclo 0008.
