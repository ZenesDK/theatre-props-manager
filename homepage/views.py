"""Представления приложения homepage: главная страница и 404.

HTML формируется шаблонами Django: homepage/index.html и
404.html наследуют базовый шаблон templates/base.html.
Функция page() из ПР5 удалена — HTML больше не собирается
в Python-коде представлений.
"""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание приложения и навигация."""
    return render(request, "homepage/index.html")


def page_not_found(
    request: HttpRequest,
    exception: Http404,
) -> HttpResponse:
    """Собственная страница 404 (handler404 в urls.py)."""
    return render(request, "404.html", status=404)
