"""Первые view-функции приложения бронирований."""

from django.http import HttpResponse


def reservations(request):
    """Список броней (временно — текстовая проверка)."""
    return HttpResponse("Список бронирований")


def reservation_detail(request, reservation_id):
    """Карточка брони (временно — текстовая проверка)."""
    return HttpResponse(f"Бронирование {reservation_id}")
