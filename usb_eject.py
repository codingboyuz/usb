import sys

import win32file
import win32con
import ctypes
import wmi


class UsbEject:
    def __init__(self):
        self.wmi = wmi.WMI()

    @staticmethod
    def __eject_drive(drive_letter):
        drive_path = f"\\\\.\\{drive_letter[0]}:"
        try:
            handle = win32file.CreateFile(
                drive_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )

            result = ctypes.windll.kernel32.DeviceIoControl(
                handle.handle,
                0x2D4808,  # IOCTL_STORAGE_EJECT_MEDIA
                None,
                0,
                None,
                0,
                ctypes.byref(ctypes.c_ulong()),
                None
            )
            handle.Close()

            if result:
                print(f"Qurilma chiqarildi: {drive_letter}")
            else:
                print(f"Qurilma chiqarilmadi: {drive_letter}")
        except Exception as e:
            print(f"[Xatolik] {drive_letter}: {e}")

    def eject_by_pnp(self, pnp_id_substring):
        found = False
        print(str(pnp_id_substring))

        for disk in self.wmi.Win32_DiskDrive():
            if pnp_id_substring in disk.PNPDeviceID:
                found = True
                for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                        drive_letter = logical_disk.DeviceID
                        self.__eject_drive(drive_letter)
                        return

        if not found:
            print("Qurilma topilmadi yoki disk harfi yo'q")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(" Foydalanish: usbeject.exe <PNPDeviceID_substring>")
        sys.exit(1)

    pnp_substring = sys.argv[1]
    print(f"pnp_substring {pnp_substring}")
    ejector = UsbEject()
    ejector.eject_by_pnp(pnp_substring)