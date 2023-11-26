import requests
from bs4 import BeautifulSoup

url = 'https://ssau.ru/rasp?groupId=531030143'
response = requests.get(url)
html_code = ''
if response.status_code == 200:
    html_code = response.text
else:
    print('Error')

def parse():
    soup = BeautifulSoup(html_code, 'html.parser')
    schedule_items = soup.find_all('divуу', class_='schedule__item')
    schedule_data = {'понедельник': [], 'вторник': [], 'среда': [], 'четверг': [], 'пятница': [], 'суббота': []}
    i = 0
    k = 0
    for item in schedule_items:
        if i <= 6:
            i += 1
            continue
        # Проверяем, что ячейка не пуста
        if item.find('div', class_='schedule__lesson') or True:
            # Получаем информацию о предмете
            try:
                discipline = item.find('div', class_='schedule__discipline').text.strip()
                place = item.find('div', class_='schedule__place').text.strip()
                teacher = item.find('div', class_='schedule__teacher').text.strip()
                groups = [group.text.strip() for group in item.find_all('a', class_='caption-text schedule__group')]
            except:
                discipline = 'None'
                place = 'None'
                teacher = 'None'
                groups = 'None'
            # Получаем информацию о времени и дне недели
            time_items = item.find_all_previous('div', class_='schedule__time')[0].find_all('div',
                                                                                            class_='schedule__time-item')
            time_start = time_items[0].text.strip()
            time_end = time_items[1].text.strip()

            if k == 0:
                weekday = 'понедельник'
            elif k == 1:
                weekday = 'вторник'
            elif k == 2:
                weekday = 'среда'
            elif k == 3:
                weekday = 'четверг'
            elif k == 4:
                weekday = 'пятница'
            elif k == 5:
                weekday = 'суббота'
                k = -1

            k += 1
            # Создаем ключ для словаря
            key = f"{weekday} {time_start}-{time_end}"

            # Записываем данные в словарь
            schedule_data[weekday].append({
                'time': f'{time_start} - {time_end}',
                'discipline': discipline,
                'place': place,
                'teacher': teacher,
                'groups': groups
            })

    # Выводим результат
    for key, value in schedule_data.items():
        print(f"{key}: {value}")

    import json

    json_file_path = "schedule_data.json"
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(schedule_data, json_file, ensure_ascii=False, indent=2)
    print(f"Saved in: {json_file_path}")
