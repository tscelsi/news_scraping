from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Literal, Any

class Article(BaseModel):
    outlet: Literal[
        # 'theage',
        'news.com.au',
        'guardian',
        'afr',
        'bbc',
        'aljazeera',
        'nytimes',
    ]
    url: str # uuid
    created: str | datetime | None
    modified: str | datetime | None
    published: str | datetime | None
    title: str | None
    body: str
    wordCount: int | None
    tags: list[str] | None
    extra: Any
    author: list[str] | None

class DBArticle(Article):
    id: str = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )

    @validator('id', pre=True)
    def _set_id(cls, v):
        """potential ObjectId cast to string"""
        return str(v)
