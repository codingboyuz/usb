import subprocess
import sys
from  settings.base import EXE_MTP_EJECT
import win32file
import win32con
import ctypes
from settings.base import EXE_USB_EJECT
# c da yozilgan usb izvlech qilish uchun

"""
disk harifini aniqlab chiqarib yuorishga tayorlaydi 
"""
class UsbEject:

    @staticmethod
    def eject_by_pnp(pnp_id_substring):
        import pythoncom
        import wmi
        pythoncom.CoInitialize()  # ✅ Har bir thread uchun boshlash
        try:
            w = wmi.WMI()  # ✅ Har safar yangi WMI sessiya
            for disk in w.Win32_DiskDrive():
                if pnp_id_substring in disk.PNPDeviceID:
                    try:
                        for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                                drive_letter = logical_disk.DeviceID
                                subprocess.run([EXE_USB_EJECT, drive_letter])
                                return
                    except Exception as e:
                        print(f"Eject qilingan qurilmaga qayta murojaat: {e}")
                    return
        finally:
            pythoncom.CoUninitialize()  # ✅ Har doim COM tozalash

    @staticmethod
    def mtp_connection_checker(mode):
        """
        Telefonni USB rejimini o‘zgartiradi.
        """
        # exe_path = r"C:\Users\nmada\CLionProjects\untitled3\cmake-build-debug\untitled3.exe"

        try:
            # .exe ni phone_id argumenti bilan ishga tushirish
            result = subprocess.run(
                [EXE_MTP_EJECT, mode],
                capture_output=True,  # stdout va stderr ni yig‘ish
                text=True,  # Chiqishni matn sifatida olish
                encoding='utf-8'  # UTF-8 kodlash
            )

            # Natijalarni ko‘rsatish
            print("stdout (natija):", result.stdout)
            print("stderr (xato):", result.stderr)
            print("Qaytarilgan kod:", result.returncode)

            if result.returncode == 0:
                print("Qurilma muvaffaqiyatli chiqarildi yoki faolsizlantirildi.")
            else:
                print("Xatolik yuz berdi. Batafsil ma'lumot yuqorida.")

        except Exception as e:
            print(f"Python xatosi: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ejector = UsbEject()
        ejector.eject_by_pnp(sys.argv[1])