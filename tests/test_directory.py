"""Тесты функций справочников: локации и сотрудники."""

from directory import add_employee, add_location, find_location_by_name


def test_add_location_first_id():
    locations: dict[int, dict] = {}
    assert add_location(locations, "Гримёрная №2") == 1
    assert locations[1]["name"] == "Гримёрная №2"


def test_add_location_sequential_ids():
    locations = {1: {"id": 1, "name": "Склад №1"}}
    assert add_location(locations, "Малая сцена") == 2


def test_find_location_by_name_case_insensitive():
    locations = {1: {"id": 1, "name": "Склад №1"}}
    found = find_location_by_name(locations, "склад №1")
    assert found is not None
    assert found["id"] == 1


def test_find_location_by_name_missing():
    locations = {1: {"id": 1, "name": "Склад №1"}}
    assert find_location_by_name(locations, "Ангар") is None


def test_add_employee():
    employees: dict[int, dict] = {}
    add_employee(employees, "Петров Пётр Петрович", "реквизитор")
    assert employees[1]["full_name"] == "Петров Пётр Петрович"
    assert employees[1]["position"] == "реквизитор"
