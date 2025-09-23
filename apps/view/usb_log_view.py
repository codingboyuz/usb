# import flet as ft
# from apps.db.database import LocalDatabase
#
#
# class UsbLogView:
#     """USB Access loglarni ko‘rsatuvchi klass (UserControl talab qilinmaydi)."""
#
#     def __init__(self):
#         self.local_db = LocalDatabase()
#         self.get_registered = ft.DataTable(
#             expand=True,
#             heading_row_height=40,
#             data_row_min_height=36,
#             columns=[ft.DataColumn(ft.Text("ID", weight="bold")),
#                      ft.DataColumn(ft.Text("Serial", weight="bold")), ],
#             rows=[
#
#             ]
#         )
#
#     def get_log_view(self) -> ft.Control:
#         rows = self.local_db.get_access_log()
#         print(rows)
#
#         data_table = ft.DataTable(
#             expand=True,
#             heading_row_height=40,
#             data_row_min_height=36,
#             columns=[
#                 ft.DataColumn(ft.Text("Time", weight="bold")),
#                 ft.DataColumn(ft.Text("Caption", weight="bold")),
#                 ft.DataColumn(ft.Text("Model", weight="bold")),
#                 ft.DataColumn(ft.Text("Interface", weight="bold")),
#                 ft.DataColumn(ft.Text("Size", weight="bold")),
#                 ft.DataColumn(ft.Text("Serial", weight="bold")),
#             ],
#             rows=[
#                 ft.DataRow(
#                     cells=[
#                         ft.DataCell(ft.Text(r["timestamp"])),
#                         ft.DataCell(ft.Text(r["caption"])),
#                         ft.DataCell(ft.Text(r["model"])),
#                         ft.DataCell(ft.Text(r["interface_type"])),
#                         ft.DataCell(ft.Text(str(r["size"]))),
#                         ft.DataCell(ft.Text(r["serial"])),
#                     ]
#                 )
#                 for r in rows
#             ],
#         )
#
#         return ft.Column(
#             expand=True,
#             spacing=200,
#             controls=[
#
#                 ft.Container(data_table, expand=True),
#             ],
#         )
#
#     def get_registered_refresh(self):
#         print("Refresh")
#         rows = self.local_db.get_registered()
#         print(f"rows {rows}")
#
#         self.get_registered.rows = [
#             ft.DataRow(cells=[
#                 ft.DataCell(ft.Text(r["id"])),
#                 ft.DataCell(ft.Text(r["serial"])),
#             ])
#             for r in rows]
#         self.get_registered.update()
#     def get_registered_view(self) -> ft.Control:
#         self.get_registered_refresh()
#         return ft.Column(
#             expand=True,
#             spacing=200,
#             controls=[
#                 self.get_registered
#             ],
#         )
import flet as ft
from apps.db.database import LocalDatabase


class UsbLogView:
    """Ro'yxatga olingan qurilmalar jadvali va loglar."""

    def __init__(self):
        self.local_db = LocalDatabase()

        # --- Registered devices jadvali (bitta marta yaratiladi)
        self.registered_table = ft.DataTable(
            expand=True,
            heading_row_height=40,
            data_row_min_height=36,
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold")),
                ft.DataColumn(ft.Text("Serial", weight="bold")),
                ft.DataColumn(ft.Text("Vaqt", weight="bold")),
            ],
            rows=[],   # dastlab bo'sh; sahifaga qo'shgandan so'ng to'ldiramiz
        )
        self._registered_view = ft.Column(expand=True, controls=[self.registered_table])

    def build_registered_view(self) -> ft.Control:
        """UI: ro'yxatga olingan qurilmalar bo'limi (update chaqirmaydi)."""
        return self._registered_view

    def refresh_registered(self):
        """DB dan ma'lumotlarni olib rows ni yangilaydi. update() NI BU YERDA CHAQRIMANG!"""
        rows = self.local_db.get_registered()  # [{'id':.., 'serial':.., 'timestamp':..}, ...]
        print(rows)
        self.registered_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(r["id"]))),
                    ft.DataCell(ft.Text(r["serial"])),
                    ft.DataCell(ft.Text(r["timestamp"])),
                ]
            ) for r in rows
        ]
        # update() NI BU YERDA EMAS! (control hali page'ga qo'shilmagan bo'lishi mumkin)

    # Ixtiyoriy: loglar bo'limi
    def build_log_view(self) -> ft.Control:
        rows = self.local_db.get_access_log()
        log_table = ft.DataTable(
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
        return ft.Column(expand=True, controls=[log_table])
