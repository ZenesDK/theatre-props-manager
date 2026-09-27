"""Тесты класса Reservation и функций бронирования."""

from datetime import date, datetime

from models.locations import Location
from models.productions import Production
from models.props import STATUS_LOST, Prop
from models.reservations import (
    Reservation,
    cancel_reservation,
    create_reservation,
    find_reservation,
    get_reservation_status,
    is_prop_available,
)

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
    """Каталог: на складе, выдан, утерян."""
    return [
        make_prop(1, "на складе"),
        make_prop(2, "выдан"),
        make_prop(3, STATUS_LOST),
    ]


def make_productions() -> list[Production]:
    """Репертуар из двух постановок."""
    return [
        Production(1, "«Онегин»", None, None),
        Production(2, "«Щелкунчик»", None, None),
    ]


def make_reservation(
    reservation_id: int,
    prop: Prop,
    production: Production,
    day: date,
    is_cancelled: bool = False,
) -> Reservation:
    """Создать бронирование с заданными параметрами."""
    return Reservation(
        reservation_id=reservation_id,
        prop=prop,
        date=day,
        production=production,
        reserved_at=datetime(2026, 9, 10, 11, 0, 0),
        is_cancelled=is_cancelled,
    )


def test_reservation_str_active():
    prop = make_prop(1, "на складе")
    production = Production(1, "«Онегин»", None, None)
    reservation = make_reservation(1, prop, production, date(2026, 10, 5))
    assert str(reservation) == (
        "[1] 05.10.2026 — Предмет №1 — «Онегин» (активно)"
    )


def test_reservation_str_cancelled():
    prop = make_prop(1, "на складе")
    production = Production(1, "«Онегин»", None, None)
    reservation = make_reservation(
        2, prop, production, date(2026, 10, 7), is_cancelled=True
    )
    assert str(reservation) == (
        "[2] 07.10.2026 — Предмет №1 — «Онегин» (ОТМЕНЕНО)"
    )


def test_reservation_to_data():
    props = make_props()
    productions = make_productions()
    reservation = make_reservation(
        1, props[0], productions[0], date(2026, 10, 5)
    )
    data = reservation.to_data()
    assert data["id"] == 1
    assert data["prop_id"] == 1
    assert data["date"] == "2026-10-05"
    assert data["production_id"] == 1
    assert data["is_cancelled"] is False


def test_reservation_data_roundtrip():
    props = make_props()
    productions = make_productions()
    reservation = make_reservation(
        3, props[1], productions[1], date(2026, 11, 1)
    )
    restored = Reservation.from_data(
        reservation.to_data(), props, productions
    )
    assert restored.id == 3
    assert restored.prop is props[1]
    assert restored.production is productions[1]
    assert restored.date == date(2026, 11, 1)
    assert restored.is_cancelled is False


def test_reservation_cancel_changes_state():
    props = make_props()
    production = Production(1, "«Онегин»", None, None)
    reservation = make_reservation(1, props[0], production, date(2026, 10, 5))
    reservation.cancel()
    assert reservation.is_cancelled is True


def test_is_prop_available_without_reservations():
    props = make_props()
    assert is_prop_available(props[0], [], date(2026, 10, 5))
    assert is_prop_available(props[1], [], date(2026, 10, 5))


def test_is_prop_available_blocked_status():
    props = make_props()
    assert not is_prop_available(props[2], [], date(2026, 10, 5))


def test_create_reservation_appends_object():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    reservation = create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    assert reservation is not None
    assert reservation.id == 1
    assert reservation.prop is props[0]
    assert reservation.production is productions[0]
    assert reservation.date == date(2026, 10, 5)
    assert len(reservations) == 1


def test_duplicate_reservation_returns_none():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    first = create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    second = create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[1]
    )
    assert first is not None
    assert second is None
    assert len(reservations) == 1


def test_same_prop_different_dates_allowed():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    first = create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    second = create_reservation(
        reservations, props[0], date(2026, 10, 7), productions[0]
    )
    assert first is not None
    assert second is not None
    assert is_prop_available(props[0], reservations, date(2026, 10, 6))


def test_find_reservation():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    created = create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    found = find_reservation(reservations, props[0], date(2026, 10, 5))
    assert found is created
    assert find_reservation(reservations, props[0], date(2026, 10, 6)) is None


def test_find_reservation_ignores_cancelled():
    props = make_props()
    production = Production(1, "«Онегин»", None, None)
    reservation = make_reservation(
        1, props[0], production, date(2026, 10, 5), is_cancelled=True
    )
    reservations = [reservation]
    assert find_reservation(reservations, props[0], date(2026, 10, 5)) is None
    assert is_prop_available(props[0], reservations, date(2026, 10, 5))


def test_cancel_reservation_keeps_record():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    assert cancel_reservation(reservations, 1) is True
    assert len(reservations) == 1
    assert reservations[0].is_cancelled is True


def test_cancel_reservation_frees_date():
    props = make_props()
    productions = make_productions()
    reservations: list[Reservation] = []
    create_reservation(
        reservations, props[0], date(2026, 10, 5), productions[0]
    )
    assert not is_prop_available(props[0], reservations, date(2026, 10, 5))
    cancel_reservation(reservations, 1)
    assert is_prop_available(props[0], reservations, date(2026, 10, 5))


def test_cancel_reservation_missing_returns_false():
    assert cancel_reservation([], 5) is False


def test_get_reservation_status_texts():
    available_text = get_reservation_status(True)
    busy_text = get_reservation_status(False)
    assert available_text == "Предмет доступен для бронирования"
    assert busy_text == "Предмет уже занят"
