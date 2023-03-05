import sys
from pydantic import BaseSettings, BaseModel
from pymongo import MongoClient
import pymongo.errors as errors
from pymongo.collection import Collection
from bson import ObjectId
from models import Strategy

class MockDeleteResult:
    deleted_count = 1

class MockCollection:
    def __init__(self, model: BaseModel):
        self._model = model
    def find(self, *args, **kwargs):
        model = self._model(name='test', outlets=[])
        return [{**model.dict(), '_id': ObjectId()}]
    def find_one(self, *args, **kwargs):
        model = self._model(name='test', outlets=[])
        _id = args[0].get("_id")
        return {**model.dict(), '_id': _id or ObjectId()}
    def find_one_and_update(self, *args, **kwargs):
        model = self._model(name='test', outlets=[])
        _id = args[0].get("_id")
        return {**model.dict(), '_id': _id or ObjectId()}
    def insert_one(self, *args, **kwargs):
        _obj = args[0]
        return {**Strategy(**_obj).dict(), '_id': ObjectId()}
    def delete_one(self, *args, **kwargs):
        return MockDeleteResult()


class MockDatabase:
    def __init__(self):
        self.strategies = MockCollection(Strategy)

class MockClient:
    def __init__(self, uri: str):
        self._uri = uri
        self.news = MockDatabase()

    @property
    def strategies(self) -> Collection:
        return self.news.strategies


class DbSettings(BaseSettings):
    MONGO_URI: str
    ENV: str
    class Config:
        env_file = '.env'

settings = DbSettings()

try:
    uri = settings.MONGO_URI
    if not uri and settings.ENV != 'test':
        raise ValueError('Make sure to set the MONGO_URI environment variable.')
    if settings.ENV == 'test':
        client = MockClient(uri)
    else:
        client = MongoClient(uri)
except errors.ConnectionFailure as e:
    print(e)
    sys.exit(1)

class Db:
    @property
    def articles(self) -> Collection:
        return client.news.articles

    @property
    def strategies(self) -> Collection:
        return client.news.strategies
