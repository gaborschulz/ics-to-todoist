import re

def get_project_by_name(api, target_project: str):
    for project in api.projects.state["projects"]:
        if re.match(target_project, project["name"][0:len(target_project)], flags=re.IGNORECASE):
            return project["id"]

    return None

def get_label_by_name(api, target_label: str):
    for label in api.labels.state["labels"]:
        if re.match(target_label, label["name"][0:len(target_label)], flags=re.IGNORECASE):
            return label['id']

    return None