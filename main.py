"""
TheaterProps — консольный сервис учёта театрального реквизита (MVP).

Реализованные функции:
  1. Каталогизация  — добавление предметов, просмотр каталога с фильтрами.
  2. Перемещения    — выдача и возврат реквизита, журнал операций.
  3. Инвентаризация — сверка наличия по локации, отчёт о расхождениях.

Хранение: SQLite (файл theater_props.db создаётся автоматически).
Запуск:   python theater_props.py
"""

import json
import sqlite3
from datetime import datetime

DB_NAME = "theater_props.db"

CATEGORIES = ["мебель", "посуда", "бутафорское оружие", "текстиль",
              "декорации", "электроника", "прочее"]
CONDITIONS = ["новое", "хорошее", "изношено", "требует ремонта"]
STATUSES = ["на складе", "выдан", "в ремонте", "утерян", "списан"]
STATUS_IN_STOCK = "на складе"
STATUS_ISSUED = "выдан"


# ------------------------------------------------------------ Утилиты ввода

def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  Значение не может быть пустым.")


def input_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  Введите целое число.")


def choose_from_list(items, title, formatter=str):
    """Нумерованный список -> выбранный элемент или None (при 0)."""
    print(f"\n{title}")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {formatter(item)}")
    print("  0. Отмена")
    num = input_int("Выбор: ")
    if num == 0 or not 1 <= num <= len(items):
        return None
    return items[num -1]


# ------------------------------------------------------------ База данных

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS locations (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS employees (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            position  TEXT
        );
        CREATE TABLE IF NOT EXISTS props (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_number TEXT NOT NULL UNIQUE,
            name             TEXT NOT NULL,
            category         TEXT,
            condition        TEXT DEFAULT 'новое',
            status           TEXT DEFAULT 'на складе',
            location_id      INTEGER REFERENCES locations(id),
            created_at       TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movements (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            prop_id       INTEGER NOT NULL REFERENCES props(id),
            movement_type TEXT NOT NULL,            -- 'выдача' | 'возврат'
            location_id   INTEGER REFERENCES locations(id),
            employee_id   INTEGER REFERENCES employees(id),
            purpose       TEXT,
            moved_at      TEXT NOT NULL
        );
    """)
    conn.commit()


def seed_demo_data(conn):
    cur = conn.cursor()
    for name in ["Склад №1", "Малая сцена", "Главная сцена",
                 "Репетиционный зал", "Мастерская реставрации"]:
        cur.execute("INSERT OR IGNORE INTO locations(name) VALUES (?)", (name,))

    for name, pos in [("Иванова Анна Петровна", "реквизитор"),
                      ("Смирнов Олег Васильевич", "зав. складом"),
                      ("Кузнецова Мария Сергеевна", "завпост")]:
        cur.execute("INSERT INTO employees(full_name, position) VALUES (?, ?)", (name, pos))

    demo_props = [
        ("ТР-0001", "Канделябр бронзовый", "мебель", "хорошее", 1),
        ("ТР-0002", "Кубок золотой (бутафория)", "посуда", "новое", 1),
        ("ТР-0003", "Шпага дворянская", "бутафорское оружие", "изношено", 5),
        ("ТР-0004", "Плащ бархатный красный", "текстиль", "хорошее", 1),
        ("ТР-0005", "Трон деревянный с резьбой", "мебель", "требует ремонта", 5),
    ]
    now = datetime.now().isoformat(timespec="seconds")
    for inv, name, cat, cond, loc in demo_props:
        cur.execute(
            "INSERT INTO props(inventory_number, name, category, condition, "
            "status, location_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (inv, name, cat, cond, STATUS_IN_STOCK, loc, now),
        )
    conn.commit()
    print("Демо-данные загружены.")


# ---------------------------------------------------- Функция 1. Каталогизация

def add_prop(conn):
    print("\n--- Добавление предмета реквизита ---")
    name = input_nonempty("Название предмета: ")
    inv = input_nonempty("Инвентарный номер: ")

    if conn.execute("SELECT id FROM props WHERE inventory_number = ?", (inv,)).fetchone():
        print("Ошибка: предмет с таким инвентарным номером уже существует.")
        return

    category = choose_from_list(CATEGORIES, "Категория:")
    if category is None:
        print("Добавление отменено.")
        return
    condition = choose_from_list(CONDITIONS, "Состояние:")
    if condition is None:
        print("Добавление отменено.")
        return

    locations = conn.execute("SELECT * FROM locations ORDER BY id").fetchall()
    location = choose_from_list(locations, "Локация хранения:", lambda r: r["name"])
    if location is None:
        print("Добавление отменено.")
        return

    cur = conn.execute(
        "INSERT INTO props(inventory_number, name, category, condition, "
        "status, location_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (inv, name, category, condition, STATUS_IN_STOCK, location["id"],
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    print(f"Предмет «{name}» добавлен (ID {cur.lastrowid}).")


def print_props_table(rows):
    print(f"{'ID':<4}{'Инв.№':<9}{'Название':<28}{'Категория':<21}"
          f"{'Состояние':<18}{'Статус':<12}Локация")
    print("-" * 115)
    for r in rows:
        print(f"{r['id']:<4}{r['inventory_number']:<9}{r['name'][:27]:<28}"
              f"{(r['category'] or '')[:20]:<21}{(r['condition'] or '')[:17]:<18}"
              f"{r['status']:<12}{r['location'] or '—'}")


def show_catalog(conn):
    print("\n--- Каталог реквизита ---")
    print("Фильтр: 1 — по категории, 2 — по статусу, 0 — показать всё")
    mode = input_int("Выбор: ")

    query = ("SELECT p.*, l.name AS location FROM props p "
             "LEFT JOIN locations l ON l.id = p.location_id ")
    params = []

    if mode == 1:
        cat = choose_from_list(CATEGORIES, "Категория:")
        if cat is None:
            return
        query += "WHERE p.category = ? "
        params.append(cat)
    elif mode == 2:
        st = choose_from_list(STATUSES, "Статус:")
        if st is None:
            return
        query += "WHERE p.status = ? "
        params.append(st)

    rows = conn.execute(query + "ORDER BY p.id", params).fetchall()
    if not rows:
        print("Ничего не найдено.")
        return
    print_props_table(rows)
    print(f"Итого: {len(rows)} шт.")


# ---------------------------------------------------- Функция 2. Перемещения

def pick_prop(conn, where, params, message):
    """Выбор предмета по условию. Возвращает sqlite3.Row или None."""
    rows = conn.execute(
        "SELECT p.*, l.name AS location FROM props p "
        "LEFT JOIN locations l ON l.id = p.location_id "
        f"WHERE {where} ORDER BY p.id", params,
    ).fetchall()
    if not rows:
        print("Подходящих предметов нет.")
        return None
    return choose_from_list(
        rows, message,
        lambda r: f"[{r['inventory_number']}] {r['name']} — {r['status']} ({r['location']})")


def issue_prop(conn):
    print("\n--- Выдача реквизита ---")
    prop = pick_prop(conn, "p.status = ?", (STATUS_IN_STOCK,), "Какой предмет выдать?")
    if prop is None:
        return

    employees = conn.execute("SELECT * FROM employees ORDER BY id").fetchall()
    emp = choose_from_list(employees, "Ответственный (кому выдаём):",
                           lambda r: f"{r['full_name']} ({r['position']})")
    if emp is None:
        print("Выдача отменена.")
        return

    locations = conn.execute("SELECT * FROM locations ORDER BY id").fetchall()
    loc = choose_from_list(locations, "Куда перемещаем:", lambda r: r["name"])
    if loc is None:
        print("Выдача отменена.")
        return

    purpose = input_nonempty("Цель (репетиция / спектакль / реставрация и т.п.): ")
    now = datetime.now().isoformat(timespec="seconds")

    conn.execute("UPDATE props SET status = ?, location_id = ? WHERE id = ?",
                 (STATUS_ISSUED, loc["id"], prop["id"]))
    conn.execute(
        "INSERT INTO movements(prop_id, movement_type, location_id, employee_id, "
        "purpose, moved_at) VALUES (?, 'выдача', ?, ?, ?, ?)",
        (prop["id"], loc["id"], emp["id"], purpose, now),
    )
    conn.commit()
    print(f"✓ «{prop['name']}» выдан: {emp['full_name']}, локация «{loc['name']}» ({purpose}).")


def return_prop(conn):
    print("\n--- Возврат реквизита ---")
    prop = pick_prop(conn, "p.status = ?", (STATUS_ISSUED,), "Какой предмет возвращают?")
    if prop is None:
        return

    warehouses = conn.execute("SELECT * FROM locations WHERE name LIKE 'Склад%'").fetchall()
    warehouses = warehouses or conn.execute("SELECT * FROM locations").fetchall()
    loc = choose_from_list(warehouses, "Принять на локацию:", lambda r: r["name"])
    if loc is None:
        print("Возврат отменён.")
        return

    condition = choose_from_list(CONDITIONS, "Зафиксируйте состояние предмета:")
    if condition is None:
        condition = prop["condition"]
        print(f"Состояние оставлено без изменений: {condition}")

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE props SET status = ?, location_id = ?, condition = ? WHERE id = ?",
                 (STATUS_IN_STOCK, loc["id"], condition, prop["id"]))
    conn.execute(
        "INSERT INTO movements(prop_id, movement_type, location_id, purpose, moved_at) "
        "VALUES (?, 'возврат', ?, 'возврат на хранение', ?)",
        (prop["id"], loc["id"], now),
    )
    conn.commit()
    print(f"✓ «{prop['name']}» принят на «{loc['name']}».")
    if condition in ("изношено", "требует ремонта"):
        print("⚠ Рекомендация: направить предмет на реставрацию.")


def show_journal(conn):
    print("\n--- Журнал перемещений (последние 20) ---")
    rows = conn.execute(
        "SELECT m.moved_at, p.inventory_number, p.name, m.movement_type, "
        "       IFNULL(l.name, '—') AS location, "
        "       IFNULL(e.full_name, '—') AS employee, IFNULL(m.purpose, '') AS purpose "
        "FROM movements m "
        "JOIN props p ON p.id = m.prop_id "
        "LEFT JOIN locations l ON l.id = m.location_id "
        "LEFT JOIN employees e ON e.id = m.employee_id "
        "ORDER BY m.id DESC LIMIT 20"
    ).fetchall()
    if not rows:
        print("Журнал пуст.")
        return
    for r in rows:
        arrow = "→ выдача " if r["movement_type"] == "выдача" else "← возврат"
        print(f"{r['moved_at']}  {arrow} [{r['inventory_number']}] {r['name']} | "
              f"{r['location']} | {r['employee']} | {r['purpose']}")


# ---------------------------------------------------- Функция 3. Инвентаризация

def run_inventory(conn):
    print("\n--- Инвентаризация ---")
    locations = conn.execute("SELECT * FROM locations ORDER BY id").fetchall()
    loc = choose_from_list(locations, "Выберите локацию для сверки:", lambda r: r["name"])
    if loc is None:
        return

    rows = conn.execute(
        "SELECT * FROM props WHERE location_id = ? AND status != 'списан' ORDER BY id",
        (loc["id"],),
    ).fetchall()
    if not rows:
        print(f"На локации «{loc['name']}» ничего не числится.")
        return

    print(f"\nК сверке: {len(rows)} шт. Отвечайте: y — найден, n — не найден.")
    found, missing = [], []
    for prop in rows:
        while True:
            ans = input(f"[{prop['inventory_number']}] {prop['name']} — найден? (y/n): ").strip().lower()
            if ans in ("y", "д", "n", "н"):
                break
        (found if ans in ("y", "д") else missing).append(prop)

    print("\n===== ОТЧЁТ ОБ ИНВЕНТАРИЗАЦИИ =====")
    print(f"Локация:    {loc['name']}")
    print(f"Дата:       {datetime.now():%d.%m.%Y %H:%M}")
    print(f"Числилось:  {len(rows)} | Найдено: {len(found)} | Не найдено: {len(missing)}")
    if missing:
        print("\nРасхождения (числится, но не найдено):")
        for p in missing:
            print(f"  [{p['inventory_number']}] {p['name']} — статус: {p['status']}")

    if missing and input("\nПометить ненайденные как «утерян»? (y/n): ").strip().lower() in ("y", "д"):
        for p in missing:
            conn.execute("UPDATE props SET status = 'утерян' WHERE id = ?", (p["id"],))
        conn.commit()
        print("Статусы обновлены.")

    report = {
        "location": loc["name"],
        "date": datetime.now().isoformat(timespec="seconds"),
        "total": len(rows),
        "found": [{"inventory_number": p["inventory_number"], "name": p["name"]} for p in found],
        "missing": [{"inventory_number": p["inventory_number"], "name": p["name"]} for p in missing],
    }
    fname = f"inventory_{datetime.now():%Y%m%d_%H%M}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Отчёт сохранён: {fname}")


# ------------------------------------------------------------ Главное меню

def main():
    conn = get_conn()
    init_db(conn)

    if conn.execute("SELECT COUNT(*) FROM props").fetchone()[0] == 0:
        if input("База пуста. Загрузить демо-данные? (y/n): ").strip().lower() in ("y", "д"):
            seed_demo_data(conn)

    actions = {
        1: add_prop,
        2: show_catalog,
        3: issue_prop,
        4: return_prop,
        5: show_journal,
        6: run_inventory,
    }
    while True:
        print("\n========== THEATER PROPS ==========")
        print(" 1. Добавить предмет (каталогизация)")
        print(" 2. Каталог реквизита (просмотр/фильтры)")
        print(" 3. Выдать реквизит (перемещение)")
        print(" 4. Принять реквизит (возврат)")
        print(" 5. Журнал перемещений")
        print(" 6. Инвентаризация")
        print(" 0. Выход")
        choice = input_int("Ваш выбор: ")
        if choice == 0:
            print("До встречи в театре!")
            break
        action = actions.get(choice)
        if action:
            action(conn)
        else:
            print("Нет такого пункта меню.")
    conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")