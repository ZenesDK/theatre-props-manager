"""Постановки: репертуар театра.

Запись постановки — словарь с полями id, title, director
(строка или None), premiere_date (ISO-строка или None).
Постановки представлены словарём вида {id: постановка};
бронирования ссылаются на постановку по идентификатору.
"""

from datetime import date

from utils import next_id


def find_production_by_title(
    productions: dict[int, dict],
    title: str,
) -> dict | None:
    """Найти постановку по названию без учёта регистра."""
    wanted = title.strip().lower()
    for production in productions.values():
        if production["title"].lower() == wanted:
            return production
    return None


def add_production(
    productions: dict[int, dict],
    title: str,
    director: str | None,
    premiere_date: date | None,
) -> int:
    """Добавить постановку и вернуть её идентификатор.

    Режиссёр и дата премьеры необязательны: им соответствует
    значение None.
    """
    production_id = next_id(productions)
    productions[production_id] = {
        "id": production_id,
        "title": title,
        "director": director,
        "premiere_date": (
            premiere_date.isoformat() if premiere_date else None
        ),
    }
    return production_id
