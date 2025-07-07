import wmi
import time
from db.database import LocalDatabase
from core.usb_eject import UsbEject
import pythoncom
from concurrent.futures import ThreadPoolExecutor

"""
Bu qisim asosy  doimiy portni nazorat qiladi ulanishlarni tekshiradi  umuman o'chmasligi kerak bo'lagan app 
"""

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
            # ulangan telefoni aniqlash
            if device.PNPClass == "WPD":
                print(f"📱 Telefon aniqlandi: {device.Caption}")
                print(f"PNPDeviceID: {device.PNPDeviceID}")
                self.db.log_access(device.Caption, "WPD Device", "WPD", None, None)
                self.eject.adb_set_usb_mode()
                print("⚠️ Bu qurilmani chiqarib bo'lmaydi (MTP protokoli)")

    def check_connection_usb(self):
        for disk in self.wmi.Win32_DiskDrive():
            # ulanish turi faqat SCSI hard disk , USB
            if disk.InterfaceType in ['SCSI', 'USB']:
                serial = getattr(disk, 'SerialNumber', None)
                if serial:
                    # usb seria raqami bo'lmasa
                    if not self.db.is_serial_registered(serial=str(serial)):
                        # PNPDeviceID disk harifini aniqlash uchun yuboradi
                        self.eject.eject_by_pnp(pnp_id_substring=disk.PNPDeviceID)
                        # ro'yxatdan o'tmagan usb ni db ga saqlab qo'yadi
                        self.db.log_access(disk.Caption, disk.Model, disk.InterfaceType, disk.Size, serial)

                else:
                    print("Diqqat: USB qurilma seriya raqami topilmadi")


if __name__ == '__main__':
    usb = UsbWatcher()
    # usbni ro'yhatdan o'tkazish sql.db ga yozib qo'yadi
    # usb.db.add_device(serial=str("E823_8FA6_BF53_0001_001B_448B_4A21_D14E."))
    try:
        while True:
            # usb.phone_checker()
            # port oqimini tekshirish
            usb.check_connection_usb()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDastur to'xtatildi")
    finally:
        usb.db.close_connection()
