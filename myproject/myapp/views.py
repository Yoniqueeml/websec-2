from django.shortcuts import render

from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup


def parse(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    schedule_items = soup.find_all('div', class_='schedule__item')
    schedule_data = {'понедельник': [], 'вторник': [], 'среда': [], 'четверг': [], 'пятница': [], 'суббота': []}
    i = 0
    k = 0
    for item in schedule_items:
        if i <= 6:
            i += 1
            continue
        if item.find('div', class_='schedule__lesson') or True:
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
            key = f"{weekday} {time_start}-{time_end}"

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
    print(f'curr_week: {curr_week}')
    return curr_week


def get_schedule(request):
    curr_week = int(get_curr_week())
    groups = {'6311': 'https://ssau.ru/rasp?groupId=531030142', '6411': 'https://ssau.ru/rasp?groupId=531030143',
              '6511': 'https://ssau.ru/rasp?groupId=531874010'}
    current_group = '6411'
    week_offset = int(request.POST.get('week_offset', 0))
    print(f'week_offset:{week_offset}')

    if request.method == 'POST':
        selected_group = request.POST.get('group_select')
        if selected_group in groups:
            current_group = selected_group
        else:
            return JsonResponse('Invalid group selected', safe=False)
    if curr_week - week_offset < 0:
        curr_week = abs(week_offset)
    print(f'link:' + f'{groups[current_group]}&selectedWeek={curr_week + week_offset}&selectedWeekday=1')
    response = requests.get(f'{groups[current_group]}&selectedWeek={curr_week + week_offset}&selectedWeekday=1')

    if response.status_code != 200:
        return JsonResponse('Error', safe=False)

    html_code = response.text
    time_slots = ['08:00 - 09:35', '09:45 - 11:20', '11:30 - 13:05', '13:30 - 15:05', '15:15 - 16:50', '17:00 - 18:35']
    schedule = parse(html_code)

    for day, entries in schedule.items():
        for entry in entries:
            for key, value in entry.items():
                if value == 'None':
                    entry[key] = ''

    return render(request, 'schedule.html',
                  {'schedule': schedule, 'time_slots': time_slots, 'groups': groups, 'current_group': current_group,
                   'curr_week': curr_week})
