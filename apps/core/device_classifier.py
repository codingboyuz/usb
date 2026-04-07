"""
Qurilma turini aniq aniqlash moduli.
USB Flash, tashqi HDD, M.2 (USB adapter), Telefon, Audio va boshqalarni farqlaydi.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class DeviceInfo:
    """Aniqlangan qurilma haqida to'liq ma'lumot."""
    device_type: str          # "USB_FLASH" | "EXTERNAL_HDD" | "M2_SSD" | "PHONE_MTP" | ...
    device_label: str         # Foydalanuvchiga ko'rsatiladigan nom
    caption: str              # Windows qurilma nomi
    model: str                # Ishlab chiqaruvchi/model
    serial: Optional[str]     # Seriya raqami
    size_bytes: Optional[int] # Hajmi baytlarda
    size_gb: Optional[float]  # Hajmi GB da
    interface: str            # "USB" | "MTP" | "ADB" | "AUDIO" | ...
    pnp_device_id: str        # Windows PNPDeviceID
    media_type: Optional[str] # Windows MediaType maydoni
    vid: Optional[str]        # Vendor ID (masalan "2717" Xiaomi)
    pid: Optional[str]        # Product ID
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    blocked: bool = False     # Bloklangani yoki yo'q


def _extract_vid_pid(pnp_id: str) -> tuple[Optional[str], Optional[str]]:
    """PNPDeviceID dan VID va PID ni ajratib oladi."""
    vid, pid = None, None
    parts = pnp_id.upper()
    if "VID_" in parts:
        try:
            vid = parts.split("VID_")[1][:4]
        except IndexError:
            pass
    if "PID_" in parts:
        try:
            pid = parts.split("PID_")[1][:4]
        except IndexError:
            pass
    return vid, pid


def classify_disk_device(disk) -> DeviceInfo:
    """
    Win32_DiskDrive obyektidan qurilma turini aniq aniqlaydi.

    Farqlash mantigi:
    ┌─────────────────┬────────────────────────────────────────────────────┐
    │ Qurilma turi    │ Belgilar                                           │
    ├─────────────────┼────────────────────────────────────────────────────┤
    │ USB Flash       │ InterfaceType=USB, MediaType=Removable, <256 GB   │
    │ Tashqi HDD      │ InterfaceType=USB, MediaType=Fixed/External HDD   │
    │ M.2 USB adapter │ InterfaceType=USB, model da NVMe/SSD/M.2 bor,     │
    │                 │ yoki hajm >512 GB                                  │
    │ Tashqi SSD      │ InterfaceType=USB, model da SSD bor, Fixed media  │
    └─────────────────┴────────────────────────────────────────────────────┘
    """
    caption     = getattr(disk, "Caption", "") or ""
    model       = getattr(disk, "Model", "") or ""
    interface   = getattr(disk, "InterfaceType", "") or ""
    serial      = getattr(disk, "SerialNumber", None)
    pnp_id      = getattr(disk, "PNPDeviceID", "") or ""
    media_type  = getattr(disk, "MediaType", "") or ""
    size_raw    = getattr(disk, "Size", None)

    size_bytes  = int(size_raw) if size_raw else None
    size_gb     = round(size_bytes / (1024 ** 3), 2) if size_bytes else None
    vid, pid    = _extract_vid_pid(pnp_id)
    model_upper = model.upper()

    # --- Qurilma turini aniqlash ---
    if interface.upper() == "USB":

        # M.2 yoki NVMe USB adapterda
        if any(kw in model_upper for kw in ("NVME", "M.2", "M2", "NVME SSD")):
            return DeviceInfo(
                device_type="M2_SSD",
                device_label="M.2 / NVMe SSD (USB adapter)",
                caption=caption, model=model, serial=serial,
                size_bytes=size_bytes, size_gb=size_gb,
                interface="USB", pnp_device_id=pnp_id,
                media_type=media_type, vid=vid, pid=pid,
            )

        # Tashqi SSD (model da SSD yozuvi bor, lekin NVMe emas)
        if "SSD" in model_upper and "REMOVABLE" not in media_type.upper():
            return DeviceInfo(
                device_type="EXTERNAL_SSD",
                device_label="Tashqi SSD",
                caption=caption, model=model, serial=serial,
                size_bytes=size_bytes, size_gb=size_gb,
                interface="USB", pnp_device_id=pnp_id,
                media_type=media_type, vid=vid, pid=pid,
            )

        # USB Flash (olinadigan media, odatda kichik hajm)
        if "REMOVABLE" in media_type.upper():
            return DeviceInfo(
                device_type="USB_FLASH",
                device_label="USB Flash xotira",
                caption=caption, model=model, serial=serial,
                size_bytes=size_bytes, size_gb=size_gb,
                interface="USB", pnp_device_id=pnp_id,
                media_type=media_type, vid=vid, pid=pid,
            )

        # Tashqi HDD (katta hajm yoki "Fixed" media)
        if "FIXED" in media_type.upper() or "EXTERNAL" in media_type.upper():
            return DeviceInfo(
                device_type="EXTERNAL_HDD",
                device_label="Tashqi HDD",
                caption=caption, model=model, serial=serial,
                size_bytes=size_bytes, size_gb=size_gb,
                interface="USB", pnp_device_id=pnp_id,
                media_type=media_type, vid=vid, pid=pid,
            )

        # Hajm bo'yicha taxminiy farqlash (media_type aniqlanmagan holat)
        if size_gb and size_gb > 256:
            return DeviceInfo(
                device_type="EXTERNAL_HDD",
                device_label="Tashqi HDD (katta hajm)",
                caption=caption, model=model, serial=serial,
                size_bytes=size_bytes, size_gb=size_gb,
                interface="USB", pnp_device_id=pnp_id,
                media_type=media_type, vid=vid, pid=pid,
            )

    # SCSI interfeys (ba'zi adapterlar SCSI sifatida ko'rinadi)
    if interface.upper() == "SCSI":
        return DeviceInfo(
            device_type="EXTERNAL_HDD",
            device_label="Tashqi HDD (SCSI/USB adapter)",
            caption=caption, model=model, serial=serial,
            size_bytes=size_bytes, size_gb=size_gb,
            interface="SCSI", pnp_device_id=pnp_id,
            media_type=media_type, vid=vid, pid=pid,
        )

    # Noma'lum disk qurilma
    return DeviceInfo(
        device_type="UNKNOWN_DISK",
        device_label="Noma'lum disk qurilma",
        caption=caption, model=model, serial=serial,
        size_bytes=size_bytes, size_gb=size_gb,
        interface=interface, pnp_device_id=pnp_id,
        media_type=media_type, vid=vid, pid=pid,
    )


def classify_pnp_device(device) -> Optional[DeviceInfo]:
    """
    Win32_PnPEntity obyektidan qurilma turini aniqlaydi.
    Disk bo'lmagan qurilmalar uchun (telefon, audio, ADB...).

    None qaytarsa — bu qurilma diskdir, classify_disk_device() ishlatilsin.
    """
    name        = getattr(device, "Name", "") or ""
    service     = getattr(device, "Service", "") or ""
    pclass      = getattr(device, "PNPClass", "") or ""
    pnp_id      = getattr(device, "PNPDeviceID", "") or ""
    manufacturer= getattr(device, "Manufacturer", "") or ""
    compatible  = getattr(device, "CompatibleID", []) or []

    service_up  = service.upper()
    name_up     = name.upper()
    pclass_up   = pclass.upper()

    # Disklar classify_disk_device() orqali aniqlanadi
    if pnp_id.startswith("USBSTOR") or service_up in ("DISK", "USBSTOR"):
        return None

    # MTP Telefon
    if service_up in ("WUDFWPDMTP", "WPD_MTP") or pclass_up == "WPD":
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="PHONE_MTP",
            device_label="Telefon (MTP protokoli)",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="MTP", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # WPD fayl tizimi (portable storage)
    if service_up in ("WUDFWPDFS", "WPDFS"):
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="WPD_STORAGE",
            device_label="WPD Portable Storage",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="WPD", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # Android ADB
    if service_up == "WINUSB" and "ADB" in name_up:
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="PHONE_ADB",
            device_label="Android Debug Bridge (ADB)",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="ADB", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # Faqat zaryad rejimidagi telefon
    if service_up == "WINUSB":
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="PHONE_CHARGE",
            device_label="Telefon (faqat zaryad rejimi)",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="USB_CHARGE", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # USB Tethering (internet ulashish)
    if service_up == "USBRNDIS6" and pclass_up == "NET":
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="USB_TETHERING",
            device_label="USB Internet (Tethering)",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="RNDIS", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # USB Audio
    if service_up == "USBAUDIO" and pclass_up == "MEDIA":
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="USB_AUDIO",
            device_label="USB Audio qurilma",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="USB_AUDIO", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # USB HID (sichqoncha, klaviatura)
    if pclass_up == "HIDCLASS" or service_up == "HIDUSB":
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="USB_HID",
            device_label="USB HID (sichqoncha/klaviatura)",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="HID", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    # Noma'lum
    if pnp_id.startswith("USB\\"):
        vid, pid = _extract_vid_pid(pnp_id)
        return DeviceInfo(
            device_type="USB_UNKNOWN",
            device_label="Noma'lum USB qurilma",
            caption=name, model=manufacturer, serial=pnp_id,
            size_bytes=None, size_gb=None,
            interface="USB", pnp_device_id=pnp_id,
            media_type=None, vid=vid, pid=pid,
        )

    return None  # USB qurilma emas
