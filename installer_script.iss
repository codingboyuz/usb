[Setup]
AppName=UsbGuard
AppVersion=1.0
DefaultDirName={commonappdata}\UsbGuard
DefaultGroupName=UsbGuard
OutputDir=output
OutputBaseFilename=UsbGuardInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupLogging=yes
Uninstallable=yes

[Files]
Source: "installer\usb_killer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer\untitled2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer\gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Autostart ro'yxatiga qo'shish
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "UsbGuardWatcher"; ValueData: "{app}\usb_killer.exe"; Flags: uninsdeletevalue

; Qo‘shimcha sozlamalar uchun maxsus kalit
Root: HKLM; Subkey: "SOFTWARE\UsbGuard"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsneveruninstall


[Run]
Filename: "{app}\usb_killer.exe"; Flags: nowait runhidden
Filename: "icacls"; Parameters: """{app}\usb_killer.exe"" /deny Everyone:(DE)"; Flags: runhidden
Filename: "icacls"; Parameters: """{app}\untitled2.exe"" /deny Everyone:(DE)"; Flags: runhidden
Filename: "icacls"; Parameters: """{app}\gui.exe"" /deny Everyone:(DE)"; Flags: runhidden

[UninstallRun]
Filename: "{app}\gui.exe"; Flags: nowait runhidden

[Code]
var
  PasswordPage: TInputQueryWizardPage;

procedure InitializeWizard();
begin
  PasswordPage := CreateInputQueryPage(wpWelcome,
    'Parolni kiriting', 'Ushbu dasturni o''rnatish uchun parol kerak.',
    'Iltimos, parolni kiriting:');
  PasswordPage.Add('Parol:', False);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = PasswordPage.ID then
  begin
    if PasswordPage.Values[0] <> 'usb2024' then
    begin
      MsgBox('Noto''g''ri parol. O''rnatish bekor qilindi.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  // Uninstall jarayonida biz gui.exe orqali parol soraymiz
  MsgBox('🛡 Parol oynasi ochiladi. Iltimos, ruxsat bering.', mbInformation, MB_OK);
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    Exec('sc', 'create UsbGuard binPath= "' + ExpandConstant('{app}\usb_killer.exe') + '" start= auto', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('sc', 'start UsbGuard', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    Exec('icacls', ExpandConstant('"{app}\usb_killer.exe"') + ' /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F /grant:r *S-1-5-18:(OI)(CI)F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('icacls', ExpandConstant('"{app}\untitled2.exe"') + ' /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F /grant:r *S-1-5-18:(OI)(CI)F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('icacls', ExpandConstant('"{app}\gui.exe"') + ' /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F /grant:r *S-1-5-18:(OI)(CI)F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
