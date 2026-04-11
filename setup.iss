[Setup]
AppName=Expense Ledger
AppVersion=1.1.0
AppPublisher=Vasudeo Bhoyar
AppPublisherURL=https://expense-ledger.onrender.com
AppSupportURL=https://github.com/babyaga852/expense-ledger
AppUpdatesURL=https://github.com/babyaga852/expense-ledger
DefaultDirName={autopf}\ExpenseLedger
DefaultGroupName=Expense Ledger
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=ExpenseLedger_Setup_v1.1_Windows
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
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ExpenseLedger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Expense Ledger";           Filename: "{app}\ExpenseLedger.exe"
Name: "{group}\{cm:UninstallProgram,Expense Ledger}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Expense Ledger";     Filename: "{app}\ExpenseLedger.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ExpenseLedger.exe"; Description: "{cm:LaunchProgram,Expense Ledger}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nExpense Ledger is a personal finance tracker with:%n  - Expense & Income tracking%n  - Dashboard with charts%n  - Export to Excel & PDF%n  - Dark/Light mode%n  - Live web app at expense-ledger.onrender.com%n%nClick Next to continue.

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
