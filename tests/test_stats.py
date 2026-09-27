"""Тесты функций статистики."""

from datetime import datetime

from models.locations import Location
from models.props import Prop
from stats import count_values, get_stats

WAREHOUSE = Location(1, "Склад №1")
SCENE = Location(2, "Малая сцена")


def make_props() -> list[Prop]:
    """Каталог из трёх предметов в двух локациях."""
    return [
        Prop(
            prop_id=1,
            inventory_number="ТР-0001",
            name="Канделябр бронзовый",
            category="мебель",
            condition="хорошее",
            location=WAREHOUSE,
            created_at=datetime(2026, 9, 1, 10, 0, 0),
            status="на складе",
        ),
        Prop(
            prop_id=2,
            inventory_number="ТР-0002",
            name="Кубок золотой",
            category="посуда",
            condition="требует ремонта",
            location=SCENE,
            created_at=datetime(2026, 9, 1, 10, 0, 0),
            status="выдан",
        ),
        Prop(
            prop_id=3,
            inventory_number="ТР-0003",
            name="Шпага дворянская",
            category="мебель",
            condition="изношено",
            location=WAREHOUSE,
            created_at=datetime(2026, 9, 1, 10, 0, 0),
            status="на складе",
        ),
    ]


def test_count_values():
    assert count_values(["a", "b", "a", "c", "a"]) == {
        "a": 3,
        "b": 1,
        "c": 1,
    }


def test_count_values_empty():
    assert count_values([]) == {}


def test_get_stats_total():
    stats = get_stats(make_props())
    assert stats["total"] == 3


def test_get_stats_by_status():
    stats = get_stats(make_props())
    assert stats["by_status"] == {"на складе": 2, "выдан": 1}


def test_get_stats_by_category():
    stats = get_stats(make_props())
    assert stats["by_category"] == {"мебель": 2, "посуда": 1}


def test_get_stats_by_location():
    stats = get_stats(make_props())
    assert stats["by_location"] == {"Склад №1": 2, "Малая сцена": 1}


def test_get_stats_needs_repair():
    stats = get_stats(make_props())
    assert stats["needs_repair"] == 1


def test_get_stats_unknown_location():
    props = make_props()
    props[2].location = Location(99, "Нигде")
    stats = get_stats(props)
    assert stats["by_location"] == {
        "Склад №1": 1,
        "Малая сцена": 1,
        "Нигде": 1,
    }
