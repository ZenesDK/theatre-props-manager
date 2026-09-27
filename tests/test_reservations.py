"""Тесты функций бронирования реквизита."""

from datetime import date, datetime

import pytest

from models.props import STATUS_LOST, Prop
from reservations import (
    cancel_reservation,
    create_reservation,
    find_reservation,
    get_reservation_status,
    is_prop_available,
)
from models.locations import Location

WAREHOUSE = Location(1, "Склад №1")


def make_prop(prop_id: int, status: str) -> Prop:
    """Создать предмет с заданным статусом."""
    return Prop(
        prop_id=prop_id,
        inventory_number=f"ТР-000{prop_id}",
        name=f"Предмет №{prop_id}",
        category="мебель",
        condition="хорошее",
        location=WAREHOUSE,
        created_at=datetime(2026, 9, 1, 10, 0, 0),
        status=status,
    )


def make_props() -> list[Prop]:
    """Каталог: на складе, выдан, списан."""
    return [
        make_prop(1, "на складе"),
        make_prop(2, "выдан"),
        make_prop(3, STATUS_LOST),
    ]


def test_is_prop_available_without_reservations():
    props = make_props()
    assert is_prop_available(props[0], [], date(2026, 10, 5))
    assert is_prop_available(props[1], [], date(2026, 10, 5))


def test_is_prop_available_blocked_status():
    props = make_props()
    assert not is_prop_available(props[2], [], date(2026, 10, 5))


def test_create_reservation_appends_record():
    props = make_props()
    reservations: list[dict] = []
    reservation = create_reservation(
        reservations,
        props[0],
        date(2026, 10, 5),
        7,
    )
    assert len(reservations) == 1
    assert reservation["id"] == 1
    assert reservation["prop_id"] == 1
    assert reservation["date"] == "2026-10-05"
    assert reservation["production_id"] == 7


def test_duplicate_reservation_forbidden():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(reservations, props[0], date(2026, 10, 5), 7)
    assert not is_prop_available(props[0], reservations, date(2026, 10, 5))
    with pytest.raises(ValueError):
        create_reservation(
            reservations,
            props[0],
            date(2026, 10, 5),
            7,
        )


def test_same_prop_different_dates_allowed():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(reservations, props[0], date(2026, 10, 5), 7)
    create_reservation(reservations, props[0], date(2026, 10, 7), 7)
    assert len(reservations) == 2
    assert is_prop_available(props[0], reservations, date(2026, 10, 6))


def test_find_reservation():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(reservations, props[0], date(2026, 10, 5), 7)
    found = find_reservation(reservations, props[0], date(2026, 10, 5))
    assert found is not None
    assert found["production_id"] == 7
    assert find_reservation(reservations, props[0], date(2026, 10, 6)) is None


def test_cancel_reservation_removes_record():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(reservations, props[0], date(2026, 10, 5), 7)
    create_reservation(reservations, props[1], date(2026, 10, 7), 8)
    cancelled = cancel_reservation(reservations, 1)
    assert cancelled["production_id"] == 7
    assert len(reservations) == 1
    assert reservations[0]["production_id"] == 8


def test_cancel_reservation_missing_raises():
    with pytest.raises(ValueError):
        cancel_reservation([], 5)


def test_get_reservation_status_texts():
    available_text = get_reservation_status(True)
    busy_text = get_reservation_status(False)
    assert available_text == "Предмет доступен для бронирования"
    assert busy_text == "Предмет уже занят"
