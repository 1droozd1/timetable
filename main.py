import json
from datetime import datetime
import arrow
from ics import Calendar, Event
import os
import hashlib
import subprocess

group_name = input("Введите название группы: ")
GROUP = group_name.split('-')[1][:3]

group_hash = hashlib.md5(group_name.encode('utf-8')).hexdigest()
LINK = "https://public.mai.ru/schedule/data/" + group_hash + ".json"
print(LINK)
output_file = f"{GROUP}.json"

subprocess.run(["curl", "-o", output_file, LINK])

with open(f"{GROUP}.json", "r", encoding="utf-8") as json_file:
    schedule_data = json.load(json_file)

# Создание календаря
cal = Calendar()

# Извлечение информации о группе
group_name = schedule_data["group"]

# Обработка дней недели
for date, day_data in schedule_data.items():
    if date != "group":
        # Преобразование даты в более удобный формат
        formatted_date = datetime.strptime(date, "%d.%m.%Y").date()
        
        # Обработка пар для данного дня
        for start_time, pair_data in day_data["pairs"].items():
            subject_name = list(pair_data.keys())[0]
            start_time = pair_data[subject_name]["time_start"]
            end_time = pair_data[subject_name]["time_end"]

            lecturer = pair_data[subject_name]["lector"]
            lector_str = [f'{value}' for name, value in lecturer.items()][0]

            room = pair_data[subject_name]["room"]
            room_str = [f'{value}' for name, value in room.items()][0]

            type_ex = [key for key in pair_data[subject_name]["type"]][0]

            # Создание события
            event = Event()
            event.name = f"{subject_name} ({type_ex})"
            event.begin = arrow.get(f"{str(formatted_date)} {start_time}", 'YYYY-MM-DD H:mm:ss').replace(tzinfo='Europe/Moscow')
            event.end = arrow.get(f"{str(formatted_date)} {end_time}", 'YYYY-MM-DD H:mm:ss').replace(tzinfo='Europe/Moscow')
            event.location = room_str
            event.description = f"Преподаватель: {lector_str}"

            cal.events.add(event)

if os.path.exists(f'{GROUP}.ics'):
    os.remove(f'{GROUP}.ics')

with open(f'{GROUP}.ics', 'w', encoding='utf-8') as f:
    f.writelines(cal)
print("Календарь успешно создан и сохранен в файл schedule.ics")