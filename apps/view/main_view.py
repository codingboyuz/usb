import flet as ft

from apps.core.route.route import RouteService
from apps.view.login_view import LoginView
from apps.view.usb_log_view import UsbLogView
from register_usb_view import UsbRegisterAlterDialog


class MainView:
    def __init__(self, page: ft.Page, log_view: UsbLogView):
        self.page = page
        self.log_view = log_view
        self.dialog = UsbRegisterAlterDialog(self.page, self.log_view)

    def view(self) -> ft.Control:
        return ft.View(
            route='/main',
            bgcolor=ft.Colors.WHITE,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.Tabs(
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
            ],
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                tooltip="Yangi serial qo'shish",
                on_click=self.dialog.open,
            ),
        )


def main(page: ft.Page):
    page.title = "Usb Secure"
    page.theme_mode = "light"
    page.bgcolor = "white"
    page.padding = 0  # ✅ Paddingni 0 qilish
    page.window.width = 1200  # ✅ Oynani kengroq qilish
    page.window.height = 700
    page.window.center()  # ✅ Oynani ekran markaziga joylashtirish

    # ✅ To'liq ekranni egallash va markazlashtirish
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Bitta log_view obyekt
    log_view = UsbLogView()

    # Router -> kwargs bilan
    router = RouteService(
        page,
        {
            "login": (LoginView, {}),
            "main": (MainView, {"log_view": log_view}),
        },
    )

    # ❗ Boshlang'ich sahifa uchun faqat .go() qo‘llang
    page.go("/login")

    # Jadvalni ma'lumot bilan to'ldirish
    log_view.refresh_registered()
    page.update()


ft.app(target=main)
