
import threading
import time

import win32con
import win32gui

from apps.core.usb_watcher import UsbWatcher
from datetime import datetime



class DeviceMonitor:
    def __init__(self):
        # Window class yaratamiz
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "DeviceChangeMonitor"
        self.class_atom = win32gui.RegisterClass(wc)
        self.watcher = UsbWatcher()

        # Ko‘rinmas (hidden) oynani yaratamiz
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "HiddenDeviceMonitor",
            0,
            0, 0, 0, 0,
            0, 0, 0, None
        )

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            if wparam == win32con.DBT_DEVICEARRIVAL:   # USB ulanadi
                print(f"🔌 Device Connected {wparam}")
                threading.Thread(target=self.watcher.phone_checker, daemon=True).start()
                threading.Thread(target=self.watcher.check_connection_usb, daemon=True).start()


            elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:  # USB uziladi
                print("❌ Device Removed")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    @staticmethod
    def run():
        print("Start monitoring (real-time)...")
        # Windows message loop
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.01)  # CPU ni 100% yeb yubormasligi uchun


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.run()
