import pytz
from ics import Calendar
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

# Regex pattern for relevant names
RELEVANT_NAMES = ["Restmüll", "Blaue Tonne", "Gelber Sack"]
TARGET_PROJECT = "GOA 🗑"

REMINDER_TIMES = [timedelta(hours=5),
                  timedelta(hours=5, minutes=15),
                  timedelta(hours=5, minutes=30),
                  timedelta(hours=5, minutes=45),
                  timedelta(hours=-5)]

def get_relevant_events(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        file_content = f.read()

    c = Calendar(file_content)

    relevant_events = Calendar()
    names_regex = re.compile("|".join(RELEVANT_NAMES), flags=re.IGNORECASE)
    for event in c.events:
        if event.begin >= datetime.today().replace(tzinfo=pytz.UTC):
            matches = names_regex.findall(event.name)
            if matches:
                relevant_events.events.add(event)

    return relevant_events


def get_project_by_name(TARGET_PROJECT, api):
    for project in api.projects.state["projects"]:
        if re.match(TARGET_PROJECT, project["name"]):
            return project["id"]

    return None


def add_task(api: TodoistAPI, task_name: str, due: datetime, project_id: int):
    task_due = due.strftime("%Y-%m-%d")
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due)

    for td in REMINDER_TIMES:
        reminder_time = (due + td).strftime("%Y-%m-%dT%H:%M")
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time)

    api.commit()
    return item


def main():
    load_dotenv()
    relevant_events = get_relevant_events("2019-2020.ics")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(TARGET_PROJECT, api)
    for event in relevant_events.events:
        print(f"{event.name}: {event.begin}...", end="")
        add_task(api, event.name, event.begin, project_id)
        print("Done")


if __name__ == '__main__':
    main()
