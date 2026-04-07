import time

from apps.db.database import LocalDatabase
from apps.core.usb_eject import UsbEject
from apps.core.device_classifier import classify_disk_device, classify_pnp_device
from apps.core.device_logger import log_device_connected, log_device_blocked, log_eject_result
from concurrent.futures import ThreadPoolExecutor

"""
Asosiy USB monitoring moduli.
Qurilma ulanishini aniqlaydi, turini klassifikatsiya qiladi,
whitelist tekshiradi, bloklaydi va log yozadi.
"""


class UsbWatcher:
    def __init__(self):
        self.db = LocalDatabase()
        self.eject = UsbEject()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def phone_checker(self, device):
        """MTP/WPD qurilmalarni aniqlaydi va bloklaydi (telefonlar, planshetlar)."""
        import pythoncom
        pythoncom.CoInitialize()
        try:
            info = classify_pnp_device(device)
            if info is None:
                return

            # MTP telefonlarni bloklash siyosati
            # (kerak bo’lsa whitelist qo’shish mumkin)
            info.blocked = True
            log_device_blocked(info, reason="MTP qurilmalarga ruxsat yo’q", db=self.db)
            self.eject.mtp_connection_eject(info.pnp_device_id)

        except Exception as e:
            print(f"MTP/WPD xato: {e}")
        finally:
            pythoncom.CoUninitialize()

    def check_connection_usb(self, device):
        """
        USB disk qurilmalarini aniqlaydi:
          - USB Flash xotira
          - Tashqi HDD
          - Tashqi SSD
          - M.2/NVMe USB adapter
        Whitelist tekshiradi, bloklaydi va log yozadi.
        """
        import pythoncom, wmi
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            pnp_id = getattr(device, "PNPDeviceID", "") or ""

            for disk in c.Win32_DiskDrive():
                if disk.InterfaceType not in (‘USB’, ‘SCSI’):
                    continue

                # Qurilma turini aniq aniqlash
                info = classify_disk_device(disk)

                if not info.serial:
                    print(f"Seriya raqami topilmadi: {info.caption}")
                    continue

                # Whitelist tekshirish
                if self.db.is_serial_registered(serial=str(info.serial)):
                    info.blocked = False
                    log_device_connected(info, db=self.db)
                else:
                    # Bloklash
                    info.blocked = True
                    log_device_blocked(info, reason="Serial whitelist’da yo’q", db=self.db)
                    ok, msg = self.eject.eject_usb_device(disk.PNPDeviceID)
                    log_eject_result(info, ok, msg)

        except wmi.x_wmi_timed_out:
            pass
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"[Xato]: {e}")
            time.sleep(1)
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


