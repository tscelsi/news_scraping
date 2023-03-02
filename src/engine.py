import logging
import sys
from dotenv import load_dotenv
load_dotenv()
from consts import ROOT_DIR 
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Engine:
    def __init__(
        self,
        config_path: str,
        debug: bool = False
    ):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        try:
            self.config = Config().from_disk(ROOT_DIR / config_path)
        except FileNotFoundError:
            print("Config file not found. The path should point from the root directory to the config file.")
            sys.exit(1)
        # import module containing list_articles and get_article
        logger.debug(f'Importing module scrapers.{self.config["globals"]["module"]}')
        _module = importlib.import_module(
            'scrapers.' + self.config['globals']['module'])
        self._db = db.get_db()
        self._list_articles: Callable[[
            httpx.AsyncClient, Any], Awaitable[list[str]]] = _module.list_articles
        self._get_article: Callable[[
            httpx.AsyncClient, str], Awaitable[Article]] = _module.get_article

    async def run(self):
        async with httpx.AsyncClient() as client:
            logger.info('Getting article urls...')
            article_urls = await self._list_articles(client, **self.config['lister_args'])  # this may raise, we want it to. We can't continue without it.
            logger.info(f'Got {len(article_urls)} article urls. Beginning article text retrieval...')
            logger.debug(article_urls)
            jobs = [functools.partial(self._get_article, client, url)
                    for url in article_urls]
            articles = await aiometer.run_all(
                jobs,
                max_at_once=self.config['globals']['max_at_once'],
                max_per_second=self.config['globals']['max_per_second']
            )
            articles = [x for x in filter(lambda x: x is not None, articles)]
            logger.info(f'Found text for {len(articles)} articles. Updating in db...')
            logger.debug(articles)
        db_ops = [
            UpdateOne(
                {'url': article.url, 'outlet': article.outlet},
                {'$set': {**article.dict(), 'url': article.url}},
                upsert=True
            ) for article in articles
        ]
        write_result = self._db.articles.bulk_write(db_ops)
        logger.info(f'updated {write_result.modified_count} articles. inserted {write_result.upserted_count} articles.')
        logger.debug(write_result)
        return articles


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized newspaper scraper.')
    parser.add_argument(
        'config', type=str, help='Path to config file. Relative to the root directory.')
    parser.add_argument(
        '--debug', action='store_true', help='Enable debug logging.'
    )
    args = parser.parse_args()
    engine = Engine(args.config, args.debug)
    asyncio.run(engine.run())
