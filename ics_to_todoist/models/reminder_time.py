from pydantic import BaseModel


class ReminderTime(BaseModel):
    """ Reminder time"""
    hour: int | None
    minute: int | None
    second: int | None
    day_offset: int | None
    hour_offset: int | None
    minute_offset: int | None
    second_offset: int | None
