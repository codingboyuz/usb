import subprocess
import sys
from  settings.base import EXE_MTP_EJECT
import os
import win32file
import win32con
import ctypes
from settings.base import EXE_USB_EJECT

# c da yozilgan usb izvlech qilish uchun

"""
disk harifini aniqlab chiqarib yuorishga tayorlaydi 
"""

class UsbEject:

    @staticmethod
    def eject_usb_device(pnp_device_id):
        """
        Tuzilgan C dasturini chaqirib, USB qurilmasini chiqaradi.

        :param pnp_device_id: USBSTOR\DISK&VEN_... kabi Device Instance ID.
        :return: (bool, str) - Muvaffaqiyat holati va xabar.
        """
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
                    print( f"VETO:=============>Qurilmani chiqarish rad etildi (VETO: {veto_code}). Fayllar hali ham ochiq bo'lishi mumkin.")
                    return False, f"Qurilmani chiqarish rad etildi (VETO: {veto_code}). Fayllar hali ham ochiq bo'lishi mumkin."

                return False, f"Qurilmani chiqarish muvaffaqiyatsiz tugadi. Noma'lum xato. stderr: {error_output}"

            # Exit code 2 - Argumentlar xatosi (C kodida o'rnatilgan)
            elif result.returncode == 2:
                return False, f"Eject dasturi xatosi: Argumentlar noto'g'ri. stderr: {result.stderr.strip()}"

            # Boshqa xato kodlari
            else:
                return False, f"Noma'lum xato. Chiqish kodi: {result.returncode}. stderr: {result.stderr.strip()}"

        except Exception as e:
            return False, f"Subprocess ishga tushirishda kutilmagan xato: {e}"

    @staticmethod
    def mtp_connection_eject(mode):
        """
        Telefonni USB rejimini o‘zgartiradi.
        """

        try:
            # .exe ni phone_id argumenti bilan ishga tushirish
            result = subprocess.run(
                [EXE_MTP_EJECT, mode],
                capture_output=True,  # stdout va stderr ni yig‘ish
                text=True,  # Chiqishni matn sifatida olish
                encoding='utf-8'  # UTF-8 kodlash
            )

            # Natijalarni ko‘rsatish
            print("stdout (natija):", result.stdout)
            print("stderr (xato):", result.stderr)
            print("Qaytarilgan kod:", result.returncode)

            if result.returncode == 0:
                print("Qurilma muvaffaqiyatli chiqarildi yoki faolsizlantirildi.")
            else:
                print("Xatolik yuz berdi. Batafsil ma'lumot yuqorida.")

        except Exception as e:
            print(f"Python xatosi: {str(e)}")

# if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         ejector = UsbEject()
#         ejector.eject_by_pnp(sys.argv[1])