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


def monitor_all_devices():
    """WMI orqali yangi qurilmalarni real vaqt rejimida aniqlash."""
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")

    try:
        device = watcher(timeout_ms=3000)
        if not device:
            return

        pnpid = getattr(device, "PNPDeviceID", "") or ""

        # ✅ Global nazorat — agar qurilma ilgari aniqlangan bo‘lsa, qayta ishlanmaydi
        if pnpid in PROCESSED_DEVICES:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔁 Takroriy event ({pnpid}) — e’tiborsiz qoldirildi.")
            return

        # Yangi qurilma
        PROCESSED_DEVICES.add(pnpid)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🆕 Yangi qurilma aniqlanmoqda...")
        classify_device(device)

    except wmi.x_wmi_timed_out:
        pass
    except Exception as e:
        print("[Xato]:", e)
    finally:
        pythoncom.CoUninitialize()




class DeviceMonitor:
    def __init__(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "DeviceChangeMonitor"
        self.class_atom = win32gui.RegisterClass(wc)

        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "HiddenDeviceMonitor",
            0,
            0, 0, 0, 0,
            0, 0, 0, None
        )

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """Windows darajasidagi qurilma hodisalarini tutadi."""
        if msg == win32con.WM_DEVICECHANGE:
            if wparam == win32con.DBT_DEVICEARRIVAL:
                print(f"🔌 [{datetime.now().strftime('%H:%M:%S')}] Qurilma ulandi.")
                threading.Thread(target=monitor_all_devices, daemon=True).start()

            elif wparam == win32con.DBT_DEVNODES_CHANGED:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Qurilma drayveri yangilandi.")
                threading.Timer(0.3, lambda: threading.Thread(target=monitor_all_devices, daemon=True).start()).start()

            elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Qurilma uzildi.")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    @staticmethod
    def run():
        print("🚀 Start monitoring (real-time)...\n")
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.05)  # CPU yukini minimal darajada saqlash


# if __name__ == "__main__":
#     monitor = DeviceMonitor()
#     monitor.run()

















#
#
# # monitor_mtp_devices()
#
# # 	Caption = "E:\\";
# # 	ClassGuid = "{eec5ad98-8080-425f-922a-dabf3de3f69a}";
#
# # PNPDeviceID .... {53F56307-B6BF-11D0-94F2-00A0C91EFB8B}
#
import pythoncom
import wmi
import time


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
            for device in c.Win32_PnPEntity():

                # print(device)
                print("\n")
                print("*" * 50)
                a += 1
                print(a)
                # print(device)
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

# if __name__ == "__main__":
#     monitor_usb_fast()

import threading
import time
import pythoncom
import wmi
from datetime import datetime


# --- O'zingizning yordamchi klaslaringiz ---
class UsbWatcher:
    def check_connection_usb(self, device):
        print("-> [UsbWatcher] USB Disk logikasi ishga tushdi.")

    def phone_checker(self, device):
        print("-> [UsbWatcher] Telefon logikasi ishga tushdi.")


# ---------------------------------------------


class ConnectionType:
    def __init__(self):
        self.usb = UsbWatcher()

    def classify_device(self, device):
        name = getattr(device, "Name", "") or ""
        service = getattr(device, "Service", "") or ""
        device_id = getattr(device, "DeviceID", "").upper()

        # Qo'shimcha ma'lumotni chiqarish
        print("-" * 50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🆕 Qurilma aniqlandi: {name}")

        # 1. USB Mass Storage (Fleshka/HDD) - Eng ishonchli
        if "USBSTOR" in device_id:
            print(f"💾 USB Flesh yoki tashqi HDD: {name}")
            self.usb.check_connection_usb(device=device)

        # 2. MTP/WPD Qurilmalari
        elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
            print(f"📱 MTP Telefon (Media Transfer Protocol): {name}")
            self.usb.phone_checker(device=device)

        # 3. WPD Fayl tizimi (Ba'zi WPD disklar)
        elif service.upper() in ("WUDFWPDFS", "WPDFS"):
            print(f"💾 WPD fayl tizimi (portable storage): {name}")
            selfar.usb.check_connection_usb(device=device)

        # 4. ADB va boshqalar (Sizning eski logikangiz)
        # ...

        else:
            print(f"❔ Aniqlanmagan qurilma: {name} [{service}]")


class DeviceMonitor:
    def __init__(self):
        self.connection_type = ConnectionType()

    def monitor_loop(self):
        # pythoncom.CoInitialize() har bir yangi WMI threadi uchun zarur
        pythoncom.CoInitialize()

        print("[WMI] Portable qurilmalarni kuzatish boshlandi...")

        try:
            c = wmi.WMI()
            # Win32_PnPEntity ning "Creation" voqeasini bloklanmagan holda kuzatish
            watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")

            while True:
                try:
                    # Time-outni kichik qilish faqat kutishni qisqartiradi,
                    # hodisa kelmasa CPU yuklamasi sezilarli o'zgarmaydi.
                    # Asosiy WMI tizimi doimiy skanerlamaydi.
                    device = watcher(timeout_ms=500)

                    if device:
                        self.connection_type.classify_device(device)

                except wmi.x_wmi_timed_out:
                    # Timeout tugadi, hech qanday hodisa yo'q. Qaytadan tinglaymiz.
                    pass
                except Exception as e:
                    print(f"[WMI Xato]: Kutilmagan xato: {e}")
                    time.sleep(5)  # Xatodan keyin 5 sekund kutish

        except Exception as e:
            print(f"[Asosiy Xato]: WMI ni ishga tushirishda xato: {e}")
        finally:
            pythoncom.CoUninitialize()

    def run(self):
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()

        # Asosiy threadni fon kuzatuvi uchun ushlab turish
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Monitoring to'xtatildi (Ctrl+C).")


# if __name__ == "__main__":
#     monitor = DeviceMonitor()
#     monitor.run()


import threading
import time
import win32con
import win32gui
import pythoncom
import wmi
from datetime import datetime


# from apps.core.usb_watcher import UsbWatcher # Bu klassni joyida bo'lmagani uchun bo'sh e'lon qilamiz

class UsbWatcher:
    # Bu metodlar sizning boshqa logikangizni bajaradi.
    def check_connection_usb(self, device):
        print("-> [UsbWatcher] USB Disk logikasi ishga tushdi.")
        print(device)

    def phone_checker(self, device):
        print("-> [UsbWatcher] Telefon logikasi ishga tushdi.")
        print(device)















# --- Asosiy o'zgartirilgan sinf ---

class ConnectionType:
    def __init__(self):
        self.usb = UsbWatcher()
        # Qurilmalarni kuzatish uchun to'plam
        self.known_devices = self.get_current_pnp_ids()

    def get_current_pnp_ids(self):
        """Hozirgi ulangan qurilmalarning DeviceID/PNPDeviceID-larini oladi."""
        # Bu yordamchi funksiya hisoblash vaqtidagi ulangan qurilmalarni saqlash uchun.
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            return {
                (getattr(d, "DeviceID", "") or getattr(d, "PNPDeviceID", ""))
                for d in c.query("SELECT DeviceID, PNPDeviceID FROM Win32_PnPEntity")
            }
        except Exception as e:
            print(f"[Xato] Hozirgi qurilmalarni olishda xato: {e}")
            return set()
        finally:
            pythoncom.CoUninitialize()

    def classify_device(self, device):
        name = getattr(device, "Name", "") or ""
        service = getattr(device, "Service", "") or ""
        device_id = getattr(device, "DeviceID", "").upper()
        pclass = getattr(device, "PNPClass", "") or ""

        # Print the detailed device info if needed
        # print(device)

        # 1. USB Mass Storage (Fleshka/HDD) - Eng ishonchli
        if "USBSTOR" in device_id:
            print(f"💾 USB Flesh yoki tashqi HDD: {name}")
            self.usb.check_connection_usb(device=device)

        # 2. MTP Telefon
        elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
            print(f"📱 MTP Telefon (Media Transfer Protocol): {name}")
            self.usb.phone_checker(device=device)

        # 3. WPD Fayl tizimi
        elif service.upper() in ("WUDFWPDFS", "WPDFS"):
            print(f"💾 WPD fayl tizimi (portable storage): {name}")
            self.usb.check_connection_usb(device=device)

        # 4. ADB, Tethering va boshqalar (Sizning asl logikangiz)
        elif service.upper() == "WINUSB" and "ADB" in name.upper():
            print(f"🐍 Android Debug (ADB Interface): {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "USBRNDIS6" and pclass.upper() == "NET":
            print(f"🌐 Internet sharing (USB tethering): {name}")
            self.usb.phone_checker(device=device)

        # ... qolgan tekshiruvlar ...

        else:
            print(f"❔ Aniqlanmagan qurilma: {name} [{service}]")

    def connection_device(self):
        """
        DBT_DEVICEARRIVAL xabari kelganda ishga tushadi.
        Faqat yangi ulangan qurilmani topadi.
        """
        print("-" * 50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WMI orqali yangi qurilma qidirilmoqda...")
        pythoncom.CoInitialize()

        try:
            c = wmi.WMI()

            # Barcha PnP obyektlarni olish
            all_current_pnp = {
                (getattr(d, "DeviceID", "") or getattr(d, "PNPDeviceID", "")): d
                for d in c.query("SELECT * FROM Win32_PnPEntity")
            }

            # Eski ro'yxat bilan taqqoslash (yangi kelgan qurilmani topish)
            new_pnp_ids = all_current_pnp.keys() - self.known_devices

            if new_pnp_ids:
                # Topilgan yangi qurilmalarni qayta ishlash
                for pnp_id in new_pnp_ids:
                    device = all_current_pnp[pnp_id]
                    self.classify_device(device)

                # Ro'yxatni yangilash
                self.known_devices = set(all_current_pnp.keys())
            else:
                # Agar to'g'ridan-to'g'ri topilmasa (vaqt muammosi)
                print("⚠️ Yangi qurilma topilmadi yoki drayverlar hali sozlanmagan.")


        except Exception as e:
            print(f"[Xato] connection_device: {e}")
        finally:
            pythoncom.CoUninitialize()


# --- Sizning asl DeviceMonitor sinfingiz ---

class DeviceMonitor:
    def __init__(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "DeviceChangeMonitor"
        self.class_atom = win32gui.RegisterClass(wc)
        self.connection_type = ConnectionType()  # Bu yerda birinchi marta ulangan qurilmalar ro'yxati olinadi.

        # Ko‘rinmas oyna yaratish
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "HiddenDeviceMonitor",
            0, 0, 0, 0, 0, 0, 0, 0, None
        )

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            if wparam == win32con.DBT_DEVICEARRIVAL:
                print(f"🔌 [{datetime.now().strftime('%H:%M:%S')}] Qurilma ulandi (WM_DEVICECHANGE).")
                # DBT_DEVICEARRIVAL kelganda yangi qurilmani qidirishni alohida threadda ishga tushiramiz
                threading.Thread(target=self.connection_type.connection_device, daemon=True).start()

            elif wparam == win32con.DBT_DEVNODES_CHANGED:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Qurilma drayveri yangilandi (WM_DEVICECHANGE).")
                # Drayver o'zgarganda qayta tekshirish foydali bo'lishi mumkin
                threading.Timer(0.3, lambda: threading.Thread(target=self.connection_type.connection_device,
                                                              daemon=True).start()).start()

            elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
                print(f"❌ [{datetime.now().strftime('%H:%M:%M')}] Qurilma uzildi (WM_DEVICECHANGE).")
                # Qurilma uzilganda ro'yxatni yangilash
                threading.Thread(target=self._update_known_devices_on_remove, daemon=True).start()

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _update_known_devices_on_remove(self):
        """Qurilma uzilganda known_devices ro'yxatini yangilash uchun."""
        time.sleep(1)  # Tizim ma'lumotni yangilashini kutish
        self.connection_type.known_devices = self.connection_type.get_current_pnp_ids()

    @staticmethod
    def run():
        print("Start monitoring (real-time)...")
        # CPU yuklamasini kamaytirish uchun PumpWaitingMessages o'rniga PumpMessages ishlatiladi.
        # win32gui.PumpMessages() CPUga deyarli nol yuklama beradi.
        win32gui.PumpMessages()


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.run()