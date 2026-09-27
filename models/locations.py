"""Локации: места хранения и использования реквизита.

Класс Location описывает отдельную локацию (склад, сцена,
репетиционный зал, мастерская). Функции модуля работают
с коллекцией объектов: list[Location].
"""

from utils import next_id


class Location:
    """Локация: место хранения или использования реквизита."""

    def __init__(self, location_id: int, name: str) -> None:
        """Создать объект локации."""
        self.id = location_id
        self.name = name

    @classmethod
    def from_data(cls, data: dict) -> "Location":
        """Создать локацию из данных JSON."""
        return cls(
            location_id=data["id"],
            name=data["name"],
        )

    def to_data(self) -> dict:
        """Преобразовать локацию в данные JSON."""
        return {
            "id": self.id,
            "name": self.name,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление локации."""
        return self.name


def add_location(locations: list[Location], name: str) -> Location:
    """Добавить локацию и вернуть созданный объект."""
    location = Location(
        location_id=next_id(locations),
        name=name,
    )
    locations.append(location)
    return location


def find_location_by_name(
    locations: list[Location],
    name: str,
) -> Location | None:
    """Найти локацию по точному имени без учёта регистра."""
    wanted = name.strip().lower()
    for location in locations:
        if location.name.lower() == wanted:
            return location
    return None
