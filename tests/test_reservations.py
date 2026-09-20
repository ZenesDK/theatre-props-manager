"""Тесты функций бронирования реквизита."""

from datetime import date

import pytest

from reservations import (
    cancel_reservation,
    create_reservation,
    find_reservation,
    get_reservation_status,
    is_prop_available,
)


def make_props() -> dict[int, dict]:
    """Подготовить каталог: на складе, выдан, списан."""
    return {
        1: {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Канделябр бронзовый",
            "category": "мебель",
            "condition": "хорошее",
            "status": "на складе",
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        2: {
            "id": 2,
            "inventory_number": "ТР-0002",
            "name": "Кубок золотой",
            "category": "посуда",
            "condition": "новое",
            "status": "выдан",
            "location_id": 2,
            "created_at": "2026-09-01T10:00:00",
        },
        3: {
            "id": 3,
            "inventory_number": "ТР-0003",
            "name": "Трон деревянный",
            "category": "мебель",
            "condition": "требует ремонта",
            "status": "списан",
            "location_id": 5,
            "created_at": "2026-09-01T10:00:00",
        },
    }


def test_is_prop_available_without_reservations():
    props = make_props()
    assert is_prop_available(props, [], 1, date(2026, 10, 5))
    assert is_prop_available(props, [], 2, date(2026, 10, 5))


def test_is_prop_available_missing_prop():
    props = make_props()
    assert not is_prop_available(props, [], 99, date(2026, 10, 5))


def test_is_prop_available_blocked_status():
    props = make_props()
    assert not is_prop_available(props, [], 3, date(2026, 10, 5))


def test_create_reservation_appends_record():
    props = make_props()
    reservations: list[dict] = []
    reservation = create_reservation(
        props,
        reservations,
        1,
        date(2026, 10, 5),
        "«Пиковая дама»",
    )
    assert len(reservations) == 1
    assert reservation["id"] == 1
    assert reservation["prop_id"] == 1
    assert reservation["date"] == "2026-10-05"
    assert reservation["production"] == "«Пиковая дама»"


def test_duplicate_reservation_forbidden():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(props, reservations, 1, date(2026, 10, 5), "«Онегин»")
    assert not is_prop_available(props, reservations, 1, date(2026, 10, 5))
    with pytest.raises(ValueError):
        create_reservation(
            props,
            reservations,
            1,
            date(2026, 10, 5),
            "«Дубль»",
        )


def test_same_prop_different_dates_allowed():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(props, reservations, 1, date(2026, 10, 5), "«Онегин»")
    create_reservation(
        props,
        reservations,
        1,
        date(2026, 10, 7),
        "«Щелкунчик»",
    )
    assert len(reservations) == 2
    assert is_prop_available(props, reservations, 1, date(2026, 10, 6))


def test_find_reservation():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(props, reservations, 1, date(2026, 10, 5), "«Онегин»")
    found = find_reservation(reservations, 1, date(2026, 10, 5))
    assert found is not None
    assert found["production"] == "«Онегин»"
    assert find_reservation(reservations, 1, date(2026, 10, 6)) is None


def test_cancel_reservation_removes_record():
    props = make_props()
    reservations: list[dict] = []
    create_reservation(props, reservations, 1, date(2026, 10, 5), "«Онегин»")
    create_reservation(
        props,
        reservations,
        2,
        date(2026, 10, 7),
        "«Щелкунчик»",
    )
    cancelled = cancel_reservation(reservations, 1)
    assert cancelled["production"] == "«Онегин»"
    assert len(reservations) == 1
    assert reservations[0]["production"] == "«Щелкунчик»"


def test_cancel_reservation_missing_raises():
    with pytest.raises(ValueError):
        cancel_reservation([], 5)


def test_get_reservation_status_texts():
    available_text = get_reservation_status(True)
    busy_text = get_reservation_status(False)
    assert available_text == "Предмет доступен для бронирования"
    assert busy_text == "Предмет уже занят"
