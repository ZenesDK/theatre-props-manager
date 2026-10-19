"""Общие представления проекта: главная страница и страница 404.

Главная страница и страница 404 переведены на шаблоны Django
(homepage/index.html и 404.html). Функция page() из ПР5 пока
сохранена: её импортируют представления props и reservations,
она будет удалена после полного перехода проекта на render().
"""

from django.http import HttpResponse
from django.shortcuts import render

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
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Собственная страница 404 (handler404 в urls.py)."""
    return render(request, "404.html", status=404)
