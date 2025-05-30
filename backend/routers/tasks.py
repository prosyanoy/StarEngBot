import math, random
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.deps import get_session
from bot.models import AddedWord, Word, Translation, User
from backend.auth import get_current_user         # JWT → User
from backend.models import WordResponse, TranslationTask

router = APIRouter(prefix="/translation", tags=["translation"])

CEFR_ATTEMPTS = {"A": 3, "B": 2, "C": 1, None: 3}

def mix_variants(correct: str, distractors: list[str]) -> tuple[list[str], int]:
    need = 4
    if len(distractors) < need:
        raise ValueError("distractor pool too small")

    opts = random.sample(distractors, k=need) + [correct]
    random.shuffle(opts)
    return opts, opts.index(correct)

# ---------- endpoint ----------
@router.get("/", response_model=List[TranslationTask])
async def translation_tasks(
    word_ids: List[int] = Query(..., alias="word_ids"),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Build translation tasks for the *exact* word-ids requested by the client.
    Example:  /translation?word_ids=12&word_ids=15
    """
    if not word_ids:
        raise HTTPException(400, detail="word_ids is required")

    # pull AddedWord rows so we also know next_repeat, audio flag, etc.
    rows_stmt = (
        select(AddedWord)
        .options(
            selectinload(AddedWord.word),  # load r.word without lazy‐load
            selectinload(AddedWord.translation),  # load r.translation without lazy‐load
        )
        .where(
            AddedWord.user_id == user.id,
            AddedWord.word_id.in_(word_ids),
        )
    )
    rows: list[AddedWord] = (await db.execute(rows_stmt)).scalars().all()
    if len(rows) != len(set(word_ids)):
        raise HTTPException(404, detail="Some word_ids not found for user")

    pool_ru = list({r.translation.translation for r in rows})  # unique set → list
    pool_eng = list({r.word.english_word for r in rows})

    # remove the correct value so it's never sampled as a distractor
    def safe_pool(value: str, pool: list[str]) -> list[str]:
        return [p for p in pool if p != value]

    if len(pool_ru) < 5:
        need = 5 - len(pool_ru)
        extra_stmt = (
            select(Translation.translation)
            .join(Word)
            .where(~Translation.translation.in_(pool_ru))  # exclude duplicates
            .order_by(func.random())
            .limit(need)
        )
        extra_ru = (await db.execute(extra_stmt)).scalars().all()
        pool_ru.extend(extra_ru)

    if len(pool_eng) < 5:
        need = 5 - len(pool_eng)
        extra_stmt = (
            select(Word.english_word)
            .where(~Word.english_word.in_(pool_eng))
            .order_by(func.random())
            .limit(need)
        )
        extra_eng = (await db.execute(extra_stmt)).scalars().all()
        pool_eng.extend(extra_eng)

    attempts = CEFR_ATTEMPTS.get(user.cefr)

    tasks: list[TranslationTask] = []
    t_id = 1

    n = len(rows)
    # ru-eng task
    for r in rows:
        variants, correct = mix_variants(
            r.word.english_word,
            safe_pool(r.word.english_word, pool_eng)
        )
        tasks.append(
            TranslationTask(
                id=f"t{t_id}", type="ru-eng", word=r.translation.translation,
                variants=variants, correct=correct, attempts=attempts
            )
        )
        t_id += 1

    # audio-ru
    audio_candidates = [r for r in rows if r.word.audio]
    n_audio = min(math.ceil(n / 2), len(audio_candidates))
    audio_rows = random.sample(audio_candidates, k=n_audio)

    for r in audio_rows:
        variants, correct = mix_variants(
            r.translation.translation,
            safe_pool(r.translation.translation, pool_ru)
        )
        tasks.append(
            TranslationTask(
                id=f"t{t_id}", type="audio-ru", word=r.word.english_word, audio=f"https://audio.stdio.bot/{r.word.english_word}_0.ogg",
                variants=variants, correct=correct, attempts=attempts
            )
        )
        t_id += 1

    # eng-ru
    eng_ru_rows = [r for r in rows if r not in audio_rows][: math.floor(n / 2)]
    for r in eng_ru_rows:
        variants, correct = mix_variants(
            r.translation.translation,
            safe_pool(r.translation.translation, pool_ru)
        )
        tasks.append(
            TranslationTask(
                id=f"t{t_id}", type="eng-ru", word=r.word.english_word,
                variants=variants, correct=correct, attempts=attempts
            )
        )
        t_id += 1

    random.shuffle(tasks)
    return tasks
