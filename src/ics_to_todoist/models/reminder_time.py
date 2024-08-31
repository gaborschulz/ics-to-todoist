from pydantic import BaseModel, Field


class ReminderTime(BaseModel):
    """ Reminder time"""
    hour: int | None = None
    minute: int | None = None
    second: int | None = None
    day_offset: int | None = Field(alias='days', default=None)
    hour_offset: int | None = Field(alias='hours', default=None)
    minute_offset: int | None = Field(alias='minutes', default=None)
    second_offset: int | None = Field(alias='seconds', default=None)

    class Config:
        # pylint: disable=missing-class-docstring,too-few-public-methods
        populate_by_name = True

    @property
    def datetime_components(self) -> dict[str, int]:
        """ Get components for the datetime initializer """
        return self.model_dump(include={'hour', 'minute', 'second'}, exclude_unset=True)

    @property
    def has_datetime_components(self):
        """ Check if datetime components are available """
        return self.hour is not None or self.minute is not None or self.second is not None

    @property
    def timedelta_components(self):
        """ Get components for the timedelta initializer """
        return self.model_dump(include={'day_offset', 'hour_offset', 'minute_offset', 'second_offset'}, by_alias=True, exclude_unset=True)
