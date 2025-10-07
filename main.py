import threading
import time
import win32con
import win32gui
import pythoncom
import wmi
from datetime import datetime
from apps.core.usb_watcher import UsbWatcher


class ConnectionType:
    def __init__(self):
        self.usb = UsbWatcher()
        self.known_devices = set()  # <-- global saqlanadi

    def classify_device(self, device):
        name = getattr(device, "Name", "") or ""
        service = getattr(device, "Service", "") or ""
        pclass = getattr(device, "PNPClass", "") or ""
        desc = getattr(device, "Description", "") or ""

        if service.startswith("USBSTOR") or "DISK" in desc.upper():
            print(f"💾 USB Flesh yoki tashqi HDD: {name}")
            print(device)

        elif service.upper() in ("WUDFWPDFS", "WPDFS"):
            print(f"💾 WPD fayl tizimi (portable storage): {name}")
            print(device)

            self.usb.check_connection_usb(device=device)

        elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
            print(f"📱 MTP Telefon (Media Transfer Protocol): {name}")
            print(device)

            self.usb.phone_checker(device=device)

        elif service.upper() == "WINUSB" and "ADB" in name.upper():
            print(f"🐍 Android Debug (ADB Interface): {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "WINUSB" and "MTP" not in desc.upper():
            print(f"🔌 Telefon zaryad rejimi: {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "USBRNDIS6" and pclass.upper() == "NET":
            print(f"🌐 Internet sharing (USB tethering): {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "USBAUDIO" and pclass.upper() == "MEDIA":
            print(f"🎧 USB Audio qurilma: {name}")
            self.usb.phone_checker(device=device)

        elif "MIDI" in name.upper():
            print(f"🎹 MIDI qurilma (telefon MIDI rejimi): {name}")

        else:
            print(device)
            print(f"❔ Aniqlanmagan qurilma: {name} [{service}]")

    def connection_device(self):
        print("Ishladim")
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()

            watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")
            # print(watcher)
            device = watcher(timeout_ms=3000)
            print("-"*50)
            print(f"device {device}")
            print("-"*50)

            if not device:
                return

            vidpid = getattr(device, "PNPDeviceID", "") or ""

            # 🔒 Faqat yangi qurilmalarni qayta ishlash
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🆕 Qurilma aniqlanmoqda...")
            self.classify_device(device)

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
        self.connection_type = ConnectionType()

        # Ko‘rinmas oyna yaratish
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "HiddenDeviceMonitor",
            0, 0, 0, 0, 0, 0, 0, 0, None
        )

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            if wparam == win32con.DBT_DEVICEARRIVAL:
                print(f"🔌 [{datetime.now().strftime('%H:%M:%S')}] Qurilma ulandi.")
                threading.Thread(target=self.connection_type.connection_device, daemon=True).start()

            elif wparam == win32con.DBT_DEVNODES_CHANGED:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Qurilma drayveri yangilandi.")
                threading.Timer(0.3, lambda: threading.Thread(target=self.connection_type.connection_device, daemon=True).start()).start()

            elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Qurilma uzildi.")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    @staticmethod
    def run():
        print("Start monitoring (real-time)...")
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.05)


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.run()
