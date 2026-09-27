"""Сохранение и загрузка данных проекта в JSON-файлах.

Чтение и запись выполняются через контекстный менеджер with,
который гарантирует закрытие файла даже при ошибке. Отсутствие
файла ошибкой не считается — возвращается пустая коллекция
(первый запуск). Повреждённый JSON прерывает запуск программы
с понятным сообщением вместо аварийной трассировки.

Локации, сотрудники и постановки — объекты классов пакета
models: при загрузке записи JSON превращаются в объекты,
при сохранении выполняется обратное преобразование. Предметы,
перемещения и бронирования на этом этапе остаются словарями.
"""

import json
import sys
from pathlib import Path

from models.employees import Employee
from models.locations import Location
from models.productions import Production

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_items(filename: str) -> list[dict]:
    """Прочитать JSON-файл и вернуть список записей."""
    path = DATA_DIR / filename
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {path.name} не найден — данные пусты.")
        return []
    except json.JSONDecodeError as exc:
        print(f"Файл {path} повреждён и не может быть прочитан: {exc}")
        sys.exit("Восстановите файл данных и запустите программу снова.")


def _save_items(filename: str, items: list[dict]) -> None:
    """Записать список записей в JSON-файл."""
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / filename
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"Не удалось сохранить данные в {path}: {exc}")


def _to_map(items: list[dict]) -> dict[int, dict]:
    """Преобразовать список записей в словарь с ключом id."""
    return {item["id"]: item for item in items}


def _to_list(mapping: dict[int, dict]) -> list[dict]:
    """Преобразовать словарь записей в список, упорядоченный по id."""
    return [mapping[key] for key in sorted(mapping)]


def load_locations() -> list[Location]:
    """Загрузить справочник локаций."""
    items = _load_items("locations.json")
    return [Location.from_data(item) for item in items]


def save_locations(locations: list[Location]) -> None:
    """Сохранить справочник локаций."""
    _save_items(
        "locations.json",
        [location.to_data() for location in locations],
    )


def load_employees() -> list[Employee]:
    """Загрузить справочник сотрудников."""
    items = _load_items("employees.json")
    return [Employee.from_data(item) for item in items]


def save_employees(employees: list[Employee]) -> None:
    """Сохранить справочник сотрудников."""
    _save_items(
        "employees.json",
        [employee.to_data() for employee in employees],
    )


def load_productions() -> list[Production]:
    """Загрузить справочник постановок."""
    items = _load_items("productions.json")
    return [Production.from_data(item) for item in items]


def save_productions(productions: list[Production]) -> None:
    """Сохранить справочник постановок."""
    _save_items(
        "productions.json",
        [production.to_data() for production in productions],
    )


def load_props() -> dict[int, dict]:
    """Загрузить каталог предметов реквизита."""
    return _to_map(_load_items("props.json"))


def save_props(props: dict[int, dict]) -> None:
    """Сохранить каталог предметов реквизита."""
    _save_items("props.json", _to_list(props))


def load_movements() -> list[dict]:
    """Загрузить журнал перемещений."""
    return _load_items("movements.json")


def save_movements(movements: list[dict]) -> None:
    """Сохранить журнал перемещений."""
    _save_items("movements.json", movements)


def load_reservations() -> list[dict]:
    """Загрузить список бронирований."""
    return _load_items("reservations.json")


def save_reservations(reservations: list[dict]) -> None:
    """Сохранить список бронирований."""
    _save_items("reservations.json", reservations)
