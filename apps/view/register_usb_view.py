# import flet as ft
# from apps.db.database import LocalDatabase
# from apps.view.usb_log_view import UsbLogView
#
#
# class UsbRegisterAlterDialog:
#     def __init__(self, page: ft.Page, refresh: UsbLogView):
#         self.page = page
#         self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#         self.page.scroll = ft.ScrollMode.ADAPTIVE
#         self.refresh =refresh
#         self.register_usb_controller = ft.TextField(label="Seria raqam", )
#         self.db = LocalDatabase()
#
#     # CupertinoAlterDialog ni yopish
#     def handle_action_click(self, e):
#         self.register_usb_controller.value = ""
#         self.page.close(e.control.parent)
#         self.page.update()
#
#     # DB ga qo'shuvchi button
#     def btn_click(self, e):
#         # DB ga yangi serial qo‘shish
#         serial = self.register_usb_controller.value.strip()
#         if serial:
#             self.db.add_device(serial=serial)
#             # 🔄 Jadvalni yangilash
#             self.refresh.refresh_registered()
#         self.handle_action_click(e)
#
#     # e argumentini qo‘shdik
#     def view(self, e):
#         return self.page.open(
#             ft.CupertinoAlertDialog(
#                 title=ft.Text("USBni Ro'yxatga olish"),
#                 content=ft.Container(content=self.register_usb_controller, height=50, margin=ft.margin.only(top=15)),
#                 actions=[
#                     ft.CupertinoDialogAction(
#                         "Yes",
#                         is_destructive_action=True,
#                         on_click=self.btn_click,
#                     ),
#                     ft.CupertinoDialogAction(
#                         text="No",
#                         is_default_action=False,
#                         on_click=self.handle_action_click,
#                     ),
#                 ],
#             )
#         ),
import flet as ft
from apps.db.database import LocalDatabase
from apps.view.usb_log_view import UsbLogView


class UsbRegisterAlterDialog:
    """Yangi USB serial qo'shish dialogi."""

    def __init__(self, page: ft.Page, log_view: UsbLogView):
        self.page = page
        self.log_view = log_view
        self.db = LocalDatabase()
        self.serial_field = ft.TextField(label="Seria raqam", autofocus=True)

    def _close(self, dlg_action_event):
        self.serial_field.value = ""
        self.page.close(dlg_action_event.control.parent)
        self.page.update()

    def _add_and_refresh(self, e):
        serial = (self.serial_field.value or "").strip()
        if serial:
            # DB ga qo'shamiz
            self.db.add_device(serial=serial)
            # Jadval rowslarini yangilaymiz
            self.log_view.refresh_registered()
            # ⚠️ Endi jadval sahifada — butun sahifani redraw qilamiz:
            self.page.update()
        self._close(e)

    def open(self, _):
        self.page.open(
            ft.CupertinoAlertDialog(
                title=ft.Text("USBni ro'yxatga olish"),
                content=ft.Container(self.serial_field, height=50, margin=ft.margin.only(top=12)),
                actions=[
                    ft.CupertinoDialogAction(text="Yes", is_destructive_action=True, on_click=self._add_and_refresh),
                    ft.CupertinoDialogAction(text="No", on_click=self._close),
                ],
            )
        )
