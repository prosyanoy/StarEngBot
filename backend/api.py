from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import lifespan_context

from backend.routers import authentication, collections, learning, tasks, pronunciation, spaced_repeat


def build_api() -> FastAPI:
    app = FastAPI(
        title="StarEng API",
        lifespan=lifespan_context,
        root_path="/stareng/api",
        docs_url="/docs",
        openapi_url="/openapi.json"
    )

    app.include_router(authentication.router)
    app.include_router(collections.router)
    app.include_router(learning.learning_router)
    app.include_router(learning.repeat_router)
    app.include_router(tasks.router)
    app.include_router(pronunciation.router)
    app.include_router(spaced_repeat.router)

    # CORS – adjust domains in prod
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    return app
