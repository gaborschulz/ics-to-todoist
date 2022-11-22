from pydantic import BaseModel


class Project(BaseModel):
    """ Project model """
    id: str
    name: str
