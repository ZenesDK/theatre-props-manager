"""Подключение к базе данных SQLite проекта TheaterProps.

Файл базы данных — data/theatre_props.sqlite, создаётся
один раз и заполняется скриптом db/import_json.py.
Каждое соединение включает проверку внешних ключей:
без PRAGMA foreign_keys = ON SQLite по умолчанию
допускает ссылки на отсутствующие записи других таблиц.
"""

import sqlite3

DB_PATH = "data/theatre_props.sqlite"


def get_connection() -> sqlite3.Connection:
    """Создать соединение с базой данных проекта."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
