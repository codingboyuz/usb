# import flet as ft
# import sqlite3
# from settings.base import DB_FILE
#
#
# def main(page: ft.Page):
#     page.title = "USB qurilmasini ro'yxatdan o'tkazish"
#     page.padding = 20
#     page.vertical_alignment = "center"
#     page.theme_mode = "light"
#
#     # --- UI elementlari
#     serial_input = ft.TextField(
#         label="USB Serial Raqami",
#         hint_text="Masalan: E823_8FA6_BF53_0001_001B_448B_4A21_D14E",
#         width=400,
#     )
#     status_text = ft.Text("", color="green")
#
#     # --- DB ga yozish funksiyasi
#     def register_usb(e):
#         serial = serial_input.value.strip()
#         if not serial:
#             status_text.value = "❗ Serial raqamni kiriting."
#             status_text.color = "red"
#             page.update()
#             return
#
#         try:
#             conn = sqlite3.connect(DB_FILE)
#             with conn:
#                 conn.execute(
#                     "INSERT INTO registered_devices (serial) VALUES (?)",
#                     (serial,)
#                 )
#             status_text.value = f"✅ Serial '{serial}' muvaffaqiyatli qo'shildi."
#             status_text.color = "green"
#             serial_input.value = ""
#         except sqlite3.IntegrityError:
#             status_text.value = "⚠️ Bu serial allaqachon ro'yxatda bor."
#             status_text.color = "orange"
#         except Exception as ex:
#             status_text.value = f"❌ Xatolik: {ex}"
#             status_text.color = "red"
#         finally:
#             page.update()
#
#     # --- Layout
#     page.add(
#         ft.Column(
#             [
#                 ft.Text("USB qurilmasini ro'yxatdan o'tkazish", size=24, weight="bold"),
#                 serial_input,
#                 ft.ElevatedButton("Ro'yxatga qo'shish", on_click=register_usb),
#                 status_text,
#             ],
#             horizontal_alignment="center",
#             spacing=20,
#         )
#     )
#
#
# if __name__ == "__main__":
#     ft.app(target=main)

import flet as ft


class UsbRegisterAlterDialog:
    def __init__(self):
        self.page = ft.Page

    def handle_action_click(self, e):
        self.page.add(ft.Text(f"Action clicked: {e.control.text}"))
        # e.control is the clicked action button, e.control.parent is the corresponding parent dialog of the button
        self.page.close(e.control.parent)

    def dialog(self):
        cupertino_actions = [
            ft.CupertinoDialogAction(
                "Yes",
                is_destructive_action=True,
                on_click=self.handle_action_click,
            ),
            ft.CupertinoDialogAction(
                text="No",
                is_default_action=False,
                on_click=self.handle_action_click,
            ),
        ]

        return cupertino_actions

    def view(self):


        self.page.open(ft.AlertDialog(
                    title=ft.Text("Material Alert Dialog"),
                    content=ft.Text("Do you want to delete this file?"),
                    actions=self.dialog(),
                )
            )
