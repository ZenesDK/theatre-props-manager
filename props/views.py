"""Первые view-функции приложения реквизита."""

from django.http import HttpResponse


def props(request):
    """Список реквизита (временно — текстовая проверка)."""
    return HttpResponse("Список реквизита")


def prop_detail(request, prop_id):
    """Карточка предмета (временно — текстовая проверка)."""
    return HttpResponse(f"Предмет {prop_id}")
