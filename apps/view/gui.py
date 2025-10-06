import pythoncom
import wmi
import time

def classify_device(device):
    """Win32_PnPEntity obyektidan qurilma turini aniqlaydi."""
    name = getattr(device, "Name", "") or ""
    service = getattr(device, "Service", "") or ""
    pclass = getattr(device, "PNPClass", "") or ""
    desc = getattr(device, "Description", "") or ""
    vidpid = getattr(device, "PNPDeviceID", "") or ""

    # ⚙️ Turi aniqlash qoidalari
    if service.startswith("USBSTOR") or "DISK" in desc.upper():
        return "💾 USB Flash yoki Tashqi HDD"
    elif service.upper() in ("WUDFWPDFS", "WPDFS"):
        return "💾 WPD fayl tizimi (portable storage)"
    elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
        return "📱 MTP Telefon (Media Transfer Protocol)"
    elif service.upper() == "WINUSB" and "ADB" in name.upper():
        return "🐍 Android Debug (ADB Interface)"
    elif service.upper() == "WINUSB" and "MTP" not in desc.upper():
        return "🔌 Telefon zaryad rejimi (faqat WINUSB)"
    elif "USBCCGP" in service.lower():
        return "🧩 USB Composite (asosiy kontroller)"
    elif "MTP" in desc.upper():
        return "📱 MTP (nomi bo‘yicha)"
    elif pclass.upper() == "WPD":
        return "📱 Portable Device (WPD)"
    else:
        return f"❔ Aniqlanmagan: {service or pclass or desc}"

def monitor_all_devices():
    """Barcha USB / MTP / ADB / Portable qurilmalarni real vaqtda kuzatish."""
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")
    print("[Monitor] Qurilmalar real vaqt rejimida kuzatilmoqda...\n")

    known = set()  # PNPDeviceID takrorlanmasligi uchun

    while True:
        try:
            device = watcher(timeout_ms=1000)
            if not device:
                continue

            pnpid = getattr(device, "PNPDeviceID", "") or ""
            if pnpid in known:
                continue
            known.add(pnpid)

            device_type = classify_device(device)

            print("=" * 70)
            print(f"🆕 Qurilma topildi: {getattr(device, 'Name', 'Nomaʼlum')}")
            print(f"PNPDeviceID: {pnpid}")
            print(f"Service: {getattr(device, 'Service', '')}")
            print(f"PNPClass: {getattr(device, 'PNPClass', '')}")
            print(f"Tasnif: {device_type}")
            print("=" * 70)

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
    monitor_all_devices()


def monitor_mtp_devices():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")
    print("[MTP] Portable qurilmalarni kuzatish boshlandi...")
    while True:
        try:
            device = watcher(timeout_ms=500)

            service = getattr(device, "Service", "") or ""

            if "WpdFs" in service:
                print("Aniqlash: 💾 USB Flesh-disk (WPD Fayl Tizimi)")
                print(device)
            elif "WpdMtp" in service:
                print("Aniqlash: 📱 MTP Telefon (WPD MTP Protokoli)")
                print(device)


        except wmi.x_wmi_timed_out:
            pass
        except Exception as e:
            print("[Xato] MTP kuzatuvchi:", e)
            time.sleep(1)


# monitor_mtp_devices()

# 	Caption = "E:\\";
# 	ClassGuid = "{eec5ad98-8080-425f-922a-dabf3de3f69a}";

# PNPDeviceID .... {53F56307-B6BF-11D0-94F2-00A0C91EFB8B}

import pythoncom
import wmi
import time



def monitor_usb_fast():
    """Yangi USB qurilma ulanayotganini aniqlaydi va Win32_DiskDrive ma'lumotini tezda oladi."""
    a =0
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
            # print(device)
            print("\n")
            print("*" * 50)
            a += 1
            print(a)
            print(device)
            print("*" * 50)

            if not device:
                continue

            # WMI obyekt atributlarini olish
            pnp_id = getattr(device, "PNPDeviceID", "") or ""
            service = getattr(device, "Service", "") or ""
            name = getattr(device, "Name", "") or ""

            # faqat USB mass storage uchun
            if not pnp_id.startswith("USBSTOR"):
                continue

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
#
# if __name__ == "__main__":
#     monitor_usb_fast()
