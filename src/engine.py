import logging
import sys
from dotenv import load_dotenv
load_dotenv()
from consts import ROOT_DIR 
from db import Db
from models import Article
import aiometer
import httpx
from pymongo import UpdateOne
import catalogue
from confection import registry, Config
import functools
import asyncio
from typing import Callable, Awaitable, Any
import importlib
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

registry.engines = catalogue.create('engine', 'engines', entry_points=True)

@registry.engines.register('engine.v1')
def _factory(module_config_path: str,
        db_uri: str | None = None,
        debug: bool = False):
    return Engine(module_config_path, db_uri, debug)


class Engine:
    def __init__(
        self,
        config_path: str,
        db_uri: str | None = None,
        debug: bool = False
    ):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        try:
            self.config = Config().from_disk(ROOT_DIR / config_path)
        except FileNotFoundError:
            print("Config file not found. The path should point from the root directory to the config file.")
            sys.exit(1)
        self._name = self.config['globals']['module']
        logger.info(f'{self._name};initialising engine...')
        # import module containing list_articles and get_article
        logger.debug(f'{self._name};importing module scrapers.{self.config["globals"]["module"]}')
        _module = importlib.import_module(
            'scrapers.' + self.config['globals']['module'])
        self._db = Db(db_uri)
        self._list_articles: Callable[[
            httpx.AsyncClient, Any], Awaitable[list[str]]] = _module.list_articles
        self._get_article: Callable[[
            httpx.AsyncClient, str], Awaitable[Article]] = _module.get_article

    async def run(self):
        async with httpx.AsyncClient() as client:
            logger.info(f'{self._name};getting article urls...')
            article_urls = await self._list_articles(client, **self.config['lister_args'])  # this may raise, we want it to. We can't continue without it.
            logger.info(f'{self._name};got {len(article_urls)} article urls. Beginning article text retrieval...')
            logger.debug(f'{self._name};{article_urls}')
            jobs = [functools.partial(self._get_article, client, url)
                    for url in article_urls]
            articles = await aiometer.run_all(
                jobs,
                max_at_once=self.config['globals']['max_at_once'],
                max_per_second=self.config['globals']['max_per_second']
            )
            articles = [x for x in filter(lambda x: x is not None, articles)]
            logger.info(f'{self._name};found text for {len(articles)} articles. Updating in db...')
            logger.debug(f'{self._name};{articles}')
        db_ops = [
            UpdateOne(
                {'url': article.url, 'outlet': article.outlet},
                {'$set': {**article.dict(), 'url': article.url}},
                upsert=True
            ) for article in articles
        ]
        write_result = self._db.get_collection('articles').bulk_write(db_ops)
        logger.info(f'{self._name};updated {write_result.modified_count} articles. inserted {write_result.upserted_count} articles.')
        logger.debug(f'{self._name};{write_result}')
        return articles


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized news outlet scraper.')
    parser.add_argument(
        'config', type=str, help='path to config file. This path should be relative to the root directory. For examples, see the templates/ folder.')
    parser.add_argument(
        '--db', dest='db_uri', help='a mongodb connection string.'
    )
    parser.add_argument(
        '--debug', action='store_true', help='enable debug logging.'
    )
    args = parser.parse_args()
    engine = Engine(args.config, db_uri=args.db_uri, debug=args.debug)
    asyncio.run(engine.run())
