"""Тесты вспомогательных функций."""

from models.locations import Location
from utils import find_by_id, next_id


def test_next_id_empty_list():
    assert next_id([]) == 1


def test_next_id_object_list():
    items = [Location(1, "Склад №1"), Location(3, "Малая сцена")]
    assert next_id(items) == 4


def test_next_id_single_item():
    assert next_id([Location(7, "Склад №7")]) == 8


def test_find_by_id():
    items = [Location(1, "Склад №1"), Location(3, "Малая сцена")]
    found = find_by_id(items, 3)
    assert found is not None
    assert found.name == "Малая сцена"
    assert find_by_id(items, 99) is None
