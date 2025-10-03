import wmi
import pythoncom

# Ulanish turini aniqlash uchun GUID'lar
GUID_WPD = "{e21287e0-1f74-47dc-873d-1a00019389c1}"
GUID_DISKDRIVE = "{4d36e967-e325-11ce-bfc1-08002be10318}"


def get_connected_usb_devices():
    """
    Tizimda ulangan barcha USB disklarni va MTP qurilmalarni topadi.
    """
    devices_list = []

    # Har bir thread uchun COM ulanishini boshlash muhim
    pythoncom.CoInitialize()

    try:
        w = wmi.WMI()

        # Barcha PnP qurilmalarni tekshirish
        for device in w.Win32_PnPEntity():
            class_guid = getattr(device, 'ClassGuid', None)
            pnp_id = getattr(device, 'PNPDeviceID', None)
            name = getattr(device, 'Name', 'Noma\'lum')

            if not class_guid or not pnp_id:
                continue

            class_guid_formatted = class_guid.lower().strip('{}')
            pnp_id_upper = pnp_id.upper()

            device_info = {
                'Name': name,
                'PNP_ID': pnp_id,
                'Type': 'UNKNOWN',
                'Is_USB': False
            }

            # 1. MTP / WPD (Telefonlar)
            if GUID_WPD.strip('{}') in class_guid_formatted:
                device_info['Type'] = 'MTP/WPD (Telefon)'
                devices_list.append(device_info)

            # 2. USB Mass Storage (Disklar, Flashkalar)
            elif GUID_DISKDRIVE.strip('{}') in class_guid_formatted:
                # Faqat USB orqali ulangan Disk Drives ni qabul qilamiz
                if 'USB' in pnp_id_upper or 'USBSTOR' in pnp_id_upper:
                    serial = getattr(device, 'SerialNumber', 'N/A')
                    device_info['Type'] = 'USB Disk (Mass Storage)'
                    device_info['Is_USB'] = True
                    device_info['Serial'] = serial
                    devices_list.append(device_info)

            # Agar siz oddiy USB qurilmalarni ham ko'rmoqchi bo'lsangiz (klaviatura, sichqoncha emas)
            # elif 'USB\' in pnp_id_upper and 'VID' in pnp_id_upper:
            #     # Bu yerda boshqa USB qurilmalar ham aniqlanadi (masalan, hublar)
            #     pass

    except Exception as e:
        print(f"❌ WMI so‘rovida xato: {e}")

    finally:
        pythoncom.CoUninitialize()

    return devices_list


# --- Dasturni sinab ko'rish ---
if __name__ == "__main__":
    print("--- Ulangan USB va MTP qurilmalar ro‘yxati ---")
    devices = get_connected_usb_devices()

    if devices:
        for i, dev in enumerate(devices):
            print(f"\n{i + 1}. Qurilma: {dev['Name']}")
            print(f"   Tur: {dev['Type']}")
            print(f"   PNP ID: {dev['PNP_ID'][:30]}...")
            if 'Serial' in dev:
                print(f"   Serial: {dev['Serial']}")
    else:
        print("Hech qanday faol USB yoki MTP qurilma topilmadi.")