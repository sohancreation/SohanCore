#define MyAppName "SohanCore"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SohanCore"
#define MyAppExeName "SohanCoreUI.exe"

[Setup]
AppId={{F3FA496A-2C10-46E4-A723-E47E72A743E4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\SohanCore
DefaultGroupName=SohanCore
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=SohanCore-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\SohanCoreUI\*"; DestDir: "{app}\SohanCoreUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\SohanCore\*"; DestDir: "{app}\SohanCore"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\.env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\run_sohancore_background.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\PACKAGING_WINDOWS.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SohanCore"; Filename: "{app}\SohanCoreUI\{#MyAppExeName}"
Name: "{group}\Run SohanCore In Background"; Filename: "{app}\run_sohancore_background.bat"
Name: "{autodesktop}\SohanCore"; Filename: "{app}\SohanCoreUI\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\SohanCoreUI\{#MyAppExeName}"; Description: "Launch SohanCore"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvSource: string;
  EnvTarget: string;
begin
  if CurStep = ssPostInstall then
  begin
    EnvSource := ExpandConstant('{app}\.env.example');
    EnvTarget := ExpandConstant('{app}\.env');
    if (FileExists(EnvSource)) and (not FileExists(EnvTarget)) then
      FileCopy(EnvSource, EnvTarget, False);
  end;
end;
