"""TheaterProps — консольный сервис учёта театрального реквизита.

Точка запуска приложения: загружает данные из JSON-файлов,
организует меню пользователя и сохраняет изменения.
Запуск: python main.py
"""

from datetime import date, datetime
from typing import Callable

from inventory import (
    build_report,
    mark_missing_lost,
    save_report,
    select_props_for_check,
    split_by_answers,
)
from models.employees import Employee, add_employee
from models.locations import (
    Location,
    add_location,
    find_location_by_name,
)
from models.productions import (
    Production,
    add_production,
    find_production_by_title,
)
from movements import MOVEMENT_ISSUE, issue_prop, return_prop
from props import (
    CATEGORIES,
    CONDITIONS,
    SORT_OPTIONS,
    STATUSES,
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    add_prop,
    filter_props,
    find_prop_by_inventory_number,
    find_props,
    sort_props,
)
from reservations import (
    BLOCKING_STATUSES,
    cancel_reservation,
    create_reservation,
    find_reservation,
    get_reservation_status,
    is_prop_available,
)
from stats import get_stats
from storage import (
    load_employees,
    load_locations,
    load_movements,
    load_props,
    load_productions,
    load_reservations,
    save_employees,
    save_locations,
    save_movements,
    save_props,
    save_productions,
    save_reservations,
)
from utils import (
    choose_from_list,
    find_by_id,
    input_date,
    input_int,
    input_nonempty,
    input_optional_date,
    input_yes_no,
)

# --- Вспомогательные функции выбора и вывода ---


def format_prop(prop: dict, locations: list[Location]) -> str:
    """Строка предмета для списков выбора."""
    location = find_by_id(locations, prop["location_id"])
    location_name = location.name if location else "—"
    return (
        f"[{prop['inventory_number']}] {prop['name']} — "
        f"{prop['status']} ({location_name})"
    )


def format_reservation(
    reservation: dict,
    props: dict[int, dict],
    productions: list[Production],
) -> str:
    """Строка бронирования для списков."""
    prop = props.get(reservation["prop_id"])
    prop_name = prop["name"] if prop else "—"
    production = find_by_id(productions, reservation["production_id"])
    production_title = production.title if production else "—"
    day = date.fromisoformat(reservation["date"])
    return (
        f"[{reservation['id']}] {day:%d.%m.%Y} — "
        f"{prop_name} — {production_title}"
    )


def choose_location(locations: list[Location], title: str) -> Location | None:
    """Выбрать локацию из справочника."""
    return choose_from_list(locations, title)


def choose_prop(
    candidates: list[dict],
    title: str,
    locations: list[Location],
) -> dict | None:
    """Выбрать предмет из списка кандидатов."""
    return choose_from_list(
        candidates,
        title,
        formatter=lambda item: format_prop(item, locations),
    )

# --- Каталог реквизита ---


def print_props_table(
    props: list[dict],
    locations: list[Location],
) -> None:
    """Вывести предметы реквизита в виде таблицы."""
    print(
        f"{'ID':<4}{'Инв.№':<9}{'Название':<26}"
        f"{'Категория':<20}{'Состояние':<16}{'Статус':<12}Локация"
    )
    print("-" * 100)
    for prop in props:
        location = find_by_id(locations, prop["location_id"])
        location_name = location.name if location else "—"
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
    locations: list[Location],
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
    locations: list[Location],
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
    location = choose_location(locations, "Локация хранения:")
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
            location.id,
        )
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_props(props)
    print(f"Предмет «{name}» добавлен (ID {prop_id}).")


def find_props_flow(
    props: dict[int, dict],
    locations: list[Location],
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

# --- Перемещения: выдача и возврат ---


def issue_prop_flow(
    props: dict[int, dict],
    movements: list[dict],
    locations: list[Location],
    employees: list[Employee],
) -> None:
    """Диалог выдачи реквизита."""
    print("\n--- Выдача реквизита ---")
    in_stock = filter_props(props, status=STATUS_IN_STOCK)
    if not in_stock:
        print("Нет предметов на складе.")
        return
    prop = choose_prop(in_stock, "Какой предмет выдать?", locations)
    if prop is None:
        print("Выдача отменена.")
        return
    employee = choose_from_list(
        employees,
        "Ответственный (кому выдаём):",
    )
    if employee is None:
        print("Выдача отменена.")
        return
    location = choose_location(locations, "Куда перемещаем:")
    if location is None:
        print("Выдача отменена.")
        return
    purpose = input_nonempty("Цель (репетиция / спектакль / прочее): ")
    try:
        issue_prop(
            props,
            movements,
            prop["id"],
            employee.id,
            location.id,
            purpose,
        )
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_props(props)
    save_movements(movements)
    print(
        f"«{prop['name']}» выдан: {employee.full_name}, "
        f"локация «{location.name}» ({purpose})."
    )


def return_prop_flow(
    props: dict[int, dict],
    movements: list[dict],
    locations: list[Location],
) -> None:
    """Диалог возврата реквизита."""
    print("\n--- Возврат реквизита ---")
    issued = filter_props(props, status=STATUS_ISSUED)
    if not issued:
        print("Нет выданных предметов.")
        return
    prop = choose_prop(issued, "Какой предмет возвращают?", locations)
    if prop is None:
        print("Возврат отменён.")
        return
    location = choose_location(locations, "Принять на локацию:")
    if location is None:
        print("Возврат отменён.")
        return
    condition = choose_from_list(
        CONDITIONS,
        "Зафиксируйте состояние предмета:",
    )
    if condition is None:
        condition = prop["condition"]
        print(f"Состояние оставлено без изменений: {condition}")
    try:
        return_prop(props, movements, prop["id"], location.id, condition)
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_props(props)
    save_movements(movements)
    print(f"«{prop['name']}» принят на «{location.name}».")
    if condition in ("изношено", "требует ремонта"):
        print("Рекомендация: направить предмет на реставрацию.")


def show_journal_flow(
    movements: list[dict],
    props: dict[int, dict],
    locations: list[Location],
    employees: list[Employee],
) -> None:
    """Вывести последние перемещения реквизита."""
    print("\n--- Журнал перемещений (последние 20) ---")
    if not movements:
        print("Журнал пуст.")
        return
    recent = movements[-20:]
    for movement in reversed(recent):
        prop = props.get(movement["prop_id"])
        prop_label = f"[{prop['inventory_number']}] {prop['name']}"
        location = find_by_id(locations, movement["location_id"])
        location_name = location.name if location else "—"
        employee = find_by_id(employees, movement["employee_id"])
        employee_name = str(employee) if employee else "—"
        moved_at = datetime.fromisoformat(movement["moved_at"])
        arrow = "→" if movement["movement_type"] == MOVEMENT_ISSUE else "←"
        print(
            f"{moved_at:%d.%m.%Y %H:%M} {arrow} {prop_label} | "
            f"{location_name} | {employee_name} | {movement['purpose']}"
        )

# --- Бронирование ---


def check_availability_flow(
    props: dict[int, dict],
    reservations: list[dict],
    locations: list[Location],
    productions: list[Production],
) -> None:
    """Диалог проверки доступности предмета на дату."""
    print("\n--- Проверка доступности ---")
    prop = choose_prop(
        list(props.values()),
        "Какой предмет проверить?",
        locations,
    )
    if prop is None:
        return
    target_date = input_date("Дата: ")
    available = is_prop_available(
        props, reservations, prop["id"], target_date
    )
    if available:
        print(get_reservation_status(available))
        return
    if prop["status"] in BLOCKING_STATUSES:
        print(f"Предмет недоступен (статус: {prop['status']}).")
        return
    conflict = find_reservation(reservations, prop["id"], target_date)
    production = find_by_id(productions, conflict["production_id"])
    production_title = production.title if production else "—"
    print(get_reservation_status(available))
    print(f"На эту дату предмет уже забронирован: {production_title}.")


def create_reservation_flow(
    props: dict[int, dict],
    reservations: list[dict],
    locations: list[Location],
    productions: list[Production],
) -> None:
    """Диалог бронирования предмета на дату."""
    print("\n--- Бронирование предмета ---")
    candidates = [
        prop
        for prop in props.values()
        if prop["status"] not in BLOCKING_STATUSES
    ]
    if not candidates:
        print("Нет предметов, доступных для бронирования.")
        return
    prop = choose_prop(
        candidates,
        "Какой предмет забронировать?",
        locations,
    )
    if prop is None:
        print("Бронирование отменено.")
        return
    target_date = input_date("Дата бронирования: ")
    available = is_prop_available(
        props, reservations, prop["id"], target_date
    )
    if not available:
        conflict = find_reservation(reservations, prop["id"], target_date)
        if conflict is not None:
            production = find_by_id(
                productions, conflict["production_id"]
            )
            title = production.title if production else "—"
            print(
                f"Предмет уже занят на {target_date:%d.%m.%Y} "
                f"({title})."
            )
        else:
            print(f"Предмет недоступен (статус: {prop['status']}).")
        return
    print("Постановка: 1 — из репертуара, 2 — новая, 0 — отмена")
    mode = input_int("Выбор: ")
    if mode == 0:
        print("Бронирование отменено.")
        return
    if mode == 1:
        if not productions:
            print("Репертуар пуст — сначала создайте постановку.")
            return
        production = choose_from_list(
            productions,
            "Постановка:",
        )
        if production is None:
            print("Бронирование отменено.")
            return
    elif mode == 2:
        production = add_production_flow(productions)
        if production is None:
            print("Бронирование отменено.")
            return
    else:
        print("Нет такого пункта.")
        return
    try:
        reservation = create_reservation(
            props,
            reservations,
            prop["id"],
            target_date,
            production.id,
        )
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_reservations(reservations)
    print(
        f"Предмет «{prop['name']}» забронирован на "
        f"{target_date:%d.%m.%Y} для {production.title} "
        f"(ID {reservation['id']})."
    )


def cancel_reservation_flow(
    reservations: list[dict],
    props: dict[int, dict],
    productions: list[Production],
) -> None:
    """Диалог отмены бронирования."""
    print("\n--- Отмена бронирования ---")
    if not reservations:
        print("Бронирований нет.")
        return
    reservation = choose_from_list(
        reservations,
        "Какое бронирование отменить?",
        formatter=lambda item: format_reservation(
            item, props, productions
        ),
    )
    if reservation is None:
        print("Операция отменена.")
        return
    try:
        cancelled = cancel_reservation(reservations, reservation["id"])
    except ValueError as exc:
        print(f"Ошибка: {exc}.")
        return
    save_reservations(reservations)
    production = find_by_id(productions, cancelled["production_id"])
    production_title = production.title if production else "—"
    print(
        f"Бронирование ID {cancelled['id']} "
        f"({production_title}) отменено."
    )


def show_reservations_flow(
    reservations: list[dict],
    props: dict[int, dict],
    productions: list[Production],
) -> None:
    """Вывести список бронирований."""
    print("\n--- Бронирования ---")
    if not reservations:
        print("Бронирований нет.")
        return
    ordered = sorted(reservations, key=lambda item: item["date"])
    for reservation in ordered:
        line = format_reservation(reservation, props, productions)
        print(f"  {line}")

# --- Постановки ---


def show_productions_flow(productions: list[Production]) -> None:
    """Вывести список постановок."""
    print("\n--- Постановки ---")
    if not productions:
        print("  Репертуар пуст.")
        return
    for production in productions:
        print(f"  [{production.id}] {production}")


def add_production_flow(productions: list[Production]) -> Production | None:
    """Диалог добавления постановки; возвращает новую запись.

    Возвращает None, если добавление отменено или постановка
    с таким названием уже существует.
    """
    print("\n--- Добавление постановки ---")
    title = input_nonempty("Название постановки: ")
    if find_production_by_title(productions, title) is not None:
        print("Такая постановка уже существует.")
        return None
    director = input("Режиссёр (Enter — не указывать): ").strip() or None
    premiere_date = input_optional_date(
        "Дата премьеры (ДД.ММ.ГГГГ, Enter — не указывать): "
    )
    production = add_production(
        productions, title, director, premiere_date
    )
    save_productions(productions)
    print(f"Постановка «{title}» добавлена (ID {production.id}).")
    return production

# --- Инвентаризация и статистика ---


def run_inventory_flow(
    props: dict[int, dict],
    locations: list[Location],
) -> None:
    """Диалог инвентаризации по выбранной локации."""
    print("\n--- Инвентаризация ---")
    location = choose_location(locations, "Локация для сверки:")
    if location is None:
        print("Инвентаризация отменена.")
        return
    to_check = select_props_for_check(props, location.id)
    if not to_check:
        print(f"На локации «{location.name}» нечего сверять.")
        return
    print(f"К сверке: {len(to_check)} шт. Ответы: y (да) / n (нет).")
    answers: dict[int, bool] = {}
    for prop in to_check:
        label = f"[{prop['inventory_number']}] {prop['name']}"
        answers[prop["id"]] = input_yes_no(f"{label} — найден? ")
    found, missing = split_by_answers(to_check, answers)
    print("\n===== ОТЧЁТ ОБ ИНВЕНТАРИЗАЦИИ =====")
    print(f"Локация: {location.name}")
    print(f"Дата: {datetime.now():%d.%m.%Y %H:%M}")
    print(
        f"Числилось: {len(to_check)} | Найдено: {len(found)} | "
        f"Не найдено: {len(missing)}"
    )
    if missing:
        print("Расхождения (числится, но не найдено):")
        for prop in missing:
            print(f"  [{prop['inventory_number']}] {prop['name']}")
        if input_yes_no("Пометить ненайденные как «утерян»? "):
            updated = mark_missing_lost(props, missing)
            save_props(props)
            print(f"Статус «утерян» присвоен {updated} предметам.")
    report = build_report(location.name, found, missing)
    path = save_report(report)
    if path is not None:
        print(f"Отчёт сохранён: {path}")


def show_stats_flow(
    props: dict[int, dict],
    locations: list[Location],
) -> None:
    """Вывести сводную статистику каталога."""
    print("\n--- Статистика реквизита ---")
    stats = get_stats(props, locations)
    print(f"Всего предметов: {stats['total']}")
    print(f"Требуют ремонта: {stats['needs_repair']}")
    print("\nПо статусам:")
    print_counts(stats["by_status"])
    print("\nПо категориям:")
    print_counts(stats["by_category"])
    print("\nПо локациям:")
    print_counts(stats["by_location"])


def print_counts(counts: dict[str, int]) -> None:
    """Вывести распределение значений с количеством."""
    if not counts:
        print("  —")
        return
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")

# --- Справочники: локации и сотрудники ---


def show_locations(locations: list[Location]) -> None:
    """Вывести список локаций."""
    print("\n--- Локации ---")
    if not locations:
        print("  Справочник пуст.")
        return
    for location in locations:
        print(f"  [{location.id}] {location}")


def show_employees(employees: list[Employee]) -> None:
    """Вывести список сотрудников."""
    print("\n--- Сотрудники ---")
    if not employees:
        print("  Справочник пуст.")
        return
    for employee in employees:
        print(f"  [{employee.id}] {employee}")


def add_location_flow(locations: list[Location]) -> None:
    """Диалог добавления локации с проверкой дублей."""
    name = input_nonempty("Название новой локации: ")
    if find_location_by_name(locations, name) is not None:
        print("Такая локация уже существует.")
        return
    location = add_location(locations, name)
    save_locations(locations)
    print(f"Локация «{location.name}» добавлена (ID {location.id}).")


def add_employee_flow(employees: list[Employee]) -> None:
    """Диалог добавления сотрудника."""
    full_name = input_nonempty("ФИО сотрудника: ")
    position = input("Должность (Enter — не указывать): ").strip() or None
    employee = add_employee(employees, full_name, position)
    save_employees(employees)
    print(f"Сотрудник {employee.full_name} добавлен (ID {employee.id}).")

# --- Главное меню ---


def main() -> None:
    """Загрузить данные, запустить меню, сохранить изменения."""
    locations = load_locations()
    employees = load_employees()
    productions = load_productions()
    props = load_props()
    movements = load_movements()
    reservations = load_reservations()

    print("=== THEATER PROPS — учёт театрального реквизита ===")
    print(
        f"Загружено: локаций — {len(locations)}, "
        f"сотрудников — {len(employees)}, "
        f"постановок — {len(productions)}, "
        f"предметов — {len(props)}, "
        f"перемещений — {len(movements)}, "
        f"бронирований — {len(reservations)}."
    )

    actions: dict[int, Callable[[], None]] = {
        1: lambda: show_catalog_flow(props, locations),
        2: lambda: add_prop_flow(props, locations),
        3: lambda: find_props_flow(props, locations),
        4: lambda: issue_prop_flow(
            props, movements, locations, employees
        ),
        5: lambda: return_prop_flow(props, movements, locations),
        6: lambda: show_journal_flow(
            movements, props, locations, employees
        ),
        7: lambda: check_availability_flow(
            props, reservations, locations, productions
        ),
        8: lambda: create_reservation_flow(
            props, reservations, locations, productions
        ),
        9: lambda: cancel_reservation_flow(
            reservations, props, productions
        ),
        10: lambda: show_reservations_flow(
            reservations, props, productions
        ),
        11: lambda: show_productions_flow(productions),
        12: lambda: add_production_flow(productions),
        13: lambda: run_inventory_flow(props, locations),
        14: lambda: show_stats_flow(props, locations),
        15: lambda: show_locations(locations),
        16: lambda: add_location_flow(locations),
        17: lambda: show_employees(employees),
        18: lambda: add_employee_flow(employees),
    }

    while True:
        print("\n--- МЕНЮ ---")
        print("РЕКВИЗИТ")
        print(" 1. Каталог (фильтры и сортировка)")
        print(" 2. Добавить предмет")
        print(" 3. Найти предмет")
        print("ПЕРЕМЕЩЕНИЯ")
        print(" 4. Выдать реквизит")
        print(" 5. Принять возврат")
        print(" 6. Журнал перемещений")
        print("БРОНИРОВАНИЕ")
        print(" 7. Проверить доступность на дату")
        print(" 8. Забронировать предмет")
        print(" 9. Отменить бронирование")
        print("10. Список бронирований")
        print("ПОСТАНОВКИ")
        print("11. Постановки: список")
        print("12. Постановки: добавить")
        print("УЧЁТ")
        print("13. Инвентаризация")
        print("14. Статистика")
        print("СПРАВОЧНИКИ")
        print("15. Локации: список")
        print("16. Локации: добавить")
        print("17. Сотрудники: список")
        print("18. Сотрудники: добавить")
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
