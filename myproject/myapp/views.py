import json

from django.shortcuts import render

from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup


def parse(html_code, student):
    soup = BeautifulSoup(html_code, 'html.parser')
    schedule_items = soup.find_all('div', class_='schedule__item')
    schedule_data = {'понедельник': [], 'вторник': [], 'среда': [], 'четверг': [], 'пятница': [], 'суббота': []}
    i = 0
    k = 0
    for item in schedule_items:
        if i <= 6:
            i += 1
            continue
        if item.find('div', class_='schedule__lesson lesson-border lesson-border-type-1') or True:
            try:
                if student:
                    discipline = item.find('div', class_='schedule__discipline').text.strip()
                    place = item.find('div', class_='schedule__place').text.strip()
                    teacher = item.find('div', class_='schedule__teacher').text.strip()
                else:
                    discipline = item.find('div', class_='body-text schedule__discipline lesson-color lesson-color-type-1').text.strip()
                    place = item.find('div', class_='caption-text schedule__place').text.strip()
                    teacher = None
                groups = [group.text.strip() for group in item.find_all('a', class_='caption-text schedule__group')]
            except:
                discipline = 'None'
                place = 'None'
                teacher = 'None'
                groups = 'None'
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

            schedule_data[weekday].append({
                'time': f'{time_start} - {time_end}',
                'discipline': discipline,
                'place': place,
                'teacher': teacher,
                'groups': groups
            })

    return schedule_data


def get_curr_week():
    url = 'https://ssau.ru/rasp?groupId=531030142'
    request = requests.get(url)
    if request.status_code != 200:
        return 0
    html_code = request.text
    soup = BeautifulSoup(html_code, 'html.parser')
    curr_week = soup.find('span', class_='h3-text week-nav-current_week')
    curr_week = curr_week.text[1:3]
    return curr_week


def get_schedule(request):
    curr_week = int(get_curr_week())
    week_offset = int(request.POST.get('week_offset', 0))
    time_slots = ['08:00 - 09:35', '09:45 - 11:20', '11:30 - 13:05', '13:30 - 15:05', '15:15 - 16:50', '17:00 - 18:35']
    search_url = 'https://ssau.ru/rasp?groupId=531030143'
    selected_param = 0
    data = []
    student_check = True
    with open('groupsTeachers.json', 'r', encoding='utf-8') as json_file:
        all_data = json.load(json_file)
    for i in range(len(all_data['groups'])):
        data.append(all_data['groups'][i]['name'])
    for i in range(len(all_data['teachers'])):
        data.append(all_data['teachers'][i]['name'])
    if request.method == 'POST':
        selected_param = request.POST.get('data_select')
        print(selected_param)
        if curr_week - week_offset < 0 and week_offset < 0:
            curr_week = abs(week_offset)
        for i in range(len(all_data['groups'])):
            if all_data['groups'][i]['name'] == selected_param:
                group_url = all_data['groups'][i]['link']
                search_url = f'https://ssau.ru/{group_url}&selectedWeek={curr_week + week_offset}&selectedWeekday=1'
                break
        for i in range(len(all_data['teachers'])):
            if type(selected_param) == str and all_data['teachers'][i]['name'].find(selected_param) != -1:
                student_check = False
                teacher_url = all_data['teachers'][i]['link']
                search_url = f'https://ssau.ru/{teacher_url}&selectedWeek={curr_week + week_offset}&selectedWeekday=1'
                break
    response = requests.get(search_url)
    html_code = response.text
    schedule = parse(html_code,student_check)
    for day, entries in schedule.items():
        for entry in entries:
            for key, value in entry.items():
                if value == 'None':
                    entry[key] = ''
    print(f'search_url:{search_url}')
    return render(request, 'schedule.html',
                  {'schedule': schedule, 'time_slots': time_slots, 'current_data': selected_param,
                   'curr_week': curr_week, 'all_data': data})
