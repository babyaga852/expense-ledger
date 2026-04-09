[Setup]
AppName=Expense Ledger
AppVersion=1.0.0
AppPublisher=Vasudeo Bhoyar
AppPublisherURL=https://github.com/babyaga852/expense-ledger
AppSupportURL=https://github.com/babyaga852/expense-ledger
AppUpdatesURL=https://github.com/babyaga852/expense-ledger
DefaultDirName={autopf}\ExpenseLedger
DefaultGroupName=Expense Ledger
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=ExpenseLedger_Setup_v1.0
SetupIconFile=compiler:default
Compression=lzma/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ExpenseLedger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\ExpenseLedger\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Expense Ledger"; Filename: "{app}\ExpenseLedger.exe"
Name: "{group}\Uninstall Expense Ledger"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Expense Ledger"; Filename: "{app}\ExpenseLedger.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ExpenseLedger.exe"; Description: "{cm:LaunchProgram,Expense Ledger}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
end;
