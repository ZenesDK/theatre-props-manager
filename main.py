import datetime

print("=" * 50)
print("   Система учёта театрального реквизита (TheaterProps)")
print("   Сценарий: Регистрация и проверка статуса предмета")
print("=" * 50)

# 1. Ввод данных (все значения изначально строки)
prop_name = input("Введите название реквизита: ")
inv_number = input("Введите инвентарный номер: ")
category = input("Введите категорию (мебель, посуда, оружие, текстиль): ")
wear_input = input("Введите процент износа (0-100): ")
location = input("Введите текущее местоположение (Склад №1, Малая сцена, Мастерская): ")

# 2. Преобразование типов
wear = int(wear_input)

# 3. Ветвление: проверка корректности данных и определение состояния
if wear < 0 or wear > 100:
    print("\n⚠️ Ошибка: процент износа должен быть в диапазоне от 0 до 100.")
else:
    if wear < 30:
        condition = "Отличное"
        can_issue = True
    elif wear <= 70:
        condition = "Удовлетворительное"
        can_issue = True
    else:
        condition = "Требует реставрации"
        can_issue = False

    # 4. Операции и расчёты
    remaining_resource = 100 - wear
    est_months_left = remaining_resource / 10  # условный коэффициент расчёта
    today_str = datetime.date.today().strftime("%d.%m.%Y")

    # 5. Вывод отчёта
    print("\n" + "-" * 40)
    print("📋 КАРТОЧКА РЕКВИЗИТА")
    print("-" * 40)
    print(f"Дата учёта:          {today_str}")
    print(f"Название:            {prop_name}")
    print(f"Инвентарный номер:   {inv_number}")
    print(f"Категория:           {category}")
    print(f"Местоположение:      {location}")
    print(f"Текущий износ:       {wear}%")
    print(f"Состояние:           {condition}")
    print(f"Оставшийся ресурс:   {remaining_resource}%")
    print(f"Прогноз эксплуатации:{est_months_left:.1f} мес.")
    print("-" * 40)

    # 6. Ветвление: итоговое решение по выдаче
    if can_issue:
        print("✅ Статус: ПРЕДМЕТ ДОСТУПЕН для выдачи на репетицию или спектакль.")
    else:
        print("🛑 Статус: ВЫДАЧА ЗАПРЕЩЕНА. Требуется направление в мастерскую реставрации.")
    print("=" * 50)