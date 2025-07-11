import subprocess
import sys

import win32file
import win32con
import ctypes
import wmi


# c da yozilgan usb izvlech qilish uchun
EXE_FILE = r'C:\Users\User-39\Documents\GitHub\usb\installer\untitled2.exe'

"""
disk harifini aniqlab chiqarib yuorishga tayorlaydi 
"""
class UsbEject:
    def __init__(self):
        self.wmi = wmi.WMI()
        # disk harifini aniqlaydi
    def eject_by_pnp(self, pnp_id_substring):
        for disk in self.wmi.Win32_DiskDrive():
            if pnp_id_substring in disk.PNPDeviceID:
                try:
                    for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                        for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                            drive_letter = logical_disk.DeviceID

                            subprocess.run([EXE_FILE, drive_letter])
                            return
                except Exception as e:
                    print(f"Eject qilingan qurilmaga qayta murojaat: {e}")
                return
    def adb_set_usb_mode(mode: str):
        """
        Telefonni USB rejimini o‘zgartiradi.
        mode: 'none' — faqat quvvat
              'mtp' yoki 'mtp,adb' — fayl uzatish uchun
        """
        try:
            cmd = ["adb", "shell", "svc", "usb", "setFunctions", mode]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Telefon USB rejimi: {mode}")
            else:
                print(f"❌ Xatolik (kod {result.returncode}): {result.stderr.strip()}")

        except FileNotFoundError:
            print("❌ ADB topilmadi. Iltimos, adb o‘rnatilganini tekshiring (Android SDK).")
        except Exception as e:
            print(f"❌ Nomaʼlum xatolik: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ejector = UsbEject()
        ejector.eject_by_pnp(sys.argv[1])