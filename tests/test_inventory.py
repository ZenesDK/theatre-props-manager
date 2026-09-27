"""Тесты функций инвентаризации."""

from datetime import datetime

from inventory import (
    build_report,
    mark_missing_lost,
    select_props_for_check,
    split_by_answers,
)
from models.locations import Location
from models.props import (
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    STATUS_LOST,
    STATUS_WRITTEN_OFF,
    Prop,
)

WAREHOUSE = Location(1, "Склад №1")
SCENE = Location(2, "Малая сцена")


def make_prop(prop_id: int, status: str, location: Location) -> Prop:
    """Создать предмет с заданным статусом и локацией."""
    return Prop(
        prop_id=prop_id,
        inventory_number=f"ТР-000{prop_id}",
        name=f"Предмет №{prop_id}",
        category="мебель",
        condition="хорошее",
        location=location,
        created_at=datetime(2026, 9, 1, 10, 0, 0),
        status=status,
    )


def make_props() -> list[Prop]:
    """Каталог: два на складе, один утерян, один списан, один на сцене."""
    return [
        make_prop(1, STATUS_IN_STOCK, WAREHOUSE),
        make_prop(2, STATUS_IN_STOCK, WAREHOUSE),
        make_prop(3, STATUS_ISSUED, SCENE),
        make_prop(4, STATUS_WRITTEN_OFF, WAREHOUSE),
        make_prop(5, STATUS_LOST, WAREHOUSE),
    ]


def test_select_props_for_check_location():
    props = make_props()
    checked = select_props_for_check(props, WAREHOUSE)
    assert [prop.id for prop in checked] == [1, 2, 5]


def test_select_props_for_check_other_location():
    props = make_props()
    checked = select_props_for_check(props, SCENE)
    assert [prop.id for prop in checked] == [3]


def test_select_props_for_check_empty_location():
    props = make_props()
    empty = Location(3, "Гримёрная")
    assert select_props_for_check(props, empty) == []


def test_split_by_answers():
    props = make_props()
    to_check = [props[0], props[1]]
    answers = {1: True, 2: False}
    found, missing = split_by_answers(to_check, answers)
    assert [prop.id for prop in found] == [1]
    assert [prop.id for prop in missing] == [2]


def test_split_by_answers_absent_counts_as_missing():
    to_check = [make_props()[0]]
    found, missing = split_by_answers(to_check, {})
    assert found == []
    assert [prop.id for prop in missing] == [1]


def test_build_report():
    props = make_props()
    found = [props[0]]
    missing = [props[1]]
    report = build_report("Склад №1", found, missing)
    assert report["location"] == "Склад №1"
    assert report["total"] == 2
    assert report["found"] == [
        {"inventory_number": "ТР-0001", "name": "Предмет №1"}
    ]
    assert report["missing"] == [
        {"inventory_number": "ТР-0002", "name": "Предмет №2"}
    ]


def test_mark_missing_lost_changes_status():
    props = make_props()
    missing = [props[0], props[1]]
    updated = mark_missing_lost(missing)
    assert updated == 2
    assert props[0].status == STATUS_LOST
    assert props[1].status == STATUS_LOST


def test_mark_missing_lost_skips_already_lost():
    props = make_props()
    missing = [props[0], props[4]]
    updated = mark_missing_lost(missing)
    assert updated == 1
    assert props[4].status == STATUS_LOST


def test_mark_missing_lost_empty():
    assert mark_missing_lost([]) == 0
