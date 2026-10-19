"""Маршруты приложения reservations."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.reservations, name="reservations"),
    path(
        "<int:reservation_id>/",
        views.reservation_detail,
        name="reservation_detail",
    ),
]
