"""Страницы реквизита: список предметов и карточка.

View-функции подготавливают контекст и вызывают шаблоны Django;
данные загружаются средствами ПР3: load_props(),
load_reservations() и функции предметного модуля, не дублируя
логику консольного приложения. HTML во view не формируется.
"""

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

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
    """Список предметов реквизита из data/props.json."""
    props_list, _ = load_domain_data()
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
