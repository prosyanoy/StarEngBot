# handlers/__init__.py
from .start import router as start_router
from .words import router as words_router
from .collections import router as collections_router

__all__ = [
    "start_router",
    "words_router",
    "collections_router"
]
