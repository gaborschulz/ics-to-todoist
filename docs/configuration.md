# Config files

Config files are the soul of the tool. These are simple `.toml` files that have the following structure:

```toml
relevant_names = "ABC|DEF|GHI|JKL"
target_project = "Inbox"
default_reminder = false
timezone = "Europe/Berlin"
todoist_api_key = "123"
only_future_events = true

[[reminder_times]]
day_offset = -1
hour_offset = 18

[[reminder_times]]
hour = 5
minute = 45

[[reminder_times]]
hour = 6
minute = 0 
```

## Root

The top section contains general settings. These are the following:

- `relevant_names`: this is a regular expression which will be used to select relevant events from the `.ics` file. This is only applied to the `SUMMARY` field
  in the `.ics` file. If this pattern appears *anywhere* in the name then the event will be added.
- `target_project`: this is a regular expression which will be used to find your project in Todoist. This string has to appear at the beginning of the project's
  name.
- `default_reminder`: if this is set to `true` and there is a time associated with the event in the file then that will be added as a default reminder
- `timezone`: the name of the timezone to use for events in the file. Defaults to UTC.
- `todoist_api_key`: you can provide the Todoist api key here. This is useful if you have different Todoist accounts, and you want to use them in separate
  configurations.
- `only_future_events`: if this is set to `true` then only those events will be submitted to Todoist that have a date in the future.

## Reminder times

You can use as many `[[reminder_times]]` sections as you like to customize the reminder time for your events. Each `[[reminder_times]]` can contain
any combination of the following values (these should be integer values):

- `hour`: the absolute hour component of the reminder time in the configured time zone. If your timezone is set to `Europe/Berlin` and you set this value to 6
  then you will get a reminder at 6:00AM Berlin time.
- `minute`: the absolute minute component of the reminder time.
- `second`: the absolute second component of the reminder time.
- `day_offset`: the relative day component of the reminder time. If you set this to -1 then you will get a reminder 1 day before the event time.
- `hour_offset`: the relative hour component of the reminder time. If you set this to -1 then you will get a reminder 1 hour before the event time.
- `minute_offset`: the relative minute component of the reminder time. If you set this to -1 then you will get a reminder 1 minute before the event time.
- `second_offset`: the relative second component of the reminder time. If you set this to -1 then you will get a reminder 1 second before the event time.