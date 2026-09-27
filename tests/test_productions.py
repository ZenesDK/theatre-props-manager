"""Тесты функций справочника постановок."""

from datetime import date

from productions import add_production, find_production_by_title


def test_add_production_first_id():
    productions: dict[int, dict] = {}
    production_id = add_production(
        productions,
        "«Пиковая дама»",
        "Ржевский А. И.",
        date(2025, 10, 12),
    )
    assert production_id == 1
    assert productions[1]["title"] == "«Пиковая дама»"
    assert productions[1]["director"] == "Ржевский А. И."
    assert productions[1]["premiere_date"] == "2025-10-12"


def test_add_production_sequential_ids():
    productions: dict[int, dict] = {}
    add_production(productions, "«Онегин»", None, None)
    assert add_production(productions, "«Маскарад»", None, None) == 2


def test_add_production_optional_fields_none():
    productions: dict[int, dict] = {}
    add_production(productions, "«Борис Годунов»", None, None)
    assert productions[1]["director"] is None
    assert productions[1]["premiere_date"] is None


def test_find_production_by_title_case_insensitive():
    productions: dict[int, dict] = {}
    add_production(productions, "«Щелкунчик»", None, None)
    found = find_production_by_title(productions, "«щелкунчик»")
    assert found is not None
    assert found["id"] == 1


def test_find_production_by_title_missing():
    productions: dict[int, dict] = {}
    add_production(productions, "«Щелкунчик»", None, None)
    assert find_production_by_title(productions, "«Русалка»") is None


def test_find_production_by_title_strips_spaces():
    productions: dict[int, dict] = {}
    add_production(productions, "«Маскарад»", None, None)
    found = find_production_by_title(productions, "  «маскарад»  ")
    assert found is not None
