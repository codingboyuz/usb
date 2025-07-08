import flet as ft
import sys


def main(page: ft.Page):
    page.title = "UsbGuard – O'chirish ruxsati"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def check_password(e):
        if password_field.value == "usb2024":
            page.clean()
            page.add(ft.Text("✅ Ruxsat berildi. Dastur o'chirilmoqda...", color="green"))
            page.update()
            sys.exit(0)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Noto'g'ri parol!", color="white"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    password_field = ft.TextField(label="Parol", password=True, can_reveal_password=True, autofocus=True)
    confirm_button = ft.ElevatedButton("Tasdiqlash", on_click=check_password)

    page.add(
        ft.Text("🔐 Dastur o'chirilmoqda. Iltimos, administrator parolini kiriting.", text_align="center"),
        password_field,
        confirm_button
    )


if __name__ == '__main__':
    ft.app(target=main)
