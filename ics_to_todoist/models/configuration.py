import os
import re
from zoneinfo import ZoneInfo

from pydantic import BaseModel, validator

from .reminder_time import ReminderTime


class Configuration(BaseModel):
    """Configuration"""
    relevant_names: str | None
    target_project: str
    default_reminder: bool = False
    timezone: str = 'UTC'
    reminder_times: list[ReminderTime]
    todoist_api_key: str = ''
    only_future_events: bool = True

    @property
    def zoneinfo(self) -> ZoneInfo:
        """Get the timezone as a ZoneInfo object"""
        return ZoneInfo(self.timezone)

    @property
    def relevant_names_regex(self) -> re.Pattern:
        """Get relevant names as a compiled regex pattern"""
        return re.compile(self.relevant_names)

    @validator('todoist_api_key', always=True, pre=True)
    def validate_todoist_api_key(cls, value: str) -> str:  # pylint: disable=no-self-argument
        """Prefill todoist_api_key if not provided directly from TODOIST_API_KEY environment variable"""
        if not value:
            value = os.getenv('TODOIST_API_KEY', '')
        if not value:
            raise ValueError('TODOIST_API_KEY environment variable has to be set or the todoist_api_key field has to be provided in the configuration file')
        return value
