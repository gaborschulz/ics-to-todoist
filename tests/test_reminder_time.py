# pylint: disable-all
# type: ignore
import pytest

from ics_to_todoist.models import ReminderTime


@pytest.fixture
def reminder_time_absolute() -> ReminderTime:
    data = ReminderTime(hour=1, minute=2, second=3)
    return data


@pytest.fixture
def reminder_time_absolute_partial() -> ReminderTime:
    data = ReminderTime(minute=2, second=3)
    return data


@pytest.fixture
def reminder_time_relative() -> ReminderTime:
    data = ReminderTime(day_offset=1, hour_offset=2, minute_offset=3, second_offset=4)
    return data


@pytest.fixture
def reminder_time_relative_partial() -> ReminderTime:
    data = ReminderTime(hour_offset=2, second_offset=4)
    return data


def test_has_datetime_components_true(reminder_time_absolute):
    assert reminder_time_absolute.has_datetime_components


def test_has_datetime_components_false(reminder_time_relative):
    assert not reminder_time_relative.has_datetime_components


def test_datetime_components_absolute(reminder_time_absolute):
    result = reminder_time_absolute.datetime_components
    assert result['hour'] == 1
    assert result['minute'] == 2
    assert result['second'] == 3


def test_datetime_components_absolute_partial(reminder_time_absolute_partial):
    result = reminder_time_absolute_partial.datetime_components
    assert 'hour' not in result
    assert result['minute'] == 2
    assert result['second'] == 3


def test_timedelta_components(reminder_time_relative):
    result = reminder_time_relative.timedelta_components
    assert result['days'] == 1
    assert result['hours'] == 2
    assert result['minutes'] == 3
    assert result['seconds'] == 4


def test_timedelta_components_partial(reminder_time_relative_partial):
    result = reminder_time_relative_partial.timedelta_components
    assert 'days' not in result
    assert result['hours'] == 2
    assert 'minutes' not in result
    assert result['seconds'] == 4
