import wmi
import time
from database import LocalDatabase
from usb_eject import UsbEject
import pythoncom
from concurrent.futures import ThreadPoolExecutor


class UsbWatcher:
    def __init__(self):
        pythoncom.CoInitialize()  # WMI har bir thread uchun initialize qilinadi
        self.wmi = wmi.WMI()

        self.db = LocalDatabase()
        self.eject = UsbEject()
        # ✅ Maksimal 10 ta thread bir vaqtning o'zida eject bajaradi
        self.executor = ThreadPoolExecutor(max_workers=10)

    def phone_checker(self):
        for device in self.wmi.Win32_PnPEntity():
            if device.PNPClass == "WPD":
                print(f"📱 Telefon aniqlandi: {device.Caption}")
                print(f"PNPDeviceID: {device.PNPDeviceID}")
                self.db.log_access(device.Caption, "WPD Device", "WPD", None, None)
                self.eject.adb_set_usb_mode()
                print("⚠️ Bu qurilmani chiqarib bo'lmaydi (MTP protokoli)")

    def check_connection_usb(self):
        for disk in self.wmi.Win32_DiskDrive():
            if disk.InterfaceType in ['SCSI', 'USB']:
                serial = getattr(disk, 'SerialNumber', None)
                if serial:
                    if not self.db.is_serial_registered(serial=str(serial)):

                        self.eject.eject_by_pnp(pnp_id_substring=disk.PNPDeviceID)
                        print(f"Nox: {disk.PNPDeviceID} - ro'yxatdan o'tmagan")
                        self.db.log_access(disk.Caption, disk.Model, disk.InterfaceType, disk.Size, serial)

                else:
                    print("Diqqat: USB qurilma seriya raqami topilmadi")


if __name__ == '__main__':
    usb = UsbWatcher()
    # usb.db.add_device(serial=str("E823_8FA6_BF53_0001_001B_448B_4A21_D14E."))

    try:
        while True:
            # usb.phone_checker()

            usb.check_connection_usb()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDastur to'xtatildi")
    finally:
        usb.db.close_connection()
