"""Справочники проекта: локации и сотрудники.

Локации — места хранения и использования реквизита (склады,
сцены, репетиционные залы, мастерская). Сотрудники —
материально ответственные лица, которым выдаётся реквизит.
"""

from utils import next_id


def add_location(locations: dict[int, dict], name: str) -> int:
    """Добавить локацию и вернуть её идентификатор."""
    location_id = next_id(locations)
    locations[location_id] = {"id": location_id, "name": name}
    return location_id


def find_location_by_name(
    locations: dict[int, dict],
    name: str,
) -> dict | None:
    """Найти локацию по точному имени без учёта регистра."""
    wanted = name.strip().lower()
    for location in locations.values():
        if location["name"].lower() == wanted:
            return location
    return None


def add_employee(
    employees: dict[int, dict],
    full_name: str,
    position: str | None,
) -> int:
    """Добавить сотрудника и вернуть его идентификатор."""
    employee_id = next_id(employees)
    employees[employee_id] = {
        "id": employee_id,
        "full_name": full_name,
        "position": position,
    }
    return employee_id
