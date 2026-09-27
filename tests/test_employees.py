"""Тесты класса Employee и функций справочника сотрудников."""

from models.employees import Employee, add_employee


def test_employee_str_with_position():
    employee = Employee(1, "Иванова Анна Петровна", "реквизитор")
    assert str(employee) == "Иванова Анна Петровна (реквизитор)"


def test_employee_str_without_position():
    employee = Employee(2, "Петров Пётр Петрович", None)
    assert str(employee) == "Петров Пётр Петрович (должность не указана)"


def test_employee_from_data():
    data = {"id": 3, "full_name": "Смирнов Олег", "position": "зав. складом"}
    employee = Employee.from_data(data)
    assert employee.id == 3
    assert employee.position == "зав. складом"


def test_employee_to_data():
    employee = Employee(1, "Иванова Анна", None)
    assert employee.to_data() == {
        "id": 1,
        "full_name": "Иванова Анна",
        "position": None,
    }


def test_employee_data_roundtrip():
    original = Employee(7, "Кузнецова Мария", "завпост")
    restored = Employee.from_data(original.to_data())
    assert restored.id == original.id
    assert restored.full_name == original.full_name
    assert restored.position == original.position


def test_add_employee():
    employees: list[Employee] = []
    employee = add_employee(employees, "Петров Пётр Петрович", "реквизитор")
    assert employee.id == 1
    assert employees[0].full_name == "Петров Пётр Петрович"
