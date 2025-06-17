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
