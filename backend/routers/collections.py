from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from sqlalchemy import select, func
import sys
import os

from backend.models import WordResponse, CollectionResponse

# Add the parent directory to the path to import from the bot directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.models import User, Collection, Word, Translation, AddedWord
from backend.deps import get_session
from backend.auth import get_current_user

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("/", response_model=List[CollectionResponse])
async def get_collections(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    # Get collections for user
    result = await db.execute(select(Collection).where(Collection.user_id == user.id))
    collections = result.scalars().all()

    response_collections = []
    now = datetime.now()

    for col in collections:
        # Count words ready to learn
        count_result = await db.execute(
            select(func.count(AddedWord.id)).where(
                AddedWord.collection_id == col.id,
                AddedWord.user_id == user.id,
                AddedWord.next_repeat == None
            )
        )
        ready_to_learn = count_result.scalar()

        # Count words ready to repeat
        count_result = await db.execute(
            select(func.count(AddedWord.id)).where(
                AddedWord.collection_id == col.id,
                AddedWord.user_id == user.id,
                AddedWord.next_repeat <= now
            )
        )
        ready_to_repeat = count_result.scalar()

        # Count total words
        count_result = await db.execute(
            select(func.count(AddedWord.id)).where(
                AddedWord.collection_id == col.id,
                AddedWord.user_id == user.id
            )
        )
        total_words = count_result.scalar()

        response_collections.append(
            CollectionResponse(
                id=col.id,
                title=col.name,
                wordsToLearn=ready_to_learn,
                wordsToRepeat=ready_to_repeat,
                total=total_words
            )
        )

    return response_collections