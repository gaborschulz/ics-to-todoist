import os
import re
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from .reminder_time import ReminderTime


class Configuration(BaseModel):
    """ Configuration """
    relevant_names: str | None
    target_project: str
    default_reminder: bool = False
    timezone: str = 'UTC'
    reminder_times: list[ReminderTime]
    todoist_api_key: str = os.getenv('TODOIST_API_KEY', '')
    only_future_events: bool = True

    @property
    def zoneinfo(self) -> ZoneInfo:
        """ Get the timezone as a ZoneInfo object"""
        return ZoneInfo(self.timezone)

    @property
    def relevant_names_regex(self) -> re.Pattern:
        """ Get relevant names as a compiled regex pattern """
        return re.compile(self.relevant_names)
