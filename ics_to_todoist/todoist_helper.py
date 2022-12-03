import re
from datetime import timedelta
from zoneinfo import ZoneInfo

from rich.progress import Progress
from todoist import TodoistAPI

from ics_to_todoist.models import Event, Configuration, Project

projects: dict[str, Project] = {}


def get_project_by_name(api: TodoistAPI, project_name: str):
    """Get project by name"""
    if project_name in projects:
        return projects[project_name]

    for project in api.state["projects"]:
        if re.match(project_name, project["name"][0:len(project_name)], flags=re.IGNORECASE):
            projects[project_name] = Project(**project.data)
            return projects[project_name]

    raise ValueError(f'{project_name} was not found')


def upload_events(api: TodoistAPI, project: Project, events: list[Event], config: Configuration, progress: Progress) -> int:
    """Upload events to Todoist"""
    counter = 0
    task = progress.add_task('Uploading to Todoist...', total=len(events))
    for event in events:
        if config.default_reminder:
            task_due = event.begin.isoformat()[0:16]
        else:
            task_due = event.begin.isoformat()[0:10]
        progress.console.print(f"\t{event.name} @ {task_due}")
        item = api.items.add(content=event.name, project_id=project.id, date_string=task_due, auto_reminder=config.default_reminder)

        for reminder_time in config.reminder_times:
            if reminder_time.has_datetime_components:
                reminder_time_value = event.begin.replace(**reminder_time.datetime_components) + timedelta(**reminder_time.timedelta_components)  # type: ignore
            else:
                reminder_time_value = event.begin + timedelta(**reminder_time.timedelta_components)
            reminder_time_value = reminder_time_value.astimezone(config.zoneinfo)
            api.reminders.add(item_id=item.temp_id, service="push", type="absolute", due_date_utc=reminder_time_value.astimezone(ZoneInfo('UTC')).isoformat())

        api.commit()
        counter += 1
        progress.update(task_id=task, advance=1)

    return counter
