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



# Phone eject with C language

telefoni eject qilishda biroz kop vaqt talab qilmoqda

```C++
  #include <windows.h>
  #include <setupapi.h>
  #include <cfgmgr32.h>
  #include <stdio.h>
  #include <string.h>
  
  int main(int argc, char *argv[]) {
      if (argc < 2) {
          printf("Xato: phone_id argumenti kiritilmadi.\n");
          printf("Namuna: phone_eject.exe USB\\VID_2717&PID_FF48&MI_00\\7&593ED88&0&0000\n");
          return 1;
      }
  
      // ASCII argumentni Unicode ga aylantirish
      size_t convertedChars = 0;
      wchar_t inputDeviceId[256];
      mbstowcs_s(&convertedChars, inputDeviceId, sizeof(inputDeviceId) / sizeof(wchar_t), argv[1], strlen(argv[1]) + 1);
  
      HDEVINFO deviceInfoSet;
      SP_DEVINFO_DATA deviceInfoData;
      DWORD i;
      CONFIGRET status;
      int found = 0;
      const wchar_t* classInterfaces[] = { L"WPD", L"USB", NULL }; // Tekshiriladigan sinflar
  
      // Har bir sinfni alohida tekshirish
      for (int classIndex = 0; classInterfaces[classIndex] != NULL; classIndex++) {
          deviceInfoSet = SetupDiGetClassDevsW(NULL, classInterfaces[classIndex], NULL, DIGCF_ALLCLASSES | DIGCF_PRESENT);
          if (deviceInfoSet == INVALID_HANDLE_VALUE) {
              printf("%S sinfi uchun ma'lumotlar to'plami olingolmadi: %d\n", classInterfaces[classIndex], GetLastError());
              continue;
          }
  
          deviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
  
          // Har bir qurilmani tekshirish
          for (i = 0; SetupDiEnumDeviceInfo(deviceInfoSet, i, &deviceInfoData); i++) {
              WCHAR devID[256];
              DWORD bufferSize = sizeof(devID);
  
              if (SetupDiGetDeviceInstanceIdW(deviceInfoSet, &deviceInfoData, devID, bufferSize, &bufferSize)) {
                  // Qurilma ID’sida moslikni tekshirish
                  if (wcsstr(devID, L"VID_2717&PID_FF48") != NULL || wcsicmp(devID, inputDeviceId) == 0) {
                      printf("Qurilma topildi: %S (Sinf: %S)\n", devID, classInterfaces[classIndex]);
                      found = 1;
  
                      DEVINST devInst;
                      status = CM_Locate_DevNodeW(&devInst, devID, CM_LOCATE_DEVNODE_NORMAL);
                      if (status != CR_SUCCESS) {
                          printf("Qurilma nodeni topilmadi: %d\n", status);
                          continue;
                      }
  
                      // Qurilmani chiqarish
                      status = CM_Request_Device_EjectW(devInst, NULL, NULL, 0, 0);
                      if (status == CR_SUCCESS) {
                          printf("Qurilma muvaffaqiyatli chiqarildi!\n");
                          SetupDiDestroyDeviceInfoList(deviceInfoSet);
                          return 0;
                      } else {
                          printf("Chiqarishda xatolik: %d\n", status);
                          // Muqobil: Qurilmani faolsizlantirish
                          status = CM_Disable_DevNode(devInst, 0);
                          if (status == CR_SUCCESS) {
                              printf("Qurilma faolsizlantirildi!\n");
                              SetupDiDestroyDeviceInfoList(deviceInfoSet);
                              return 0;
                          } else {
                              printf("Faolsizlantirishda xatolik: %d\n", status);
                          }
                      }
                  }
              }
          }
          SetupDiDestroyDeviceInfoList(deviceInfoSet);
      }
  
      if (!found) {
          printf("Qurilma topilmadi: %S\n", inputDeviceId);
      }
      return 1;
  }
```



wmi Win32_PnPEntity orqali chiqgan ma'limot
```json
    instance of Win32_PnPEntity
    {
        Caption = "D:\\";
        ClassGuid = "{eec5ad98-8080-425f-922a-dabf3de3f69a}";
        CompatibleID = {"wpdbusenum\\fs", "SWD\\Generic"};
        ConfigManagerErrorCode = 0;
        ConfigManagerUserConfig = FALSE;
        CreationClassName = "Win32_PnPEntity";
        Description = "UDisk           ";
        DeviceID = "SWD\\WPDBUSENUM\\_??_USBSTOR#DISK&VEN_GENERAL&PROD_UDISK&REV_5.00#7&339ADA2C&0&_&0#{53F56307-B6BF-11D0-94F2-00A0C91EFB8B}";
        Manufacturer = "General ";
        Name = "D:\\";
        PNPClass = "WPD";
        PNPDeviceID = "SWD\\WPDBUSENUM\\_??_USBSTOR#DISK&VEN_GENERAL&PROD_UDISK&REV_5.00#7&339ADA2C&0&_&0#{53F56307-B6BF-11D0-94F2-00A0C91EFB8B}";
        Present = TRUE;
        Service = "WUDFWpdFs";
        Status = "OK";
        SystemCreationClassName = "Win32_ComputerSystem";
        SystemName = "DESKTOP-8KM6DT0";
    };


```



```json
C:\Users\User-39\Documents\GitHub\usb\.venv\Scripts\python.exe C:\Users\User-39\Documents\GitHub\usb\apps\view\gui.py 
run USB connection search 

instance of Win32_DiskDrive
{
	BytesPerSector = 512;
	Capabilities = {3, 4};
	CapabilityDescriptions = {"Random Access", "Supports Writing"};
	Caption = "TOSHIBA DT01ACA100";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_DiskDrive";
	Description = "Дисковый накопитель";
	DeviceID = "\\\\.\\PHYSICALDRIVE1";
	FirmwareRevision = "MS2OA8A0";
	Index = 1;
	InterfaceType = "IDE";
	Manufacturer = "(Стандартные дисковые накопители)";
	MediaLoaded = TRUE;
	MediaType = "Fixed hard disk media";
	Model = "TOSHIBA DT01ACA100";
	Name = "\\\\.\\PHYSICALDRIVE1";
	Partitions = 4;
	PNPDeviceID = "SCSI\\DISK&VEN_ATA&PROD_TOSHIBA_DT01ACA1\\4&301B2274&0&000200";
	SCSIBus = 0;
	SCSILogicalUnit = 0;
	SCSIPort = 1;
	SCSITargetId = 2;
	SectorsPerTrack = 63;
	SerialNumber = "           325Z11EMS";
	Size = "1000202273280";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-8KM6DT0";
	TotalCylinders = "121601";
	TotalHeads = 255;
	TotalSectors = "1953520065";
	TotalTracks = "31008255";
	TracksPerCylinder = 255;
};


instance of Win32_DiskDrive
{
	BytesPerSector = 512;
	Capabilities = {3, 4};
	CapabilityDescriptions = {"Random Access", "Supports Writing"};
	Caption = "Lexar SSD NM620 256GB";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_DiskDrive";
	Description = "Дисковый накопитель";
	DeviceID = "\\\\.\\PHYSICALDRIVE0";
	FirmwareRevision = "11099";
	Index = 0;
	InterfaceType = "SCSI";
	Manufacturer = "(Стандартные дисковые накопители)";
	MediaLoaded = TRUE;
	MediaType = "Fixed hard disk media";
	Model = "Lexar SSD NM620 256GB";
	Name = "\\\\.\\PHYSICALDRIVE0";
	Partitions = 3;
	PNPDeviceID = "SCSI\\DISK&VEN_NVME&PROD_LEXAR_SSD_NM620\\5&1CFF39D7&0&000000";
	SCSIBus = 0;
	SCSILogicalUnit = 0;
	SCSIPort = 0;
	SCSITargetId = 0;
	SectorsPerTrack = 63;
	SerialNumber = "0000_0006_2401_2676_CAF2_5B02_0000_127F.";
	Size = "256052966400";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-8KM6DT0";
	TotalCylinders = "31130";
	TotalHeads = 255;
	TotalSectors = "500103450";
	TotalTracks = "7938150";
	TracksPerCylinder = 255;
};



```

```json lines
instance of Win32_DiskDrive
{
	BytesPerSector = 512;
	Capabilities = {3, 4, 7};
	CapabilityDescriptions = {"Random Access", "Supports Writing", "Supports Removable Media"};
	Caption = "General UDisk USB Device";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_DiskDrive";
	Description = "Дисковый накопитель";
	DeviceID = "\\\\.\\PHYSICALDRIVE2";
	FirmwareRevision = "5.00";
	Index = 2;
	InterfaceType = "USB";
	Manufacturer = "(Стандартные дисковые накопители)";
	MediaLoaded = TRUE;
	MediaType = "Removable Media";
	Model = "General UDisk USB Device";
	Name = "\\\\.\\PHYSICALDRIVE2";
	Partitions = 1;
	PNPDeviceID = "USBSTOR\\DISK&VEN_GENERAL&PROD_UDISK&REV_5.00\\7&339ADA2C&0&_&0";
	SCSIBus = 0;
	SCSILogicalUnit = 0;
	SCSIPort = 0;
	SCSITargetId = 0;
	SectorsPerTrack = 63;
	SerialNumber = "\t";
	Signature = 1;
	Size = "526417920";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-8KM6DT0";
	TotalCylinders = "64";
	TotalHeads = 255;
	TotalSectors = "1028160";
	TotalTracks = "16320";
	TracksPerCylinder = 255;
};
```


### Micro SD ma'lumotlari

```json lines
instance of Win32_DiskDrive
{
	BytesPerSector = 512;
	Capabilities = {3, 4, 7};
	CapabilityDescriptions = {"Random Access", "Supports Writing", "Supports Removable Media"};
	Caption = "Mass Storage Device USB Device";
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_DiskDrive";
	Description = "Дисковый накопитель";
	DeviceID = "\\\\.\\PHYSICALDRIVE2";
	FirmwareRevision = "1.00";
	Index = 2;
	InterfaceType = "USB";
	Manufacturer = "(Стандартные дисковые накопители)";
	MediaLoaded = TRUE;
	MediaType = "Removable Media";
	Model = "Mass Storage Device USB Device";
	Name = "\\\\.\\PHYSICALDRIVE2";
	Partitions = 1;
	PNPDeviceID = "USBSTOR\\DISK&VEN_MASS&PROD_STORAGE_DEVICE&REV_1.00\\121220160204&0";
	SCSIBus = 0;
	SCSILogicalUnit = 0;
	SCSIPort = 0;
	SCSITargetId = 0;
	SectorsPerTrack = 63;
	SerialNumber = "121220160204";
	Signature = 0;
	Size = "127861977600";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-8KM6DT0";
	TotalCylinders = "15545";
	TotalHeads = 255;
	TotalSectors = "249730425";
	TotalTracks = "3963975";
	TracksPerCylinder = 255;
};
        
        
instance of Win32_PnPEntity
{
	Caption = "Mass Storage Device USB Device";
	ClassGuid = "{4d36e967-e325-11ce-bfc1-08002be10318}";
	CompatibleID = {"USBSTOR\\Disk", "USBSTOR\\RAW", "GenDisk"};
	ConfigManagerErrorCode = 0;
	ConfigManagerUserConfig = FALSE;
	CreationClassName = "Win32_PnPEntity";
	Description = "Дисковый накопитель";
	DeviceID = "USBSTOR\\DISK&VEN_MASS&PROD_STORAGE_DEVICE&REV_1.00\\121220160204&0";
	HardwareID = {"USBSTOR\\DiskMass____Storage_Device__1.00", "USBSTOR\\DiskMass____Storage_Device__", "USBSTOR\\DiskMass____", "USBSTOR\\Mass____Storage_Device__1", "Mass____Storage_Device__1", "USBSTOR\\GenDisk", "GenDisk"};
	Manufacturer = "(Стандартные дисковые накопители)";
	Name = "Mass Storage Device USB Device";
	PNPClass = "DiskDrive";
	PNPDeviceID = "USBSTOR\\DISK&VEN_MASS&PROD_STORAGE_DEVICE&REV_1.00\\121220160204&0";
	Present = TRUE;
	Service = "disk";
	Status = "OK";
	SystemCreationClassName = "Win32_ComputerSystem";
	SystemName = "DESKTOP-8KM6DT0";
};

```