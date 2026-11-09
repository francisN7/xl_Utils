; Instalador por usuário do xl_Utils (Windows x64).
; Compilar com scripts/build_windows.ps1 (iscc) ou:
;   iscc /DAppVersion=0.3.0 /DSourceDir=build\app\xl_Utils /DOutputDir=build\installer installer\xl_utils.iss

#ifndef AppVersion
  #define AppVersion "0.3.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\build\app\xl_Utils"
#endif
#ifndef OutputDir
  #define OutputDir "..\build\installer"
#endif

#define AppName "xl_Utils"
#define AppPublisher "francisN7"
#define AppExeName "xl_Utils.exe"
#define AppId "{{7C1E2A54-9B3D-4F6A-9E71-2D5C8B4A1F03}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#OutputDir}
OutputBaseFilename={#AppName}-{#AppVersion}-setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
MinVersion=10.0

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Fecha uma instância aberta antes de apagar arquivos; ignorado se não houver.
Filename: "{sys}\taskkill.exe"; Parameters: "/IM {#AppExeName} /F"; Flags: runhidden; RunOnceId: "FechaXlUtils"

[UninstallDelete]
; Desinstalação destrutiva por decisão do dono: some tudo o que o app criou,
; inclusive contas, tokens e preferências em %LOCALAPPDATA%\xl_utils.
; O cache do cliente Flet (~/.flet) é apagado em [Code], identificado pelo
; fingerprint do zip empacotado, para não afetar outros apps Flet.
; Arquivos exportados pelo usuário para pastas escolhidas não são tocados.
Type: filesandordirs; Name: "{localappdata}\xl_utils"
Type: filesandordirs; Name: "{%USERPROFILE}\.xl_utils"
Type: filesandordirs; Name: "{app}"

[Code]
var
  FletFingerprint: String;

function ReadFletFingerprint(): String;
var
  Lines: TArrayOfString;
  Archive, Hash: String;
  Sep: Integer;
begin
  // O flet pack grava <sha256> <tamanho> ao lado do zip do cliente; o cliente
  // usa os 12 primeiros dígitos no nome da pasta extraída.
  Archive := ExpandConstant('{app}\_internal\flet_desktop\app\flet-windows.zip');
  Result := '';
  if LoadStringsFromFile(Archive + '.sha256', Lines) and
     (GetArrayLength(Lines) > 0) then
  begin
    Hash := Trim(Lines[0]);
    Sep := Pos(' ', Hash);
    if Sep > 0 then
      Hash := Copy(Hash, 1, Sep - 1);
    if Length(Hash) >= 12 then
      Result := Lowercase(Copy(Hash, 1, 12));
  end;
  if (Result = '') and FileExists(Archive) then
    Result := Lowercase(Copy(GetSHA256OfFile(Archive), 1, 12));
end;

procedure StopFletClients();
var
  Params: String;
  Code: Integer;
begin
  if FletFingerprint = '' then
    Exit;
  // Só mata o cliente extraído deste app: o caminho do processo contém o
  // fingerprint da pasta de cache.
  Params :=
    '-NoProfile -ExecutionPolicy Bypass -Command "Get-Process flet ' +
    '-ErrorAction SilentlyContinue | Where-Object { $_.Path -like ' +
    '''*\.flet\client\flet-desktop-*-' + FletFingerprint + '*'' } | ' +
    'Stop-Process -Force -ErrorAction SilentlyContinue"';
  Exec('powershell.exe', Params, '', SW_HIDE, ewWaitUntilTerminated, Code);
end;

procedure RemoveFletCache();
var
  ClientRoot, CacheDir: String;
  FindRec: TFindRec;
begin
  if FletFingerprint = '' then
    Exit;
  ClientRoot := ExpandConstant('{%USERPROFILE}\.flet\client');
  if not DirExists(ClientRoot) then
    Exit;
  if FindFirst(ClientRoot + '\flet-desktop-*-' + FletFingerprint, FindRec) then
  begin
    try
      repeat
        if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
        begin
          CacheDir := ClientRoot + '\' + FindRec.Name;
          DelTree(CacheDir, True, True, True);
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
  // Remove as pastas vazias; se ainda houver cache de outro app Flet, ficam.
  RemoveDir(ClientRoot);
  RemoveDir(ExpandConstant('{%USERPROFILE}\.flet'));
end;

function InitializeUninstall(): Boolean;
begin
  FletFingerprint := ReadFletFingerprint();
  Result := MsgBox(
    'A desinstalação vai apagar TODOS os dados do xl_Utils: contas, tokens do ' +
    'Drive, preferências, cache e logs.' + Chr(13) + Chr(10) + Chr(13) + Chr(10) +
    'Planilhas que você exportou para suas próprias pastas não serão tocadas.' +
    Chr(13) + Chr(10) + Chr(13) + Chr(10) + 'Continuar?',
    mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    StopFletClients();
    RemoveFletCache();
  end;
end;
