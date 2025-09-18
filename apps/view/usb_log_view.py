import flet as ft
import sqlite3
from settings.base import DB_FILE


def main(page: ft.Page):
    page.title = "USB Access Logs"
    page.scroll = "auto"
    page.padding = 20
    page.theme_mode = "dark"   # dark ham qilishingiz mumkin

    # --- DB dan loglarni olish
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, caption, model, interface_type, size, serial "
        "FROM usb_access_log ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    # --- DataTable ustunlari
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time")),
            ft.DataColumn(ft.Text("Caption")),
            ft.DataColumn(ft.Text("Model")),
            ft.DataColumn(ft.Text("Interface")),
            ft.DataColumn(ft.Text("Size")),
            ft.DataColumn(ft.Text("Serial")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(r[0] or "")),
                    ft.DataCell(ft.Text(r[1] or "")),
                    ft.DataCell(ft.Text(r[2] or "")),
                    ft.DataCell(ft.Text(r[3] or "")),
                    ft.DataCell(ft.Text(r[4] or "")),
                    ft.DataCell(ft.Text(r[5] or "")),
                ]
            )
            for r in rows
        ],
    )

    # --- Asosiy layout
    page.add(
        ft.Column(
            controls=[
                ft.Text("USB Access Log", size=24, weight="bold"),
                ft.Divider(),
                table
            ],
            expand=True,
            spacing=20,
        )
    )


# Flet ilovani ishga tushirish
if __name__ == "__main__":
    ft.app(target=main)
