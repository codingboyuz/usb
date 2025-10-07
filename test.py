# import threading
# import time
# import win32con
# import win32gui
# import win32file  # Volume ma'lumotlarini olish uchun
# import pythoncom
# from datetime import datetime
# import ctypes  # SetupAPI uchun (murakkabroq ma'lumotlar uchun)
#
# # Qurilmalarni kuzatish uchun to'plam
# initial_drives = set()
#
#
# def get_disk_info(drive_letter):
#     """
#     Berilgan disk harfi (masalan, 'E:\\') bo'yicha ma'lumotlarni qaytaradi.
#     Bu WMI'siz fayl tizimi ma'lumotlarini olishning asosiy Win32 API usuli.
#     """
#     try:
#         # 1. Volume nomini, seriya raqamini va FS turini olish
#         volume_info = win32file.GetVolumeInformation(drive_letter)
#
#
#
#         # volume_info quyidagi tartibda ma'lumot qaytaradi:
#         # (VolumeName, VolumeSerialNumber, MaxComponentLength, FileSystemFlags, FileSystemName)
#
#         name = volume_info[0]
#         serial = volume_info[1]
#         fs_name = volume_info[4]
#         print("=" * 50)
#         print(str(name))
#
#         print(f"volume_info {volume_info}")
#         print("=" * 50)
#         return {
#             "name": name,
#             "serial_number": serial,  # Fayl tizimi Seriya raqami (Diskning o'ziniki emas)
#             "file_system": fs_name,
#             "path": drive_letter
#         }
#
#     except Exception as e:
#         # Agar disk harfi topilmasa yoki ruxsat muammosi bo'lsa
#         return None
#
#
# def monitor_new_drive_connection():
#     """
#     Hozirgi disk harflari ro'yxatini oladi va yangi ulangan qurilmani aniqlaydi.
#     """
#     global initial_drives
#
#     # Win32 API yordamida hozirgi ulangan disk harflari ro'yxatini olish
#     drive_bits = ctypes.windll.kernel32.GetLogicalDrives()
#     print(drive_bits)
#     current_drives = set()
#
#     for i in range(26):
#         if (drive_bits >> i) & 1:
#             drive_letter = chr(ord('A') + i) + ":\\"
#             # Faqat USB/Portable tipidagi qurilmalarni qiziqtirsa,
#             # GetDriveType(drive_letter) = 3 (FIXED) yoki 2 (REMOVABLE) tekshirish mumkin.
#             current_drives.add(drive_letter)
#
#     new_drives = current_drives - initial_drives
#
#     if new_drives:
#         print("\n" + "=" * 50)
#         print("🎉 Yangi Qurilma Aniqlangan!")
#
#         for drive in sorted(list(new_drives)):
#             info = get_disk_info(drive)
#             print(info)
#             if info:
#                 print(f"  📂 Disk Harfi: {info['path']}")
#                 print(f"  📝 Nom: {info['name'] or 'Noma\'lum'}")
#                 print(f"  🔢 Seriya Raqami (FS): {info['serial_number']}")
#                 print(f"  ⚙️ Fayl Tizimi: {info['file_system']}")
#             else:
#                 print(f"  ⚠️ Disk Harfi: {drive}. Ma'lumot olishda xato yuz berdi.")
#
#         print("=" * 50)
#         # Ro'yxatni yangilash
#         initial_drives = current_drives
#
#     # Har doim ro'yxatni uzilgan qurilmalar uchun ham yangilash
#     initial_drives = current_drives
#
#
# class DeviceMonitor:
#     def __init__(self):
#         wc = win32gui.WNDCLASS()
#         wc.lpfnWndProc = self.wnd_proc
#         wc.lpszClassName = "DeviceChangeMonitorWin32"
#         self.class_atom = win32gui.RegisterClass(wc)
#
#         # Ko‘rinmas oyna yaratish
#         self.hwnd = win32gui.CreateWindow(
#             self.class_atom, "HiddenDeviceMonitor",
#             0, 0, 0, 0, 0, 0, 0, 0, None
#         )
#
#         # Dastur ishga tushganda, dastlabki ulangan drayverlar ro'yxatini olish
#         monitor_new_drive_connection()
#         print(f"✅ Boshlang'ich drayverlar ro'yxati olindi: {initial_drives}")
#
#     def wnd_proc(self, hwnd, msg, wparam, lparam):
#         if msg == win32con.WM_DEVICECHANGE:
#             if wparam == win32con.DBT_DEVICEARRIVAL or wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
#                 # WM_DEVICECHANGE xabari kelganda, disk harflari ro'yxatini yangilash
#                 print(f"🔌 [{datetime.now().strftime('%H:%M:%S')}] Qurilma ulanishi/uzilishi (API).")
#
#                 # Drayver sozlanishi uchun biroz kutish muhim (API chaqiruvlari uchun)
#                 threading.Timer(0.5, monitor_new_drive_connection).start()
#
#         return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
#
#     @staticmethod
#     def run():
#         print("Start monitoring (Win32 API Only)...")
#         # Eng kam CPU yuklamasi uchun
#         win32gui.PumpMessages()
#
#
# if __name__ == "__main__":
#     monitor = DeviceMonitor()
#     monitor.run()


import sys
import struct
import win32api
import win32file
import winioctlcon


def get_media_type(drive_letter):
    # Drive device path, masalan 'E:' uchun '\\\\.\\E:'
    drive_device = f"\\\\.\\{drive_letter}:"

    # Handle yaratish
    handle = win32file.CreateFile(drive_device,
                                  0,
                                  win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                                  None,
                                  win32file.OPEN_EXISTING,
                                  0,
                                  None)
    if handle == win32file.INVALID_HANDLE_VALUE:
        print(f"Xato: {drive_letter} diskini ochib bo'lmadi.")
        return None

    try:
        # Disk geometriyasini olish (IOCTL_DISK_GET_DRIVE_GEOMETRY)
        disk_geometry = win32file.DeviceIoControl(handle,
                                                  winioctlcon.IOCTL_DISK_GET_DRIVE_GEOMETRY,
                                                  None,
                                                  24)

        # Media turini parse qilish (offset 8 dan 4 byte)
        media_type_code = struct.unpack("<I", disk_geometry[8:12])[0]

        # Media turini nomiga aylantirish (masalan, 0xB = RemovableMedia USB uchun)
        media_types = {
            0x0: "Unknown",
            0xB: "RemovableMedia",  # USB fleshka
            0xC: "FixedMedia",
            # Boshqalar...
        }
        media_type = media_types.get(media_type_code, f"Noma'lum kod: {media_type_code}")

        print(f"{drive_letter}: Media turi: {media_type}")

        # Qo'shimcha media turlari olish (IOCTL_STORAGE_GET_MEDIA_TYPES_EX)
        media_types_ex = win32file.DeviceIoControl(handle,
                                                   winioctlcon.IOCTL_STORAGE_GET_MEDIA_TYPES_EX,
                                                   None,
                                                   2048)

        # Device kod va media sonini parse qilish
        device_code = struct.unpack("<I", media_types_ex[0:4])[0]
        media_count = struct.unpack("<I", media_types_ex[4:8])[0]

        offset = 8
        supported_media = []
        for _ in range(media_count):
            if device_code in [31, 32]:  # Tape devices
                mt_code = struct.unpack("<I", media_types_ex[offset:offset + 4])[0]
                offset += 8
            else:
                offset += 8  # Cylinders skip
                mt_code = struct.unpack("<I", media_types_ex[offset:offset + 4])[0]
                offset += 24  # Qolgan qism
            supported_media.append(media_types.get(mt_code, f"Noma'lum: {mt_code}"))

        print(f"Qo'llab-quvvatlanadigan media turlari: {supported_media}")

    finally:
        win32file.CloseHandle(handle)


# Misol: C, D, E disklarini tekshirish
drives = ['C', 'D', 'E']  # USB ulanganda uning harfini qo'shing
for drive in drives:
    get_media_type(drive)