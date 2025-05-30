# backend/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import lifespan_context   # re-uses same engine

from backend.routers import authentication, collections, learning

def build_api() -> FastAPI:
    app = FastAPI(title="StarEng API", lifespan=lifespan_context)

    app.include_router(authentication.router)
    app.include_router(collections.router)
    app.include_router(learning.learning_router)
    app.include_router(learning.repeat_router)

    # CORS – adjust domains in prod
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
