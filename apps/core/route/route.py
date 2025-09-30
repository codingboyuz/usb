# apps/core/route/route.py
import flet as ft
from typing import Union, Tuple, Dict, Any
from enum import  Enum


class RouteName:
    LOGIN_VIEW = "/login"
    MAIN_VIEW = "/main"
    DEFAULT_VIEW = "/"






class RouteService:
    """
    routes misol:
    {
        "login": (LoginView, {}),                      # kwargs yo‘q
        "main":  (MainView, {"log_view": log_view}),   # kwargs bor
    }
    """

    def __init__(self, page: ft.Page, routes: Dict[str, Tuple[type, Dict[str, Any]]]):
        self.page = page
        self.routes = routes
        self.page.on_route_change = self._on_route_change

    def _on_route_change(self, e: ft.RouteChangeEvent):
        self.page.views.clear()
        key = e.route.strip(RouteName.DEFAULT_VIEW)

        if key in self.routes:
            view_class, kwargs = self.routes[key]
            instance = view_class(self.page, **kwargs)
            # ✅ instance.view() ft.View qaytaradi
            self.page.views.append(instance.view())
        else:
            self.page.views.append(ft.View(RouteName.DEFAULT_VIEW, [ft.Text("404 - Sahifa topilmadi")]))

        self.page.update()
