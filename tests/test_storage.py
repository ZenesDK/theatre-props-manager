"""Тесты загрузки данных: битые ссылки и пропущенные поля.

Проверяется поведение _convert_items: корректные записи
превращаются в объекты, а запись с битой ссылкой или без
обязательного поля прерывает запуск с SystemExit (без
аварийной трассировки).
"""

import pytest

import storage
from models.employees import Employee
from models.locations import Location
from models.props import Prop


def test_convert_items_converts_records():
    items = [
        {
            "id": 1,
            "full_name": "Иванова Анна Петровна",
            "position": "реквизитор",
        }
    ]
    employees = storage._convert_items(
        "employees.json", items, Employee.from_data
    )
    assert employees[0].full_name == "Иванова Анна Петровна"
    assert employees[0].position == "реквизитор"


def test_convert_items_empty_list():
    assert storage._convert_items(
        "locations.json", [], Location.from_data
    ) == []


def test_convert_items_broken_reference_exits():
    items = [
        {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Шпага",
            "category": "бутафорское оружие",
            "condition": "новое",
            "status": "на складе",
            "location_id": 99,
            "created_at": "2026-09-01T10:00:00",
        }
    ]
    with pytest.raises(SystemExit):
        storage._convert_items(
            "props.json",
            items,
            lambda item: Prop.from_data(item, []),
        )


def test_convert_items_missing_field_exits():
    items = [{"id": 1}]  # нет обязательного поля name
    with pytest.raises(SystemExit):
        storage._convert_items(
            "locations.json", items, Location.from_data
        )
