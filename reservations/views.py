"""Страницы бронирований: список и карточка брони.

View-функции подготавливают контекст и вызывают шаблоны Django;
данные загружаются средствами ПР3: load_reservations() и
работа с объектами Reservation сохраняют связи с предметом,
постановкой и оформителем. HTML во view не формируется.
"""

from django.shortcuts import render

from storage import (
    load_employees,
    load_locations,
    load_productions,
    load_props,
    load_reservations,
)
from utils import find_by_id


def load_domain_data():
    """Загрузить коллекции предметной области средствами ПР3."""
    locations = load_locations()
    props_list = load_props(locations)
    productions = load_productions()
    employees = load_employees()
    reservations = load_reservations(
        props_list, productions, employees
    )
    return reservations, props_list


def reservations(request):
    """Список бронирований из data/reservations.json."""
    reservations_list, _ = load_domain_data()
    context = {
        "reservations": reservations_list,
    }
    return render(
        request,
        "reservations/reservation_list.html",
        context,
    )


def reservation_detail(request, reservation_id):
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
