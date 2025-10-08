import threading
import time

import pythoncom
import wmi

from apps.core.usb_watcher import UsbWatcher


class ConnectionType:
    def __init__(self):
        self.usb = UsbWatcher()
        self.known_devices = set()  # <-- global saqlanadi

    def classify_device(self, device):

        # print("I'm Worked")
        name = getattr(device, "Name", "") or ""
        service = getattr(device, "Service", "") or ""
        pclass = getattr(device, "PNPClass", "") or ""
        desc = getattr(device, "Description", "") or ""

        # if service.startswith("USBSTOR") or "DISK" in desc.upper():
        #     print(f"💾 USB Flesh yoki tashqi HDD: {device}")
        #     self.usb.check_connection_usb(device=device)
        if service=="DISK":

            print(f"💾 USB Flesh yoki tashqi DISK HDD: {device}")
            self.usb.check_connection_usb(device=device)

        elif service.upper() in ("WUDFWPDFS", "WPDFS"):
            # print(f"💾 WPD fayl tizimi (portable storage): {device}")
            pass

            # self.usb.check_connection_usb(device=device)

        elif service.upper() in ("WUDFWPDMTP", "WPD_MTP"):
            print(f"📱 MTP Telefon (Media Transfer Protocol): {name}")
            # print(device)

            # self.usb.phone_checker(device=device)

        elif service.upper() == "WINUSB" and "ADB" in name.upper():
            print(f"🐍 Android Debug (ADB Interface): {name}")
            # self.usb.phone_checker(device=device)

        elif service.upper() == "WINUSB" and "MTP" not in desc.upper():
            print(f"🔌 Telefon zaryad rejimi: {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "USBRNDIS6" and pclass.upper() == "NET":
            print(f"🌐 Internet sharing (USB tethering): {name}")
            self.usb.phone_checker(device=device)

        elif service.upper() == "USBAUDIO" and pclass.upper() == "MEDIA":
            print(f"🎧 USB Audio qurilma: {name}")
            # self.usb.phone_checker(device=device)

        elif "MIDI" in name.upper():
            print(f"🎹 MIDI qurilma (telefon MIDI rejimi): {name}")

        else:
            # print(device)
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
                        # print(device)
                        threading.Timer(0.1,lambda :threading.Thread(target=self.connection_type.classify_device(device),daemon=True).start()).start()
                        threading.Thread(target=self.connection_type.classify_device(device), daemon=True).start()

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


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.run()