"""Перенос данных проекта из JSON-файлов в SQLite.

Читает data/*.json (хранилище ПР1–ПР6) и вставляет записи
в таблицы базы методом executemany(). Значения передаются
параметрами ?, SQL-текст не собирается из строк.

Порядок импорта соответствует внешним ключам: сначала
справочники (локации, постановки, сотрудники), затем
предметы, брони и журнал перемещений.

Запуск из корня проекта:
    python -m db.import_json
"""

import json
import sqlite3

from db.database import get_connection

LOCATIONS_FILE = "data/locations.json"
PRODUCTIONS_FILE = "data/productions.json"
EMPLOYEES_FILE = "data/employees.json"
PROPS_FILE = "data/props.json"
RESERVATIONS_FILE = "data/reservations.json"
MOVEMENTS_FILE = "data/movements.json"


def load_json(filename: str) -> list:
    """Загрузить список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_locations(conn: sqlite3.Connection) -> None:
    """Перенести локации."""
    locations = load_json(LOCATIONS_FILE)
    conn.executemany(
        """
        INSERT INTO locations (id, name)
        VALUES (?, ?)
        """,
        [
            (location["id"], location["name"])
            for location in locations
        ],
    )


def import_productions(conn: sqlite3.Connection) -> None:
    """Перенести постановки."""
    productions = load_json(PRODUCTIONS_FILE)
    conn.executemany(
        """
        INSERT INTO productions (
            id, title, director, premiere_date
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                production["id"],
                production["title"],
                production.get("director"),
                production.get("premiere_date"),
            )
            for production in productions
        ],
    )


def import_employees(conn: sqlite3.Connection) -> None:
    """Перенести сотрудников."""
    employees = load_json(EMPLOYEES_FILE)
    conn.executemany(
        """
        INSERT INTO employees (id, full_name, position)
        VALUES (?, ?, ?)
        """,
        [
            (
                employee["id"],
                employee["full_name"],
                employee.get("position"),
            )
            for employee in employees
        ],
    )


def import_props(conn: sqlite3.Connection) -> None:
    """Перенести предметы реквизита."""
    props_list = load_json(PROPS_FILE)
    conn.executemany(
        """
        INSERT INTO props (
            id,
            inventory_number,
            name,
            category,
            condition,
            status,
            location_id,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                prop["id"],
                prop["inventory_number"],
                prop["name"],
                prop["category"],
                prop["condition"],
                prop["status"],
                prop.get("location_id"),
                prop["created_at"],
            )
            for prop in props_list
        ],
    )


def import_reservations(conn: sqlite3.Connection) -> None:
    """Перенести бронирования."""
    reservations = load_json(RESERVATIONS_FILE)
    conn.executemany(
        """
        INSERT INTO reservations (
            id,
            prop_id,
            production_id,
            reserved_by_id,
            reservation_date,
            reserved_at,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                reservation["id"],
                reservation["prop_id"],
                reservation["production_id"],
                reservation.get("reserved_by_id"),
                reservation["date"],
                reservation["reserved_at"],
                int(reservation.get("is_cancelled", False)),
            )
            for reservation in reservations
        ],
    )


def import_movements(conn: sqlite3.Connection) -> None:
    """Перенести журнал перемещений."""
    movements = load_json(MOVEMENTS_FILE)
    conn.executemany(
        """
        INSERT INTO movements (
            id,
            prop_id,
            movement_type,
            location_id,
            employee_id,
            purpose,
            moved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                movement["id"],
                movement["prop_id"],
                movement["movement_type"],
                movement.get("location_id"),
                movement.get("employee_id"),
                movement["purpose"],
                movement["moved_at"],
            )
            for movement in movements
        ],
    )


def main() -> None:
    """Импортировать все JSON-файлы в базу данных."""
    conn = get_connection()
    try:
        import_locations(conn)
        import_productions(conn)
        import_employees(conn)
        import_props(conn)
        import_reservations(conn)
        import_movements(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
