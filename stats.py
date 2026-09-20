"""Статистика каталога реквизита.

Модуль собирает сводные данные о фонде реквизита: общее
количество предметов, распределения по статусам, категориям
и локациям, количество предметов, требующих ремонта.
"""


def count_values(values: list[str]) -> dict[str, int]:
    """Подсчитать количество повторений каждого значения."""
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _location_name(prop: dict, locations: dict[int, dict]) -> str:
    """Вернуть имя локации предмета или прочерк."""
    location = locations.get(prop["location_id"])
    return location["name"] if location else "—"


def get_stats(
    props: dict[int, dict],
    locations: dict[int, dict],
) -> dict:
    """Собрать сводную статистику по каталогу реквизита.

    Возвращает словарь: total — всего предметов, needs_repair —
    требующих ремонта, by_status, by_category, by_location —
    распределения количества предметов по значениям.
    """
    prop_values = list(props.values())
    return {
        "total": len(prop_values),
        "needs_repair": sum(
            1
            for prop in prop_values
            if prop["condition"] == "требует ремонта"
        ),
        "by_status": count_values(
            [prop["status"] for prop in prop_values]
        ),
        "by_category": count_values(
            [prop["category"] or "—" for prop in prop_values]
        ),
        "by_location": count_values(
            [_location_name(prop, locations) for prop in prop_values]
        ),
    }
