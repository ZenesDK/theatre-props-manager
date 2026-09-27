"""Каталог реквизита: класс Prop и функции коллекции.

Предмет реквизита — объект класса Prop. Локация хранится
ссылкой на объект Location. Статус предмета меняется только
через методы mark_issued(), mark_returned() и mark_lost():
объект сам охраняет допустимые переходы состояний.
"""

from datetime import datetime

from models.locations import Location
from utils import find_by_id, next_id

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
    "название": lambda prop: prop.name.lower(),
    "категория": lambda prop: prop.category,
    "состояние": lambda prop: prop.condition,
    "статус": lambda prop: prop.status,
}


class Prop:
    """Предмет театрального реквизита."""

    def __init__(
        self,
        prop_id: int,
        inventory_number: str,
        name: str,
        category: str,
        condition: str,
        location: Location | None,
        created_at: datetime,
        status: str = STATUS_IN_STOCK,
    ) -> None:
        """Создать объект предмета реквизита."""
        self.id = prop_id
        self.inventory_number = inventory_number
        self.name = name
        self.category = category
        self.condition = condition
        self.location = location
        self.created_at = created_at
        self.status = status

    @staticmethod
    def validate_status(status: str) -> bool:
        """Проверить, известен ли статус предмета."""
        return status in STATUSES

    @classmethod
    def from_data(cls, data: dict, locations: list[Location]) -> "Prop":
        """Создать предмет из данных JSON.

        Локация восстанавливается по идентификатору из коллекции.

        Raises:
            ValueError: если статус предмета неизвестен.
        """
        location = find_by_id(locations, data["location_id"])
        if not cls.validate_status(data["status"]):
            raise ValueError(f"Неизвестный статус: {data['status']}")
        return cls(
            prop_id=data["id"],
            inventory_number=data["inventory_number"],
            name=data["name"],
            category=data["category"],
            condition=data["condition"],
            location=location,
            created_at=datetime.fromisoformat(data["created_at"]),
            status=data["status"],
        )

    def to_data(self) -> dict:
        """Преобразовать предмет в данные JSON."""
        return {
            "id": self.id,
            "inventory_number": self.inventory_number,
            "name": self.name,
            "category": self.category,
            "condition": self.condition,
            "status": self.status,
            "location_id": self.location.id if self.location else None,
            "created_at": self.created_at.isoformat(timespec="seconds"),
        }

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в номере или названии."""
        wanted = query.strip().lower()
        in_number = wanted in self.inventory_number.lower()
        in_name = wanted in self.name.lower()
        return in_number or in_name

    def is_bookable(self) -> bool:
        """Проверить, можно ли бронировать предмет."""
        return self.status not in (STATUS_LOST, STATUS_WRITTEN_OFF)

    def needs_repair(self) -> bool:
        """Проверить, требует ли предмет ремонта."""
        return self.condition == "требует ремонта"

    def mark_issued(self, location: Location) -> None:
        """Выдать предмет: сменить статус и локацию.

        Raises:
            ValueError: если предмет не находится на складе.
        """
        if self.status != STATUS_IN_STOCK:
            raise ValueError(
                f"Предмет «{self.name}» нельзя выдать "
                f"(текущий статус: {self.status})"
            )
        self.status = STATUS_ISSUED
        self.location = location

    def mark_returned(self, location: Location, condition: str) -> None:
        """Принять предмет: вернуть на склад и зафиксировать состояние.

        Raises:
            ValueError: если предмет не выдан.
        """
        if self.status != STATUS_ISSUED:
            raise ValueError(
                f"Предмет «{self.name}» не выдан "
                f"(текущий статус: {self.status})"
            )
        self.status = STATUS_IN_STOCK
        self.location = location
        self.condition = condition

    def mark_lost(self) -> None:
        """Пометить предмет утерянным."""
        self.status = STATUS_LOST

    def __str__(self) -> str:
        """Вернуть строковое представление предмета."""
        location_name = self.location.name if self.location else "—"
        return (
            f"[{self.inventory_number}] {self.name} — "
            f"{self.status} ({location_name})"
        )


def add_prop(
    props: list[Prop],
    inventory_number: str,
    name: str,
    category: str,
    condition: str,
    location: Location,
) -> Prop:
    """Добавить предмет в каталог и вернуть созданный объект.

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
    prop = Prop(
        prop_id=next_id(props),
        inventory_number=inventory_number,
        name=name,
        category=category,
        condition=condition,
        location=location,
        created_at=datetime.now(),
    )
    props.append(prop)
    return prop


def find_prop_by_inventory_number(
    props: list[Prop],
    inventory_number: str,
) -> Prop | None:
    """Найти предмет по инвентарному номеру без учёта регистра."""
    wanted = inventory_number.strip().lower()
    for prop in props:
        if prop.inventory_number.lower() == wanted:
            return prop
    return None


def find_props(props: list[Prop], query: str) -> list[Prop]:
    """Найти предметы по подстроке названия или инвентарного номера."""
    wanted = query.strip().lower()
    return [prop for prop in props if prop.matches(wanted)]


def filter_props(
    props: list[Prop],
    category: str | None = None,
    status: str | None = None,
) -> list[Prop]:
    """Отбирать предметы по категории и/или статусу.

    Аргументы со значением None в отборе не участвуют;
    без аргументов возвращаются все предметы каталога.
    """
    selected = []
    for prop in props:
        if category is not None and prop.category != category:
            continue
        if status is not None and prop.status != status:
            continue
        selected.append(prop)
    return selected


def sort_props(props: list[Prop], sort_key: str) -> list[Prop]:
    """Отсортировать предметы по полю из SORT_OPTIONS.

    Исходный список не изменяется, возвращается новый.

    Raises:
        ValueError: если передан неизвестный ключ сортировки.
    """
    key_function = _SORT_KEYS.get(sort_key)
    if key_function is None:
        raise ValueError(f"Неизвестный ключ сортировки: {sort_key}")
    return sorted(props, key=key_function)
