-- ==========================================
-- TheaterProps: SQL-запросы проекта (ПР7)
-- Проверены в SQLite на data/theatre_props.sqlite
-- ==========================================

-- Запрос 1. Список всего реквизита (выборка, сортировка
-- по названию) — основа страницы «Реквизит»
SELECT
    id,
    inventory_number,
    name,
    category,
    status
FROM props
ORDER BY name;

-- Запрос 2. Список постановок репертуара
-- (выборка, сортировка по дате премьеры)
SELECT
    id,
    title,
    director,
    premiere_date
FROM productions
ORDER BY premiere_date;

-- Запрос 3. Реквизит на складе
-- (фильтрация WHERE по статусу)
SELECT
    id,
    inventory_number,
    name,
    category
FROM props
WHERE status = 'на складе'
ORDER BY name;

-- Запрос 4. Предметы на складе, требующие ремонта
-- (несколько условий: AND)
SELECT
    id,
    inventory_number,
    name,
    condition
FROM props
WHERE condition = 'требует ремонта'
  AND status = 'на складе'
ORDER BY name;

-- Запрос 5. Поиск предметов по подстроке названия
-- (WHERE LIKE, в Django значение подставляется
-- параметром: '%' || ? || '%')
SELECT
    id,
    inventory_number,
    name,
    status
FROM props
WHERE name LIKE '%Кубок%'
ORDER BY name;

-- Запрос 6. Активные брони: полная информация
-- (JOIN четырёх таблиц вместо идентификаторов —
-- предмет, постановка, оформитель)
SELECT
    reservations.id,
    strftime('%d.%m.%Y', reservations.reservation_date)
        AS reservation_date,
    props.name AS prop_name,
    props.inventory_number,
    productions.title AS production_title,
    employees.full_name AS reserved_by_name
FROM reservations
JOIN props
    ON reservations.prop_id = props.id
JOIN productions
    ON reservations.production_id = productions.id
LEFT JOIN employees
    ON reservations.reserved_by_id = employees.id
WHERE reservations.is_cancelled = 0
ORDER BY reservations.reservation_date;

-- Запрос 7. Журнал перемещений с предметами, локациями
-- и сотрудниками (JOIN + LEFT JOIN: локация и сотрудник
-- могут быть неизвестны)
SELECT
    movements.id,
    strftime('%d.%m.%Y %H:%M', movements.moved_at)
        AS moved_at,
    movements.movement_type,
    props.name AS prop_name,
    props.inventory_number,
    locations.name AS location_name,
    employees.full_name AS employee_name,
    movements.purpose
FROM movements
JOIN props
    ON movements.prop_id = props.id
LEFT JOIN locations
    ON movements.location_id = locations.id
LEFT JOIN employees
    ON movements.employee_id = employees.id
ORDER BY movements.moved_at DESC, movements.id DESC;

-- Запрос 8. Свободный реквизит на выбранную дату
-- (подзапрос NOT IN: предметы без активной брони
-- на дату и не утерянные/не списанные — аналог
-- is_prop_available() из ПР3, дата передаётся
-- параметром ?)
SELECT
    id,
    inventory_number,
    name,
    category,
    status
FROM props
WHERE id NOT IN (
    SELECT prop_id
    FROM reservations
    WHERE reservation_date = ?
      AND is_cancelled = 0
)
  AND status NOT IN ('утерян', 'списан')
ORDER BY name;

-- Запрос 9. Количество активных броней
-- (агрегатная функция COUNT)
SELECT
    COUNT(*) AS active_reservations
FROM reservations
WHERE is_cancelled = 0;

-- Запрос 10. Количество предметов, требующих ремонта
-- (COUNT + WHERE)
SELECT
    COUNT(*) AS repair_needed
FROM props
WHERE condition = 'требует ремонта';

-- Запрос 11. Количество предметов по статусам
-- (группировка GROUP BY)
SELECT
    status,
    COUNT(*) AS props_count
FROM props
GROUP BY status
ORDER BY props_count DESC;

-- Запрос 12. Количество активных броней по предметам,
-- включая предметы без броней (LEFT JOIN + GROUP BY:
-- предмет без броней получает 0, а не исчезает)
SELECT
    props.name AS prop_name,
    COUNT(reservations.id) AS reservations_count
FROM props
LEFT JOIN reservations
    ON props.id = reservations.prop_id
    AND reservations.is_cancelled = 0
GROUP BY props.id, props.name
ORDER BY reservations_count DESC, props.name;

-- Запрос 13. Предметы с числом активных броней больше
-- порогового (фильтрация групп HAVING, порог 1 — для
-- проверки, по мере накопления данных вырастет)
SELECT
    props.name AS prop_name,
    COUNT(reservations.id) AS reservations_count
FROM props
JOIN reservations
    ON props.id = reservations.prop_id
WHERE reservations.is_cancelled = 0
GROUP BY props.id, props.name
HAVING COUNT(reservations.id) > 1
ORDER BY reservations_count DESC;

-- Запрос 14. Последние 5 записей журнала перемещений
-- (сортировка ORDER BY + ограничение LIMIT)
SELECT
    movements.id,
    strftime('%d.%m.%Y %H:%M', movements.moved_at)
        AS moved_at,
    movements.movement_type,
    props.name AS prop_name
FROM movements
JOIN props
    ON movements.prop_id = props.id
ORDER BY movements.moved_at DESC, movements.id DESC
LIMIT 5;
