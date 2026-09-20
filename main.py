"""TheaterProps — консольный сервис учёта театрального реквизита.

Точка запуска приложения: загружает данные из JSON-файлов,
организует меню пользователя и сохраняет изменения.
Запуск: python main.py
"""

from typing import Callable

from directory import add_employee, add_location, find_location_by_name
from props import (
    CATEGORIES,
    CONDITIONS,
    SORT_OPTIONS,
    STATUSES,
    add_prop,
    filter_props,
    find_prop_by_inventory_number,
    find_props,
    sort_props,
)
from storage import (
    load_employees,
    load_locations,
    load_movements,
    load_props,
    load_reservations,
    save_employees,
    save_locations,
    save_props,
)
from utils import choose_from_list, input_int, input_nonempty

# --- Справочники: локации и сотрудники ---


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
    if find_location_by_name(locations, name) is not None:
        print("Такая локация уже существует.")
        return
    location_id = add_location(locations, name)
    save_locations(locations)
    print(f"Локация «{name}» добавлена (ID {location_id}).")


def add_employee_flow(employees: dict[int, dict]) -> None:
    """Диалог добавления сотрудника."""
    full_name = input_nonempty("ФИО сотрудника: ")
    position = input("Должность (Enter — не указывать): ").strip() or None
    employee_id = add_employee(employees, full_name, position)
    save_employees(employees)
    print(f"Сотрудник {full_name} добавлен (ID {employee_id}).")

# --- Каталог реквизита ---


def print_props_table(
    props: list[dict],
    locations: dict[int, dict],
) -> None:
    """Вывести предметы реквизита в виде таблицы."""
    print(
        f"{'ID':<4}{'Инв.№':<9}{'Название':<26}"
        f"{'Категория':<20}{'Состояние':<16}{'Статус':<12}Локация"
    )
    print("-" * 100)
    for prop in props:
        location = locations.get(prop["location_id"])
        location_name = location["name"] if location else "—"
        print(
            f"{prop['id']:<4}"
            f"{prop['inventory_number']:<9}"
            f"{prop['name'][:25]:<26}"
            f"{prop['category'][:19]:<20}"
            f"{prop['condition'][:15]:<16}"
            f"{prop['status'][:11]:<12}"
            f"{location_name}"
        )


def show_catalog_flow(
    props: dict[int, dict],
    locations: dict[int, dict],
) -> None:
    """Диалог просмотра каталога: фильтр, сортировка, таблица."""
    print("\n--- Каталог реквизита ---")
    print("Фильтр: 1 — по категории, 2 — по статусу, 0 — без фильтра")
    mode = input_int("Выбор: ")
    category = None
    status = None
    if mode == 1:
        category = choose_from_list(CATEGORIES, "Категория:")
        if category is None:
            return
    elif mode == 2:
        status = choose_from_list(STATUSES, "Статус:")
        if status is None:
            return
    selected = filter_props(props, category=category, status=status)
    if not selected:
        print("Ничего не найдено.")
        return
    sort_key = choose_from_list(SORT_OPTIONS, "Сортировка:")
    if sort_key is None:
        return
    ordered = sort_props(selected, sort_key)
    print_props_table(ordered, locations)
    print(f"Итого: {len(ordered)} шт.")


def add_prop_flow(
    props: dict[int, dict],
    locations: dict[int, dict],
) -> None:
    """Диалог добавления предмета реквизита.

    Инвентарный номер проверяется на уникальность сразу после
    ввода: пока не введён свободный номер, запрос повторяется.
    """
    print("\n--- Добавление предмета реквизита ---")
    name = input_nonempty("Название предмета: ")
    inventory_number = input_nonempty("Инвентарный номер: ")
    while find_prop_by_inventory_number(props, inventory_number) is not None:
        print("  Предмет с таким инвентарным номером уже существует.")
        inventory_number = input_nonempty("Инвентарный номер: ")
    category = choose_from_list(CATEGORIES, "Категория:")
    if category is None:
        print("Добавление отменено.")
        return
    condition = choose_from_list(CONDITIONS, "Состояние:")
    if condition is None:
        print("Добавление отменено.")
        return
    location = choose_from_list(
        list(locations.values()),
        "Локация хранения:",
        formatter=lambda item: item["name"],
    )
    if location is None:
        print("Добавление отменено.")
        return
    try:
        prop_id = add_prop(
            props,
            inventory_number,
            name,
            category,
            condition,
            location["id"],
        )
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_props(props)
    print(f"Предмет «{name}» добавлен (ID {prop_id}).")


def find_props_flow(
    props: dict[int, dict],
    locations: dict[int, dict],
) -> None:
    """Диалог поиска предметов по подстроке."""
    print("\n--- Поиск реквизита ---")
    query = input_nonempty("Строка поиска (название или инв. №): ")
    found = find_props(props, query)
    if not found:
        print("Ничего не найдено.")
        return
    print_props_table(found, locations)
    print(f"Найдено: {len(found)} шт.")

# --- Главное меню ---


def main() -> None:
    """Загрузить данные, запустить меню, сохранить изменения."""
    locations = load_locations()
    employees = load_employees()
    props = load_props()
    movements = load_movements()
    reservations = load_reservations()

    print("=== THEATER PROPS — учёт театрального реквизита ===")
    print(
        f"Загружено: локаций — {len(locations)}, "
        f"сотрудников — {len(employees)}, "
        f"предметов — {len(props)}, "
        f"перемещений — {len(movements)}, "
        f"бронирований — {len(reservations)}."
    )

    actions: dict[int, Callable[[], None]] = {
        1: lambda: show_catalog_flow(props, locations),
        2: lambda: add_prop_flow(props, locations),
        3: lambda: find_props_flow(props, locations),
        4: lambda: show_locations(locations),
        5: lambda: add_location_flow(locations),
        6: lambda: show_employees(employees),
        7: lambda: add_employee_flow(employees),
    }

    while True:
        print("\n--- МЕНЮ ---")
        print(" 1. Каталог реквизита (фильтры и сортировка)")
        print(" 2. Добавить предмет")
        print(" 3. Найти предмет")
        print(" 4. Локации: список")
        print(" 5. Локации: добавить")
        print(" 6. Сотрудники: список")
        print(" 7. Сотрудники: добавить")
        print(" 0. Выход")
        choice = input_int("Ваш выбор: ")
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
