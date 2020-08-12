from collections import namedtuple

import pytz
from ics import Calendar
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

from shared import get_project_by_name

# Regex pattern for relevant names
RELEVANT_NAMES = ["Restmüll", "Blaue Tonne", "Gelber Sack", "Bioabfall"]
TARGET_PROJECT = "GOA"
DEFAULT_REMINDER = False
TIMEZONE = pytz.timezone("Europe/Berlin")

reminder_struct = namedtuple("reminder_struct", "hour, minute, dayoffset, houroffset, minuteoffset")
REMINDER_TIMES = [reminder_struct(hour=0, minute=0, dayoffset=-1, houroffset=18, minuteoffset=0),
                  reminder_struct(hour=5, minute=45, dayoffset=0, houroffset=0, minuteoffset=0),
                  reminder_struct(hour=6, minute=0, dayoffset=0, houroffset=0, minuteoffset=0)]


def get_relevant_events(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        file_content = f.read()

    c = Calendar(file_content)

    relevant_events = Calendar()
    names_regex = re.compile("|".join(RELEVANT_NAMES), flags=re.IGNORECASE)
    for event in c.events:
        if event.begin >= datetime.now(tz=TIMEZONE):
            matches = names_regex.findall(event.name)
            if matches:
                event.begin = event.begin.astimezone(TIMEZONE).replace(hour=0)
                relevant_events.events.add(event)

    return relevant_events


def add_task(api: TodoistAPI, task_name: str, due: datetime, project_id: int, auto_reminder: bool):
    task_due = due.isoformat()[0:10]
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due, auto_reminder=auto_reminder)

    for td in REMINDER_TIMES:
        if td.hour != 0 or td.minute != 0:
            reminder_time = due.replace(hour=td.hour, minute=td.minute) + \
                            timedelta(days=td.dayoffset, hours=td.houroffset, minutes=td.minuteoffset)
        else:
            reminder_time = due + timedelta(days=td.dayoffset, hours=td.houroffset, minutes=td.minuteoffset)
        reminder_time = reminder_time.astimezone(TIMEZONE)
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time.astimezone(pytz.utc).isoformat())

    api.commit()
    return item


def main():
    load_dotenv()
    relevant_events = get_relevant_events("imschwenksbrunnenwesthausen.ics")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()
    state = api.state

    project_id = get_project_by_name(api, TARGET_PROJECT)
    for event in relevant_events.events:
        print(f"{event.name}: {event.begin}...", end="")
        result = add_task(api, event.name, event.begin.astimezone(TIMEZONE), project_id, auto_reminder=DEFAULT_REMINDER)
        print("Done")


if __name__ == '__main__':
    main()
