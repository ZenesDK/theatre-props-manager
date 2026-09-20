"""Тесты функций каталога реквизита."""

import pytest

from props import (
    add_prop,
    filter_props,
    find_prop_by_inventory_number,
    find_props,
    sort_props,
)


def make_props() -> dict[int, dict]:
    """Подготовить каталог из трёх предметов с разными полями."""
    return {
        1: {
            "id": 1,
            "inventory_number": "ТР-0001",
            "name": "Шпага дворянская",
            "category": "бутафорское оружие",
            "condition": "изношено",
            "status": "на складе",
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
        2: {
            "id": 2,
            "inventory_number": "ТР-0002",
            "name": "Кубок золотой",
            "category": "посуда",
            "condition": "новое",
            "status": "выдан",
            "location_id": 2,
            "created_at": "2026-09-01T10:00:00",
        },
        3: {
            "id": 3,
            "inventory_number": "ТР-0003",
            "name": "Канделябр бронзовый",
            "category": "мебель",
            "condition": "хорошее",
            "status": "на складе",
            "location_id": 1,
            "created_at": "2026-09-01T10:00:00",
        },
    }


def test_add_prop_first_id_and_status():
    props: dict[int, dict] = {}
    prop_id = add_prop(
        props,
        "ТР-0100",
        "Зеркало в резной раме",
        "мебель",
        "хорошее",
        1,
    )
    assert prop_id == 1
    assert props[1]["inventory_number"] == "ТР-0100"
    assert props[1]["status"] == "на складе"
    assert props[1]["location_id"] == 1


def test_add_prop_sequential_ids():
    props = make_props()
    prop_id = add_prop(
        props,
        "ТР-0100",
        "Зеркало в резной раме",
        "мебель",
        "хорошее",
        1,
    )
    assert prop_id == 4


def test_add_prop_duplicate_inventory_number():
    props = make_props()
    with pytest.raises(ValueError):
        add_prop(props, "тр-0002", "Дубль кубка", "посуда", "новое", 1)


def test_find_prop_by_inventory_number_case_insensitive():
    props = make_props()
    found = find_prop_by_inventory_number(props, "тр-0003")
    assert found is not None
    assert found["id"] == 3


def test_find_prop_by_inventory_number_missing():
    props = make_props()
    found = find_prop_by_inventory_number(props, "ТР-9999")
    assert found is None


def test_find_props_by_name_substring():
    props = make_props()
    found = find_props(props, "золот")
    assert [prop["id"] for prop in found] == [2]


def test_find_props_by_inventory_substring():
    props = make_props()
    found = find_props(props, "000")
    assert len(found) == 3


def test_find_props_no_results():
    props = make_props()
    assert find_props(props, "балалайка") == []


def test_filter_props_by_category():
    props = make_props()
    furniture = filter_props(props, category="мебель")
    assert [prop["id"] for prop in furniture] == [3]


def test_filter_props_by_status():
    props = make_props()
    in_stock = filter_props(props, status="на складе")
    assert [prop["id"] for prop in in_stock] == [1, 3]


def test_filter_props_without_filters():
    props = make_props()
    assert len(filter_props(props)) == 3


def test_sort_props_by_name():
    props = make_props()
    ordered = sort_props(list(props.values()), "название")
    assert [prop["id"] for prop in ordered] == [3, 2, 1]


def test_sort_props_by_status():
    props = make_props()
    ordered = sort_props(list(props.values()), "статус")
    assert [prop["id"] for prop in ordered] == [2, 1, 3]


def test_sort_props_does_not_modify_source():
    source = list(make_props().values())
    original_ids = [prop["id"] for prop in source]
    sort_props(source, "название")
    assert [prop["id"] for prop in source] == original_ids


def test_sort_props_unknown_key():
    with pytest.raises(ValueError):
        sort_props([], "вес")
