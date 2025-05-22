import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta, UTC
from sqlalchemy import select, func
import sys
import os

from backend.auth import get_current_user
from backend.models import WordResponse, WordStatusUpdate, CollectionResponse

# Add the parent directory to the path to import from the bot directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.models import User, Collection, Word, Translation, AddedWord
from bot.config import DATABASE_URL, SECRET_KEY
from db import lifespan, get_session

app = FastAPI(title="StarEng API", lifespan=lifespan)

# CORS middleware to allow requests from Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to your Mini App domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get user's collections
@app.get("/collections", response_model=List[CollectionResponse])
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
        
        response_collections.append(
            CollectionResponse(
                id=col.id,
                name=col.name,
                ready_to_learn=ready_to_learn,
                ready_to_repeat=ready_to_repeat,
            )
        )
    
    return response_collections

# Get words for a specific collection
@app.get("/collections/{collection_id}/words", response_model=List[WordResponse])
async def get_collection_words(
    collection_id: int, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_session)
):
    # Verify the collection belongs to the user
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    )
    collection = result.scalars().first()
    
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Get words for the collection
    result = await db.execute(
        select(AddedWord, Word, Translation)
        .join(Word, AddedWord.word_id == Word.id)
        .join(Translation, AddedWord.translation_id == Translation.id)
        .where(
            AddedWord.collection_id == collection_id,
            AddedWord.user_id == user.id,
            (AddedWord.next_repeat == None) | (AddedWord.next_repeat <= datetime.now())
        )
    )
    rows = result.all()
    
    words = []
    for added_word, word, translation in rows:
        words.append(
            WordResponse(
                id=added_word.id,
                word=word.english_word,
                translation=translation.translation,
                example_en=translation.example_en,
                example_ru=translation.example_ru
            )
        )
    
    return words

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)