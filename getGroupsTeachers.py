import json

import requests
from bs4 import BeautifulSoup
import tqdm

def get_groups_and_teachers():
    result = {"groups": [], "teachers": []}

    for i in range(1, 6):
        url = f"https://ssau.ru/rasp/faculty/492430598?course={i}"
        response = requests.get(url)
        if response.status_code == 200:
            root = BeautifulSoup(response.text, 'html.parser')
            groups = root.select(".group-catalog__groups > a")
            for group in groups:
                group_id = ''.join(filter(str.isdigit, group.get("href")))
                result["groups"].append({"name": group.text, "link": f"/rasp?groupId={group_id}"})

    for i in tqdm.tqdm(range(1, 120)):
        url = f"https://ssau.ru/staff?page={i}"
        response = requests.get(url)
        if response.status_code == 200:
            root = BeautifulSoup(response.text, 'html.parser')
            teachers = root.select(".list-group-item > a")
            for teacher in teachers:
                teacher_id = ''.join(filter(str.isdigit, teacher.get("href")))
                result["teachers"].append({"name": teacher.text, "link": f"/rasp?staffId={teacher_id}"})

    with open("groupsTeachers.json", "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False)


#get_groups_and_teachers()
