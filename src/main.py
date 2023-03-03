from typing import Awaitable
import argparse
import asyncio
import logging
import functools
import itertools

from confection import registry, Config
import aiometer

from consts import ROOT_DIR
from models import Article
import engine

logger = logging.getLogger(__name__)

async def main(config_path: str) -> Awaitable[list[Article]]:
    config = Config().from_disk(ROOT_DIR / config_path)
    resolved = registry.resolve(config)
    async def _wrapper(engine):
        try:
            articles = await engine.run()
            return articles
        except Exception as e:
            logger.error(f'Engine {engine._name} failed with error {e}')
    results = await aiometer.run_all([functools.partial(_wrapper, engine) for engine in resolved.values()])
    results = filter(None, results)
    return list(itertools.chain.from_iterable(results))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized news outlet scraper.')
    parser.add_argument(
        'config', type=str, help='path to config file. This path should be relative to the root directory. For examples, see the templates/ folder.')
    args = parser.parse_args()
    asyncio.run(main(args.config))
