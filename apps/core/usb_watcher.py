import time

from apps.db.database import LocalDatabase
from apps.core.usb_eject import UsbEject
from concurrent.futures import ThreadPoolExecutor
from settings.base import EXE_USB_EJECT

"""
Bu qisim asosy  doimiy portni nazorat qiladi ulanishlarni tekshiradi  umuman o'chmasligi kerak bo'lagan app
 UsbWatcher alohida exe fayil bo'ladi va doimiy ishlaydi 
"""


class UsbWatcher:
    def __init__(self):
        self.db = LocalDatabase()
        self.eject = UsbEject()
        # ✅ Maksimal 10 ta thread bir vaqtning o'zida eject bajaradi
        self.executor = ThreadPoolExecutor(max_workers=10)

    def phone_checker(self, device):
        import pythoncom

        pythoncom.CoInitialize()  # Har bir thread uchun COM initialize

        """
        MTP/WPD qurilmalarni aniqlaydi (telefonlar, planshetlar).
        """
        try:
            # instance of Win32_PnPEntity
            # {
            # 	Caption = "Redmi Note 13 Pro";
            # 	ClassGuid = "{eec5ad98-8080-425f-922a-dabf3de3f69a}";
            # 	CompatibleID = {"USB\\MS_COMP_MTP", "USB\\Class_06&SubClass_01&Prot_01", "USB\\Class_06&SubClass_01", "USB\\Class_06"};
            # 	ConfigManagerErrorCode = 0;
            # 	ConfigManagerUserConfig = FALSE;
            # 	CreationClassName = "Win32_PnPEntity";
            # 	Description = "Redmi Note 13 Pro";
            # 	DeviceID = "USB\\VID_2717&PID_FF48&MI_00\\7&593ED88&0&0000";
            # 	HardwareID = {"USB\\VID_2717&PID_FF48&REV_0223&MI_00", "USB\\VID_2717&PID_FF48&MI_00"};
            # 	Manufacturer = "Xiaomi";
            # 	Name = "Redmi Note 13 Pro";
            # 	PNPClass = "WPD";
            # 	PNPDeviceID = "USB\\VID_2717&PID_FF48&MI_00\\7&593ED88&0&0000";
            # 	Present = TRUE;
            # 	Service = "WUDFWpdMtp";
            # 	Status = "OK";
            # 	SystemCreationClassName = "Win32_ComputerSystem";
            # 	SystemName = "DESKTOP-8KM6DT0";
            # };
            caption = getattr(device, "Caption", "") or ""
            manufacturer = getattr(device, "Manufacturer", "") or ""
            pnpid = getattr(device, "PNPDeviceID", "") or ""

            self.eject.mtp_connection_eject(pnpid)
            self.db.log_access(caption=caption, model=manufacturer, serial=pnpid, size=None, interface_type="MTP", )

        except Exception as e:
            print(f"❌ MTP/WPD qidirishda xato: {e}")
        finally:
            pythoncom.CoUninitialize()  # COM resurslarini tozalash



    def check_connection_usb(self, device):
        print("run USB connection search ")

        import pythoncom, wmi
        pythoncom.CoInitialize()
        try:

            pnp_id = getattr(device, "PNPDeviceID", "") or ""

            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                if getattr(disk, "PNPDeviceID", "").strip().lower() == pnp_id.strip().lower():
                    print(getattr(disk, "PNPDeviceID", ""))

                    print("\n📀 Qurilma haqida to‘liq ma’lumot:")
                    print(f"  Model: {disk.Model}")
                    print(f"  InterfaceType: {disk.InterfaceType}")
                    print(f"  SerialNumber: {getattr(disk, 'SerialNumber', 'Nomaʼlum')}")
                    print(f"  Size: {int(disk.Size) / (1024 ** 3):.2f} GB")
                    print(f"  FirmwareRevision: {disk.FirmwareRevision}")
                    print(f"  MediaType: {disk.MediaType}")
                    print(f"  DeviceID: {disk.DeviceID}")
                    print(f"  Status: {disk.Status}")
                    print(f"  Caption: {disk.Caption}")
                    print("-" * 70)

                    print(disk)

                    print("-" * 70)
                    break
        except wmi.x_wmi_timed_out:
            pass
        except KeyboardInterrupt:
            print("To‘xtatildi.")
            pass

        except Exception as e:
            print("[Xato]:", e)
            time.sleep(1)

        pythoncom.CoUninitialize()

# if __name__ == '__main__':
#     usb = UsbWatcher()
#     # usbni ro'yhatdan o'tkazish sql.db ga yozib qo'yadi
#     # usb.db.add_device(serial=str("E823_8FA6_BF53_0001_001B_448B_4A21_D14E."))
#     try:
#         while True:
#             # usb.phone_checker()
#             # port oqimini tekshirish
#             usb.check_connection_usb()
#             time.sleep(1.0)
#     except KeyboardInterrupt:
#         print("\nDastur to'xtatildi")
#     finally:
#         usb.db.close_connection()
#
#                         if not registered:
#                             print(disk.PNPDeviceID)
#                             self.eject.eject_usb_device(pnp_device_id=disk.PNPDeviceID)
#                             # try:
#                             #     pnp_id = str(disk.PNPDeviceID)
#                             #     print("PNPDeviceID yuborilmoqda:", pnp_id)
#                             #
#                             #     # ✅ argumentni to‘liq yuborish
#                             #     # subprocess.run(f'"{EXE_USB_EJECT}" "{disk.PNPDeviceID}"', shell=True)
#                             #
#                             # except Exception as e:
#                             #     print(f"Eject xatolik: {e}")
#
#                             self.db.log_access(
#                                 disk.Caption,
#                                 disk.Model,
#                                 disk.InterfaceType,
#                                 disk.Size,
#                                 serial
#                             )


