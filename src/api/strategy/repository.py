from bson import ObjectId
from pymongo.results import DeleteResult
from pymongo import ReturnDocument
from models import Strategy, DBStrategy
from ..lib.db import Db

class RepositoryException(Exception):
    message: str
    def __init__(self, message: str):
        self.message = message


def is_valid_id(id: str):
    try:
        ObjectId(id)
        return True
    except Exception:
        return False

_db = Db()

class StrategyRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def create(strategy: Strategy) -> DBStrategy:
        result = _db.strategies.insert_one(strategy.dict())
        return DBStrategy(**{'_id': result.inserted_id, **strategy.dict()})

    @staticmethod
    def read(id: str) -> DBStrategy:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.strategies.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBStrategy(**result)

    @staticmethod
    def list() -> list[DBStrategy]:
        result = _db.strategies.find()
        return [DBStrategy(**r) for r in result]

    @staticmethod
    def update(id: str, strategy: Strategy) -> DBStrategy:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.strategies.find_one_and_update(
            {'_id': ObjectId(id)}, {'$set': strategy.dict()},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise RepositoryException('Not found')
        return DBStrategy(**result)

    @staticmethod
    def delete(id: str) -> DeleteResult:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.strategies.delete_one({'_id': ObjectId(id)})
        if not result.deleted_count:
            raise RepositoryException('Not found')
        return result
