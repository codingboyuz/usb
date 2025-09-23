import flet as ft
from apps.view.usb_log_view import UsbLogView
from register_usb_view import UsbRegisterAlterDialog


class MainView:
    def __init__(self, page: ft.Page, log_view: UsbLogView):
        self.page = page
        self.log_view = log_view

    def view(self) -> ft.Control:
        return ft.Tabs(
            adaptive=True,
            selected_index=0,
            animation_duration=300,
            expand=1,
            tabs=[
                ft.Tab(
                    text="Ro'yxatga olinmagan",
                    content=self.log_view.build_log_view()
                ),
                ft.Tab(
                    text="Ro'yxatga olingan",
                    content=self.log_view.build_registered_view()
                ),
            ],
        )


def main(page: ft.Page):
    page.title = "Usb Killer"
    page.theme_mode = "light"
    page.bgcolor = "white"
    page.padding = 20
    page.scroll = "auto"
    page.horizontal_alignment = "stretch"

    # --- Bitta log_view obyekt
    log_view = UsbLogView()
    dialog = UsbRegisterAlterDialog(page, log_view)
    app = MainView(page, log_view)

    # --- FloatingActionButton sahifaga qo'shish
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,          # ✅ ft.icons.ADD ishlatish ishonchliroq
        tooltip="Yangi serial qo'shish",
        on_click=dialog.open,
    )

    # --- Asosiy UI
    page.add(app.view())

    # Jadvalni ma'lumot bilan to'ldirish
    log_view.refresh_registered()
    page.update()




if __name__ == "__main__":
    ft.app(target=main)
