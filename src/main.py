from typing import Awaitable
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

async def main() -> Awaitable[list[Article]]:
    config = Config().from_disk(ROOT_DIR / 'base.cfg')
    resolved = registry.resolve(config)
    async def wrapper(engine):
        try:
            articles = await engine.run()
            return articles
        except Exception as e:
            logger.error(f'Engine {engine} failed with error {e}')
    results = await aiometer.run_all([functools.partial(wrapper, engine) for engine in resolved.values()])
    results = filter(None, results)
    return list(itertools.chain.from_iterable(results))

if __name__ == "__main__":
    asyncio.run(main())
