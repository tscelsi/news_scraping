import asyncio
import logging
import functools

from confection import registry, Config
import aiometer

from consts import ROOT_DIR
import engine

logger = logging.getLogger(__name__)

async def main():
    config = Config().from_disk(ROOT_DIR / 'base.cfg')
    resolved = registry.resolve(config)
    async def wrapper(engine):
        try:
            await engine.run()
        except Exception as e:
            logger.error(f'Engine {engine} failed with error {e}')
    await aiometer.run_all([functools.partial(wrapper, engine) for engine in resolved.values()])

if __name__ == "__main__":
    asyncio.run(main())
