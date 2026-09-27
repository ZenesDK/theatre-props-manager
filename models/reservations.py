"""Бронирование реквизита: класс Reservation и функции коллекции.

Бронирование хранит ссылки на объекты Prop и Production.
Отмена выполняется методом cancel(): объект остаётся
в коллекции (сохраняется история бронирований), но меняет
состояние is_cancelled и перестаёт блокировать предмет.
"""

from datetime import date, datetime

from models.productions import Production
from models.props import Prop
from utils import find_by_id, next_id


class Reservation:
    """Бронирование предмета реквизита на дату постановки."""

    def __init__(
        self,
        reservation_id: int,
        prop: Prop,
        date: date,
        production: Production,
        reserved_at: datetime,
        is_cancelled: bool = False,
    ) -> None:
        """Создать объект бронирования."""
        self.id = reservation_id
        self.prop = prop
        self.date = date
        self.production = production
        self.reserved_at = reserved_at
        self.is_cancelled = is_cancelled

    @classmethod
    def from_data(
        cls,
        data: dict,
        props: list[Prop],
        productions: list[Production],
    ) -> "Reservation":
        """Создать бронирование из данных JSON.

        Ссылки на предмет и постановку восстанавливаются
        по идентификаторам из коллекций.

        Raises:
            ValueError: если предмет или постановка по
                идентификатору из записи не найдены
                (повреждённые данные).
        """
        prop = find_by_id(props, data["prop_id"])
        if prop is None:
            raise ValueError(f"Предмет {data['prop_id']} не найден")
        production = find_by_id(productions, data["production_id"])
        if production is None:
            raise ValueError(
                f"Постановка {data['production_id']} не найдена"
            )
        return cls(
            reservation_id=data["id"],
            prop=prop,
            date=date.fromisoformat(data["date"]),
            production=production,
            reserved_at=datetime.fromisoformat(data["reserved_at"]),
            is_cancelled=data.get("is_cancelled", False),
        )

    def to_data(self) -> dict:
        """Преобразовать бронирование в данные JSON."""
        return {
            "id": self.id,
            "prop_id": self.prop.id,
            "date": self.date.isoformat(),
            "production_id": self.production.id,
            "reserved_at": self.reserved_at.isoformat(timespec="seconds"),
            "is_cancelled": self.is_cancelled,
        }

    def cancel(self) -> None:
        """Отменить бронирование.

        Объект остаётся в коллекции — сохраняется история
        ранее созданных бронирований, — но перестаёт
        блокировать предмет на свою дату.
        """
        self.is_cancelled = True

    def __str__(self) -> str:
        """Вернуть строковое представление бронирования."""
        if self.is_cancelled:
            status = "ОТМЕНЕНО"
        else:
            status = "активно"
        return (
            f"[{self.id}] {self.date:%d.%m.%Y} — {self.prop.name} — "
            f"{self.production.title} ({status})"
        )


def find_reservation(
    reservations: list[Reservation],
    prop: Prop,
    target_date: date,
) -> Reservation | None:
    """Найти активное бронирование предмета на указанную дату.

    Отменённые бронирования не учитываются: после отмены
    предмет снова свободен на эту дату.
    """
    for reservation in reservations:
        same_prop = reservation.prop.id == prop.id
        same_date = reservation.date == target_date
        if same_prop and same_date and not reservation.is_cancelled:
            return reservation
    return None


def is_prop_available(
    prop: Prop,
    reservations: list[Reservation],
    target_date: date,
) -> bool:
    """Проверить, свободен ли предмет на указанную дату.

    Предмет недоступен, если он списан или утерян, либо если
    на эту дату есть активное бронирование. Отменённые
    бронирования предмет не блокируют.
    """
    if not prop.is_bookable():
        return False
    return find_reservation(reservations, prop, target_date) is None


def create_reservation(
    reservations: list[Reservation],
    prop: Prop,
    target_date: date,
    production: Production,
) -> Reservation | None:
    """Создать бронирование и вернуть созданный объект.

    Возвращает None, если предмет недоступен на указанную
    дату: активное бронирование блокирует предмет.
    """
    if not is_prop_available(prop, reservations, target_date):
        return None
    reservation = Reservation(
        reservation_id=next_id(reservations),
        prop=prop,
        date=target_date,
        production=production,
        reserved_at=datetime.now(),
    )
    reservations.append(reservation)
    return reservation


def cancel_reservation(
    reservations: list[Reservation],
    reservation_id: int,
) -> bool:
    """Отменить бронирование по идентификатору.

    Бронирование не удаляется из коллекции: вызывается его
    метод cancel(). Возвращает True, если бронирование найдено,
    и False, если идентификатор неизвестен.
    """
    for reservation in reservations:
        if reservation.id == reservation_id:
            reservation.cancel()
            return True
    return False


def get_reservation_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности предмета."""
    if is_available:
        return "Предмет доступен для бронирования"
    return "Предмет уже занят"
