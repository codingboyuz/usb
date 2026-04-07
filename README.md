# Eject phone
● ---                                
  Natija — Arxitektura                                                                    

  USB qurilma ulanadi                                                                                                                                                                                                               
          │
          ▼                                                                                                                                                                                                                         
  ┌───────────────────────────┐                                                                                                                                                                                                   
  │  KMDF Filter Driver       │  ← KERNEL daraja (0 ms kechikish)
  │  (UsbFilter.sys)          │     IRP_MN_START_DEVICE ushlanadi
  │  Serial → whitelist?      │     Yo'q → STATUS_ACCESS_DENIED
  │  Ha → IRP o'tkaziladi     │     Qurilma hech qachon ishga tushmaydi
  └───────────────────────────┘
          │ (ruxsat etilgan qurilma)
          ▼
  ┌───────────────────────────┐
  │  Python UsbWatcher        │  ← USER daraja (WMI, ~500ms)
  │  device_classifier.py     │     Qurilma turini aniq aniqlaydi
  │  device_logger.py         │     Fayl + DB ga log yozadi
  │  usb_watcher.py           │     GUI'ga xabar beradi
  └───────────────────────────┘

  ---
  Qurilma turi farqlash jadvali

  ┌───────────────────┬───────────────┬─────────────────┬─────────────────────┐
  │      Qurilma      │ InterfaceType │    MediaType    │ Model da kalit so'z │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ USB Flash         │ USB           │ Removable Media │ —                   │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ Tashqi HDD        │ USB           │ Fixed/External  │ —                   │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ Tashqi SSD        │ USB           │ Fixed           │ SSD                 │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ M.2 adapter       │ USB           │ Fixed           │ NVMe, M.2, M2       │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ Tashqi HDD (SCSI) │ SCSI          │ —               │ —                   │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ Telefon MTP       │ —             │ —               │ PNPClass=WPD        │
  ├───────────────────┼───────────────┼─────────────────┼─────────────────────┤
  │ Telefon ADB       │ —             │ —               │ Service=WinUSB+ADB  │
  └───────────────────┴───────────────┴─────────────────┴─────────────────────┘

  ---
  KMDF driver qurilish uchun kerakli dasturlar

  # 1. O'rnatish
  Visual Studio 2022  →  https://visualstudio.microsoft.com/
  WDK (Windows Driver Kit) → https://learn.microsoft.com/windows-hardware/drivers/download-the-wdk

  # 2. Test rejimini yoqish (imzosiz driver uchun)
  bcdedit /set testsigning on
  # Kompyuterni qayta yuklash

  # 3. Driverni o'rnatish
  pnputil /add-driver UsbFilter.inf /install

  # 4. DebugView bilan KdPrint loglarini ko'rish
  # DebugView → https://learn.microsoft.com/sysinternals/downloads/debugview

  Muhim: KMDF driver avval Virtual Machine (VMware/VirtualBox) da sinab ko'ring — noto'g'ri driver BSOD chiqarishi mumkin.

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


# Bu ko'd windows api bilan ishlaydi


```python
import threading
import time
import win32con
import win32gui
import pythoncom
import wmi
from datetime import datetime
from apps.core.usb_watcher import UsbWatcher

class DeviceMonitor:
    def __init__(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "DeviceChangeMonitor"
        self.class_atom = win32gui.RegisterClass(wc)
        self.connection_type = ConnectionType()

        # Ko‘rinmas oyna yaratish
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "HiddenDeviceMonitor",
            0, 0, 0, 0, 0, 0, 0, 0, None
        )

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            if wparam == win32con.DBT_DEVICEARRIVAL:
                print(f"🔌 [{datetime.now().strftime('%H:%M:%S')}] Qurilma ulandi.")
                threading.Thread(target=self.connection_type.connection_device, daemon=True).start()

            elif wparam == win32con.DBT_DEVNODES_CHANGED:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Qurilma drayveri yangilandi.")
                threading.Timer(0.3, lambda: threading.Thread(target=self.connection_type.connection_device, daemon=True).start()).start()

            elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Qurilma uzildi.")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    @staticmethod
    def run():
        print("Start monitoring (real-time)...")
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.05)


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.run()

```


c++ ko'di 
```c++
// // Windows API ni har doim Unicode (Wide-Character) versiyalarini ishlatishga majburlash
// #define UNICODE
// #define _UNICODE
//
// #include <windows.h>
// #include <iostream>
// #include <dbt.h>        // USB hodisalari uchun
// #include <initguid.h>
// #include <setupapi.h>   // SetupAPI funksiyalari uchun
// #include <cfgmgr32.h>   // Configuration Manager funksiyalari uchun
// #include <string>
// #include <io.h>
// #include <fcntl.h>
// #include <cstdio> // _fileno uchun
//
//
// // USB qurilmalar interfeysi GUID si.
// DEFINE_GUID(GUID_DEVINTERFACE_USB_DEVICE,
//             0xA5DCBF10L, 0x6530, 0x11D2, 0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB9, 0x51, 0xED);
//
//
// // --------------------------------------------------------------------------
// // PnP Ma'lumotlarini (VID/PID) Qurilma Yo'lidan Ajratib Olish
// // --------------------------------------------------------------------------
// // --------------------------------------------------------------------------
// // PnP Ma'lumotlarini (VID/PID) Qurilma Yo'lidan Ajratib Olish (Tuzatilgan)
// // --------------------------------------------------------------------------
// std::wstring extract_vid_pid(const std::wstring &devicePath) {
//     // vid_ qismining boshlanishini qidirish
//     size_t vidStartPos = devicePath.find(L"VID_");
//
//     // Agar topilmasa, kichik harf bilan ham qidirib ko'ramiz (ba'zi tizimlarda farq qilishi mumkin)
//     if (vidStartPos == std::wstring::npos) {
//         vidStartPos = devicePath.find(L"vid_");
//     }
//
//     if (vidStartPos == std::wstring::npos) {
//         return L"Noma'lum VID/PID (VID topilmadi)";
//     }
//
//     // vid_ dan keyin 4ta belgi VID bo'ladi
//     std::wstring vid = devicePath.substr(vidStartPos + 4, 4);
//
//     // pid_ qismining boshlanishini qidirish
//     size_t pidStartPos = devicePath.find(L"PID_");
//
//     if (pidStartPos == std::wstring::npos) {
//         pidStartPos = devicePath.find(L"pid_");
//     }
//
//     if (pidStartPos == std::wstring::npos) {
//         return L"Noma'lum VID/PID (PID topilmadi)";
//     }
//
//     // pid_ dan keyin 4ta belgi PID bo'ladi
//     std::wstring pid = devicePath.substr(pidStartPos + 4, 4);
//
//     return L"VID: " + vid + L", PID: " + pid;
// }
//
// // --------------------------------------------------------------------------
// // Qurilmaning qo'shimcha PnP ma'lumotlarini olish (Hardware ID, Tavsif)
// // --------------------------------------------------------------------------
// void get_full_pnp_info(const std::wstring &devicePath) {
//     // Qurilmalar ro'yxatini shakllantirish
//     HDEVINFO hDevInfo = SetupDiGetClassDevs(
//         &GUID_DEVINTERFACE_USB_DEVICE,
//         NULL,
//         NULL,
//         DIGCF_PRESENT | DIGCF_DEVICEINTERFACE
//     );
//
//     if (hDevInfo == INVALID_HANDLE_VALUE) return;
//
//     SP_DEVICE_INTERFACE_DATA deviceInterfaceData = {sizeof(SP_DEVICE_INTERFACE_DATA)};
//     DWORD memberIndex = 0;
//
//     // Qurilmalar ro'yxatini aylanib chiqish
//     while (SetupDiEnumDeviceInterfaces(hDevInfo, NULL, &GUID_DEVINTERFACE_USB_DEVICE, memberIndex,
//                                        &deviceInterfaceData)) {
//         memberIndex++;
//
//         DWORD requiredSize = 0;
//         SetupDiGetDeviceInterfaceDetail(hDevInfo, &deviceInterfaceData, NULL, 0, &requiredSize, NULL);
//
//         if (GetLastError() == ERROR_INSUFFICIENT_BUFFER) {
//             // Zarur bufer hajmini ajratish
//             SP_DEVICE_INTERFACE_DETAIL_DATA *detailData = (SP_DEVICE_INTERFACE_DETAIL_DATA *) malloc(requiredSize);
//             if (!detailData) continue;
//             detailData->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);
//
//             SP_DEVINFO_DATA deviceInfoData = {sizeof(SP_DEVINFO_DATA)};
//
//             if (SetupDiGetDeviceInterfaceDetail(hDevInfo, &deviceInterfaceData, detailData, requiredSize, NULL,
//                                                 &deviceInfoData)) {
//                 // Topilgan qurilma interfeysi yo'lini solishtirish
//                 if (devicePath == detailData->DevicePath) {
//                     WCHAR buffer[1024];
//                     DWORD size = sizeof(buffer);
//
//                     std::wcout << L"  - To'liq PnP ma'lumotlari: " << std::endl;
//
//                     // 1. Hardware ID (Apparat ID)ni olish
//                     if (SetupDiGetDeviceRegistryProperty(
//                         hDevInfo, &deviceInfoData, SPDRP_HARDWAREID,
//                         NULL, (PBYTE) buffer, size, NULL)) {
//                         std::wcout << L"    > Hardware ID: " << buffer << std::endl;
//                     }
//
//                     // 2. Qurilmaning Tavsifini olish
//                     if (SetupDiGetDeviceRegistryProperty(
//                         hDevInfo, &deviceInfoData, SPDRP_DEVICEDESC,
//                         NULL, (PBYTE) buffer, size, NULL)) {
//                         std::wcout << L"    > Tavsifi: " << buffer << std::endl;
//                     }
//
//                     // 3. Qurilma Instansiyasi Yo'lini olish
//                     if (SetupDiGetDeviceRegistryProperty(
//                         hDevInfo, &deviceInfoData, SPDRP_SERVICE,
//                         NULL, (PBYTE) buffer, size, NULL)) {
//                         std::wcout << L"    > Xizmat/Drayver: " << buffer << std::endl;
//                     }
//
//                     free(detailData);
//                     SetupDiDestroyDeviceInfoList(hDevInfo);
//                     return; // Ma'lumotlar topildi
//                 }
//             }
//             free(detailData);
//         }
//     }
//
//     SetupDiDestroyDeviceInfoList(hDevInfo);
// }
//
//
// // --------------------------------------------------------------------------
// // Hodisalarni Qayta Ishlash Funksiyasi
// // --------------------------------------------------------------------------
//
// void HandleDeviceChange(WPARAM wParam, LPARAM lParam) {
//     if (wParam == DBT_DEVICEARRIVAL) {
//         DEV_BROADCAST_HDR *dbh = (DEV_BROADCAST_HDR *) lParam;
//
//         if (dbh->dbch_devicetype == DBT_DEVTYP_DEVICEINTERFACE) {
//             DEV_BROADCAST_DEVICEINTERFACE *dbdi =
//                     (DEV_BROADCAST_DEVICEINTERFACE *) dbh;
//
//             std::wstring devicePath(dbdi->dbcc_name);
//             std::wstring vidPidInfo = extract_vid_pid(devicePath);
//
//             std::wcout << L"\n==============================================" << std::endl;
//             std::wcout << L"[+] USB Qurilmasi Ulandi!" << std::endl;
//             std::wcout << L"    PnP Interfeys Yo'li: " << devicePath << std::endl;
//             std::wcout << L"    Asosiy ID: " << vidPidInfo << std::endl;
//
//             get_full_pnp_info(devicePath);
//             std::wcout << L"==============================================" << std::endl;
//         }
//     } else if (wParam == DBT_DEVICEREMOVECOMPLETE) {
//         DEV_BROADCAST_HDR *dbh = (DEV_BROADCAST_HDR *) lParam;
//         if (dbh->dbch_devicetype == DBT_DEVTYP_DEVICEINTERFACE) {
//             DEV_BROADCAST_DEVICEINTERFACE *dbdi =
//                     (DEV_BROADCAST_DEVICEINTERFACE *) dbh;
//
//             std::wcout << L"\n[-] USB Qurilmasi Uzildi: " << dbdi->dbcc_name << std::endl;
//         }
//     }
// }
//
//
// // --------------------------------------------------------------------------
// // Oyna Protsedurasi (WndProc) - Xabarlarni Qayta Ishlash
// // --------------------------------------------------------------------------
//
// LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
//     switch (message) {
//         case WM_DEVICECHANGE:
//             HandleDeviceChange(wParam, lParam);
//             return TRUE;
//
//         case WM_CLOSE:
//             PostQuitMessage(0);
//             break;
//
//         default:
//             return DefWindowProc(hWnd, message, wParam, lParam);
//     }
//     return 0;
// }
//
//
// // --------------------------------------------------------------------------
// // USB Hodisalariga Obuna Bo'lish
// // --------------------------------------------------------------------------
//
// HDEVNOTIFY RegisterForUsbNotifications(HWND hWnd) {
//     DEV_BROADCAST_DEVICEINTERFACE NotificationFilter;
//
//     ZeroMemory(&NotificationFilter, sizeof(NotificationFilter));
//     NotificationFilter.dbcc_size = sizeof(DEV_BROADCAST_DEVICEINTERFACE);
//     NotificationFilter.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
//     NotificationFilter.dbcc_classguid = GUID_DEVINTERFACE_USB_DEVICE;
//
//     return RegisterDeviceNotification(
//         hWnd,
//         &NotificationFilter,
//         DEVICE_NOTIFY_WINDOW_HANDLE
//     );
// }
//
// // --------------------------------------------------------------------------
// // Asosiy Kirish Nuqtasi
// // --------------------------------------------------------------------------
//
// int main() {
//     // Konsol chiqqisini Unicode rejimiga o'rnatish
//     _setmode(_fileno(stdout), _O_U16TEXT);
//
//     std::wcout << L"==============================================" << std::endl;
//     std::wcout << L"USB Monitor: Ishga Tushdi (Administrator huquqi talab qilinadi!)" << std::endl;
//     std::wcout << L"Chiqish uchun oynani yoping yoki Ctrl+C bosing." << std::endl;
//     std::wcout << L"==============================================" << std::endl;
//
//     // Oyna sinfini ro'yxatdan o'tkazish
//     WNDCLASSEX wc = {sizeof(WNDCLASSEX)};
//     wc.lpfnWndProc = WndProc;
//     wc.hInstance = GetModuleHandle(NULL);
//     wc.lpszClassName = L"UsbMonitorClass";
//
//     if (!RegisterClassEx(&wc)) {
//         std::wcerr << L"Xato: Oyna sinfini ro'yxatdan o'tkazib bo'lmadi." << std::endl;
//         return 1;
//     }
//
//     // Yashirin (xabar) oynasini yaratish.
//     HWND hWnd = CreateWindowEx(
//         0,
//         L"UsbMonitorClass",
//         NULL,
//         0,
//         0, 0, 0, 0,
//         HWND_MESSAGE,
//         NULL,
//         GetModuleHandle(NULL),
//         NULL
//     );
//
//     if (hWnd == NULL) {
//         std::wcerr << L"Xato: Yashirin oyna yaratib bo'lmadi. Kod: " << GetLastError() << std::endl;
//         return 1;
//     }
//
//     HDEVNOTIFY hNotify = RegisterForUsbNotifications(hWnd);
//
//     if (hNotify == NULL) {
//         std::wcerr << L"Xato: Hodisalarga obuna bo'lib bo'lmadi. Kod: " << GetLastError() << std::endl;
//         DestroyWindow(hWnd);
//         return 1;
//     }
//
//     // Asosiy xabarlar tsikli (Message Loop)
//     MSG msg;
//     while (GetMessage(&msg, NULL, 0, 0) > 0) {
//         TranslateMessage(&msg);
//         DispatchMessage(&msg);
//     }
//
//     UnregisterDeviceNotification(hNotify);
//     DestroyWindow(hWnd);
//
//     return 0;
// }
// Windows API ni har doim Unicode (Wide-Character) versiyalarini ishlatishga majburlash

// Windows API ni har doim Unicode (Wide-Character) versiyalarini ishlatishga majburlash




#include <iostream>
#include <string>
#include <windows.h>
#include <comdef.h>     // _bstr_t, _com_error uchun
#include <Wbemidl.h>    // WMI interfeyslari uchun

#include <io.h>         // _setmode, _fileno uchun
#include <fcntl.h>      // _O_U16TEXT uchun
#include <cstdio>       // _fileno uchun

#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")

using namespace std;

// WMI dan string xususiyatini o'qish va chop etish uchun yordamchi funksiya
void PrintWmiProperty(IWbemClassObject* pclsObj, LPCWSTR propertyName) {
    VARIANT vtProp;
    VariantInit(&vtProp);
    HRESULT hr = pclsObj->Get(propertyName, 0, &vtProp, 0, 0);

    wcout << L"  " << propertyName << L" = ";

    if (SUCCEEDED(hr) && vtProp.vt == VT_BSTR) {
        wcout << vtProp.bstrVal << endl;
    } else if (SUCCEEDED(hr) && (vtProp.vt == VT_I4 || vtProp.vt == VT_BOOL)) {
        // Raqamlar (ErrorCode) yoki Bool qiymatlarini chiqarish
        wcout << vtProp.lVal << endl;
    }
    else {
        wcout << L"[Mavjud emas]" << endl;
    }

    if (vtProp.vt != VT_EMPTY) {
        VariantClear(&vtProp);
    }
}

// Win32_PnPEntity ma'lumotlarini olishning asosiy funksiyasi
void GetPnpEntityInfo() {
    HRESULT hres;

    // 1. COM ni ishga tushirish
    hres = CoInitializeEx(0, COINIT_MULTITHREADED);
    if (FAILED(hres)) {
        wcerr << L"Xato: CoInitializeEx. Kod: " << hex << hres << endl;
        return;
    }

    // 2. Xavfsizlik darajasini o'rnatish
    hres = CoInitializeSecurity(
        NULL, -1, NULL, NULL, RPC_C_AUTHN_LEVEL_DEFAULT, RPC_C_IMP_LEVEL_IMPERSONATE, NULL, EOAC_NONE, NULL
    );

    if (FAILED(hres)) {
        wcerr << L"Xato: CoInitializeSecurity. Kod: " << hex << hres << endl;
        CoUninitialize();
        return;
    }

    // 3. WMI xizmatiga ulanish
    IWbemLocator* pLoc = NULL;
    hres = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER, IID_IWbemLocator, (LPVOID*)&pLoc);

    if (FAILED(hres)) {
        wcerr << L"Xato: IWbemLocator yaratish. Kod: " << hex << hres << endl;
        CoUninitialize();
        return;
    }

    IWbemServices* pSvc = NULL;
    hres = pLoc->ConnectServer(_bstr_t(L"ROOT\\CIMV2"), NULL, NULL, 0, 0, 0, NULL, &pSvc);

    if (FAILED(hres)) {
        wcerr << L"Xato: ConnectServer. Kod: " << hex << hres << endl;
        pLoc->Release();
        CoUninitialize();
        return;
    }

    // 4. Service xavfsizlik darajasini o'rnatish
    hres = CoSetProxyBlanket(
       pSvc, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, NULL, RPC_C_AUTHN_LEVEL_CALL, RPC_C_IMP_LEVEL_IMPERSONATE, NULL, EOAC_NONE
    );

    if (FAILED(hres)) {
        wcerr << L"Xato: CoSetProxyBlanket. Kod: " << hex << hres << endl;
        pSvc->Release();
        pLoc->Release();
        CoUninitialize();
        return;
    }

    // 5. Ma'lumotlarni so'rash (Win32_PnPEntity klassini so'raymiz)
    IEnumWbemClassObject* pEnumerator = NULL;
    hres = pSvc->ExecQuery(
        _bstr_t(L"WQL"),
        _bstr_t(L"SELECT * FROM Win32_PnPEntity"),
        WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY,
        NULL,
        &pEnumerator
    );

    if (FAILED(hres)) {
        wcerr << L"Xato: ExecQuery. Kod: " << hex << hres << endl;
        pSvc->Release();
        pLoc->Release();
        CoUninitialize();
        return;
    }

    // 6. Natijalarni ko'rsatish
    IWbemClassObject* pclsObj = NULL;
    ULONG uReturn = 0;

    wcout << L"\n=======================================================" << endl;
    wcout << L"Win32_PnPEntity WMI Ma'lumotlari (Barcha PnP Qurilmalar)" << endl;
    wcout << L"=======================================================" << endl;

    while (pEnumerator) {
        HRESULT hr = pEnumerator->Next(WBEM_INFINITE, 1, &pclsObj, &uReturn);

        if (0 == uReturn) break;

        wcout << L"\n--- YANGI PnP QURILMASI ---" << endl;

        // Siz so'ragan xususiyatlarni chiqarish
        PrintWmiProperty(pclsObj, L"Caption");
        PrintWmiProperty(pclsObj, L"Name");
        PrintWmiProperty(pclsObj, L"Description");
        PrintWmiProperty(pclsObj, L"DeviceID");
        PrintWmiProperty(pclsObj, L"PNPClass");
        PrintWmiProperty(pclsObj, L"ClassGuid");
        PrintWmiProperty(pclsObj, L"PNPDeviceID");
        PrintWmiProperty(pclsObj, L"Manufacturer");
        PrintWmiProperty(pclsObj, L"Service");
        PrintWmiProperty(pclsObj, L"Status");
        PrintWmiProperty(pclsObj, L"ConfigManagerErrorCode");

        // Majmuaviy (Array) qiymatlar uchun (CompatibleID, HardwareID) maxsus ishlov berish kerak.
        // Hozirda faqat oddiy string/son qiymatlari chiqariladi.

        pclsObj->Release();
    }

    // 7. Resurslarni tozalash
    if (pSvc) pSvc->Release();
    if (pLoc) pLoc->Release();
    if (pEnumerator) pEnumerator->Release();
    CoUninitialize();
}

int main() {
    // Chiqishni Unicode qilib sozlash
    if (_setmode(_fileno(stdout), _O_U16TEXT) == -1) {
        cerr << "Xato: Chiqishni Unicode formatiga o'rnatib bo'lmadi." << endl;
    }

    GetPnpEntityInfo();

    wcout << L"\nChiqish uchun istalgan tugmani bosing..." << endl;

    // Konsol yopilishini kutish
    cin.get();
    return 0;
}
```
```
#cmake_minimum_required(VERSION 3.27)
#project(usb_monitor CXX)
#
#set(CMAKE_CXX_STANDARD 17)
#
#add_executable(usb_monitor main.cpp)
#
## Windows API funksiyalarini ishlata olish uchun majburiy kutubxonalarni qo'shamiz
#target_link_libraries(usb_monitor PRIVATE
#        # Asosiy Windows kutubxonalari
#        kernel32
#        user32
#        advapi32
#
#        # SetupAPI va Configuration Manager (PnP ma'lumotlari uchun)
#        setupapi
#        cfgmgr32
#)
#
## Konsol dasturini majburlash (WinMain xatosini hal qiladi)
#target_link_options(usb_monitor PRIVATE
#        "-Wl,-subsystem,console"
#)


cmake_minimum_required(VERSION 3.27)
project(pnp_entity_info CXX)

set(CMAKE_CXX_STANDARD 17)

add_executable(pnp_entity_info main.cpp)

# WMI va COM uchun zarur kutubxonalar
target_link_libraries(pnp_entity_info PRIVATE
        kernel32
        user32
        advapi32
        ole32       # COM funksiyalari uchun
        oleaut32    # BSTR va Variantlar uchun
        wbemuuid    # WMI GUIDlari uchun
)

target_link_options(pnp_entity_info PRIVATE
        "-Wl,-subsystem,console"
)
```

```c++
#include <iostream>
#include <Windows.h>
#include <SetupAPI.h>
#include <devguid.h>
#include <Cfgmgr32.h>
#include <initguid.h>
#include <io.h>
#include <fcntl.h>

// Eslatma: Bu kodni ishlatish uchun CMakeLists.txt ga
// target_link_libraries(my_usb_only PRIVATE setupapi) qatorini qo'shing.
const GUID GUID_DEVCLASS_WPD = {0xEEC5AD98, 0x8080, 0x425F, {0x92, 0x2A, 0xDA, 0xBF, 0x3D, 0xE3, 0xF6, 0x9A}};
const GUID GUID_DEVCLASS_USB =
        {0x36fc9e60L, 0xc465, 0x11cf, {0x80, 0x56, 0x44, 0x45, 0x53, 0x54, 0x00, 0x00}};
// Windowsda USB qurilmalarining GUIDlarini chiqarish funksiyasi
void PrintDeviceGUIDs() {
    HDEVINFO hDevInfo;
    SP_DEVINFO_DATA DevInfoData;
    DWORD i;

    // Barcha USB qurilmalari ro'yxatini olish
    hDevInfo = SetupDiGetClassDevs(
        &GUID_DEVCLASS_USB, // Faqat Sichqoncha sinfini qidir
        NULL, // Enumerator yo'q (Windows barcha drayverlarni tekshiradi)
        NULL,
        DIGCF_PRESENT // Faqat mavjud qurilmalar
        // DIGCF_ALLCLASSES ni olib tashladik
    );

    if (hDevInfo == INVALID_HANDLE_VALUE) {
        // Xato xabarini ham Unicode (wchar_t) da chiqarish
        std::wcerr << L"Xatolik: SetupDiGetClassDevs() bajarilmadi. Xato kodi: " << GetLastError() << std::endl;
        return;
    }

    DevInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    // Ro'yxatdagi qurilmalarni aylanib chiqish
    for (i = 0; SetupDiEnumDeviceInfo(hDevInfo, i, &DevInfoData); i++) {
        // Qurilma nomini (tavsifini) olish (Bu wchar_t bo'lishi kerak, shuning uchun L"..." dan foydalanamiz)
        wchar_t DeviceName[MAX_PATH];
        if (SetupDiGetDeviceRegistryPropertyW( // W - wide character versiyasini chaqiramiz
            hDevInfo,
            &DevInfoData,
            SPDRP_DEVICEDESC,
            NULL,
            (PBYTE) DeviceName,
            sizeof(DeviceName),
            NULL
        )) {
            // Class GUIDni olish va stringga o'tkazish
            OLECHAR GuidString[40];

            if (StringFromGUID2(DevInfoData.ClassGuid, GuidString, ARRAYSIZE(GuidString))) {
                std::wcout << L"--------------------------------------" << std::endl;
                // Barcha chiqishlar std::wcout orqali amalga oshiriladi
                std::wcout << L"Qurilma nomi: " << DeviceName << std::endl;
                std::wcout << L"  Class GUID: " << GuidString << std::endl;
            } else {
                std::wcout << L"Qurilma nomi: " << DeviceName << L" (GUID'ni o'qib bo'lmadi)" << std::endl;
            }
        }
    }

    SetupDiDestroyDeviceInfoList(hDevInfo);
}

int main() {
    // RUNTIME LIBRARY XATOSINI KELTIRIB CHIQARUVCHI QATOR OLIB TASHLANDI.
    // std::wcout endi o'zbekcha va unicode matnlarni ishonchliroq chiqarishi kerak.

    std::wcout << L"Kompyuterga ulangan USB qurilmalarining GUIDlari:" << std::endl;
    PrintDeviceGUIDs();
    return 0;
}

```

---
```c++
cmake_minimum_required(VERSION 3.20)
project(my_usb_only)

set(CMAKE_CXX_STANDARD 17)

add_executable(my_usb_only main.cpp)

target_link_libraries(my_usb_only setupapi)

```
