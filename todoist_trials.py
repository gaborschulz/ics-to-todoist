from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI

def labelize_string(string: str) -> str:
    return string.lower().replace(' ', '_')

def find_label(label_to_find: str, state):
    if 'labels' in state:
        for label in state['labels']:
            if label_to_find == label['name']:
                return label
    
    return None

def find_section(section_to_find: str, project_id: int, state):
    if 'sections' in state:
        for section in state['sections']:
            if section_to_find == section['name']:
                if project_id:
                    if project_id == section['project_id']:
                        return section
                    else:
                        continue
                else:
                    return section
    
    return None


def main():
    load_dotenv()
    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()
    label = find_label('ios', api.state)
    section = find_section('in progress', 2197434882, api.state)
    pass

if __name__ == "__main__":
    main()