from fastapi import APIRouter, Response, HTTPException, BackgroundTasks
from ..lib.db import Db
from models import Strategy, DBStrategy, Article
from .repository import StrategyRepository, RepositoryException
from main import run_from_list

router = APIRouter(prefix='/strategy', tags=['strategy'])
db = Db()


@router.post('',
    description='Create a new strategy',
    response_model=DBStrategy,
    )
def create_strategy(strategy: Strategy) -> DBStrategy:
    result = StrategyRepository.create(strategy)
    return result


@router.get('', description='List all strategies', response_model=list[DBStrategy])
def list_strategies():
    return StrategyRepository.list()


@router.get('/{id}', description='Get a strategy by id', response_model=DBStrategy | None)
def read_strategy(id: str):
    try:
        result = StrategyRepository.read(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result


@router.post('/{id}', description='Update a strategy by id', response_model=DBStrategy | None)
def update_strategy(id: str, strategy: Strategy):
    try:
        result = StrategyRepository.update(id, strategy)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result


@router.delete('/{id}', description='Delete a strategy by id')
def delete_strategy(id: str):
    try:
        _ = StrategyRepository.delete(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.post('/{id}/run', description='Run a strategy by id', status_code=202)
async def run_strategy(id: str, background_tasks: BackgroundTasks):
    try:
        result = read_strategy(id)
        config = result.dict()['outlets']
    except HTTPException as e:
        raise e
    except KeyError as e:
        raise HTTPException(status_code=400, detail='Invalid strategy format')
    # run scrape
    background_tasks.add_task(run_from_list, config)
