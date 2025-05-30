# api/learning.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, asc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from backend.auth import get_current_user
from backend.deps import get_session
from backend.models import WordResponse, Context
from bot.models import AddedWord, Translation

learning_router = APIRouter(prefix="/learning", tags=["learning"])
repeat_router   = APIRouter(prefix="/repeat",   tags=["repeat"])


# ───────────────────────────────── helper ──────────────────────────────────
def build_response(added: AddedWord) -> WordResponse:
    """Convert ORM objects into the API response model."""
    tr: Translation = added.translation
    ctx: Optional[List[Context]] = None
    if tr.example_en or tr.example_ru:
        ctx = [Context(en=tr.example_en or "", ru=tr.example_ru or "")]

    return WordResponse(
        id=added.word.id,
        en=added.word.english_word,
        ru=tr.translation,
        transcription=getattr(added.word, "transcription", None),
        contexts=ctx
    )


# ───────────────────────────────── endpoints ───────────────────────────────
@learning_router.get("/{collection_id}", response_model=List[WordResponse])
async def get_learning_words(
    collection_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Return ≤5 words from *collection_id* whose next_repeat is **NULL**.
    """
    stmt = (
        select(AddedWord)
        .where(
            AddedWord.collection_id == collection_id,
            AddedWord.next_repeat.is_(None),
        )
        .join(AddedWord.word)
        .join(AddedWord.translation)
        .limit(5)
    )

    result = (await db.execute(stmt)).scalars().all()

    if not result:
        raise HTTPException(status_code=404, detail="No words to learn")

    return [build_response(a) for a in result]


@repeat_router.get("/{collection_id}", response_model=List[WordResponse])
async def get_repeat_words(
    collection_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Return ≤5 earliest-due words (next_repeat ≤ NOW()) from *collection_id*.
    """
    now = datetime.now(tz=timezone.utc)

    stmt = (
        select(AddedWord)
        .where(
            AddedWord.collection_id == collection_id,
            AddedWord.next_repeat.is_not(None),
            AddedWord.next_repeat <= now,
        )
        .order_by(asc(AddedWord.next_repeat))
        .join(AddedWord.word)
        .join(AddedWord.translation)
        .limit(5)
    )

    result = (await db.execute(stmt)).scalars().all()

    if not result:
        raise HTTPException(status_code=404, detail="No words to repeat")

    return [build_response(a) for a in result]
