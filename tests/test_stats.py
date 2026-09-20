"""Тесты функций статистики."""

from stats import count_values, get_stats


def make_props() -> dict[int, dict]:
    """Каталог из трёх предметов в двух локациях."""
    return {
        1: {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Канделябр бронзовый",
            "category": "мебель",
            "condition": "хорошее",
            "status": "на складе",
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        2: {
            "id": 2,
            "inventory_number": "ТР-0002",
            "name": "Кубок золотой",
            "category": "посуда",
            "condition": "требует ремонта",
            "status": "выдан",
            "location_id": 2,
            "created_at": "2026-09-01T10:00:00",
        },
        3: {
            "id": 3,
            "inventory_number": "ТР-0003",
            "name": "Шпага дворянская",
            "category": "мебель",
            "condition": "изношено",
            "status": "на складе",
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
    }


def make_locations() -> dict[int, dict]:
    """Справочник из двух локаций."""
    return {
        1: {"id": 1, "name": "Склад №1"},
        2: {"id": 2, "name": "Малая сцена"},
    }


def test_count_values():
    assert count_values(["a", "b", "a", "c", "a"]) == {
        "a": 3,
        "b": 1,
        "c": 1,
    }


def test_count_values_empty():
    assert count_values([]) == {}


def test_get_stats_total():
    stats = get_stats(make_props(), make_locations())
    assert stats["total"] == 3


def test_get_stats_by_status():
    stats = get_stats(make_props(), make_locations())
    assert stats["by_status"] == {"на складе": 2, "выдан": 1}


def test_get_stats_by_category():
    stats = get_stats(make_props(), make_locations())
    assert stats["by_category"] == {"мебель": 2, "посуда": 1}


def test_get_stats_by_location():
    stats = get_stats(make_props(), make_locations())
    assert stats["by_location"] == {"Склад №1": 2, "Малая сцена": 1}


def test_get_stats_needs_repair():
    stats = get_stats(make_props(), make_locations())
    assert stats["needs_repair"] == 1


def test_get_stats_unknown_location():
    props = make_props()
    props[3]["location_id"] = 99
    stats = get_stats(props, make_locations())
    assert stats["by_location"] == {"Склад №1": 1, "Малая сцена": 1, "—": 1}
