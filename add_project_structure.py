from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

from shared import get_project_by_name

TARGET_PROJECT = 'Production Analytics'
SECTIONS = ['Bugfixes', 'In progress', 'Up next', 'Icebox']

def main():
    load_dotenv()
    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, TARGET_PROJECT)
    if project_id:
        for section in SECTIONS:
            result = api.sections.add(section, project_id)
            api.commit()
            print(f'{section} - {result}')
    else:
        print('Project does not exist')


if __name__ == '__main__':
    main()
