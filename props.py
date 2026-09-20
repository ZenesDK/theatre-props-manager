"""Каталог реквизита: добавление, поиск, фильтрация, сортировка.

Предмет реквизита — словарь с полями id, inventory_number, name,
category, condition, status, location_id, created_at. Каталог
предметов представлен словарём вида {id: предмет}.
"""

from datetime import datetime

from utils import next_id

CATEGORIES = [
    "мебель",
    "посуда",
    "бутафорское оружие",
    "текстиль",
    "декорации",
    "электроника",
    "прочее",
]
CONDITIONS = ["новое", "хорошее", "изношено", "требует ремонта"]

STATUS_IN_STOCK = "на складе"
STATUS_ISSUED = "выдан"
STATUS_IN_REPAIR = "в ремонте"
STATUS_LOST = "утерян"
STATUS_WRITTEN_OFF = "списан"

STATUSES = [
    STATUS_IN_STOCK,
    STATUS_ISSUED,
    STATUS_IN_REPAIR,
    STATUS_LOST,
    STATUS_WRITTEN_OFF,
]

SORT_OPTIONS = ["название", "категория", "состояние", "статус"]
_SORT_KEYS = {
    "название": lambda prop: prop["name"].lower(),
    "категория": lambda prop: prop["category"],
    "состояние": lambda prop: prop["condition"],
    "статус": lambda prop: prop["status"],
}


def find_prop_by_inventory_number(
    props: dict[int, dict],
    inventory_number: str,
) -> dict | None:
    """Найти предмет по инвентарному номеру без учёта регистра."""
    wanted = inventory_number.strip().lower()
    for prop in props.values():
        if prop["inventory_number"].lower() == wanted:
            return prop
    return None


def add_prop(
    props: dict[int, dict],
    inventory_number: str,
    name: str,
    category: str,
    condition: str,
    location_id: int,
) -> int:
    """Добавить предмет в каталог и вернуть его идентификатор.

    Raises:
        ValueError: если предмет с таким инвентарным номером
            уже есть в каталоге.
    """
    duplicate = find_prop_by_inventory_number(props, inventory_number)
    if duplicate is not None:
        raise ValueError(
            f"Предмет с инвентарным номером {inventory_number} "
            "уже существует"
        )
    prop_id = next_id(props)
    props[prop_id] = {
        "id": prop_id,
        "inventory_number": inventory_number,
        "name": name,
        "category": category,
        "condition": condition,
        "status": STATUS_IN_STOCK,
        "location_id": location_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    return prop_id


def _matches_query(prop: dict, wanted: str) -> bool:
    """Проверить, встречается ли подстрока в имени или номере."""
    name_match = wanted in prop["name"].lower()
    number_match = wanted in prop["inventory_number"].lower()
    return name_match or number_match


def find_props(props: dict[int, dict], query: str) -> list[dict]:
    """Найти предметы по подстроке названия или инвентарного номера.

    Поиск ведётся без учёта регистра; возвращается список
    найденных предметов в порядке их id.
    """
    wanted = query.strip().lower()
    return list(
        prop
        for prop in props.values()
        if _matches_query(prop, wanted)
    )


def filter_props(
    props: dict[int, dict],
    category: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Отбирать предметы по категории и/или статусу.

    Аргументы со значением None в отборе не участвуют;
    без аргументов возвращаются все предметы каталога.
    """
    selected = []
    for prop in props.values():
        if category is not None and prop["category"] != category:
            continue
        if status is not None and prop["status"] != status:
            continue
        selected.append(prop)
    return selected


def sort_props(props: list[dict], sort_key: str) -> list[dict]:
    """Отсортировать предметы по полю из SORT_OPTIONS.

    Ключом сортировки служит lambda-функция из _SORT_KEYS.
    Исходный список не изменяется, возвращается новый.

    Raises:
        ValueError: если передан неизвестный ключ сортировки.
    """
    key_function = _SORT_KEYS.get(sort_key)
    if key_function is None:
        raise ValueError(f"Неизвестный ключ сортировки: {sort_key}")
    return sorted(props, key=key_function)
