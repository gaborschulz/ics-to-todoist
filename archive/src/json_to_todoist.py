import json
import os
from datetime import datetime

from dateutil import tz, parser
from dotenv import load_dotenv
from todoist.api import TodoistAPI

from .shared import get_project_by_name

# Regex pattern for relevant names
TARGET_PROJECT = "Inbox"
DEFAULT_REMINDER = False
TIMEZONE = tz.gettz("Europe/Berlin")


def get_relevant_events(filename: str):
    """ Get relevant events from Todoist """
    with open(filename, "r", encoding="utf-8") as fp:  # pylint: disable=invalid-name
        file_content = json.load(fp)

    relevant_events = []
    for day in file_content['schedule']['conference']['days']:
        for event in day['rooms']['Virtual']:
            if parser.parse(event['date']) >= datetime.now(tz=TIMEZONE):
                relevant_events.append(event)

    return relevant_events


def add_task(api: TodoistAPI, event, project_id: str):
    """ Add task to Todoist """
    task_due = event['date']
    task_name = f'{event["url"]} ({event["title"]})'
    auto_reminder = True
    item = api.items.add(content=task_name, project_id=project_id, date_string=task_due, auto_reminder=auto_reminder)

    api.notes.add(item_id=item.temp_id, content=event["abstract"])

    api.commit()
    return item


def main():
    """ Main function """
    load_dotenv()
    relevant_events = get_relevant_events("../jsons/djangocon.json")

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, TARGET_PROJECT)
    for event in relevant_events:
        print(f"{event['title']}: {event['date']}...", end="")
        add_task(api=api, event=event, project_id=project_id)
        print("Done")


if __name__ == '__main__':
    main()