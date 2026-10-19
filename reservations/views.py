"""Страницы бронирований: список и карточка брони.

Данные загружаются средствами ПР3: view-функции вызывают
load_reservations() и работают с объектами Reservation,
сохраняя связи с предметом, постановкой и оформителем.
"""

from django.http import HttpResponse

from homepage.views import page
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
    items = ""
    for reservation in reservations_list:
        if reservation.is_cancelled:
            status = "отменена"
            badge = "bg-secondary"
        else:
            status = "активна"
            badge = "bg-success"
        items += f"""
<li class="list-group-item d-flex justify-content-between">
    <a href="/reservations/{reservation.id}/">
        №{reservation.id} — {reservation.prop.name} —
        {reservation.date:%d.%m.%Y} — {reservation.production.title}
    </a>
    <span class="badge {badge}">{status}</span>
</li>
"""
    content = f"""
<h1>Бронирования</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(
        page("TheaterProps — бронирования", content)
    )


def reservation_detail(request, reservation_id):
    """Карточка брони; 404, если бронирование не найдено."""
    reservations_list, _ = load_domain_data()
    reservation = find_by_id(reservations_list, reservation_id)
    if reservation is None:
        content = """
<h1 class="text-danger">Бронирование не найдено</h1>
<a href="/reservations/" class="btn btn-outline-secondary">
    ← к списку бронирований
</a>
"""
        return HttpResponse(
            page("Бронирование не найдено", content),
            status=404,
        )
    if reservation.is_cancelled:
        status = "отменена"
        badge = "bg-secondary"
    else:
        status = "активна"
        badge = "bg-success"
    reserved_by = (
        reservation.reserved_by.full_name
        if reservation.reserved_by
        else "—"
    )
    content = f"""
<div class="card">
    <div class="card-body">
        <h5 class="card-title">Бронирование №{reservation.id}</h5>

        <p class="card-text">
            Предмет:
            <a href="/props/{reservation.prop.id}/">
                {reservation.prop.name}
            </a>
        </p>
        <p class="card-text">
            Дата постановки: {reservation.date:%d.%m.%Y}
        </p>
        <p class="card-text">
            Постановка: {reservation.production.title}
        </p>
        <p class="card-text">Оформил: {reserved_by}</p>
        <p class="card-text">
            Статус: <span class="badge {badge}">{status}</span>
        </p>

        <a href="/reservations/" class="btn btn-outline-secondary">
            ← к списку бронирований
        </a>
    </div>
</div>
"""
    return HttpResponse(
        page(f"Бронирование №{reservation.id}", content),
        status=200,
    )
