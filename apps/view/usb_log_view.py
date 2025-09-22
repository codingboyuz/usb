import flet as ft
from apps.db.database import LocalDatabase


class UsbLogApp:
    """USB Access loglarni ko‘rsatuvchi klass (UserControl talab qilinmaydi)."""

    def __init__(self):
        self.local_db = LocalDatabase()

    def view(self) -> ft.Control:
        rows = self.local_db.get_access_log()

        data_table = ft.DataTable(
            expand=True,
            heading_row_height=40,
            data_row_min_height=36,
            columns=[
                ft.DataColumn(ft.Text("Time", weight="bold")),
                ft.DataColumn(ft.Text("Caption", weight="bold")),
                ft.DataColumn(ft.Text("Model", weight="bold")),
                ft.DataColumn(ft.Text("Interface", weight="bold")),
                ft.DataColumn(ft.Text("Size", weight="bold")),
                ft.DataColumn(ft.Text("Serial", weight="bold")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["timestamp"])),
                        ft.DataCell(ft.Text(r["caption"])),
                        ft.DataCell(ft.Text(r["model"])),
                        ft.DataCell(ft.Text(r["interface_type"])),
                        ft.DataCell(ft.Text(str(r["size"]))),
                        ft.DataCell(ft.Text(r["serial"])),
                    ]
                )
                for r in rows
            ],
        )

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                ft.Text("Noqonuniy ulangan qrulmalar", size=24, weight="bold"),
                ft.Divider(),
                ft.Container(data_table, expand=True),
            ],
        )

from register_usb_view import UsbRegisterAlterDialog
def main(page: ft.Page):
    page.title = "Usb Killer"
    page.theme_mode = "light"
    page.padding = 20
    page.scroll = "auto"
    page.horizontal_alignment = "stretch"
    usb = UsbRegisterAlterDialog()

    app = UsbLogApp()
    page.floating_action_button  = ft.FloatingActionButton(icon="add",on_click=usb.view)

    page.add(app.view())   # klassdan view() orqali Control ni qo‘shamiz


if __name__ == "__main__":
    ft.app(target=main)
