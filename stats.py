"""Статистика каталога реквизита.

Модуль собирает сводные данные о фонде реквизита: общее
количество предметов, распределения по статусам, категориям
и локациям, количество предметов, требующих ремонта.
"""

from models.props import Prop


def count_values(values: list[str]) -> dict[str, int]:
    """Подсчитать количество повторений каждого значения."""
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def get_stats(props: list[Prop]) -> dict:
    """Собрать сводную статистику по каталогу реквизита.

    Возвращает словарь: total — всего предметов, needs_repair —
    требующих ремонта, by_status, by_category, by_location —
    распределения количества предметов по значениям.
    """
    return {
        "total": len(props),
        "needs_repair": sum(1 for prop in props if prop.needs_repair()),
        "by_status": count_values(
            [prop.status for prop in props]
        ),
        "by_category": count_values(
            [prop.category or "—" for prop in props]
        ),
        "by_location": count_values(
            [
                prop.location.name if prop.location else "—"
                for prop in props
            ]
        ),
    }
