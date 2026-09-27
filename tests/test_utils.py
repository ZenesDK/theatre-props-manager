"""Тесты вспомогательных функций."""

from models.locations import Location
from utils import next_id


def test_next_id_empty_dict():
    assert next_id({}) == 1


def test_next_id_dict():
    assert next_id({1: {}, 5: {}}) == 6


def test_next_id_list():
    items = [{"id": 1}, {"id": 3}]
    assert next_id(items) == 4


def test_next_id_empty_list():
    assert next_id([]) == 1


def test_next_id_object_list():
    items = [Location(1, "Склад №1"), Location(3, "Малая сцена")]
    assert next_id(items) == 4
