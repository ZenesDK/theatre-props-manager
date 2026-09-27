"""Тесты класса Production и функций справочника постановок."""

from datetime import date

from models.productions import (
    Production,
    add_production,
    find_production_by_title,
)


def test_production_str_with_all_fields():
    production = Production(1, "«Пиковая дама»", "Ржевский А. И.",
                            date(2025, 10, 12))
    assert str(production) == (
        "«Пиковая дама» — Ржевский А. И. (премьера 12.10.2025)"
    )


def test_production_str_without_optional_fields():
    production = Production(2, "«Онегин»", None, None)
    assert str(production) == (
        "«Онегин» — режиссёр не указан (премьера не указана)"
    )


def test_production_from_data():
    data = {
        "id": 1,
        "title": "«Щелкунчик»",
        "director": "Соколова Е. В.",
        "premiere_date": "2025-12-21",
    }
    production = Production.from_data(data)
    assert production.id == 1
    assert production.premiere_date == date(2025, 12, 21)


def test_production_from_data_without_premiere():
    data = {"id": 2, "title": "«Маскарад»", "director": None}
    production = Production.from_data(data)
    assert production.director is None
    assert production.premiere_date is None


def test_production_to_data():
    production = Production(1, "«Пиковая дама»", "Ржевский А. И.",
                            date(2025, 10, 12))
    assert production.to_data() == {
        "id": 1,
        "title": "«Пиковая дама»",
        "director": "Ржевский А. И.",
        "premiere_date": "2025-10-12",
    }


def test_production_data_roundtrip():
    original = Production(4, "«Борис Годунов»", None, date(2026, 11, 15))
    restored = Production.from_data(original.to_data())
    assert restored.id == original.id
    assert restored.director is None
    assert restored.premiere_date == original.premiere_date


def test_add_production_first_id():
    productions: list[Production] = []
    production = add_production(
        productions, "«Пиковая дама»", "Ржевский А. И.", None
    )
    assert production.id == 1
    assert production.title == "«Пиковая дама»"


def test_add_production_sequential_ids():
    productions = [Production(1, "«Онегин»", None, None)]
    production = add_production(productions, "«Маскарад»", None, None)
    assert production.id == 2


def test_find_production_by_title_case_insensitive():
    productions = [Production(1, "«Щелкунчик»", None, None)]
    found = find_production_by_title(productions, "«щелкунчик»")
    assert found is not None
    assert found.id == 1


def test_find_production_by_title_missing():
    productions = [Production(1, "«Щелкунчик»", None, None)]
    assert find_production_by_title(productions, "«Русалка»") is None


def test_find_production_by_title_strips_spaces():
    productions = [Production(1, "«Маскарад»", None, None)]
    found = find_production_by_title(productions, "  «маскарад»  ")
    assert found is not None
