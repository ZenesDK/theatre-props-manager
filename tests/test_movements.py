"""Тесты класса Movement и функций выдачи/возврата."""

from datetime import datetime

import pytest

from models.employees import Employee
from models.locations import Location
from models.movements import (
    MOVEMENT_ISSUE,
    MOVEMENT_RETURN,
    Movement,
    issue_prop,
    return_prop,
)
from models.props import STATUS_IN_STOCK, STATUS_ISSUED, Prop

STOCK = Location(1, "Склад №1")
SCENE = Location(2, "Малая сцена")
ACTOR = Employee(1, "Иванова Анна Петровна", "реквизитор")


def make_prop(prop_id: int, status: str) -> Prop:
    """Создать предмет с заданным статусом."""
    return Prop(
        prop_id=prop_id,
        inventory_number=f"ТР-000{prop_id}",
        name=f"Предмет №{prop_id}",
        category="мебель",
        condition="хорошее",
        location=STOCK,
        created_at=datetime(2026, 9, 1, 10, 0, 0),
        status=status,
    )


def test_movement_to_data():
    prop = make_prop(1, STATUS_ISSUED)
    movement = Movement(
        movement_id=1,
        prop=prop,
        movement_type=MOVEMENT_ISSUE,
        location=SCENE,
        employee=ACTOR,
        purpose="репетиция",
        moved_at=datetime(2026, 9, 15, 14, 30, 0),
    )
    data = movement.to_data()
    assert data["prop_id"] == 1
    assert data["movement_type"] == "выдача"
    assert data["location_id"] == 2
    assert data["employee_id"] == 1
    assert data["moved_at"] == "2026-09-15T14:30:00"


def test_movement_data_roundtrip():
    prop = make_prop(1, STATUS_ISSUED)
    movement = Movement(
        movement_id=1,
        prop=prop,
        movement_type=MOVEMENT_RETURN,
        location=STOCK,
        employee=None,
        purpose="возврат на хранение",
        moved_at=datetime(2026, 9, 16, 10, 0, 0),
    )
    restored = Movement.from_data(
        movement.to_data(),
        [prop],
        [STOCK, SCENE],
        [ACTOR],
    )
    assert restored.id == movement.id
    assert restored.prop is prop
    assert restored.location is STOCK
    assert restored.employee is None
    assert restored.moved_at == movement.moved_at


def test_issue_prop_changes_status_and_adds_movement():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = issue_prop(movements, prop, ACTOR, SCENE, "репетиция")
    assert prop.status == STATUS_ISSUED
    assert prop.location is SCENE
    assert len(movements) == 1
    assert movements[0] is movement
    assert movement.movement_type == MOVEMENT_ISSUE
    assert movement.employee is ACTOR


def test_issue_prop_not_in_stock_raises():
    prop = make_prop(1, STATUS_ISSUED)
    movements: list[Movement] = []
    with pytest.raises(ValueError):
        issue_prop(movements, prop, ACTOR, SCENE, "спектакль")
    assert movements == []


def test_return_prop_changes_status_and_condition():
    prop = make_prop(1, STATUS_ISSUED)
    movements: list[Movement] = []
    movement = return_prop(movements, prop, STOCK, "изношено")
    assert prop.status == STATUS_IN_STOCK
    assert prop.location is STOCK
    assert prop.condition == "изношено"
    assert movement.movement_type == MOVEMENT_RETURN
    assert movement.employee is None


def test_return_prop_not_issued_raises():
    prop = make_prop(1, STATUS_IN_STOCK)
    with pytest.raises(ValueError):
        return_prop([], prop, STOCK, "хорошее")


def test_movements_get_sequential_ids():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    issue_prop(movements, prop, ACTOR, SCENE, "репетиция")
    return_prop(movements, prop, STOCK, "хорошее")
    issue_prop(movements, prop, ACTOR, SCENE, "спектакль")
    ids = [movement.id for movement in movements]
    assert ids == [1, 2, 3]
    types = [movement.movement_type for movement in movements]
    assert types == [MOVEMENT_ISSUE, MOVEMENT_RETURN, MOVEMENT_ISSUE]


def test_movement_from_data_unknown_prop():
    prop = make_prop(1, STATUS_ISSUED)
    data = {
        "id": 1,
        "prop_id": 99,
        "movement_type": "выдача",
        "location_id": 2,
        "employee_id": 1,
        "purpose": "репетиция",
        "moved_at": "2026-09-15T14:30:00",
    }
    with pytest.raises(ValueError):
        Movement.from_data(data, [prop], [STOCK, SCENE], [ACTOR])
