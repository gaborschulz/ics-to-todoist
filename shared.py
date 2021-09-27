import random
import re
from datetime import date
from typing import List, Optional


def get_random_color():
    MIN_COLOR = 30
    MAX_COLOR = 49
    return random.randint(MIN_COLOR, MAX_COLOR)

projects = {}
def get_project_by_name(api, project_name: str):
    if project_name in projects:
        return projects[project_name]

    for project in api.state["projects"]:
        if re.match(project_name, project["name"][0:len(project_name)], flags=re.IGNORECASE):
            projects[project_name] = project
            return project

    return None

def get_or_create_project(api, project_name):
    project = get_project_by_name(api=api, project_name=project_name)
    PARENT_ID = 2197278352
    COLOR_ID = get_random_color()
    if not project:
        project = api.projects.add(
            name=project_name,
            color=COLOR_ID,
            parent_id=PARENT_ID
        )
        api.commit()
        projects[project_name] = project
        
    return project

sections = {}
def get_section_by_name(api, section_name: str, project_id: int):
    if project_id not in sections:
        sections[project_id] = {}

    if section_name in sections[project_id]:
        return sections[project_id][section_name]

    for section in api.state['sections']:
        if section_name == section['name']:
            if project_id:
                if project_id == section['project_id']:
                    sections[project_id][section_name] = section
                    return section
                else:
                    continue
            else:
                return section
    
    return None

def get_or_create_section(api, section_name: str, project_id: int):
    section = get_section_by_name(api=api, section_name=section_name, project_id=project_id)
    if not section:
        section = api.sections.add(name=section_name, project_id=project_id)
        api.commit()
        if project_id not in sections:
            sections[project_id] = {}
        sections[project_id][section_name] = section
        
    return section

labels = {}
def get_label_by_name(api, label_name: str):
    if label_name in labels:
        return labels[label_name]

    for label in api.labels.state["labels"]:
        if re.match(label_name, label["name"][0:len(label_name)], flags=re.IGNORECASE):
            labels[label_name] = label
            return label

    return None

def get_or_create_label(api, label_name: str):
    label = get_label_by_name(api=api, label_name=label_name)
    if not label:
        label = api.labels.add(name=label_name, color=get_random_color())
        api.commit()
        labels[label_name] = label
    
    return label

def add_or_update_task(api, content: str, description: str, project_id: int, target_date: date, section_id: int, labels: List[int], item_id: Optional[int] = None):
    if item_id:
        item = api.items.get_by_id(item_id)
        if item['checked'] == 1:
            return item

        if item:
            update_task(content, description, project_id, target_date, section_id, labels, item)
        else:
            item = create_task(api, content, description, project_id, target_date, section_id, labels)
    else:
        item = create_task(api, content, description, project_id, target_date, section_id, labels)
    api.commit()
    return item

def create_task(api, content, description, project_id, target_date, section_id, labels):
    item = api.items.add(
                content=content, 
                description=description,
                project_id=project_id,
                date_string=target_date.isoformat(),
                section_id=section_id,
                labels=labels
            )
        
    return item

def update_task(content, description, project_id, target_date, section_id, labels, item):
    item.update(
                content=content, 
                description=description,
                labels=labels,
                date_string=target_date.isoformat(),
            )
    if item['project_id'] != project_id:
        item.move(project_id=project_id)
    if item['section_id'] != section_id:
        item.move(section_id=section_id)


def check_task_completed(api, item_id: int) -> bool:
    item = api.items.get_by_id(item_id)
    if item:
        return item['checked'] == 1
    
    return False
