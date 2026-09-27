"""Постановки: репертуар театра.

Класс Production описывает постановку, под которую
бронируется реквизит. Дата премьеры хранится в объекте
как date, в JSON — ISO-строкой. Функции модуля работают
с коллекцией объектов: list[Production].
"""

from datetime import date

from utils import next_id


class Production:
    """Постановка из репертуара театра."""

    def __init__(
        self,
        production_id: int,
        title: str,
        director: str | None,
        premiere_date: date | None,
    ) -> None:
        """Создать объект постановки."""
        self.id = production_id
        self.title = title
        self.director = director
        self.premiere_date = premiere_date

    @classmethod
    def from_data(cls, data: dict) -> "Production":
        """Создать постановку из данных JSON."""
        premiere = data.get("premiere_date")
        return cls(
            production_id=data["id"],
            title=data["title"],
            director=data.get("director"),
            premiere_date=(
                date.fromisoformat(premiere) if premiere else None
            ),
        )

    def to_data(self) -> dict:
        """Преобразовать постановку в данные JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "premiere_date": (
                self.premiere_date.isoformat()
                if self.premiere_date
                else None
            ),
        }

    def __str__(self) -> str:
        """Вернуть строковое представление постановки."""
        director = self.director or "режиссёр не указан"
        if self.premiere_date is not None:
            premiere_text = f"премьера {self.premiere_date:%d.%m.%Y}"
        else:
            premiere_text = "премьера не указана"
        return f"{self.title} — {director} ({premiere_text})"


def add_production(
    productions: list[Production],
    title: str,
    director: str | None,
    premiere_date: date | None,
) -> Production:
    """Добавить постановку и вернуть созданный объект."""
    production = Production(
        production_id=next_id(productions),
        title=title,
        director=director,
        premiere_date=premiere_date,
    )
    productions.append(production)
    return production


def find_production_by_title(
    productions: list[Production],
    title: str,
) -> Production | None:
    """Найти постановку по названию без учёта регистра."""
    wanted = title.strip().lower()
    for production in productions:
        if production.title.lower() == wanted:
            return production
    return None
