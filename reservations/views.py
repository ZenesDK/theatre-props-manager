"""Страницы бронирований: список и карточка брони.

Начиная с ПР7 список броней получает данные из базы SQLite
(см. sql/queries.sql): JOIN соединяет reservations с props,
productions и employees, поэтому на странице видны понятные
названия, а не идентификаторы. Карточка брони продолжает
работать на данных ПР3: JSON-хранилище сохранено как
предыдущая реализация предметной области.
"""

import sqlite3

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.props import Prop
from models.reservations import Reservation
from storage import (
    load_employees,
    load_locations,
    load_productions,
    load_props,
    load_reservations,
)
from utils import find_by_id


def load_domain_data(
) -> tuple[list[Reservation], list[Prop]]:
    """Загрузить коллекции предметной области средствами ПР3."""
    locations = load_locations()
    props_list = load_props(locations)
    productions = load_productions()
    employees = load_employees()
    reservations = load_reservations(
        props_list, productions, employees
    )
    return reservations, props_list


def reservations(request: HttpRequest) -> HttpResponse:
    """Активные брони из SQLite: JOIN предметов и постановок."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    reservations_list = conn.execute(
        """
        SELECT reservations.id,
               strftime('%d.%m.%Y',
                        reservations.reservation_date)
                   AS reservation_date,
               props.name AS prop_name,
               productions.title AS production_title,
               employees.full_name AS reserved_by_name,
               reservations.is_cancelled
        FROM reservations
        JOIN props
            ON reservations.prop_id = props.id
        JOIN productions
            ON reservations.production_id = productions.id
        LEFT JOIN employees
            ON reservations.reserved_by_id = employees.id
        WHERE reservations.is_cancelled = 0
        ORDER BY reservations.reservation_date;
        """
    ).fetchall()
    conn.close()
    context = {
        "reservations": reservations_list,
    }
    return render(
        request,
        "reservations/reservation_list.html",
        context,
    )


def reservation_detail(
    request: HttpRequest,
    reservation_id: int,
) -> HttpResponse:
    """Карточка брони; 404, если бронирование не найдено."""
    reservations_list, _ = load_domain_data()
    reservation = find_by_id(reservations_list, reservation_id)
    context = {
        "reservation": reservation,
    }
    return render(
        request,
        "reservations/reservation_detail.html",
        context,
        status=404 if reservation is None else 200,
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Статистика: число активных броней по предметам.

    LEFT JOIN включает предметы без броней: группа с
    COUNT = 0 остаётся в результате. Данные группируются
    средствами SQL (GROUP BY), а не в Python.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    statistics_data = conn.execute(
        """
        SELECT props.name AS prop_name,
               COUNT(reservations.id) AS reservations_count
        FROM props
        LEFT JOIN reservations
            ON props.id = reservations.prop_id
            AND reservations.is_cancelled = 0
        GROUP BY props.id, props.name
        ORDER BY reservations_count DESC, props.name;
        """
    ).fetchall()
    conn.close()
    context = {
        "statistics": statistics_data,
    }
    return render(
        request,
        "reservations/statistics.html",
        context,
    )
