from pathlib import Path

import toml
import typer
from ics import Calendar
from rich import print

from models import Event, Configuration


def load_ics_data(ics_file: str) -> list[Event]:
    """ Load ics file into a list of events"""
    with Path(ics_file).open('r', encoding='utf-8') as fp:
        file_content = fp.read()

    events: list[Event] = []
    calendar = Calendar(file_content)

    for cal_event in calendar.events:
        event = Event(uid=cal_event.uid, name=cal_event.name, description=cal_event.description, begin=cal_event.begin.datetime,
                      end=cal_event.end.datetime, location=cal_event.location, precision=cal_event._begin_precision)
        events.append(event)

    return events


def load_config(config_file: str) -> Configuration:
    """ Load configuration from toml file """
    config_json = toml.load(config_file)
    config = Configuration(**config_json)
    return config


def main(ics_file: str, config_file: str = typer.Option(..., help="Path of the config file (TOML)")):
    """ Main function """
    print(f'Reading .ics file [bold yellow]{ics_file}[/bold yellow]...', end='')
    ics_data = load_ics_data(ics_file=ics_file)
    print('\t\t\t\tOK')
    print(f'Reading configuration from file [bold yellow]{config_file}[/bold yellow]...', end='')
    config = load_config(config_file=config_file)
    print('\tOK')


if __name__ == "__main__":
    typer.run(main)
