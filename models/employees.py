"""Сотрудники: материально ответственные лица театра.

Класс Employee описывает сотрудника, которому выдаётся
реквизит. Функции модуля работают с коллекцией объектов:
list[Employee].
"""

from utils import next_id


class Employee:
    """Сотрудник: материально ответственное лицо."""

    def __init__(
        self,
        employee_id: int,
        full_name: str,
        position: str | None,
    ) -> None:
        """Создать объект сотрудника."""
        self.id = employee_id
        self.full_name = full_name
        self.position = position

    @classmethod
    def from_data(cls, data: dict) -> "Employee":
        """Создать сотрудника из данных JSON."""
        return cls(
            employee_id=data["id"],
            full_name=data["full_name"],
            position=data.get("position"),
        )

    def to_data(self) -> dict:
        """Преобразовать сотрудника в данные JSON."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "position": self.position,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление сотрудника."""
        position = self.position or "должность не указана"
        return f"{self.full_name} ({position})"


def add_employee(
    employees: list[Employee],
    full_name: str,
    position: str | None,
) -> Employee:
    """Добавить сотрудника и вернуть созданный объект."""
    employee = Employee(
        employee_id=next_id(employees),
        full_name=full_name,
        position=position,
    )
    employees.append(employee)
    return employee
