"""Перемещения реквизита: выдача и возврат предметов.

Запись журнала перемещений — словарь с полями id, prop_id,
movement_type ('выдача' или 'возврат'), location_id, employee_id,
purpose, moved_at. Журнал представлен списком записей.
"""

from datetime import datetime

from props import STATUS_IN_STOCK, STATUS_ISSUED
from utils import next_id

MOVEMENT_ISSUE = "выдача"
MOVEMENT_RETURN = "возврат"


def issue_prop(
    props: dict[int, dict],
    movements: list[dict],
    prop_id: int,
    employee_id: int,
    location_id: int,
    purpose: str,
) -> dict:
    """Выдать предмет: сменить статус и добавить запись в журнал.

    Предмет получает статус «выдан» и новую локацию.

    Raises:
        ValueError: если предмет не найден или не находится
            на складе.
    """
    prop = props.get(prop_id)
    if prop is None:
        raise ValueError(f"Предмет {prop_id} не найден")
    if prop["status"] != STATUS_IN_STOCK:
        raise ValueError(
            f"Предмет «{prop['name']}» нельзя выдать "
            f"(текущий статус: {prop['status']})"
        )
    prop["status"] = STATUS_ISSUED
    prop["location_id"] = location_id
    movement = {
        "id": next_id(movements),
        "prop_id": prop_id,
        "movement_type": MOVEMENT_ISSUE,
        "location_id": location_id,
        "employee_id": employee_id,
        "purpose": purpose,
        "moved_at": datetime.now().isoformat(timespec="seconds"),
    }
    movements.append(movement)
    return movement


def return_prop(
    props: dict[int, dict],
    movements: list[dict],
    prop_id: int,
    location_id: int,
    condition: str,
) -> dict:
    """Принять предмет: вернуть на склад и записать перемещение.

    Предмет получает статус «на складе», новую локацию
    и зафиксированное состояние.

    Raises:
        ValueError: если предмет не найден или не выдан.
    """
    prop = props.get(prop_id)
    if prop is None:
        raise ValueError(f"Предмет {prop_id} не найден")
    if prop["status"] != STATUS_ISSUED:
        raise ValueError(
            f"Предмет «{prop['name']}» не выдан "
            f"(текущий статус: {prop['status']})"
        )
    prop["status"] = STATUS_IN_STOCK
    prop["location_id"] = location_id
    prop["condition"] = condition
    movement = {
        "id": next_id(movements),
        "prop_id": prop_id,
        "movement_type": MOVEMENT_RETURN,
        "location_id": location_id,
        "employee_id": None,
        "purpose": "возврат на хранение",
        "moved_at": datetime.now().isoformat(timespec="seconds"),
    }
    movements.append(movement)
    return movement
