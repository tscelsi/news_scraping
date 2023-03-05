from pydantic import BaseModel, Field, validator

class OutletConfig(BaseModel):
    module: str
    path: str
    max_at_once: int = Field(default=4)
    max_per_second: int = Field(default=4)
    db_uri: str | None = Field(default=None)
    db_must_connect: bool = Field(default=True, const=True)
    debug: bool = Field(default=True, const=True)


class Strategy(BaseModel):
    name: str
    outlets: list[OutletConfig]

class DBStrategy(Strategy):
    id: str = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )

    @validator('id', pre=True)
    def _set_id(cls, v):
        """potential ObjectId cast to string"""
        return str(v)
