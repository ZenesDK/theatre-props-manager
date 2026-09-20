"""Тесты функций инвентаризации."""

from inventory import (
    build_report,
    mark_missing_lost,
    select_props_for_check,
    split_by_answers,
)
from props import (
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    STATUS_LOST,
    STATUS_WRITTEN_OFF,
)


def make_props() -> dict[int, dict]:
    """Каталог для сверки локации 1: два на складе, один утерян,
    один списан (исключается), один выдан в локации 2."""
    return {
        1: {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Канделябр бронзовый",
            "category": "мебель",
            "condition": "хорошее",
            "status": STATUS_IN_STOCK,
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        2: {
            "id": 2,
            "inventory_number": "ТР-0002",
            "name": "Кубок золотой",
            "category": "посуда",
            "condition": "новое",
            "status": STATUS_IN_STOCK,
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        3: {
            "id": 3,
            "inventory_number": "ТР-0003",
            "name": "Шпага дворянская",
            "category": "бутафорское оружие",
            "condition": "изношено",
            "status": STATUS_ISSUED,
            "location_id": 2,
            "created_at": "2026-09-01T10:00:00",
        },
        4: {
            "id": 4,
            "inventory_number": "ТР-0004",
            "name": "Плащ бархатный красный",
            "category": "текстиль",
            "condition": "хорошее",
            "status": STATUS_WRITTEN_OFF,
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        5: {
            "id": 5,
            "inventory_number": "ТР-0005",
            "name": "Трон деревянный",
            "category": "мебель",
            "condition": "требует ремонта",
            "status": STATUS_LOST,
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
    }


def test_select_props_for_check_location():
    props = make_props()
    checked = select_props_for_check(props, 1)
    assert [prop["id"] for prop in checked] == [1, 2, 5]


def test_select_props_for_check_other_location():
    props = make_props()
    checked = select_props_for_check(props, 2)
    assert [prop["id"] for prop in checked] == [3]


def test_select_props_for_check_empty_location():
    props = make_props()
    assert select_props_for_check(props, 3) == []


def test_split_by_answers():
    props = make_props()
    to_check = [props[1], props[2]]
    answers = {1: True, 2: False}
    found, missing = split_by_answers(to_check, answers)
    assert [prop["id"] for prop in found] == [1]
    assert [prop["id"] for prop in missing] == [2]


def test_split_by_answers_absent_counts_as_missing():
    to_check = [make_props()[1]]
    found, missing = split_by_answers(to_check, {})
    assert found == []
    assert [prop["id"] for prop in missing] == [1]


def test_build_report():
    props = make_props()
    found = [props[1]]
    missing = [props[2]]
    report = build_report("Склад №1", found, missing)
    assert report["location"] == "Склад №1"
    assert report["total"] == 2
    assert report["found"] == [
        {"inventory_number": "ТР-0001", "name": "Канделябр бронзовый"}
    ]
    assert report["missing"] == [
        {"inventory_number": "ТР-0002", "name": "Кубок золотой"}
    ]


def test_mark_missing_lost_changes_status():
    props = make_props()
    missing = [props[1], props[2]]
    updated = mark_missing_lost(props, missing)
    assert updated == 2
    assert props[1]["status"] == STATUS_LOST
    assert props[2]["status"] == STATUS_LOST


def test_mark_missing_lost_skips_already_lost():
    props = make_props()
    missing = [props[1], props[5]]
    updated = mark_missing_lost(props, missing)
    assert updated == 1
    assert props[5]["status"] == STATUS_LOST


def test_mark_missing_lost_empty():
    props = make_props()
    assert mark_missing_lost(props, []) == 0
