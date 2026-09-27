"""Тесты класса Prop и функций каталога реквизита."""

from datetime import datetime

import pytest

from models.locations import Location
from models.props import (
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    STATUS_LOST,
    Prop,
    add_prop,
    filter_props,
    find_prop_by_inventory_number,
    find_props,
    sort_props,
)


def make_location() -> Location:
    """Склад для предметов каталога."""
    return Location(1, "Склад №1")


def make_prop(prop_id: int, status: str) -> Prop:
    """Создать предмет с заданным статусом."""
    return Prop(
        prop_id=prop_id,
        inventory_number=f"ТР-000{prop_id}",
        name=f"Предмет №{prop_id}",
        category="мебель",
        condition="хорошее",
        location=make_location(),
        created_at=datetime(2026, 9, 1, 10, 0, 0),
        status=status,
    )


def make_props() -> list[Prop]:
    """Каталог из трёх предметов с разными полями."""
    return [
        make_prop(1, STATUS_IN_STOCK),
        make_prop(2, STATUS_ISSUED),
        make_prop(3, STATUS_LOST),
    ]


def test_prop_str():
    prop = make_prop(1, STATUS_IN_STOCK)
    assert str(prop) == "[ТР-0001] Предмет №1 — на складе (Склад №1)"


def test_prop_to_data():
    prop = make_prop(1, STATUS_IN_STOCK)
    data = prop.to_data()
    assert data["id"] == 1
    assert data["inventory_number"] == "ТР-0001"
    assert data["location_id"] == 1
    assert data["status"] == STATUS_IN_STOCK


def test_prop_data_roundtrip():
    locations = [make_location()]
    prop = make_prop(2, STATUS_ISSUED)
    restored = Prop.from_data(prop.to_data(), locations)
    assert restored.id == prop.id
    assert restored.name == prop.name
    assert restored.status == prop.status
    assert restored.location is locations[0]


def test_validate_status():
    assert Prop.validate_status("выдан")
    assert not Prop.validate_status("в полёте")


def test_from_data_unknown_status():
    data = {
        "id": 1,
        "inventory_number": "ТР-0001",
        "name": "Канделябр",
        "category": "мебель",
        "condition": "хорошее",
        "status": "исчез",
        "location_id": 1,
        "created_at": "2026-09-01T10:00:00",
    }
    with pytest.raises(ValueError):
        Prop.from_data(data, [make_location()])


def test_matches_case_insensitive():
    prop = make_prop(1, STATUS_IN_STOCK)
    prop.name = "Кубок золотой"
    assert prop.matches("золот")
    assert prop.matches("ТР-0001")
    assert not prop.matches("шпага")


def test_mark_issued_changes_status():
    prop = make_prop(1, STATUS_IN_STOCK)
    location = Location(2, "Малая сцена")
    prop.mark_issued(location)
    assert prop.status == STATUS_ISSUED
    assert prop.location is location


def test_mark_issued_not_in_stock_raises():
    prop = make_prop(1, STATUS_ISSUED)
    with pytest.raises(ValueError):
        prop.mark_issued(Location(2, "Малая сцена"))


def test_mark_returned_changes_status_and_condition():
    prop = make_prop(1, STATUS_ISSUED)
    location = Location(1, "Склад №1")
    prop.mark_returned(location, "изношено")
    assert prop.status == STATUS_IN_STOCK
    assert prop.location is location
    assert prop.condition == "изношено"


def test_mark_returned_not_issued_raises():
    prop = make_prop(1, STATUS_IN_STOCK)
    with pytest.raises(ValueError):
        prop.mark_returned(Location(1, "Склад №1"), "хорошее")


def test_mark_lost():
    prop = make_prop(1, STATUS_IN_STOCK)
    prop.mark_lost()
    assert prop.status == STATUS_LOST


def test_is_bookable():
    assert make_prop(1, STATUS_IN_STOCK).is_bookable()
    assert make_prop(2, STATUS_ISSUED).is_bookable()
    assert not make_prop(3, STATUS_LOST).is_bookable()


def test_needs_repair():
    prop = make_prop(1, STATUS_IN_STOCK)
    prop.condition = "требует ремонта"
    assert prop.needs_repair()
    prop.condition = "хорошее"
    assert not prop.needs_repair()


def test_add_prop_returns_object():
    props: list[Prop] = []
    prop = add_prop(
        props, "ТР-0100", "Зеркало", "мебель", "хорошее", make_location()
    )
    assert prop.id == 1
    assert props[0] is prop
    assert prop.status == STATUS_IN_STOCK


def test_add_prop_duplicate_inventory_number():
    props = make_props()
    with pytest.raises(ValueError):
        add_prop(
            props, "ТР-0002", "Дубль", "мебель", "новое", make_location()
        )


def test_find_prop_by_inventory_number():
    props = make_props()
    found = find_prop_by_inventory_number(props, "тр-0002")
    assert found is not None
    assert found.id == 2
    assert find_prop_by_inventory_number(props, "ТР-9999") is None


def test_find_props_by_substring():
    props = make_props()
    found = find_props(props, "предмет")
    assert len(found) == 3
    assert find_props(props, "незабудка") == []


def test_filter_props_by_status():
    props = make_props()
    in_stock = filter_props(props, status=STATUS_IN_STOCK)
    assert [prop.id for prop in in_stock] == [1]


def test_filter_props_without_filters():
    props = make_props()
    assert len(filter_props(props)) == 3


def test_sort_props_by_name():
    props = make_props()
    props[0].name = "Ядро"
    props[1].name = "Арфа"
    props[2].name = "Гобой"
    ordered = sort_props(props, "название")
    assert [prop.id for prop in ordered] == [2, 3, 1]


def test_sort_props_does_not_modify_source():
    props = make_props()
    original_ids = [prop.id for prop in props]
    sort_props(props, "статус")
    assert [prop.id for prop in props] == original_ids


def test_sort_props_unknown_key():
    with pytest.raises(ValueError):
        sort_props([], "вес")
