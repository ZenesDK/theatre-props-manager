"""Страницы реквизита: список, карточка, поиск, журнал.

Начиная с ПР7 список предметов, поиск свободных предметов
и журнал перемещений получают данные из базы SQLite
(см. sql/queries.sql) средствами модуля sqlite3: соединение
с row_factory = sqlite3.Row позволяет обращаться к полям
результата по именам прямо в шаблоне. Карточка предмета
продолжает работать на данных ПР3: JSON-хранилище сохранено
как предыдущая реализация предметной области.
"""

import sqlite3
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.props import Prop
from models.reservations import (
    Reservation,
    find_upcoming_reservation,
    is_prop_available,
)
from storage import (
    load_employees,
    load_locations,
    load_productions,
    load_props,
    load_reservations,
)
from utils import find_by_id


def load_domain_data() -> tuple[list[Prop], list[Reservation]]:
    """Загрузить коллекции предметной области средствами ПР3."""
    locations = load_locations()
    props_list = load_props(locations)
    productions = load_productions()
    employees = load_employees()
    reservations = load_reservations(
        props_list, productions, employees
    )
    return props_list, reservations


def props(request: HttpRequest) -> HttpResponse:
    """Список предметов реквизита из базы данных SQLite."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    props_list = conn.execute(
        """
        SELECT id, inventory_number, name, category, status
        FROM props
        ORDER BY name;
        """
    ).fetchall()
    conn.close()
    context = {
        "props": props_list,
    }
    return render(request, "props/prop_list.html", context)


def prop_detail(request: HttpRequest, prop_id: int) -> HttpResponse:
    """Карточка предмета; 404, если предмет не найден."""
    props_list, reservations = load_domain_data()
    prop = find_by_id(props_list, prop_id)
    available = False
    upcoming = None
    if prop is not None:
        available = is_prop_available(
            prop, reservations, date.today()
        )
        upcoming = find_upcoming_reservation(
            reservations, prop, date.today()
        )
    context = {
        "prop": prop,
        "available": available,
        "upcoming": upcoming,
    }
    return render(
        request,
        "props/prop_detail.html",
        context,
        status=404 if prop is None else 200,
    )


def available(request: HttpRequest) -> HttpResponse:
    """Поиск предметов, свободных на выбранную дату.

    Дата приходит из формы параметром GET ?date=ГГГГ-ММ-ДД
    и подставляется в SQL отдельным параметром ?. Если дата
    не выбрана, запрос к базе не выполняется: страница
    показывает только форму поиска.
    """
    search_date = request.GET.get("date")
    props_list = []
    if search_date:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        props_list = conn.execute(
            """
            SELECT id, inventory_number, name, category, status
            FROM props
            WHERE id NOT IN (
                SELECT prop_id
                FROM reservations
                WHERE reservation_date = ?
                  AND is_cancelled = 0
            )
              AND status NOT IN ('утерян', 'списан')
            ORDER BY name;
            """,
            [search_date],
        ).fetchall()
        conn.close()
    context = {
        "props": props_list,
        "search_date": search_date,
    }
    return render(request, "props/available.html", context)


def movements(request: HttpRequest) -> HttpResponse:
    """Журнал перемещений из SQLite (JOIN трёх таблиц)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    movements_list = conn.execute(
        """
        SELECT movements.id,
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
        """
    ).fetchall()
    conn.close()
    context = {
        "movements": movements_list,
    }
    return render(request, "props/movements.html", context)
