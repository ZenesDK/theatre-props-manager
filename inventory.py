"""Инвентаризация: сверка наличия реквизита по локациям.

Модуль отвечает за отбор предметов для сверки, разделение
результатов на найденные и ненайденные, отметку утери
и сохранение отчёта в формате JSON в каталог reports/.
"""

import json
from datetime import datetime
from pathlib import Path

from props import STATUS_LOST, STATUS_WRITTEN_OFF

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def select_props_for_check(
    props: dict[int, dict],
    location_id: int,
) -> list[dict]:
    """Отобрать предметы локации для сверки.

    Списанные предметы в сверке не участвуют: они выведены
    из эксплуатации и учитываются только в отчётах.
    """
    selected = []
    for prop in props.values():
        at_location = prop["location_id"] == location_id
        not_written_off = prop["status"] != STATUS_WRITTEN_OFF
        if at_location and not_written_off:
            selected.append(prop)
    return selected


def split_by_answers(
    props: list[dict],
    answers: dict[int, bool],
) -> tuple[list[dict], list[dict]]:
    """Разделить предметы сверки на найденные и ненайденные.

    answers сопоставляет идентификатору предмета ответ:
    True — найден, False — не найден. Предмет без ответа
    считается ненайденным.
    """
    found = []
    missing = []
    for prop in props:
        if answers.get(prop["id"], False):
            found.append(prop)
        else:
            missing.append(prop)
    return found, missing


def _brief(prop: dict) -> dict:
    """Краткая запись предмета для отчёта."""
    return {
        "inventory_number": prop["inventory_number"],
        "name": prop["name"],
    }


def build_report(
    location_name: str,
    found: list[dict],
    missing: list[dict],
) -> dict:
    """Собрать отчёт инвентаризации по результатам сверки.

    Отчёт содержит локацию, дату сверки, количество предметов
    и списки найденных и ненайденных (инв. номер, название).
    """
    return {
        "location": location_name,
        "date": datetime.now().isoformat(timespec="seconds"),
        "total": len(found) + len(missing),
        "found": [_brief(prop) for prop in found],
        "missing": [_brief(prop) for prop in missing],
    }


def mark_missing_lost(props: dict[int, dict], missing: list[dict]) -> int:
    """Пометить ненайденные предметы как утерянные.

    Возвращает количество предметов, сменивших статус:
    уже утерянные предметы повторно не пересчитываются.
    """
    updated = 0
    for prop in missing:
        target = props[prop["id"]]
        if target["status"] != STATUS_LOST:
            target["status"] = STATUS_LOST
            updated += 1
    return updated


def save_report(report: dict) -> Path | None:
    """Сохранить отчёт инвентаризации в каталог reports/.

    Имя файла формируется из даты и времени сверки.
    Возвращает путь к файлу или None при ошибке записи.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"inventory_{stamp}.json"
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"Не удалось сохранить отчёт в {path}: {exc}")
        return None
    return path
