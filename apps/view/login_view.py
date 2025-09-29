import flet as ft

from apps.core.route.route import RouteService
from apps.db.database import LocalDatabase


class LoginView:
    def __init__(self, page: ft.Page):

        self.local_db = LocalDatabase()
        self.page = page

        self.username_text_field = ft.TextField(label='Username', value='admin', border_color='white')
        self.password_text_field = ft.TextField(label='Password', border_color='white', password=True,
                                                can_reveal_password=True, error=True)

    def login_click_btn(self, e):

        password = self.password_text_field.value.strip()
        username = self.username_text_field.value.strip()

        if not password:
            # Bo'sh bo'lsa xato ko'rsatamiz
            self.password_text_field.error_text = "Password bo'sh qolib ketdi."
            self.page.update()

            return
        elif not username:
            self.username_text_field.error_text = "Password bo'sh qolib ketdi."
            self.page.update()

            return

        # Agar to‘ldirilgan bo‘lsa rangini oq qilib xatoni tozalaymiz
        self.password_text_field.error_text = None
        self.password_text_field.border_color = "white"
        self.username_text_field.error_text = None
        self.username_text_field.border_color = "white"
        self.page.update()

        rows = self.local_db.verify_admin(username=str(username),
                                          password=str(password))

        if rows:
            self.page.go('/main')
            self.page.update()
            print(f"if rows {rows}")
        else:
            print(f"else rows{rows}")
            self.page.open(
                ft.SnackBar(ft.Text(f"Username yoki parol noto'g'ri", ), bgcolor=ft.Colors.RED, behavior="floating",duration=3000))
            self.page.update()

    def view(self) -> ft.View:
        # Markaziy o‘rnatish uchun eng tashqi container
        return ft.View(
            route='/login',
            bgcolor=ft.Colors.WHITE,
            controls=[
                ft.Container(
                    expand=True,  # butun sahifani egallaydi
                    alignment=ft.alignment.center,  # ichidagi contentni markazga
                    content=ft.Container(
                        width=600,  # karta kengligi
                        height=350,
                        border_radius=8,
                        alignment=ft.alignment.center,
                        bgcolor="white",
                        shadow=[
                            ft.BoxShadow(spread_radius=1, blur_radius=15, color="white", offset=ft.Offset(-6, -6)),
                            ft.BoxShadow(spread_radius=1, blur_radius=15, color="#bebebe", offset=ft.Offset(6, 6)),
                        ],
                        content=ft.Row(
                            [
                                ft.Container(
                                    expand=True,
                                    # bgcolor="blue",
                                    content=ft.Image(
                                        expand=1,
                                        src=f'../assets/images/logo.png',

                                    ),
                                ),
                                ft.Container(
                                    expand=True,

                                    bgcolor="#00CFFF",
                                    padding=10,
                                    content=ft.Column(
                                        [
                                            ft.Text('Admin Panel', style=ft.TextStyle(size=25, color=ft.Colors.WHITE,
                                                                                      weight=ft.FontWeight.BOLD)),
                                            self.username_text_field,
                                            self.password_text_field,
                                            ft.ElevatedButton(
                                                "Login",
                                                on_click=self.login_click_btn,
                                                width=350,
                                                height=40,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=4),
                                                    bgcolor=ft.Colors.WHITE,
                                                ),
                                            ),
                                        ],
                                        spacing=20,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                )

                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,  # ✅ Vertikal markazlashtiris
                        )
                    ),
                )

            ]
        )
#
# import flet as ft
#
# class LoginView(ft.View):
#     def __init__(self, page: ft.Page):
#         super().__init__(route="/")
#         self.page = page
#
#         self.username = ft.TextField(label="Username")
#         self.password = ft.TextField(label="Password", password=True, can_reveal_password=True)
#         self.info = ft.Text()
#
#         # View tarkibi
#         self.controls = [
#             ft.AppBar(title=ft.Text("Login")),
#             ft.Column(
#                 [
#                     self.username,
#                     self.password,
#                     ft.ElevatedButton("Login", on_click=self.do_login),
#                     self.info,
#                 ],
#                 alignment=ft.MainAxisAlignment.CENTER,
#                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             ),
#         ]
#
#     def do_login(self, e):
#         if self.username.value == "admin" and self.password.value == "123":
#             self.page.go("/main")
#         else:
#             self.info.value = "❌ Noto‘g‘ri login yoki parol!"
#             self.page.update()
#
#
#
# class MainView(ft.View):
#     def __init__(self, page: ft.Page):
#         super().__init__(route="/main")
#         self.page = page
#
#         self.controls = [
#             ft.AppBar(title=ft.Text("Main View")),
#             ft.Column(
#                 [
#                     ft.Text("Salom, admin!", size=24, weight=ft.FontWeight.BOLD),
#                     ft.ElevatedButton("Log out", on_click=self.logout),
#                 ],
#                 alignment=ft.MainAxisAlignment.CENTER,
#                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             ),
#         ]
#
#     def logout(self, e):
#         self.page.go("/")
#
#
#
# # def main(page: ft.Page):
# #     page.title = "Flet Routing (Class-based)"
# #
# #     # Route o‘zgarganda sahifani yangilash
# #     def route_change(e: ft.RouteChangeEvent):
# #         page.views.clear()
# #         if page.route == "/":
# #             page.views.append(LoginView(page))
# #         elif page.route == "/main":
# #             page.views.append(MainView(page))
# #         page.update()
# #
# #     page.on_route_change = route_change
# #     page.go("/")   # start route
# #
# # ft.app(target=main)
