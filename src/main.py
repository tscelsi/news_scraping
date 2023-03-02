import asyncio

from confection import registry, Config
import aiometer

from consts import ROOT_DIR
import engine

async def main():
    config = Config().from_disk(ROOT_DIR / 'base.cfg')
    resolved = registry.resolve(config)
    await aiometer.run_all([engine.run for engine in resolved.values()])

if __name__ == "__main__":
    asyncio.run(main())
