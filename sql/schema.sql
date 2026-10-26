-- ==========================================
-- TheaterProps: структура базы данных
-- Предметная область: учёт театрального реквизита
-- ==========================================

-- Локации: места хранения и использования реквизита
-- (склад, сцена, репетиционный зал, мастерская)
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Постановки: репертуар театра, под который
-- бронируется реквизит
CREATE TABLE IF NOT EXISTS productions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    director TEXT,
    premiere_date TEXT
);

-- Сотрудники: материально ответственные лица
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    position TEXT
);

-- Реквизит: предметы театрального каталога.
-- status: на складе | выдан | в ремонте | утерян | списан
-- condition: новое | хорошее | изношено | требует ремонта
CREATE TABLE IF NOT EXISTS props (
    id INTEGER PRIMARY KEY,
    inventory_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    condition TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'на складе',
    location_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- Бронирования: предмет под постановку на дату.
-- is_cancelled: 0 — активна, 1 — отменена
-- (логическое значение хранится числом)
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    prop_id INTEGER NOT NULL,
    production_id INTEGER NOT NULL,
    reserved_by_id INTEGER,
    reservation_date TEXT NOT NULL,
    reserved_at TEXT NOT NULL,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (prop_id) REFERENCES props(id),
    FOREIGN KEY (production_id) REFERENCES productions(id),
    FOREIGN KEY (reserved_by_id) REFERENCES employees(id)
);

-- Журнал перемещений: события с предметами
-- (выдача, возврат, утеря, списание, в ремонт, из ремонта).
-- location_id, employee_id допустимо NULL: на момент
-- события локация или сотрудник могли быть неизвестны
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY,
    prop_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,
    location_id INTEGER,
    employee_id INTEGER,
    purpose TEXT NOT NULL,
    moved_at TEXT NOT NULL,
    FOREIGN KEY (prop_id) REFERENCES props(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
