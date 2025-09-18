from apps.db.database import LocalDatabase
from apps.core.usb_eject import UsbEject
from concurrent.futures import ThreadPoolExecutor
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

    def phone_checker(self):
        import pythoncom, wmi
        pythoncom.CoInitialize()  # WMI har bir thread uchun initialize qilinadi
        w = wmi.WMI()
        for device in w.Win32_PnPEntity():
            # ulangan telefoni aniqlash
            if device.PNPClass == "WPD" and "MTP" in str(device.CompatibleID):
                print(f"📱 Telefon aniqlandi: {device.Caption}")
                print(f"PNPDeviceID: {device.PNPDeviceID}")
                self.db.log_access(device.Caption, "WPD Device", "WPD", None, None)
                self.eject.mtp_connection_checker(mode=device.PNPDeviceID)

    def check_connection_usb(self):
        import pythoncom, wmi

        pythoncom.CoInitialize()  # WMI har bir thread uchun initialize qilinadi
        w = wmi.WMI()
        for disk in w.Win32_DiskDrive():
            # ulanish turi faqat SCSI hard disk , USB
            if disk.InterfaceType in ['SCSI', 'USB']:
                serial = getattr(disk, 'SerialNumber', None)
                print(serial)
                if serial:
                    # usb seria raqami bo'lmasa
                    if not self.db.is_serial_registered(serial=str(serial)):
                        # PNPDeviceID disk harifini aniqlash uchun yuboradi
                        self.eject.eject_by_pnp(pnp_id_substring=disk.PNPDeviceID)
                        # ro'yxatdan o'tmagan usb ni db ga saqlab qo'yadi
                        self.db.log_access(disk.Caption, disk.Model, disk.InterfaceType, disk.Size, serial)

                else:
                    print("Diqqat: USB qurilma seriya raqami topilmadi")


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
