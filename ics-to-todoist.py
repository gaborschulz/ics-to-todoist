from collections import namedtuple

from dateutil import tz
from ics import Calendar
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

from shared import get_project_by_name

# Regex pattern for relevant names
RELEVANT_NAMES = [".*"]
TARGET_PROJECT = "Inbox"
DEFAULT_REMINDER = False
TIMEZONE = tz.gettz("Europe/Berlin")

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
                if event.alarms:
                    print('Alarm at: ', event.begin.datetime + event.alarms[0].trigger)
                relevant_events.events.add(event)

    return relevant_events


def add_task(api: TodoistAPI, event, project_id: str):
    task_due = event.begin.datetime.isoformat()
    task_name = event.name
    auto_reminder = len(event.alarms) == 0
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due, auto_reminder=auto_reminder)

    for reminder_timedelta in event.alarms: 
        reminder_time = event.begin.datetime + reminder_timedelta.trigger
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time.astimezone(tz.UTC).isoformat())
    
    api.notes.add(item_id=item.temp_id, content=event.description)

    api.commit()
    return item


def main():
    load_dotenv()
    relevant_events = get_relevant_events("icals/med.ics")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, TARGET_PROJECT)
    for event in relevant_events.events:
        print(f"{event.name}: {event.begin}...", end="")
        result = add_task(api=api, event=event, project_id=project_id)
        print("Done")


if __name__ == '__main__':
    main()
