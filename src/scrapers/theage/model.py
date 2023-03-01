from pydantic import BaseModel, Field
from pydantic.fields import ModelField


class TheAgeArticleHeadlines(BaseModel):
    headline: str = Field(__mapping="title")


class TheAgeArticleAsset(BaseModel):
    about: str
    body: str
    headlines: TheAgeArticleHeadlines
    wordCount: int


class TheAgeArticleDates(BaseModel):
    created: str
    firstPublished: str
    imported: str
    modified: str
    published: str
    saved: str


class TheAgeArticleSource(BaseModel):
    id: str
    name: str


class TheAgeArticle(BaseModel):
    @classmethod
    def article_convert_map(cls):
        for fname, f in cls.__fields__.items():
            if issubclass(f.type_, BaseModel):
                res = cls.article_convert_map(f.type_)
                # fill rest
            if '_mapping' in f.field_info.extra:
                {
                    [f.field_info.extra['_mapping']]: f
                }
    assetType: str = Field()
    asset: TheAgeArticleAsset
    categories: list[str]
    dates: TheAgeArticleDates
    id: str
    publicState: str # published or not
    sources: list[TheAgeArticleSource]
    tags: dict
    url: str = Field(__mapping="url") # uuid
