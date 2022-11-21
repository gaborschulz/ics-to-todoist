from pydantic import BaseModel

from .reminder_time import ReminderTime


class Configuration(BaseModel):
    """ Configuration """
    relevant_names: str | None
    target_project: str
    default_reminder: bool = False
    timezone: str | None
    reminder_times: list[ReminderTime]
