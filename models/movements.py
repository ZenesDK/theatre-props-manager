"""Перемещения реквизита: класс Movement и функции выдачи/возврата.

Запись журнала хранит ссылки на объекты Prop, Location
и Employee (для возврата сотрудник не указывается — None).
Сами изменения состояния предмета выполняют его методы
mark_issued() и mark_returned(); функции модуля лишь
создают запись журнала и добавляют её в коллекцию.
"""

from datetime import datetime

from models.employees import Employee
from models.locations import Location
from models.props import Prop
from utils import find_by_id, next_id

MOVEMENT_ISSUE = "выдача"
MOVEMENT_RETURN = "возврат"


class Movement:
    """Запись о выдаче или возврате предмета реквизита."""

    def __init__(
        self,
        movement_id: int,
        prop: Prop,
        movement_type: str,
        location: Location,
        employee: Employee | None,
        purpose: str,
        moved_at: datetime,
    ) -> None:
        """Создать запись журнала перемещений."""
        self.id = movement_id
        self.prop = prop
        self.movement_type = movement_type
        self.location = location
        self.employee = employee
        self.purpose = purpose
        self.moved_at = moved_at

    @classmethod
    def from_data(
        cls,
        data: dict,
        props: list[Prop],
        locations: list[Location],
        employees: list[Employee],
    ) -> "Movement":
        """Создать запись из данных JSON.

        Ссылки на предмет, локацию и сотрудника восстанавливаются
        по идентификаторам из коллекций.

        Raises:
            ValueError: если предмет или локация по идентификатору
                из записи не найдены (повреждённые данные).
        """
        prop = find_by_id(props, data["prop_id"])
        if prop is None:
            raise ValueError(f"Предмет {data['prop_id']} не найден")
        location = find_by_id(locations, data["location_id"])
        if location is None:
            raise ValueError(f"Локация {data['location_id']} не найдена")
        employee_id = data.get("employee_id")
        employee = (
            find_by_id(employees, employee_id)
            if employee_id is not None
            else None
        )
        return cls(
            movement_id=data["id"],
            prop=prop,
            movement_type=data["movement_type"],
            location=location,
            employee=employee,
            purpose=data["purpose"],
            moved_at=datetime.fromisoformat(data["moved_at"]),
        )

    def to_data(self) -> dict:
        """Преобразовать запись в данные JSON."""
        return {
            "id": self.id,
            "prop_id": self.prop.id,
            "movement_type": self.movement_type,
            "location_id": self.location.id,
            "employee_id": self.employee.id if self.employee else None,
            "purpose": self.purpose,
            "moved_at": self.moved_at.isoformat(timespec="seconds"),
        }

    def __str__(self) -> str:
        """Вернуть строковое представление записи журнала."""
        prop_label = f"[{self.prop.inventory_number}] {self.prop.name}"
        if self.movement_type == MOVEMENT_ISSUE:
            arrow = "→"
        else:
            arrow = "←"
        employee_name = str(self.employee) if self.employee else "—"
        return (
            f"{self.moved_at:%d.%m.%Y %H:%M} {arrow} {prop_label} | "
            f"{self.location.name} | {employee_name} | {self.purpose}"
        )


def issue_prop(
    movements: list[Movement],
    prop: Prop,
    employee: Employee,
    location: Location,
    purpose: str,
) -> Movement:
    """Выдать предмет и добавить запись в журнал.

    Изменение состояния предмета выполняет его метод
    mark_issued(); при недопустимом переходе он возбуждает
    ValueError, которое передаётся вызывающему коду.

    Raises:
        ValueError: если предмет не находится на складе.
    """
    prop.mark_issued(location)
    movement = Movement(
        movement_id=next_id(movements),
        prop=prop,
        movement_type=MOVEMENT_ISSUE,
        location=location,
        employee=employee,
        purpose=purpose,
        moved_at=datetime.now(),
    )
    movements.append(movement)
    return movement


def return_prop(
    movements: list[Movement],
    prop: Prop,
    location: Location,
    condition: str,
) -> Movement:
    """Принять предмет и добавить запись в журнал.

    Raises:
        ValueError: если предмет не выдан.
    """
    prop.mark_returned(location, condition)
    movement = Movement(
        movement_id=next_id(movements),
        prop=prop,
        movement_type=MOVEMENT_RETURN,
        location=location,
        employee=None,
        purpose="возврат на хранение",
        moved_at=datetime.now(),
    )
    movements.append(movement)
    return movement
