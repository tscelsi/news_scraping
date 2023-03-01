import pytest
from src.engine import Engine

@pytest.mark.asyncio
async def test_engine_e2e():
    engine = Engine("templates/newscomau.cfg")
    await engine.run()
