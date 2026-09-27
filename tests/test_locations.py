"""Тесты класса Location и функций справочника локаций."""

from models.locations import Location, add_location, find_location_by_name


def test_location_str():
    location = Location(1, "Склад №1")
    assert str(location) == "Склад №1"


def test_location_from_data():
    location = Location.from_data({"id": 2, "name": "Малая сцена"})
    assert location.id == 2
    assert location.name == "Малая сцена"


def test_location_to_data():
    location = Location(1, "Склад №1")
    assert location.to_data() == {"id": 1, "name": "Склад №1"}


def test_location_data_roundtrip():
    original = Location(5, "Мастерская реставрации")
    restored = Location.from_data(original.to_data())
    assert restored.id == original.id
    assert restored.name == original.name


def test_add_location_first_id():
    locations: list[Location] = []
    location = add_location(locations, "Гримёрная №2")
    assert location.id == 1
    assert location.name == "Гримёрная №2"


def test_add_location_sequential_ids():
    locations = [Location(1, "Склад №1")]
    assert add_location(locations, "Малая сцена").id == 2


def test_find_location_by_name_case_insensitive():
    locations = [Location(1, "Склад №1")]
    found = find_location_by_name(locations, "склад №1")
    assert found is not None
    assert found.id == 1


def test_find_location_by_name_missing():
    locations = [Location(1, "Склад №1")]
    assert find_location_by_name(locations, "Ангар") is None
