# Release Windows

Como gerar, validar e publicar o instalador do xl_Utils. O build é local, em
Windows x64, e não depende de Flutter nem de certificado de assinatura.

## Pré-requisitos

- `uv` e Python 3.15 na máquina de build.
- Inno Setup 6 (`iscc`): `choco install innosetup -y`.
- Ícone em `assets/icon.ico` — gerado por
  `uv run python scripts/make_icons.py --pick conceito_2b_x_planilha_vazada`
  (arte completa em 48–256 px e versão simplificada em 16–32 px).

## Build

```powershell
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

O script limpa `artifacts/`, gera o wheel, cria `artifacts/venv`, instala o wheel
e o PyInstaller, empacota com `flet pack` (onedir) e compila o Inno Setup.
Saídas:

- `artifacts/app/xl_Utils/xl_Utils.exe` — executável empacotado;
- `artifacts/installer/xl_Utils-<versão>-setup.exe` — instalador;
- `artifacts/installer/SHA256SUMS.txt` — checksum para publicar.

O build aplica um patch idempotente no `flet-cli` 1.1.2 (bug do overlay ao
gravar a versão do `flet.exe`) e copia `python3t.dll` de `abi3t-compat/` para
`_internal/`; sem esse shim o app empacotado falha no import do google-auth.
Remover o patch quando o Flet corrigir.

## Validação (Windows Sandbox)

O Windows Sandbox é uma máquina limpa, sem Python nem `uv`. Habilitar uma vez:

```powershell
# Terminal como Administrador
Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -All -NoRestart
Restart-Computer
```

Roteiro em `C:\Windows\System32\WindowsSandbox.exe`:

1. Copiar o instalador e o `SHA256SUMS.txt` para a área compartilhada
   (`artifacts/share`, que o build não apaga).
2. Conferir o checksum: `Get-FileHash .\xl_Utils-0.3.0-setup.exe -Algorithm SHA256`.
3. Instalar, escolher o atalho opcional e abrir pelo menu Iniciar.
4. Rodar uma ferramenta com planilha fictícia e abrir o menu de perfis.
5. Desinstalar em Configurações → Aplicativos; confirmar o aviso.
6. Conferir que `%LOCALAPPDATA%\xl_utils`, `%USERPROFILE%\.flet` e os atalhos
   sumiram. O `.flet` é o cache do cliente Flet, extraído na primeira execução;
   o desinstalador apaga só a pasta deste app (identificada pelo fingerprint do
   zip empacotado), não o cache de outros apps Flet.

O desinstalador apaga contas, tokens, preferências, cache e logs. Planilhas
exportadas pelo usuário para pastas próprias ficam intactas.

## Publicação

```powershell
gh release create v0.3.0 `
  artifacts/installer/xl_Utils-0.3.0-setup.exe `
  artifacts/installer/SHA256SUMS.txt `
  --title "xl_Utils 0.3.0" `
  --notes-file artifacts/installer/notes.md
```

As notas trazem requisitos (Windows 10/11 x64), tamanho, checksum e o aviso de
SmartScreen: sem assinatura de código, o Windows pode exibir “aplicativo não
reconhecido”; a release publica o SHA-256 para conferência. Se `gh` não estiver
no PATH, use `C:\Program Files\GitHub CLI\gh.exe`.
