"""Маршруты приложения reservations."""

from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("", views.reservations, name="reservations"),
    path(
        "<int:reservation_id>/",
        views.reservation_detail,
        name="reservation_detail",
    ),
]
