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
    ] = Field(description="The outlet the article was scraped from")
    url: str = Field(description="The URL of the article")
    prefix: str = Field(description='The URL prefix where the article was listed')
    created: str | datetime | None = Field(description="The date the article was created")
    modified: str | datetime | None = Field(description="The date the article was last modified")
    published: str | datetime | None = Field(description="The date the article was published")
    title: str | None = Field(description="The title of the article")
    body: str | None = Field(description="The text content of the article")
    wordCount: int | None = Field(description="The number of words in the article")
    tags: list[str] | None = Field(description="Descriptive tags summarising the topics of the article")
    extra: Any | None = Field(description="Any extra data that may be useful")
    author: list[str] | None = Field(description="The author(s) of the article")
    _scrape_time: datetime = Field(description="The time the article was last scraped")

class DBArticle(Article):
    id: str = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )

    @validator('id', pre=True)
    def _set_id(cls, v):
        """potential ObjectId cast to string"""
        return str(v)
