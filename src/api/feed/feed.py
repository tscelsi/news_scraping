from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..lib.db import Db
from models import DBFeed, OutletConfig
from .repository import FeedRepository, RepositoryException
from main import run_from_list
from ..feedoutlet import list_feedoutlets

router = APIRouter(prefix='/feed', tags=['feed'])
db = Db()


@router.get('', description='List all feeds', response_model=list[DBFeed])
def list_feeds():
    return FeedRepository.list()


@router.get('/{id}', description='Get a feed by id', response_model=DBFeed | None)
def read_feed(id: str):
    try:
        result = FeedRepository.read(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result


@router.post('/{id}/run', description='Gather articles for a particular news feed', status_code=202)
async def run_feed(id: str, background_tasks: BackgroundTasks):
    try:
        outlets = list_feedoutlets(id)
        config = [OutletConfig(**o.dict()).dict() for o in outlets]
    except HTTPException as e:
        raise e
    except KeyError as e:
        raise HTTPException(status_code=400, detail='Invalid feed format')
    # run scrape
    background_tasks.add_task(run_from_list, config)
