import threading
import time
import win32con
import win32gui
import pythoncom
import wmi
from datetime import datetime

# 🔹 Global ro‘yxat — faqat 1 marta har bir PNPDeviceID qayta ishlanishini ta’minlaydi
PROCESSED_DEVICES = set()


def classify_device(device):
    """Win32_PnPEntity obyektidan qurilma turini aniqlaydi."""
    name = getattr(device, "Name", "") or ""
    service = getattr(device, "Service", "") or ""
    pclass = getattr(device, "PNPClass", "") or ""
    desc = getattr(device, "Description", "") or ""
    pnpid = getattr(device, "PNPDeviceID", "") or ""

    # Qurilma turi aniqlash
    if service.startswith("USBSTOR") or "DISK" in desc.upper():
        dev_type = "💾 USB Flesh yoki tashqi HDD"
    elif service.upper() in ("WUDFWPDFS", "WPDFS"):
        dev_type = "💾 WPD fayl tizimi (portable storage)"
    elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
        dev_type = "📱 MTP Telefon (Media Transfer Protocol)"
    elif service.upper() == "WINUSB" and "ADB" in name.upper():
        dev_type = "🐍 Android Debug (ADB Interface)"
    elif service.upper() == "WINUSB" and "MTP" not in desc.upper():
        dev_type = "🔌 Telefon zaryad rejimi"
    elif service.upper() == "USBRNDIS6" and pclass.upper() == "NET":
        dev_type = "🌐 Internet sharing (USB tethering)"
    elif service.upper() == "USBAUDIO" and pclass.upper() == "MEDIA":
        dev_type = "🎧 USB Audio qurilma"
    else:
        dev_type = "❔ Noma’lum qurilma"

    print("=" * 70)
    print(f"🆕 {dev_type}")
    print(f"📦 Name: {name}")
    print(f"🔧 Service: {service}")
    print(f"🪪 PNPClass: {pclass}")
    print(f"🆔 PNPDeviceID: {pnpid}")
    print("=" * 70)



def monitor_usb_fast():
    """Yangi USB qurilma ulanayotganini aniqlaydi va Win32_DiskDrive ma'lumotini tezda oladi."""
    a = 0
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.watch_for(
        # notification_type="Creation",
        wmi_class="Win32_PnPEntity"
    )
    print("[Monitor] USB / MTP qurilmalarni kuzatish boshlandi...\n")

    while True:
        try:
            device = watcher(timeout_ms=500)

            if not device:
                continue

            # WMI obyekt atributlarini olish
            pnp_id = getattr(device, "PNPDeviceID", "") or ""
            service = getattr(device, "Service", "") or ""
            name = getattr(device, "Name", "") or ""

            # faqat USB mass storage uchun
            if not pnp_id.startswith("USBSTOR"):
                continue
            classify_device(device)
            print(f"\n[Yangi USB Qurilma topildi] {name}")
            print(f"PNPDeviceID: {pnp_id}")
            print(f"Service: {service}")

            # ⚡ Tez qidirish: Win32_DiskDrive da shu PNPDeviceID bilan mos obyektni topish
            for disk in c.Win32_DiskDrive():
                if getattr(disk, "PNPDeviceID", "").strip().lower() == pnp_id.strip().lower():
                    print(getattr(disk, "PNPDeviceID", ""))

                    print("\n📀 Qurilma haqida to‘liq ma’lumot:")
                    print(f"  Model: {disk.Model}")
                    print(f"  InterfaceType: {disk.InterfaceType}")
                    print(f"  SerialNumber: {getattr(disk, 'SerialNumber', 'Nomaʼlum')}")
                    print(f"  Size: {int(disk.Size) / (1024 ** 3):.2f} GB")
                    print(f"  FirmwareRevision: {disk.FirmwareRevision}")
                    print(f"  MediaType: {disk.MediaType}")
                    print(f"  DeviceID: {disk.DeviceID}")
                    print(f"  Status: {disk.Status}")
                    print(f"  Caption: {disk.Caption}")
                    print("-" * 70)

                    print(disk)

                    print("-" * 70)
                    break

        except wmi.x_wmi_timed_out:
            continue
        except KeyboardInterrupt:
            print("To‘xtatildi.")
            break
        except Exception as e:
            print("[Xato]:", e)
            time.sleep(1)
    pythoncom.CoUninitialize()

if __name__ == "__main__":
    monitor_usb_fast()
