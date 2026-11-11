# Gera o instalador Windows a partir do wheel da versão corrente.
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -SkipInstaller
#
# Requisitos: uv, Inno Setup 6 (iscc no PATH) e o ícone em assets/icon.ico.
# O build usa um venv limpo em artifacts/venv, instala o wheel e empacota com
# flet pack + PyInstaller. Nada de .venv, output/ ou cache do Drive entra.
# artifacts/ fica fora de build/ porque o flet pack apaga a pasta build/.

param(
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$version = (& uv version --short).Trim()
if (-not $version) {
    throw "Não foi possível ler a versão do pyproject.toml."
}
if (-not (Test-Path "assets/icon.ico")) {
    throw "assets/icon.ico não existe; gere com scripts/make_icons.py --pick N."
}

$work = Join-Path $root "artifacts"
$venv = Join-Path $work "venv"
$app = Join-Path $work "app"
$wheelDir = Join-Path $work "wheel"
$installerDir = Join-Path $work "installer"

Write-Host "== Limpando artefatos =="
foreach ($path in @($venv, $app, $wheelDir, $installerDir)) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
    }
}

Write-Host "== Gerando o wheel $version =="
& uv build --wheel --out-dir $wheelDir
$wheel = Get-ChildItem $wheelDir -Filter "*.whl" | Select-Object -First 1
if (-not $wheel) {
    throw "uv build não gerou wheel."
}

Write-Host "== Criando venv limpo e instalando o wheel =="
& uv venv --python 3.15 $venv
& uv pip install --python (Join-Path $venv "Scripts/python.exe") $wheel.FullName pyinstaller "flet[cli]>=1.0.5"

# flet-cli 1.1.2 quebra no Windows ao reanexar o overlay do flet.exe:
# open(exe_path, "ab", encoding="utf-8") é inválido em modo binário. O patch é
# idempotente e falha alto se o trecho não existir (versão diferente do Flet).
$winUtils = Join-Path $venv "Lib/site-packages/flet_cli/__pyinstaller/win_utils.py"
$content = Get-Content $winUtils -Raw
if ($content.Contains('open(exe_path, "ab", encoding="utf-8")')) {
    $content = $content.Replace(
        'open(exe_path, "ab", encoding="utf-8")',
        'open(exe_path, "ab")'
    )
    Set-Content -Path $winUtils -Value $content -NoNewline -Encoding UTF8
    Write-Host "== Patch do flet-cli 1.1.2 aplicado =="
} elseif (-not $content.Contains('open(exe_path, "ab")')) {
    throw "Patch do flet-cli não encontrado; confira a versão do Flet."
}

Write-Host "== Empacotando com flet pack (onedir) =="
$configs = Join-Path $venv "Lib/site-packages/xl_utils/configs"
# O _rust.pyd do cryptography importa python3t.dll, que o Python 3.15 instala
# em abi3t-compat/ e só adiciona ao path no interpretador normal. Sem copiar
# esse shim, o app empacotado morre no import do google-auth.
$python3t = (& (Join-Path $venv "Scripts/python.exe") -c "import pathlib, sys; print(pathlib.Path(sys.base_prefix) / 'abi3t-compat' / 'python3t.dll')").Trim()
if (-not (Test-Path $python3t)) {
    throw "python3t.dll não encontrado em $python3t (abi3t-compat do Python 3.15)."
}
& (Join-Path $venv "Scripts/flet.exe") pack scripts/pack_entry.py `
    -n "xl_Utils" `
    -D `
    --distpath $app `
    --icon "assets/icon.ico" `
    --add-data "$configs;xl_utils/configs" `
    --add-binary "$python3t;." `
    --product-name "xl_Utils" `
    --file-description "Utilitários de planilha" `
    --product-version $version `
    --file-version $version `
    --company-name "francisN7" `
    -y `
    -- --copy-metadata xl-utils --copy-metadata flet --copy-metadata pandas

$exe = Join-Path $app "xl_Utils/xl_Utils.exe"
if (-not (Test-Path $exe)) {
    throw "O executável não foi gerado em $exe."
}

# A área de plugins usa tarfile + lzma no mesmo processo. O PyInstaller precisa
# embutir o módulo compilado _lzma; sem ele, instalar/ler pacote quebra no exe.
$lzma = Get-ChildItem (Join-Path $app "xl_Utils") -Recurse -Filter "_lzma*.pyd" |
    Select-Object -First 1
if (-not $lzma) {
    throw "Módulo _lzma não foi embutido no bundle do app."
}
Write-Host "Módulo lzma: $($lzma.FullName)"

if ($SkipInstaller) {
    Write-Host "Build pronto: $exe"
    exit 0
}

Write-Host "== Gerando o instalador =="
New-Item -ItemType Directory -Force -Path $installerDir | Out-Null
$iscc = (Get-Command iscc -ErrorAction SilentlyContinue).Source
if (-not $iscc) {
    $candidate = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if (Test-Path $candidate) {
        $iscc = $candidate
    } else {
        throw "iscc não encontrado; instale o Inno Setup 6."
    }
}
& $iscc `
    "/DAppVersion=$version" `
    "/DSourceDir=$app\xl_Utils" `
    "/DOutputDir=$installerDir" `
    "installer/xl_utils.iss"

$setup = Get-ChildItem $installerDir -Filter "*.exe" | Select-Object -First 1
if (-not $setup) {
    throw "O instalador não foi gerado."
}
$hash = (Get-FileHash $setup.FullName -Algorithm SHA256).Hash.ToLower()
$checksum = Join-Path $installerDir "SHA256SUMS.txt"
"$hash  $($setup.Name)" | Set-Content -Path $checksum -Encoding ASCII

Write-Host "Instalador: $($setup.FullName)"
Write-Host "Tamanho: $([math]::Round($setup.Length / 1MB, 1)) MB"
Write-Host "SHA-256: $hash"
