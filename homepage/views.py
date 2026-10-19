"""Общий каркас страниц и главная страница проекта.

Функция page() собирает HTML-документ: кодировка, заголовок
вкладки, подключение Bootstrap 5.3 через CDN и навигация.
Остальные приложения импортируют page(), поэтому каркас
задаётся в одном месте — точке входа проекта.
"""

from django.http import HttpResponse

BOOTSTRAP = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    """Собрать HTML-документ с единым каркасом проекта."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{BOOTSTRAP}">
</head>
<body>
<nav class="nav bg-light border-bottom px-3">
  <a class="nav-link" href="/">Главная</a>
  <a class="nav-link" href="/props/">Реквизит</a>
  <a class="nav-link" href="/reservations/">Брони</a>
</nav>
<main class="container py-4">{content}</main>
</body>
</html>"""


def index(request):
    """Главная страница: описание приложения и навигация."""
    content = """
<h1 class="display-4">TheaterProps</h1>
<p class="lead">Учёт театрального реквизита.</p>
<p>Каталогизация реквизита, выдача и возврат, бронирование
под постановки, инвентаризация и статистика. Консольная
версия приложения (ПР3) дополнена веб-интерфейсом (ПР5).</p>
<p>Основные разделы:</p>
<a href="/props/" class="btn btn-primary me-2">Реквизит</a>
<a href="/reservations/" class="btn btn-secondary">Брони</a>
"""
    return HttpResponse(page("TheaterProps", content))


def page_not_found(request, exception):
    """Собственная страница 404 (handler404 в urls.py)."""
    content = """
<h1 class="text-danger">404 — страница не найдена</h1>
<p>Проверьте адрес или вернитесь на главную.</p>
<a href="/" class="btn btn-primary">На главную</a>
"""
    return HttpResponse(
        page("404 — страница не найдена", content),
        status=404,
    )
