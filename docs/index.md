# Getting Started

ics-to-todoist is a simple command line utility that reads an `.ics` file and submits the events it contains to Todoist. This is great if you would like to
collect a list of events as to-dos in Todoist.

## Requirements

The tool needs Python >= 3.10 to run. It has been tested with Python 3.10 and 3.11.

## Installation

The easiest way to install and use this package is through [pipx](https://pypa.github.io/pipx/).

Make sure pipx is installed on your system. You can check this by running the `pipx --version` command.  
Once that's in place, you can install `ics-to-todoist` by running the following command in your terminal:

```bash
pipx install ics-to-todoist
```

## Usage

**Step 1**

- You'll need to provide an API key to the tool to interact with Todoist.
  To do so, visit the <a href="https://todoist.com/app/today" target="_blank">Todoist Website</a>
- Click on your initials in the upper right hand corner.
- Click on `Integrations`.
- In the pop-up, scroll down to the bottom to the sectin `API token`.
- Click on `Copy to clipboard` to copy your token

**Step 2**

You can provide the token you generated in **Step 1** to the tool in 2 ways:

- **as an environment variable (preferred):** create a new environment variable called `TODOIST_API_KEY` and set it to the value of the token you got in **Step
  1**.
- **in the config file:** you can use the config file to provide the api key. This is useful if you use multiple Todoist accounts. Just make sure to not share
  the
  config file with anybody you would not share your password with.

** Step 3**

Create a config file for your upload. For more details, check out [this section](configuration.md).

** Step 4**

Run the tool like this:

```bash
ics-to-todoist <ICS_FILE> --config-path <CONFIG_FILE>
```

Replace `<ICS_FILE>` with the path of your `.ics` file and `<CONFIG_FILE>` with the path of your configuration file.

## Privacy Policy

This site does not collect any personal data about you. It does not use cookies, tracking or anything similar. The sole purpose of this site is to provide a
documentation for the `ics-to-todoist` package. For more details, please, visit the
<a href="https://www.iubenda.com/privacy-policy/8008630" target="_blank">Privacy Policy</a> page.

## Imprint

The imprint required by the German Telemediengesetz is available here: <a href="https://gaborschulz.com/imprint/index.html" target="_blank">Imprint</a>