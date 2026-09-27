"""Бронирование реквизита на даты постановок.

Запись бронирования — словарь с полями id, prop_id, date
(ISO-строка ГГГГ-ММ-ДД), production_id, reserved_at.
Бронирования представлены списком записей. На следующем
этапе записи станут объектами класса Reservation.
"""

from datetime import date, datetime

from models.props import Prop
from utils import next_id


def find_reservation(
    reservations: list[dict],
    prop: Prop,
    target_date: date,
) -> dict | None:
    """Найти бронирование предмета на указанную дату.

    Возвращает None, если на эту дату брони нет.
    """
    date_iso = target_date.isoformat()
    for reservation in reservations:
        same_prop = reservation["prop_id"] == prop.id
        same_date = reservation["date"] == date_iso
        if same_prop and same_date:
            return reservation
    return None


def is_prop_available(
    prop: Prop,
    reservations: list[dict],
    target_date: date,
) -> bool:
    """Проверить, свободен ли предмет на указанную дату.

    Предмет недоступен, если он списан или утерян,
    либо если на эту дату уже есть бронирование.
    """
    if not prop.is_bookable():
        return False
    return find_reservation(reservations, prop, target_date) is None


def create_reservation(
    reservations: list[dict],
    prop: Prop,
    target_date: date,
    production_id: int,
) -> dict:
    """Создать бронирование и вернуть его запись.

    Raises:
        ValueError: если предмет недоступен на указанную дату.
    """
    if not is_prop_available(prop, reservations, target_date):
        raise ValueError("Предмет недоступен на выбранную дату")
    reservation = {
        "id": next_id(reservations),
        "prop_id": prop.id,
        "date": target_date.isoformat(),
        "production_id": production_id,
        "reserved_at": datetime.now().isoformat(timespec="seconds"),
    }
    reservations.append(reservation)
    return reservation


def cancel_reservation(
    reservations: list[dict],
    reservation_id: int,
) -> dict:
    """Отменить бронирование и вернуть удалённую запись.

    Raises:
        ValueError: если бронирование с таким идентификатором
            не найдено.
    """
    for index, reservation in enumerate(reservations):
        if reservation["id"] == reservation_id:
            return reservations.pop(index)
    raise ValueError(f"Бронирование {reservation_id} не найдено")


def get_reservation_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности предмета."""
    if is_available:
        return "Предмет доступен для бронирования"
    return "Предмет уже занят"
