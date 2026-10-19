"""Страницы реквизита: список предметов и карточка.

Данные загружаются средствами ПР3: view-функции вызывают
load_props(), load_reservations() и функции предметного
модели, не дублируя логику консольного приложения.
"""

from datetime import date

from django.http import HttpResponse

from homepage.views import page
from models.reservations import (
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

STATUS_BADGES = {
    "на складе": "bg-success",
    "выдан": "bg-warning text-dark",
    "в ремонте": "bg-info text-dark",
    "утерян": "bg-danger",
    "списан": "bg-secondary",
}


def load_domain_data():
    """Загрузить коллекции предметной области средствами ПР3."""
    locations = load_locations()
    props_list = load_props(locations)
    productions = load_productions()
    employees = load_employees()
    reservations = load_reservations(
        props_list, productions, employees
    )
    return props_list, reservations


def props(request):
    """Список предметов реквизита из data/props.json."""
    props_list, _ = load_domain_data()
    items = ""
    for prop in props_list:
        badge = STATUS_BADGES.get(prop.status, "bg-secondary")
        items += f"""
<li class="list-group-item d-flex justify-content-between">
    <a href="/props/{prop.id}/">
        [{prop.inventory_number}] {prop.name}
    </a>
    <span class="badge {badge}">{prop.status}</span>
</li>
"""
    content = f"""
<h1>Реквизит</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(page("TheaterProps — реквизит", content))


def prop_detail(request, prop_id):
    """Карточка предмета; 404, если предмет не найден."""
    props_list, reservations = load_domain_data()
    prop = find_by_id(props_list, prop_id)
    if prop is None:
        content = """
<h1 class="text-danger">Предмет не найден</h1>
<a href="/props/" class="btn btn-outline-secondary">
    ← к списку реквизита
</a>
"""
        return HttpResponse(
            page("Предмет не найден", content),
            status=404,
        )
    available = is_prop_available(prop, reservations, date.today())
    status = "свободен на сегодня" if available else "занят на сегодня"
    badge = "bg-success" if available else "bg-danger"
    location_name = (
        prop.location.name if prop.location else "не указана"
    )
    upcoming = find_upcoming_reservation(
        reservations, prop, date.today()
    )
    if upcoming is None:
        next_text = "нет активных броней"
    else:
        next_text = (
            f"{upcoming.date:%d.%m.%Y}"
            f" — {upcoming.production.title}"
        )
    prop_badge = STATUS_BADGES.get(prop.status, "bg-secondary")
    content = f"""
<div class="card">
    <div class="card-body">
        <h5 class="card-title">{prop.name}</h5>

        <p class="card-text">
            <strong>Инвентарный номер:</strong>
            {prop.inventory_number}
        </p>
        <p class="card-text">
            <strong>Категория:</strong> {prop.category}
        </p>
        <p class="card-text">
            <strong>Состояние:</strong> {prop.condition}
        </p>
        <p class="card-text">
            <strong>Локация:</strong> {location_name}
        </p>
        <p class="card-text">
            Статус:
            <span class="badge {prop_badge}">{prop.status}</span>
        </p>
        <p class="card-text">
            Бронирование на текущую дату:
            <span class="badge {badge}">{status}</span>
        </p>
        <p class="card-text">
            <strong>Ближайшая бронь:</strong> {next_text}
        </p>

        <a href="/props/" class="btn btn-outline-secondary">
            ← к списку реквизита
        </a>
    </div>
</div>
"""
    return HttpResponse(page(prop.name, content), status=200)
