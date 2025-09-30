import subprocess
import os
from settings.base import EXE_USB_EJECT


def eject_usb_device(pnp_device_id):
    """
    Tuzilgan C dasturini chaqirib, USB qurilmasini chiqaradi.

    :param pnp_device_id: USBSTOR\DISK&VEN_... kabi Device Instance ID.
    :return: (bool, str) - Muvaffaqiyat holati va xabar.
    """

    # 1. C dasturining yo'lini aniqlash
    # exe_path ni o'zingizning to'g'ri yo'lingizga o'zgartiring!

    # Agar C dasturi mavjud bo'lmasa
    if not os.path.exists(EXE_USB_EJECT):
        return False, f"Xato: Eject dasturi topilmadi: {EXE_USB_EJECT}"

    try:
        # 2. subprocess.run orqali C dasturini chaqirish
        # 'shell=True' administrator huquqlari bilan ishlashga yordam beradi,
        # ammo 'check=True' xato bo'lsa istisno tashlaydi
        result = subprocess.run(
            [EXE_USB_EJECT, pnp_device_id],  # Argumentlar ro'yxati
            capture_output=True,  # Natijani va xatoni ushlab turish
            text=True,  # Natijani string sifatida olish
            check=False,  # Xato kodini qaytarsa ham istisno tashlamaslik
            creationflags=subprocess.CREATE_NO_WINDOW  # Konsol oynasini yashirish
        )

        # 3. Natijalarni tekshirish

        # Exit code 0 - muvaffaqiyat
        if result.returncode == 0:
            return True, f"Qurilma muvaffaqiyatli chiqarildi: {pnp_device_id}"

        # Exit code 1 - Eject qilish muvaffaqiyatsiz tugadi (VETO bo'lishi mumkin)
        elif result.returncode == 1:
            error_output = result.stderr.strip()

            # Agar C dasturidan VETO sababi kelgan bo'lsa
            if error_output.startswith("VETO:"):
                veto_code = error_output.split(":")[1]
                return False, f"Qurilmani chiqarish rad etildi (VETO: {veto_code}). Fayllar hali ham ochiq bo'lishi mumkin."

            return False, f"Qurilmani chiqarish muvaffaqiyatsiz tugadi. Noma'lum xato. stderr: {error_output}"

        # Exit code 2 - Argumentlar xatosi (C kodida o'rnatilgan)
        elif result.returncode == 2:
            return False, f"Eject dasturi xatosi: Argumentlar noto'g'ri. stderr: {result.stderr.strip()}"

        # Boshqa xato kodlari
        else:
            return False, f"Noma'lum xato. Chiqish kodi: {result.returncode}. stderr: {result.stderr.strip()}"

    except FileNotFoundError:
        return False, f"Eject dasturi topilmadi. Yo'l: {EXE_USB_EJECT}"
    except Exception as e:
        return False, f"Subprocess ishga tushirishda kutilmagan xato: {e}"


# --- Sinov uchun foydalanish ---

# Sizning Python kodingizdan keladigan ID
device_id = r"USBSTOR\DISK&VEN_VENDORCO&PROD_PRODUCTCODE&REV_2.00\3759361002453620343&0"

# O'zingizning haqiqiy ID ni qo'ying
# misol_id = r"USBSTOR\DISK&VEN_SAMSUNG&PROD_FLASH_DRIVE&REV_1100\0300096C617FA101&0"
# success, message = eject_usb_device(misol_id)

success, message = eject_usb_device(device_id)

print(f"Holat: {'Muvaffaqiyatli' if success else 'Xato'}")
print(f"Xabar: {message}")