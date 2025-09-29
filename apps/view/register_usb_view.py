
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
