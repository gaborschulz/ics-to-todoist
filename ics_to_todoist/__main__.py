from pathlib import Path

import typer
from ics import Calendar
from rich import print

from models import Event


def load_ics_data(ics_file: str) -> list[Event]:
    """ Load ics file into a list of events"""
    with Path(ics_file).open('r', encoding='utf-8') as fp:
        file_content = fp.read()

    events: list[Event] = []
    calendar = Calendar(file_content)

    for cal_event in calendar.events:
        event = Event(uid=cal_event.uid, name=cal_event.name, description=cal_event.description, begin=cal_event.begin.datetime,
                      end=cal_event.end.datetime, location=cal_event.location, precision=cal_event._begin_precision)
        events.add(event)

    return events


def main(ics_file: str):
    """ Main function """
    print(f'Loading ics file [bold yellow]{ics_file}[/bold yellow]...', end='')
    ics_data = load_ics_data(ics_file=ics_file)
    print('OK')


if __name__ == "__main__":
    typer.run(main)
