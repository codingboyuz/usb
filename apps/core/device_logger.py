"""
Qurilma hodisalarini log qilish moduli.
Fayl + SQLite ga yozadi, qurilma turi va bloklash holati bilan.
"""

import logging
import os
from datetime import datetime
from apps.core.device_classifier import DeviceInfo


LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Fayl logger ---
_file_logger = logging.getLogger("usb_device_log")
_file_logger.setLevel(logging.DEBUG)

_log_path = os.path.join(LOG_DIR, f"usb_{datetime.now().strftime('%Y-%m-%d')}.log")
_fh = logging.FileHandler(_log_path, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_file_logger.addHandler(_fh)

# Konsolga ham chiqaradi
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_file_logger.addHandler(_ch)


# Qurilma turi ikonkasi
DEVICE_ICONS = {
    "USB_FLASH":    "💾",
    "EXTERNAL_HDD": "🖴",
    "EXTERNAL_SSD": "⚡",
    "M2_SSD":       "🔲",
    "PHONE_MTP":    "📱",
    "PHONE_ADB":    "🐍",
    "PHONE_CHARGE": "🔌",
    "WPD_STORAGE":  "📦",
    "USB_TETHERING":"🌐",
    "USB_AUDIO":    "🎧",
    "USB_HID":      "⌨️",
    "USB_UNKNOWN":  "❔",
    "UNKNOWN_DISK": "❔",
}


def log_device_connected(info: DeviceInfo, db=None):
    """Qurilma ulanganini log qiladi."""
    icon = DEVICE_ICONS.get(info.device_type, "🔌")
    status = "BLOKLANDI" if info.blocked else "RUXSAT"

    msg = (
        f"{icon} ULANDI [{status}] "
        f"| Tur: {info.device_label} "
        f"| Model: {info.model or '?'} "
        f"| Serial: {info.serial or '?'} "
        f"| Hajm: {f'{info.size_gb} GB' if info.size_gb else '-'} "
        f"| VID:{info.vid or '?'} PID:{info.pid or '?'} "
        f"| PNP: {info.pnp_device_id}"
    )

    if info.blocked:
        _file_logger.warning(msg)
    else:
        _file_logger.info(msg)

    # DB ga yozish
    if db:
        try:
            db.log_access(
                caption=info.caption,
                model=f"[{info.device_type}] {info.model}",
                interface_type=info.interface,
                size=str(info.size_bytes) if info.size_bytes else None,
                serial=info.serial or info.pnp_device_id,
            )
        except Exception as e:
            _file_logger.error(f"DB log xatosi: {e}")


def log_device_blocked(info: DeviceInfo, reason: str = "", db=None):
    """Qurilma bloklanganini alohida log qiladi."""
    icon = DEVICE_ICONS.get(info.device_type, "🔌")
    msg = (
        f"{icon} BLOKLANDI "
        f"| Tur: {info.device_label} "
        f"| Model: {info.model or '?'} "
        f"| Serial: {info.serial or '?'} "
        f"| Sabab: {reason or 'Ro\\'yxatda yo\\'q'} "
        f"| PNP: {info.pnp_device_id}"
    )
    _file_logger.warning(msg)

    if db:
        try:
            db.log_access(
                caption=f"[BLOCKED] {info.caption}",
                model=f"[{info.device_type}] {info.model}",
                interface_type=info.interface,
                size=str(info.size_bytes) if info.size_bytes else None,
                serial=info.serial or info.pnp_device_id,
            )
        except Exception as e:
            _file_logger.error(f"DB log xatosi: {e}")


def log_eject_result(info: DeviceInfo, success: bool, message: str = ""):
    """Eject natijasini log qiladi."""
    icon = DEVICE_ICONS.get(info.device_type, "🔌")
    if success:
        _file_logger.info(f"{icon} EJECT OK | {info.device_label} | {info.serial or info.pnp_device_id} | {message}")
    else:
        _file_logger.error(f"{icon} EJECT XATO | {info.device_label} | {info.serial or info.pnp_device_id} | {message}")
