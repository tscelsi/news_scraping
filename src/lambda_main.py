import asyncio
import logging
import json
from api.feedoutlet import list_feedoutlets
from models import OutletConfig
from exceptions import BaseException
from main import run_from_list

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info(event)
    body = json.loads(event['body'])
    id = body.get('id', None)
    if id is None:
        raise BaseException('No feed id provided')
    outlets = list_feedoutlets(id)
    config = [OutletConfig(**o.dict()).dict() for o in outlets]
    asyncio.get_event_loop().run_until_complete(run_from_list(config))
