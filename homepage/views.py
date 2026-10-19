"""Первые view-функции: проверка прохождения запроса.

На этом этапе view возвращает короткие HttpResponse:
браузер -> URL -> urls.py -> view -> response.
"""

from django.http import HttpResponse


def index(request):
    """Главная страница (временно — текстовая проверка)."""
    return HttpResponse(
        "TheaterProps - система учёта театрального реквизита"
    )
