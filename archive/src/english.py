import os
import re
from collections import namedtuple
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv
from ics import Calendar
from todoist.api import TodoistAPI

from .shared import get_project_by_name

# Regex pattern for relevant names
RELEVANT_NAMES = ["Englisch A 2"]
TARGET_PROJECT = "Shared"
DEFAULT_REMINDER = False
TIMEZONE = pytz.timezone("Europe/Berlin")

ReminderStruct = namedtuple("ReminderStruct", "hour, minute, dayoffset, houroffset, minuteoffset")
# REMINDER_TIMES = [reminder_struct(hour=0, minute=0, dayoffset=-1, houroffset=18, minuteoffset=0),
#                   reminder_struct(hour=5, minute=45, dayoffset=0, houroffset=0, minuteoffset=0),
#                   reminder_struct(hour=6, minute=0, dayoffset=0, houroffset=0, minuteoffset=0)]
REMINDER_TIMES = [ReminderStruct(hour=0, minute=0, dayoffset=0, houroffset=-1, minuteoffset=0)]


def get_relevant_events(filename: str):
    """ Get relevent events from ics file """
    with open(filename, "r", encoding="utf-8") as fp:  # pylint: disable=invalid-name
        file_content = fp.read()

    cal = Calendar(file_content)

    relevant_events = Calendar()
    names_regex = re.compile("|".join(RELEVANT_NAMES), flags=re.IGNORECASE)
    for event in cal.events:
        if event.begin >= datetime.now(tz=TIMEZONE):
            matches = names_regex.findall(event.name)
            if matches:
                event.begin = event.begin.astimezone(TIMEZONE).replace(hour=0)
                relevant_events.events.add(event)

    return relevant_events


def add_task(api: TodoistAPI, task_name: str, due: datetime, project_id: int, auto_reminder: bool, notes: list):  # pylint: disable=too-many-arguments
    """ Add tasks to Todoist """
    task_due = due.isoformat()
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due, auto_reminder=auto_reminder)

    for task_data in REMINDER_TIMES:
        if task_data.hour != 0 or task_data.minute != 0:
            reminder_time = due.replace(hour=task_data.hour, minute=task_data.minute) + \
                            timedelta(days=task_data.dayoffset, hours=task_data.houroffset, minutes=task_data.minuteoffset)
        else:
            reminder_time = due + timedelta(days=task_data.dayoffset, hours=task_data.houroffset, minutes=task_data.minuteoffset)
        reminder_time = reminder_time.astimezone(TIMEZONE)
        api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time.astimezone(pytz.utc).isoformat())

    for note in notes:
        api.notes.add(item_id=item.temp_id, content=note)

    api.commit()
    return item


def main():
    """ Main function """
    load_dotenv()
    relevant_events = get_relevant_events("5531498.ics")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, TARGET_PROJECT)
    for event in relevant_events.events:
        event.begin = event.begin.replace(hour=18)
        print(f"{event.name}: {event.begin}...", end="")
        add_task(api,
                 event.name,
                 event.begin.astimezone(TIMEZONE),
                 project_id,
                 auto_reminder=DEFAULT_REMINDER,
                 notes=[event.location, event.description])
        print("Done")


if __name__ == '__main__':
    main()