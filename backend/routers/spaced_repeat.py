from typing import List
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.deps import get_session
from backend.auth import get_current_user
from bot.models import AddedWord, Word, User
from pydantic import BaseModel

router = APIRouter(prefix="/spaced_repeat", tags=["spaced_repeat"])

class RepeatResult(BaseModel):
    word: str
    score: float

@router.post("/{collection_id}")
async def update_spaced_repeat(
    collection_id: int,
    results: List[RepeatResult],
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    now = datetime.now(tz=timezone.utc)
    for r in results:
        stmt = (
            select(AddedWord)
            .join(Word)
            .where(
                AddedWord.collection_id == collection_id,
                AddedWord.user_id == user.id,
                Word.english_word == r.word,
            )
        )
        row = (await db.execute(stmt)).scalars().first()
        if not row:
            continue
        days = 7 if r.score >= 80 else 3 if r.score >= 50 else 1
        row.next_repeat = now + timedelta(days=days)
    await db.commit()
    return {"status": "ok"}
