from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    uid: str
    name: str
    description: str
    begin: datetime
    end: datetime
    location: str
    precision: str

