from datetime import timedelta
from zoneinfo import ZoneInfo

from rich.progress import Progress
from synctodoist import TodoistAPI
from synctodoist.models import Due, Project, Task, Reminder, ReminderTypeEnum

from ics_to_todoist.models import Event, Configuration


def upload_events(api: TodoistAPI, project: Project, events: list[Event], config: Configuration, progress: Progress) -> int:
    """Upload events to Todoist"""
    counter = 0
    task = progress.add_task('Uploading to Todoist...', total=len(events))
    for event in events:
        if config.default_reminder:
            task_due = Due(string=event.begin.isoformat()[0:16])
        else:
            task_due = Due(string=event.begin.isoformat()[0:10])
        progress.console.print(f"\t{event.name} @ {task_due.string}")
        item = Task(content=event.name, project_id=project.id, due=task_due, auto_reminder=config.default_reminder)
        api.tasks.add(item)

        for reminder_time in config.reminder_times:
            if reminder_time.has_datetime_components:
                reminder_time_value = event.begin.replace(**reminder_time.datetime_components) + timedelta(**reminder_time.timedelta_components)  # type: ignore
            else:
                reminder_time_value = event.begin + timedelta(**reminder_time.timedelta_components)
            reminder_time_value = reminder_time_value.astimezone(config.zoneinfo)
            reminder = Reminder(item_id=item.temp_id,
                                type=ReminderTypeEnum.absolute,
                                due=Due(string=reminder_time_value.astimezone(ZoneInfo('UTC')).isoformat()))
            api.reminders.add(reminder)

        api.commit()
        counter += 1
        progress.update(task_id=task, advance=1)

    return counter
