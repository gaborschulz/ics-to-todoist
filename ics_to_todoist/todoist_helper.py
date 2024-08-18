import uuid
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

import httpx
from rich.progress import Progress
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Project

from ics_to_todoist.models import Event, Configuration

URL = 'https://api.todoist.com/sync/v9/sync'


def upload_events(api: TodoistAPI, project: Project, events: list[Event], config: Configuration, progress: Progress) -> int:
    """Upload events to Todoist"""
    counter = 0
    task = progress.add_task('Uploading to Todoist...', total=len(events))
    parameters = {}
    for event in events:
        if config.default_reminder:
            parameters['due_datetime'] = event.begin.isoformat()[0:16]
        else:
            parameters['due_date'] = event.begin.isoformat()[0:10]
        progress.console.print(f"\t{event.name} @ {parameters}")
        item = api.add_task(content=event.name, project_id=project.id, **parameters)

        reminders = []
        for reminder_time in config.reminder_times:
            if reminder_time.has_datetime_components:
                reminder_time_value = event.begin.replace(**reminder_time.datetime_components) + timedelta(**reminder_time.timedelta_components)  # type: ignore
            else:
                reminder_time_value = event.begin + timedelta(**reminder_time.timedelta_components)
            reminder_time_value = reminder_time_value.astimezone(config.zoneinfo)
            reminders.append(reminder_time_value.astimezone(ZoneInfo('UTC')))

        if reminders:
            add_reminders(todoist_token=api._token, task_id=item.id, reminders=reminders)  # pylint: disable=protected-access

        counter += 1
        progress.update(task_id=task, advance=1)

    return counter


def add_reminders(todoist_token: str, task_id: str, reminders: list[datetime]) -> dict:
    """Add reminders using the Todoist Sync API"""
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }

    commands = {'commands': [
        {
            'type': 'reminder_add',
            'temp_id': str(uuid.uuid4()),
            'uuid': str(uuid.uuid4()),
            'args': {
                'item_id': f'{task_id}',
                'type': 'absolute',
                'due': {
                    'date': x.isoformat(timespec='seconds'),
                }
            }
        } for x in reminders
    ]
    }

    response = httpx.post(url=URL, headers=headers, json=commands)
    response.raise_for_status()
    return response.json()
