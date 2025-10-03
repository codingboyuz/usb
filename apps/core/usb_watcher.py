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
        import pythoncom
        import wmi

        """
        MTP/WPD qurilmalarni aniqlaydi (telefonlar, planshetlar).
        """
        print("🔍 MTP/WPD qurilmalarni qidirish boshlandi")
        try:
            pythoncom.CoInitialize()  # Har bir thread uchun COM initialize
            w = wmi.WMI()

            for device in w.Win32_PnPEntity():
                try:
                    # MTP/WPD qurilmalarni aniqlash uchun kengroq shartlar
                    pnp_class = getattr(device, 'PNPClass', None) or ""
                    name = getattr(device, 'Name', 'Noma\'lum qurilma')
                    compatible_id = str(getattr(device, 'CompatibleID', ''))
                    device_id = getattr(device, 'DeviceID', '')

                    # MTP yoki WPD qurilmalarni tekshirish
                    if (pnp_class.upper() in ['WPD', 'PORTABLEDEVICE'] or
                            any(keyword in compatible_id.upper() for keyword in ['MTP', 'WPD']) or
                            any(keyword in name.upper() for keyword in ['MTP', 'PORTABLE DEVICE', 'PHONE'])):
                        # print(f"📱 Telefon aniqlandi: {name}")
                        # print(f"  PNPDeviceID: {device_id}")
                        # print(f"  PNPClass: {pnp_class}")
                        # print(f"  CompatibleID: {compatible_id}")
                        # print("*"*50)
                        # print("\n")

                        # Ma'lumotlarni bazaga yozish
                        self.db.log_access(name, "WPD Device", pnp_class, None, None)

                        # MTP ulanishini tekshirish
                        self.eject.mtp_connection_checker(mode=device_id)

                except Exception as inner_e:
                    print(f"⚠️ Qurilma tekshirishda xato: {inner_e}")

        except Exception as e:
            print(f"❌ MTP/WPD qidirishda xato: {e}")
        finally:
            pythoncom.CoUninitialize()  # COM resurslarini tozalash


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
        print("run USB connection search ")

        import pythoncom, wmi
        pythoncom.CoInitialize()
        try:
            w = wmi.WMI()
            for disk in w.Win32_DiskDrive():
                # print("run USB connection search with for loop")

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
                        self.eject.eject_usb_device(pnp_device_id=disk.PNPDeviceID)
                        # try:
                        #     pnp_id = str(disk.PNPDeviceID)
                        #     print("PNPDeviceID yuborilmoqda:", pnp_id)
                        #
                        #     # ✅ argumentni to‘liq yuborish
                        #     # subprocess.run(f'"{EXE_USB_EJECT}" "{disk.PNPDeviceID}"', shell=True)
                        #
                        # except Exception as e:
                        #     print(f"Eject xatolik: {e}")

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
