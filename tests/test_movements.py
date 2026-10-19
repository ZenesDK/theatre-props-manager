"""Тесты класса Movement и функций журнала событий."""

from datetime import datetime

import pytest

from models.employees import Employee
from models.locations import Location
from models.movements import (
    MOVEMENT_ISSUE,
    MOVEMENT_LOSS,
    MOVEMENT_REPAIR,
    MOVEMENT_REPAIRED,
    MOVEMENT_RETURN,
    MOVEMENT_WRITE_OFF,
    Movement,
    complete_repair,
    issue_prop,
    record_loss,
    return_prop,
    send_to_repair,
    write_off_prop,
)
from models.props import (
    STATUS_IN_REPAIR,
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    STATUS_LOST,
    STATUS_WRITTEN_OFF,
    Prop,
)

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


def test_movement_from_data_unknown_location():
    prop = make_prop(1, STATUS_ISSUED)
    data = {
        "id": 1,
        "prop_id": 1,
        "movement_type": "выдача",
        "location_id": 99,
        "employee_id": None,
        "purpose": "репетиция",
        "moved_at": "2026-09-15T14:30:00",
    }
    with pytest.raises(ValueError):
        Movement.from_data(data, [prop], [STOCK], [ACTOR])


def test_movement_location_none_roundtrip():
    prop = make_prop(1, STATUS_IN_STOCK)
    movement = Movement(
        movement_id=1,
        prop=prop,
        movement_type=MOVEMENT_LOSS,
        location=None,
        employee=None,
        purpose="утерян при перевозке",
        moved_at=datetime(2026, 9, 20, 12, 0, 0),
    )
    data = movement.to_data()
    assert data["location_id"] is None
    restored = Movement.from_data(data, [prop], [], [ACTOR])
    assert restored.location is None


def test_movement_str_labels_special_types():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    loss = record_loss(movements, prop)
    assert "утеря:" in str(loss)
    prop2 = make_prop(2, STATUS_IN_STOCK)
    write_off = write_off_prop(movements, prop2)
    assert "списание:" in str(write_off)


def test_movement_str_issue_format_unchanged():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = issue_prop(movements, prop, ACTOR, SCENE, "репетиция")
    movement.moved_at = datetime(2026, 9, 15, 14, 30, 0)
    assert str(movement) == (
        "15.09.2026 14:30 → [ТР-0001] Предмет №1 | "
        "Малая сцена | Иванова Анна Петровна (реквизитор) | репетиция"
    )


def test_send_to_repair_changes_status_and_logs():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = send_to_repair(movements, prop)
    assert prop.status == STATUS_IN_REPAIR
    assert movement.movement_type == MOVEMENT_REPAIR
    assert movement.location is STOCK
    assert movement.employee is None
    assert len(movements) == 1


def test_send_to_repair_not_in_stock_raises():
    prop = make_prop(1, STATUS_ISSUED)
    movements: list[Movement] = []
    with pytest.raises(ValueError):
        send_to_repair(movements, prop)
    assert movements == []


def test_complete_repair_changes_status_and_condition():
    prop = make_prop(1, STATUS_IN_REPAIR)
    movements: list[Movement] = []
    movement = complete_repair(movements, prop, "хорошее")
    assert prop.status == STATUS_IN_STOCK
    assert prop.condition == "хорошее"
    assert movement.movement_type == MOVEMENT_REPAIRED
    assert movement.location is STOCK


def test_complete_repair_wrong_status_raises():
    prop = make_prop(1, STATUS_IN_STOCK)
    with pytest.raises(ValueError):
        complete_repair([], prop, "новое")


def test_repair_cycle_logs_two_entries():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    send_to_repair(movements, prop)
    complete_repair(movements, prop, "новое")
    types = [movement.movement_type for movement in movements]
    assert types == [MOVEMENT_REPAIR, MOVEMENT_REPAIRED]
    ids = [movement.id for movement in movements]
    assert ids == [1, 2]


def test_write_off_prop_changes_status_and_logs():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = write_off_prop(movements, prop)
    assert prop.status == STATUS_WRITTEN_OFF
    assert movement.movement_type == MOVEMENT_WRITE_OFF
    assert movement.location is STOCK
    assert len(movements) == 1


def test_write_off_issued_prop_raises():
    prop = make_prop(1, STATUS_ISSUED)
    with pytest.raises(ValueError):
        write_off_prop([], prop)


def test_record_loss_marks_and_logs():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = record_loss(movements, prop)
    assert prop.status == STATUS_LOST
    assert movement.movement_type == MOVEMENT_LOSS
    assert movement.employee is None
    assert movement.location is STOCK
    assert movement.purpose == "не найден при инвентаризации"


def test_record_loss_custom_purpose():
    prop = make_prop(1, STATUS_IN_STOCK)
    movements: list[Movement] = []
    movement = record_loss(movements, prop, purpose="утерян при перевозке")
    assert movement.purpose == "утерян при перевозке"
