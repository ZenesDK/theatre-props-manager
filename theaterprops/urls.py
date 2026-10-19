"""Корневая маршрутизация Django-проекта TheaterProps.

Файл подключает маршруты приложений функцией include():
часть адреса указывается здесь, оставшаяся - в urls.py
приложения (распределение адресов по приложениям).
"""

from django.contrib import admin
from django.urls import include, path

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("props/", include("props.urls")),
    path("reservations/", include("reservations.urls")),
]
