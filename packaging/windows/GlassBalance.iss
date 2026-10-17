; Inno Setup 6 script: run ISCC after PyInstaller creates dist\GlassBalance\.
#define AppVersion "0.3.0-alpha.2"
[Setup]
AppId={{B58CE8F3-85B9-4B7B-BF3F-9139B17BB057}
AppName=GlassBalance
AppVersion={#AppVersion}
AppPublisher=Onimee58
AppPublisherURL=https://github.com/Onimee58/GlassBalance
AppSupportURL=https://github.com/Onimee58/GlassBalance/issues
DefaultDirName={localappdata}\Programs\GlassBalance
DefaultGroupName=GlassBalance
UninstallDisplayIcon={app}\GlassBalance.exe
OutputDir=..\..\installer-out
OutputBaseFilename=GlassBalance-Setup-v{#AppVersion}-Windows-x64
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
SetupIconFile=..\..\glassbalance\assets\glassbalance_icon.ico
CloseApplications=yes
RestartApplications=no
; Only app binaries are installed or uninstalled. User ledger and backups are in AppData.
[Files]
Source: "..\..\dist\GlassBalance\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
[Icons]
Name: "{group}\GlassBalance"; Filename: "{app}\GlassBalance.exe"
Name: "{autodesktop}\GlassBalance"; Filename: "{app}\GlassBalance.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\GlassBalance.exe"; Description: "Launch GlassBalance"; Flags: nowait postinstall skipifsilent
