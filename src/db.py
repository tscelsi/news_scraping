from pymongo import MongoClient
from pymongo.database import Database
import pymongo.errors as errors
from pymongo.collection import Collection
import sys
import os

class Db:
    def __init__(self, uri: str | None = None):
        try:
            uri = uri or os.environ.get('MONGO_URI', None)
            if not uri:
                raise ValueError('Make sure to set the MONGO_URI environment variable, or pass in a database URI with the --db command line argument.')
            self.client = MongoClient(uri)
        except errors.ConnectionFailure as e:
            print(e)
            sys.exit(1)
    
    def get(self) -> Database:
        return self.client.news
    
    def get_collection(self, collection_name: str) -> Collection:
        return self.get()[collection_name]
