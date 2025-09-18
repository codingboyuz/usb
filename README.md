# Eject phone

```python
import subprocess


def switch_to_charge_only():
    subprocess.run(["adb", "shell", "svc", "usb", "setFunctions", "none"])
    print("✅ Qurilma endi faqat zaryad rejimida (MTP uzildi)")

```

# Check Phone 
```python

import wmi
c = wmi.WMI()
for device in c.Win32_PnPEntity():
    if device.PNPClass == "WPD" and "MTP" in str(device.CompatibleID):
        print(f"📱 Telefon topildi: {device.Name}")
        print(f"PNPDeviceID: {device.PNPDeviceID}")
        print("⚠️ Bu qurilmani chiqarib bo'lmaydi (MTP protokoli)")
```



# USB

```json
{
	BytesPerSector = 512;
	Capabilities = {3, 4, 7};
	CapabilityDescriptions = {"Random Access", "Supports Writing", "Supports Removable Media"};
	Caption = "VendorCo ProductCode USB Device";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_DiskDrive";
	Description = "Дисковый накопитель";
	DeviceID = "\\\\.\\PHYSICALDRIVE1";
	FirmwareRevision = "2.00";
	Index = 1;
	InterfaceType = "USB";
	Manufacturer = "(Стандартные дисковые накопители)";
	MediaLoaded = TRUE;
	MediaType = "Removable Media";
	Model = "VendorCo ProductCode USB Device";
	Name = "\\\\.\\PHYSICALDRIVE1";
	Partitions = 2;
	PNPDeviceID = "USBSTOR\\DISK&VEN_VENDORCO&PROD_PRODUCTCODE&REV_2.00\\7956101095918431346&0";
	SCSIBus = 0;
	SCSILogicalUnit = 0;
	SCSIPort = 0;
	SCSITargetId = 0;
	SectorsPerTrack = 63;
	SerialNumber = "7956101095918431346";
	Size = "31453470720";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-MMT8C66";
	TotalCylinders = "3824";
	TotalHeads = 255;
	TotalSectors = "61432560";
	TotalTracks = "975120";
	TracksPerCylinder = 255;
};
```
endi iss ni qilib ber
[Setup]
AppName=My Secure App
AppVersion=1.0
DefaultDirName={pf}\MySecureApp
DefaultGroupName=My Secure App
OutputDir=output
OutputBaseFilename=MySecureAppSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupLogging=yes

[Files]
Source: "MyApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "required_dll1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "required_dll2.dll"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Dastur o'zini avtomatik ishga tushiradi
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "MySecureApp"; ValueData: "{app}\MyApp.exe"; Flags: uninsdeletevalue

; O'chirishni blokirovka qilish uchun maxsus registry kaliti
Root: HKLM; Subkey: "SOFTWARE\MySecureApp"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsneveruninstall

; Windows xizmati sifatida ro'yxatdan o'tkazish
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\MySecureApp"; ValueType: string; ValueName: "DisplayName"; ValueData: "My Secure App Service"; Flags: uninsneveruninstall
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\MySecureApp"; ValueType: string; ValueName: "ImagePath"; ValueData: "{app}\MyApp.exe --service"; Flags: uninsneveruninstall
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\MySecureApp"; ValueType: dword; ValueName: "Start"; ValueData: "2"; Flags: uninsneveruninstall

[Run]
Filename: "{app}\MyApp.exe"; Parameters: "--install"; Flags: nowait postinstall runhidden; Description: "Dasturni ishga tushirish"

[UninstallRun]
; O'chirish jarayonida parol so'rash uchun
Filename: "{app}\MyApp.exe"; Parameters: "--uninstall"; Flags: runhidden

[Code]
var
  PasswordPage: TInputQueryWizardPage;

procedure InitializeWizard();
begin
  // Parol sahifasini yaratish
  PasswordPage := CreateInputQueryPage(wpWelcome,
    'Parolni kiriting', 'Dasturni o''rnatish uchun maxsus parol kerak',
    'Iltimos, administrator parolini kiriting:');
  PasswordPage.Add('Parol:', False);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Parolni tekshirish
  if CurPageID = PasswordPage.ID then
  begin
    if PasswordPage.Values[0] <> 'sizning_maxfiy_parol' then
    begin
      MsgBox('Noto''g''ri parol! Dasturni o''rnatish mumkin emas.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  Password: String;
begin
  Result := True;
  
  // O'chirishda parol so'rash
  if not InputQuery('Parol', 'Dasturni o''chirish uchun parolni kiriting:', Password) then
    Result := False
  else if Password <> 'sizning_maxfiy_parol' then
  begin
    MsgBox('Noto''g''ri parol! Dasturni o''chirish mumkin emas.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Dasturni xizmat sifatida ishga tushirish
    Exec('sc', 'create MySecureApp binPath= "' + ExpandConstant('{app}\MyApp.exe') + '" start= auto', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('sc', 'start MySecureApp', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Dastur fayllariga ruxsatlarni o'zgartirish
    Exec('icacls', ExpandConstant('"{app}\*"') + ' /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F /grant:r *S-1-5-18:(OI)(CI)F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;


shuni to'g'rila ikida dasturga untitled2.exe va usb_killer.exe uchun qil shartlar o'zgarmagan
