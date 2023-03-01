import sys
from dotenv import load_dotenv
load_dotenv()
from consts import ROOT_DIR, SCRAPER_DIR 
import db
from models import Article
import aiometer
import httpx
from pymongo import UpdateOne
from confection import Config
import functools
import asyncio
from typing import Callable, Awaitable, Any
import importlib
import argparse

class Engine:
    def __init__(
        self,
        config_path: str,
    ):
        try:
            self.config = Config().from_disk(ROOT_DIR / config_path)
        except FileNotFoundError:
            print("Config file not found. The path should point from the root directory to the config file.")
            sys.exit(1)
        # import module containing list_articles and get_article
        _module = importlib.import_module(
            'scrapers.' + self.config['globals']['module'])
        self._db = db.get_db()
        self._list_articles: Callable[[
            httpx.AsyncClient, Any], Awaitable[list[str]]] = _module.list_articles
        self._get_article: Callable[[
            httpx.AsyncClient, str], Awaitable[Article]] = _module.get_article

    async def run(self):
        async with httpx.AsyncClient() as client:
            list_articles = functools.partial(
                self._list_articles, client, **self.config['lister_args'])
            article_urls = await list_articles()  # this may raise, we want it to. We can't continue without it.
            jobs = [functools.partial(self._get_article, client, url)
                    for url in article_urls]
            articles = await aiometer.run_all(
                jobs,
                max_at_once=self.config['globals']['max_at_once'],
                max_per_second=self.config['globals']['max_per_second']
            )
            articles = [x for x in filter(lambda x: x is not None, articles)]
        db_ops = [
            UpdateOne(
                {'url': article.url, 'outlet': article.outlet},
                {'$set': {**article.dict(), 'url': article.url}},
                upsert=True
            ) for article in articles
        ]
        self._db.articles.bulk_write(db_ops)
        return articles


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized newspaper scraper.')
    parser.add_argument(
        'config', type=str, help='Path to config file. Relative to the root directory.')
    args = parser.parse_args()
    engine = Engine(args.config)
    asyncio.run(engine.run())
