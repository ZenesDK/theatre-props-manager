# Сервис учёта театрального реквизита (TheaterProps)

Приложение для учёта, выдачи, бронирования и инвентаризации
театрального реквизита. Консольная версия (ПР3) дополнена
веб-интерфейсом на Django (ПР5), переведена на систему
шаблонов Django (ПР6) и получила слой реляционного хранения
данных SQLite (ПР7). Предметная область представлена
объектной моделью: шесть классов, коллекции объектов,
хранение данных в JSON и базе данных SQLite.

## Назначение

Информационная система предназначена для автоматизации учёта,
контроля перемещений и инвентаризации театрального реквизита,
бутафории, костюмов и декораций. Проект решает проблему хаоса
на складах, исключает утерю ценных предметов и оптимизирует
процесс подготовки к спектаклям и репетициям.

## Целевая аудитория

* **Заведующие постановочной частью (завпосты)** — контроль
  готовности материальной базы к спектаклям.
* **Заведующие складами и реквизиторы** — оперативный учёт,
  выдача и приёмка предметов.
* **Режиссёры и помощники режиссёров** — поиск и бронирование
  предметов под конкретные постановки.
* **Администрация театра** — инвентаризация и контроль
  имуществом.

## Классы предметной области

Сущности реализованы классами пакета `models`; импорт —
из пакета: `from models import Prop, Location, ...`

| Класс | Атрибуты | Методы |
|---|---|---|
| **Prop** — предмет | id, inventory_number, name, category, condition, status, location (ссылка на Location), created_at | `mark_issued()`, `mark_returned()`, `mark_lost()`, `mark_in_repair()`, `mark_repaired()`, `write_off()`, `is_bookable()`, `needs_repair()`, `matches()`, `from_data()`, `to_data()`, `__str__()` |
| **Location** — локация | id, name | `from_data()`, `to_data()`, `__str__()` |
| **Employee** — сотрудник | id, full_name, position | `from_data()`, `to_data()`, `__str__()` |
| **Production** — постановка | id, title, director, premiere_date | `from_data()`, `to_data()`, `__str__()` |
| **Movement** — запись журнала | id, prop, movement_type, location, employee, purpose, moved_at | `from_data()`, `to_data()`, `__str__()` |
| **Reservation** — бронирование | id, prop, date, production, reserved_at, is_cancelled, reserved_by (сотрудник, оформивший бронь) | `cancel()`, `from_data()`, `to_data()`, `__str__()` |

Ключевые принципы модели:

* **Статус предмета меняют только его методы** `mark_issued()`,
  `mark_returned()`, `mark_lost()`, `mark_in_repair()`,
  `mark_repaired()`, `write_off()`: объект сам охраняет
  допустимые переходы состояний (выдать не со склада нельзя —
  `ValueError`; списать выданный — тоже). Полная схема
  переходов — в docstring модуля `models/props.py`.
* **Отмена брони — состояние, а не удаление**: `cancel()`
  устанавливает `is_cancelled`; запись остаётся в коллекции
  (история бронирований) и перестаёт блокировать предмет.
* **Бронь помнит оформителя**: `reserved_by` — сотрудник,
  который оформил бронирование; поле необязательное.
* **`@classmethod` `from_data()`** у всех классов — восстановление
  объекта из JSON; **`@staticmethod` `Prop.validate_status()`** —
  проверка значения без данных объекта.

## Взаимодействие объектов

* `Movement` хранит ссылки на `Prop`, `Location`, `Employee`;
  `Reservation` — на `Prop`, `Production` и `Employee`
  (оформитель); `Prop` — на `Location`. Данные связанных
  объектов доступны напрямую: `movement.prop.name`,
  `reservation.production.title`, `reservation.reserved_by.full_name`.
* В JSON связи хранятся идентификаторами (`prop_id`,
  `production_id`); преобразование объект ↔ данные выполняется
  методами `from_data()` / `to_data()` в модуле storage.
* Функции коллекций (поиск, фильтрация, сортировка, создание
  и отмена) — обычные функции модулей; методами становятся
  только операции над конкретным объектом.
* Полиморфизм без наследования: `__str__` определён у всех
  классов — списки и журнал печатаются единообразно;
  `find_by_id()` — generic-функция (typing.Protocol), работающая
  с любым классом с атрибутом id.

## Возможности

* **Каталогизация:** добавление предметов с контролем
  уникальности инвентарного номера; фильтры по категории
  и статусу; поиск по подстроке; сортировка.
* **Перемещения:** выдача реквизита сотруднику; возврат
  с фиксацией состояния; журнал событий (выдача, возврат,
  утеря, списание, в ремонт, из ремонта).
* **Бронирование:** проверка доступности на дату; создание
  и отмена броней; фиксация оформителя брони; предупреждение
  о бронях при выдаче предмета; отменённые записи
  сохраняются в истории.
* **Ремонт и списание:** отправка предмета в ремонт
  (только со склада), возврат из ремонта с переоценкой
  состояния, безвозвратное списание с подтверждением.
* **Инвентаризация:** сверка наличия по локации; отметка
  утерянных с записью в журнал; отчёт в JSON.
* **Статистика:** распределения по статусам, категориям
  и локациям.
* **Репертуар и справочники:** постановки, локации, сотрудники.

## Веб-интерфейс (ПР5–ПР6)

Веб-версия построена на Django 5.2: три Django-приложения
(`homepage`, `props`, `reservations`), маршрутизация двух
уровней (urls.py проекта -> urls.py приложений),
view-функции и собственная страница 404 (handler404).

После ПР6 HTML формируется системой шаблонов Django:
view-функции подготавливают данные и передают их в шаблоны
через контекст (`render(request, "...", context)`).
Генерация HTML в Python-коде не используется; функция
`page()` из ПР5 удалена.

Данные загружаются средствами ПР3: view-функции вызывают
`load_props()`, `load_reservations()`, `find_by_id()`
и `is_prop_available()` — предметная логика не дублируется,
JSON временно остаётся источником данных до перехода
на Django ORM.

### Django Template Language

* **Базовый шаблон** `templates/base.html` — общая структура
  страницы: подключение Bootstrap 5.3 (CDN), собственного CSS,
  логотипа и JavaScript, подвал с текущим годом. Дочерние
  шаблоны наследуют его через `{% extends "base.html" %}` и
  переопределяют блоки `{% block title %}` и
  `{% block content %}`.
* **Включаемые шаблоны** (`{% include %}`):
  `templates/includes/navigation.html` (общая навигация),
  `props/includes/prop_card.html` (карточка предмета),
  `props/includes/prop_status.html` (статус предмета),
  `reservations/includes/reservation_status.html`
  (статус брони).
* **Циклы и условия**: списки строятся `{% for %}` с веткой
  `{% empty %}` для пустых коллекций; статусы и ситуации
  «объект не найден» обрабатываются `{% if %}`/{% elif %}`.
* **Именованные URL и пространства имён**: маршруты имён
  `homepage:index`, `props:props`, `props:prop_detail`,
  `reservations:reservations`, `reservations:reservation_detail`
  (пространства имён заданы `app_name`); все ссылки в шаблонах
  формируются тегом `{% url %}`, жёстких адресов нет.
* **Фильтры шаблонов**: количество элементов `{{ props|length }}`,
  значение по умолчанию `{{ prop.name|default:"Без названия" }}`,
  форматирование дат `{{ reservation.date|date:"d.m.Y" }}`.

### Статические файлы

Статика приложения homepage подключается через
`{% load static %}` и `{% static %}`:

* `homepage/static/homepage/css/style.css` — собственные стили
  проекта (карточки реквизита, статусные бейджи, логотип,
  подвал, активный пункт навигации);
* `homepage/static/homepage/img/logo.png` — логотип в шапке;
* `homepage/static/homepage/js/main.js` — текущий год в подвале
  и подсветка активного пункта навигации.

Bootstrap 5.3 сохранён для базовой вёрстки; собственный CSS
отвечает за оформление элементов проекта.

### Страницы

| URL | Страница | View-функция |
|---|---|---|
| `/` | главная: описание и навигация | `homepage.views.index()` |
| `/props/` | список реквизита из SQLite (статусы-бейджи) | `props.views.props()` |
| `/props/available/` | поиск свободного реквизита на дату (форма GET, подзапрос NOT IN) | `props.views.available()` |
| `/props/movements/` | журнал перемещений из SQLite (JOIN) | `props.views.movements()` |
| `/props/<int:prop_id>/` | карточка предмета: статус, локация, свободность на сегодня (логика ПР3), ближайшая бронь | `props.views.prop_detail()` |
| `/reservations/` | активные брони из SQLite (JOIN трёх таблиц) | `reservations.views.reservations()` |
| `/reservations/statistics/` | статистика: количество активных броней по предметам (COUNT + GROUP BY) | `reservations.views.statistics()` |
| `/reservations/<int:reservation_id>/` | карточка брони: предмет, дата, постановка, оформитель | `reservations.views.reservation_detail()` |
| любой неизвестный адрес | страница «404 — страница не найдена» | `homepage.views.page_not_found()` |

Если предмет или бронирование с указанным идентификатором
не найдены, страница возвращает код статуса 404.

## База данных (ПР7)

На ПР7 проект получил слой реляционного хранения: база
SQLite `data/theatre_props.sqlite`, SQL-схема, скрипт
переноса данных и набор SQL-запросов. Django ORM на этом
этапе не используется — данные получает модуль sqlite3.

### Структура базы данных

| Таблица | Поля (тип) | Ключи |
|---|---|---|
| `locations` | id (INTEGER), name (TEXT NOT NULL) | id — PRIMARY KEY |
| `productions` | id (INTEGER), title (TEXT NOT NULL), director (TEXT), premiere_date (TEXT) | id — PRIMARY KEY |
| `employees` | id (INTEGER), full_name (TEXT NOT NULL), position (TEXT) | id — PRIMARY KEY |
| `props` | id (INTEGER), inventory_number (TEXT NOT NULL UNIQUE), name, category, condition, status (TEXT NOT NULL), location_id (INTEGER), created_at (TEXT) | id — PRIMARY KEY; location_id — FOREIGN KEY -> locations.id |
| `reservations` | id (INTEGER), prop_id, production_id (INTEGER NOT NULL), reserved_by_id (INTEGER), reservation_date, reserved_at (TEXT NOT NULL), is_cancelled (INTEGER NOT NULL DEFAULT 0) | id — PRIMARY KEY; prop_id -> props.id; production_id -> productions.id; reserved_by_id -> employees.id |
| `movements` | id (INTEGER), prop_id, movement_type, purpose, moved_at (TEXT NOT NULL), location_id, employee_id (INTEGER) | id — PRIMARY KEY; prop_id -> props.id; location_id -> locations.id; employee_id -> employees.id |

Смысловые правила, перенесённые из объектной модели ПР3:

* `props.status` — пять статусов предмета; значение по
  умолчанию «на складе» (DEFAULT);
* `props.inventory_number` UNIQUE — дубли инвентарных
  номеров блокирует сама база;
* `reservations.is_cancelled` хранится числом (0 — активна,
  1 — отменена): отменённая бронь остаётся в истории и не
  блокирует предмет;
* даты — строки формата YYYY-MM-DD (допускают лексическое
  сравнение и сортировку SQL), отметки времени — ISO-строки;
* NULL допустим там, где смысл допускает отсутствие
  значения: director, premiere_date, position, location_id
  предмета, reserved_by_id брони, локация и сотрудник
  записи журнала.

### Файлы слоя данных

| Файл | Назначение |
|---|---|
| `sql/schema.sql` | CREATE TABLE IF NOT EXISTS всех шести таблиц; повторный запуск безопасен |
| `sql/queries.sql` | 14 проверенных SQL-запросов с комментариями |
| `db/database.py` | `get_connection()`: соединение sqlite3 + `PRAGMA foreign_keys = ON` |
| `db/import_json.py` | перенос данных из data/*.json в таблицы: `executemany()`, параметры `?`, commit/rollback; запуск `python -m db.import_json` |

Файл базы не коммитится (добавлен в .gitignore): база
создаётся и заполняется скриптами. Для пересоздания:

```
python -c "import sqlite3; sqlite3.connect('data/theatre_props.sqlite').close()"
python -c "import sqlite3; conn = sqlite3.connect('data/theatre_props.sqlite'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.commit(); conn.close()"
python -m db.import_json
```

### SQL-запросы проекта

`sql/queries.sql` содержит 14 запросов: выборки списков
(реквизит, постановки), фильтрация WHERE — по статусу,
по состоянию с несколькими условиями, поиск по подстроке
LIKE; JOIN и LEFT JOIN — активные брони с предметами,
постановками и оформителями, журнал перемещений; подзапрос
NOT IN — свободный реквизит на дату (аналог
`is_prop_available()` из ПР3); агрегаты COUNT; группировка
GROUP BY — предметы по статусам, брони по предметам;
HAVING — предметы с числом броней больше порогового;
ORDER BY и LIMIT — последние записи журнала.

### Получение данных в Django

Представления выполняют запросы через
`db.database.get_connection()` с
`conn.row_factory = sqlite3.Row` и обращаются к полям
результата по именам (в шаблоне — `{{ prop.name }}`).
Значения от пользователя передаются только параметрами
`?` — параметризованный запрос не допускает подстановки
данных в текст SQL. Данные на страницах списка реквизита,
активных броней, поиска свободного реквизита, журнала
перемещений и статистики берутся из SQLite; JSON-хранилище
сохранено: карточки предмета и брони (ПР5–ПР6) работают
на объектной модели ПР3, консольная версия не изменена.

## Структура проекта

| Файл / каталог | Назначение |
|---|---|
| manage.py | команда управления Django-проектом |
| theaterprops/ | пакет настроек Django-проекта (settings, urls, asgi, wsgi) |
| templates/ | шаблоны уровня проекта: base.html, 404.html, includes/navigation.html |
| homepage/ | Django-приложение: главная страница и 404 (шаблоны, static) |
| props/ | Django-приложение: страницы реквизита (шаблоны) |
| reservations/ | Django-приложение: страницы бронирований (шаблоны) |
| sql/ | SQL-файлы: schema.sql (схема БД), queries.sql (запросы проекта) |
| db/ | Пакет работы с БД: database.py (подключение), import_json.py (импорт JSON) |
| main.py | Точка запуска консольной версии: меню и диалоги |
| models/ | Пакет классов предметной области |
| models/props.py | Класс Prop + функции каталога |
| models/movements.py | Класс Movement + выдача/возврат |
| models/reservations.py | Класс Reservation + функции брони |
| models/productions.py | Класс Production + репертуар |
| models/locations.py | Класс Location + справочник |
| models/employees.py | Класс Employee + справочник |
| storage.py | Загрузка/сохранение JSON (объекты ↔ данные) |
| utils.py | Безопасный ввод, generic-поиск, идентификаторы |
| inventory.py | Инвентаризация и отчёты |
| stats.py | Статистика каталога |
| conftest.py | Конфигурация pytest |
| setup.cfg | Настройки flake8 |
| requirements.txt | Django 5.2, pytest, flake8 |
| data/ | JSON-данные приложения и база data/theatre_props.sqlite (создаётся скриптами, gitignored) |
| reports/ | Отчёты инвентаризаций (gitignored) |
| tests/ | Автоматические тесты pytest (126 тестов) |

## Формат хранения данных

Основное хранилище с ПР7 — реляционная база
`data/theatre_props.sqlite` (см. раздел «База данных»).
Исходные данные ПР1–ПР6 сохраняются в JSON-файлах каталога
`data/`: `props.json`, `locations.json`, `employees.json`,
`movements.json`, `reservations.json`, `productions.json`.
Записи содержат идентификаторы связанных объектов (`prop_id`,
`location_id`, `reserved_by_id` и т.д.); даты — в ISO-формате;
у бронирований хранятся состояние `is_cancelled` и оформитель
`reserved_by_id`. Журнал перемещений ведёт события шести типов:
выдача, возврат, утеря, списание, в ремонт, из ремонта.
При запуске консольной версии записи преобразуются в объекты
с восстановлением ссылок; битая ссылка или пропущенное поле
прерывают запуск с понятным сообщением. После изменений
JSON-данных перенос в базу повторяется скриптом
`python -m db.import_json` (предварительно очистив таблицы
либо пересоздав базу по sql/schema.sql).

## Требования

* Python 3.10+;
* Django 5.2 — веб-фреймворк;
* Django Template Language — шаблоны страниц;
* HTML5, CSS3 (собственный style.css) и Bootstrap 5.3 —
  оформление веб-страниц;
* JavaScript (main.js) — небольшое клиентское поведение;
* pytest, flake8.

Установка зависимостей:

```
pip install -r requirements.txt
```

## Запуск приложения

Веб-версия (Django):

```
python manage.py migrate
python manage.py runserver
```

После запуска открыть в браузере:

```
http://127.0.0.1:8000/
```

Консольная версия (сохранена с ПР3):

```
python main.py
```

## Запуск тестов

```
pytest
```

## Проверка качества кода

```
flake8
```

## План развития

1. **Этап 1 (ПР1–ПР2, выполнен):** консольное приложение —
   функции, коллекции, JSON-хранение.
2. **Этап 2 (ПР3, выполнен):** объектная модель — шесть
   классов, ссылки между объектами, состояния.
3. **Этап 3 (ПР5–ПР12):** веб-приложение на Django.
   ПР5 выполнен: Django-проект и три приложения,
   маршрутизация, view-функции, страницы на данных JSON,
   Bootstrap 5.3, обработка 404. ПР6 выполнен: перевод
   веб-части на Django-шаблоны — base.html и наследование,
   include-фрагменты, контекст, именованные URL с
   пространствами имён, фильтры шаблонов, статические
   файлы (CSS, логотип, JavaScript), отказ от page().
   ПР7 выполнен: слой SQLite — база data/theatre_props.sqlite,
   схема sql/schema.sql (6 таблиц, первичные и внешние
   ключи), перенос данных db/import_json.py, 14 запросов
   в sql/queries.sql; страницы списка реквизита, активных
   броней, поиска свободного реквизита, журнала перемещений
   и статистики получают данные из SQLite (sqlite3.Row,
   параметризованные запросы ?).
   Далее: перенос сущностей в Django ORM, формы и
   POST-запросы (создание/отмена броней, выдача),
   пользователи и аутентификация, API.
4. **Этап 4:** контейнеризация и CI/CD.
