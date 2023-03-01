from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class Article(BaseModel):
    outlet: Literal['theage', 'news.com.au']
    url: str # uuid
    created: str | datetime | None
    modified: str | datetime | None
    published: str | datetime | None
    title: str | None
    body: str
    wordCount: int | None
