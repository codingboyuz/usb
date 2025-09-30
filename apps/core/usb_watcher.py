import subprocess
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

    # def check_connection_usb(self):
    #     import pythoncom, wmi
    #     pythoncom.CoInitialize()
    #     try:
    #         w = wmi.WMI()
    #         for disk in w.Win32_DiskDrive():
    #             if disk.InterfaceType in ['SCSI', 'USB']:
    #                 serial = getattr(disk, 'SerialNumber', None)
    #                 if not serial:
    #                     print("⚠️ Diqqat: USB qurilma seriya raqami topilmadi")
    #                     continue
    #
    #                 # serialni normalize qilish
    #                 serial = serial.strip().rstrip('.')
    #                 print(f"Serial: {serial}")
    #
    #                 registered = self.db.is_serial_registered(serial)
    #                 print(f"DB register: {registered}")
    #
    #                 if not registered:
    #                     # qurilmani eject qilish
    #                     try:
    #                         self.eject.eject_by_pnp(pnp_id_substring=disk.PNPDeviceID)
    #                         # logga yozish
    #                         self.db.log_access(
    #                             disk.Caption,
    #                             disk.Model,
    #                             disk.InterfaceType,
    #                             disk.Size,
    #                             serial
    #                         )
    #                     except Exception as e:
    #                         print(f"❌ Eject xatolik: {e}")
    #                 else:
    #                     print(f"✅ Bu USB allaqachon ro‘yxatdan o‘tgan {serial}")
    #     finally:
    #         pythoncom.CoUninitialize()
    def check_connection_usb(self):
        import pythoncom, wmi
        pythoncom.CoInitialize()
        try:
            w = wmi.WMI()
            for disk in w.Win32_DiskDrive():
                try:
                    # ❗ faqat USB disklarni tekshirish
                    if disk.InterfaceType != 'USB':
                        continue

                    serial = getattr(disk, 'SerialNumber', None)
                    if not serial:
                        print("⚠️ Serial topilmadi")
                        continue

                    # serial = normalize_serial(serial)
                    print(f"Serial: {serial}")

                    registered = self.db.is_serial_registered(serial)
                    print(f"DB register: {registered}")

                    if not registered:
                        print(disk.PNPDeviceID)
                        # self.eject.eject_by_pnp(pnp_id_substring=disk.PNPDeviceID)
                        # subprocess.run([EXE_USB_EJECT, disk.PNPDeviceID])
                        try:
                            pnp_id = str(disk.PNPDeviceID)
                            print("PNPDeviceID yuborilmoqda:", pnp_id)

                            # ✅ argumentni to‘liq yuborish
                            subprocess.run(f'"{EXE_USB_EJECT}" "{disk.PNPDeviceID}"', shell=True)

                        except Exception as e:
                            print(f"Eject xatolik: {e}")

                        self.db.log_access(
                            disk.Caption,
                            disk.Model,
                            disk.InterfaceType,
                            disk.Size,
                            serial
                        )
                    else:
                        print(f"✅ Ro‘yxatdan o‘tgan: {serial}")
                except Exception as inner:
                    print(f"⚠️ Diskni tekshirishda xato: {inner}")
        finally:
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
