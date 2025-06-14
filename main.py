import subprocess
import wmi
import time

registered_serials = set()

USB_FILE ="usb_list.txt"

def read_file():
    with open(USB_FILE,'r',encoding='utf-8')as f:
        for line in f:
            print(line)
            registered_serials.add(line)

def get_connected_usb_serials():
    c = wmi.WMI()
    usb_serials = []

    for disk in c.Win32_DiskDrive():
        if disk.InterfaceType == "USB":
            serial = getattr(disk, 'SerialNumber', 'Yo‘q')
            if serial not in registered_serials:
                print(f"❌ Ro'yxatdan o'tmagan USB aniqlandi")
                print(f"Model: {disk.Model}")
                print(f"DeviceID: {disk.DeviceID}")
                print(f"PNPDeviceID: {disk.PNPDeviceID}")
                print(f"SerialNumber: {serial}")
                print("-" * 40)
                usb_serials.append(disk.PNPDeviceID)
    return usb_serials


def usb_kill():
    DEVCON_PATH = r"devcon.exe"
    for usb in get_connected_usb_serials():
        device_id = fr"@{usb}"
        print(f"➡ USB qurilma o‘chirilmoqda: {device_id}")

        # Avval disable qilib ko‘ramiz
        subprocess.run(
            [DEVCON_PATH, "disable", device_id],
            capture_output=True, text=True
        )
        time.sleep(1)  # Qurilmani to‘liq bo‘shatish uchun kutamiz

        # Endi remove qilamiz
        result = subprocess.run(
            [DEVCON_PATH, "remove", device_id],
            capture_output=True, text=True
        )

        print(result.stdout)
        print(result.stderr)
        print("=" * 50)


if __name__ == '__main__':
    while True:
        usb_kill()
        time.sleep(3)  # Har 3 soniyada tekshirib chiqilsin
