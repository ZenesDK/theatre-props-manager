"""Тесты функций перемещений: выдача и возврат."""

import pytest

from movements import issue_prop, return_prop
from props import STATUS_IN_STOCK, STATUS_ISSUED


def make_props() -> dict[int, dict]:
    """Подготовить каталог: один предмет на складе, один выдан."""
    return {
        1: {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Шпага дворянская",
            "category": "бутафорское оружие",
            "condition": "изношено",
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
            "status": STATUS_ISSUED,
            "location_id": 2,
            "created_at": "2026-09-01T10:00:00",
        },
    }


def test_issue_prop_changes_status_and_adds_movement():
    props = make_props()
    movements: list[dict] = []
    movement = issue_prop(props, movements, 1, 2, 3, "репетиция")
    assert props[1]["status"] == STATUS_ISSUED
    assert props[1]["location_id"] == 3
    assert len(movements) == 1
    assert movements[0] is movement
    assert movement["prop_id"] == 1
    assert movement["movement_type"] == "выдача"
    assert movement["employee_id"] == 2
    assert movement["purpose"] == "репетиция"


def test_issue_prop_not_in_stock_raises():
    props = make_props()
    with pytest.raises(ValueError):
        issue_prop(props, [], 2, 1, 1, "спектакль")


def test_issue_prop_missing_prop_raises():
    props = make_props()
    with pytest.raises(ValueError):
        issue_prop(props, [], 99, 1, 1, "спектакль")


def test_return_prop_changes_status_and_condition():
    props = make_props()
    movements: list[dict] = []
    movement = return_prop(props, movements, 2, 1, "изношено")
    assert props[2]["status"] == STATUS_IN_STOCK
    assert props[2]["location_id"] == 1
    assert props[2]["condition"] == "изношено"
    assert movement["movement_type"] == "возврат"
    assert movement["prop_id"] == 2


def test_return_prop_not_issued_raises():
    props = make_props()
    with pytest.raises(ValueError):
        return_prop(props, [], 1, 1, "хорошее")


def test_movements_get_sequential_ids():
    props = make_props()
    movements: list[dict] = []
    issue_prop(props, movements, 1, 2, 3, "репетиция")
    return_prop(props, movements, 1, 1, "хорошее")
    issue_prop(props, movements, 1, 2, 3, "спектакль")
    ids = [movement["id"] for movement in movements]
    assert ids == [1, 2, 3]
    types = [movement["movement_type"] for movement in movements]
    assert types == ["выдача", "возврат", "выдача"]
