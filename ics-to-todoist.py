from collections import namedtuple

import pytz
from ics import Calendar
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

# Regex pattern for relevant names
# RELEVANT_NAMES = ["Restmüll", "Blaue Tonne", "Gelber Sack"]
RELEVANT_NAMES = ["Betriebliche Steuerpraxis"]
TARGET_PROJECT = "Education 🎓"

reminder_struct = namedtuple("reminder_struct", "hour, minute, dayoffset, houroffset, minuteoffset")
REMINDER_TIMES = [reminder_struct(hour=0, minute=0, dayoffset=0, houroffset=0, minuteoffset=-15)]


def get_relevant_events(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        file_content = f.read()

    c = Calendar(file_content)

    relevant_events = Calendar()
    names_regex = re.compile("|".join(RELEVANT_NAMES), flags=re.IGNORECASE)
    for event in c.events:
        if event.begin >= datetime.now(tz=pytz.utc):
            matches = names_regex.findall(event.name)
            if matches:
                relevant_events.events.add(event)

    return relevant_events


def get_project_by_name(api: TodoistAPI, target_project: str):
    for project in api.projects.state["projects"]:
        if re.fullmatch(target_project, project["name"], flags=re.IGNORECASE):
            return project["id"]

    return None


def add_task(api: TodoistAPI, task_name: str, due: datetime, project_id: int, direct_reminder: bool):
    task_due = due.isoformat()
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due)

    if direct_reminder:
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=due.isoformat())

    for td in REMINDER_TIMES:
        if td.hour != 0 or td.minute != 0:
            reminder_time = due.replace(hour=td.hour, minute=td.minute) + \
                            timedelta(days=td.dayoffset, hours=td.houroffset, minutes=td.minuteoffset)
        else:
            reminder_time = due + timedelta(days=td.dayoffset, hours=td.houroffset, minutes=td.minuteoffset)
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time.isoformat())

    api.commit()
    return item


def main():
    load_dotenv()
    relevant_events = get_relevant_events("4906797.ics")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, TARGET_PROJECT)
    for event in relevant_events.events:
        print(f"{event.name}: {event.begin}...", end="")
        add_task(api, event.name, event.begin, project_id, direct_reminder=True)
        print("Done")


if __name__ == '__main__':
    main()
