#define MyAppName "Sinister Inc. Stringtable Changer"

[Setup]
AppName=MyAppName
AppVersion=1.0.0
DefaultDirName={pf}\SinisterInc_StringtableChanger
DisableDirPage=no
OutputDir=dist
OutputBaseFilename=SinisterInc_StringtableChanger_Installer

[Files]
Source: "dist\SinisterInc_StringtableChanger.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "stringtables\*"; DestDir: "{app}\stringtables"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\SinisterInc_StringtableChanger.exe"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\SinisterInc_StringtableChanger.exe"
