import uvicorn
from fastapi import FastAPI
from api.strategy import router as strategy_router
from api.article import router as article_router


def setup():
    app = FastAPI(title="Bite-sized news", version="0.0.1")
    app.include_router(strategy_router)
    app.include_router(article_router)
    return app


if __name__ == "__main__":
    app = setup()
    uvicorn.run('app:setup', port=5000, reload=True, factory=True)
