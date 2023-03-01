from pymongo import MongoClient
from pymongo.database import Database
import pymongo.errors as errors
from pymongo.collection import Collection
import sys
import os

try:
    uri = os.environ.get('MONGO_URI', None)
    if not uri:
        raise ValueError('MONGO_URI not set')
    client = MongoClient(uri)
except errors.ConnectionFailure as e:
    print(e)
    sys.exit(1)

def get_db() -> Database:
    return client.news

def get_collection(collection_name: str) -> Collection:
    return get_db()[collection_name]

