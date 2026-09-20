"""TheaterProps — консольный сервис учёта театрального реквизита.

Точка запуска приложения: загружает данные из JSON-файлов,
организует меню пользователя и сохраняет изменения.
Запуск: python main.py
"""

from typing import Callable

import directory
import storage
import utils
from utils import input_nonempty


def show_locations(locations: dict[int, dict]) -> None:
    """Вывести список локаций."""
    print("\n--- Локации ---")
    if not locations:
        print("  Справочник пуст.")
        return
    for location in locations.values():
        print(f"  [{location['id']}] {location['name']}")


def show_employees(employees: dict[int, dict]) -> None:
    """Вывести список сотрудников."""
    print("\n--- Сотрудники ---")
    if not employees:
        print("  Справочник пуст.")
        return
    for employee in employees.values():
        position = employee["position"] or "должность не указана"
        print(f"  [{employee['id']}] {employee['full_name']} ({position})")


def add_location_flow(locations: dict[int, dict]) -> None:
    """Диалог добавления локации с проверкой дублей."""
    name = input_nonempty("Название новой локации: ")
    if directory.find_location_by_name(locations, name) is not None:
        print("Такая локация уже существует.")
        return
    location_id = directory.add_location(locations, name)
    storage.save_locations(locations)
    print(f"Локация «{name}» добавлена (ID {location_id}).")


def add_employee_flow(employees: dict[int, dict]) -> None:
    """Диалог добавления сотрудника."""
    full_name = input_nonempty("ФИО сотрудника: ")
    position = input("Должность (Enter — не указывать): ").strip() or None
    employee_id = directory.add_employee(employees, full_name, position)
    storage.save_employees(employees)
    print(f"Сотрудник {full_name} добавлен (ID {employee_id}).")


def main() -> None:
    """Загрузить данные, запустить меню, сохранить изменения."""
    locations = storage.load_locations()
    employees = storage.load_employees()
    props = storage.load_props()
    movements = storage.load_movements()
    reservations = storage.load_reservations()

    print("=== THEATER PROPS — учёт театрального реквизита ===")
    print(
        f"Загружено: локаций — {len(locations)}, "
        f"сотрудников — {len(employees)}, "
        f"предметов — {len(props)}, "
        f"перемещений — {len(movements)}, "
        f"бронирований — {len(reservations)}."
    )

    actions: dict[int, Callable[[], None]] = {
        1: lambda: show_locations(locations),
        2: lambda: add_location_flow(locations),
        3: lambda: show_employees(employees),
        4: lambda: add_employee_flow(employees),
    }

    while True:
        print("\n--- МЕНЮ ---")
        print(" 1. Локации: список")
        print(" 2. Локации: добавить")
        print(" 3. Сотрудники: список")
        print(" 4. Сотрудники: добавить")
        print(" 0. Выход")
        choice = utils.input_int("Ваш выбор: ")
        if choice == 0:
            print("До встречи в театре!")
            return
        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта меню.")
        else:
            action()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
