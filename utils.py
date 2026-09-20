"""Вспомогательные функции: безопасный ввод и идентификаторы.

Функции ввода перехватывают ошибки преобразования (ValueError),
поэтому некорректный ввод пользователя не завершает программу
аварийно, а приводит к повторному запросу.
"""

from datetime import date
from typing import Any, Callable


def input_nonempty(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  Значение не может быть пустым.")


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    Некорректный ввод перехватывается исключением ValueError,
    после чего запрос повторяется.
    """
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  Введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ДД.ММ.ГГГГ и вернуть объект date."""
    while True:
        raw = input(prompt).strip()
        try:
            day, month, year = (int(part) for part in raw.split("."))
            return date(year, month, day)
        except ValueError:
            print("  Введите дату в формате ДД.ММ.ГГГГ, например 05.11.2026.")


def choose_from_list(
    items: list[Any],
    title: str,
    formatter: Callable[[Any], str] = str,
) -> Any | None:
    """Показать нумерованный список и вернуть выбранный элемент.

    Возвращает None, если пользователь ввёл 0 (отмена)
    или несуществующий номер.
    """
    print(f"\n{title}")
    for number, item in enumerate(items, start=1):
        print(f"  {number}. {formatter(item)}")
    print("  0. Отмена")
    choice = input_int("Выбор: ")
    if choice == 0:
        return None
    if 1 <= choice <= len(items):
        return items[choice - 1]
    print("  Нет такого пункта.")
    return None


def next_id(collection: dict[int, dict] | list[dict]) -> int:
    """Вернуть следующий свободный идентификатор коллекции.

    Подходит для словаря вида {id: запись} и для списка записей
    с полем id. Для пустой коллекции возвращается 1.
    """
    if isinstance(collection, dict):
        return max(collection, default=0) + 1
    return max((item["id"] for item in collection), default=0) + 1
