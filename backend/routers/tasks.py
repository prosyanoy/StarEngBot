import asyncio
import math, random
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.deps import get_session
from bot.models import AddedWord, Word, Translation, User
from backend.auth import get_current_user         # JWT → User
from backend.models import TranslationTask, TasksResponse, SpellingTask, PronunciationTask, Pair, MatchingTask, \
    ContextTask

from bot.ai import Sentences, get_context_sentences

router = APIRouter(prefix="/tasks", tags=["tasks"])

CEFR_ATTEMPTS = {"A": 3, "B": 2, "C": 1, None: 3}

async def build_task(idx: int, row, cefr) -> ContextTask:
    """
    Wrap one OpenAI request.  Runs concurrently thanks to create_task().
    """
    res: Sentences = await get_context_sentences(
        row.word.english_word,
        row.translation.translation,
        cefr,
    )
    if cefr is None:
        cefr = "A"
    return ContextTask(id=f"t{idx}", en=res.en, ru=res.ru, level=cefr)

def mix_variants(correct: str, distractors: list[str]) -> tuple[list[str], int]:
    need = 4
    if len(distractors) < need:
        raise ValueError("distractor pool too small")

    opts = random.sample(distractors, k=need) + [correct]
    random.shuffle(opts)
    return opts, opts.index(correct)

# ---------- endpoint ----------
@router.get("/{collection_id}", response_model=TasksResponse)
async def translation_tasks(
    collection_id: int,
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
            AddedWord.collection_id == collection_id,
        )
    )
    rows: list[AddedWord] = (await db.execute(rows_stmt)).scalars().all()
    if len(rows) != len(set(word_ids)):
        raise HTTPException(404, detail="Some word_ids not found for user")

    pool_ru = list({r.translation.translation for r in rows})  # unique set → list
    pool_eng = list({r.word.english_word for r in rows})

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

    tr_tasks: list[TranslationTask] = []
    t_id = 1

    n = len(rows)
    print("audio: ")
    print(rows[0].word.audio)
    # 1) ── TranslationTask
    # ru-eng task
    for r in rows:
        variants, correct = mix_variants(
            r.word.english_word,
            safe_pool(r.word.english_word, pool_eng)
        )
        tr_tasks.append(
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
        tr_tasks.append(
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
        tr_tasks.append(
            TranslationTask(
                id=f"t{t_id}", type="eng-ru", word=r.word.english_word,
                variants=variants, correct=correct, attempts=attempts
            )
        )
        t_id += 1

    random.shuffle(tr_tasks)

    # 2) ── SpellingTask
    sp_tasks: list[SpellingTask] = []
    for r in rows:
        typo_limit = 1 if user.cefr == "A" else 0
        sp_tasks.append(
            SpellingTask(
                id=f"t{t_id}",
                en=r.word.english_word,
                ru=r.translation.translation,
                mistakes=typo_limit,
            )
        )
        t_id += 1
    random.shuffle(sp_tasks)

    # 3) ── PronunciationTask
    pr_tasks: list[PronunciationTask] = []
    for r in audio_candidates:
        if not r.word.audio:
            continue
        pr_tasks.append(
            PronunciationTask(
                id=f"t{t_id}",
                en=r.word.english_word,
                ru=r.translation.translation,
            )
        )
        t_id += 1
        # second card: Russian prompt (same audio)
        pr_tasks.append(
            PronunciationTask(
                id=f"t{t_id}",
                en=r.word.english_word,
                ru=r.translation.translation,
            )
        )
        t_id += 1
    random.shuffle(pr_tasks)

    created_tasks = [
        asyncio.create_task(build_task(idx, row, user.cefr))
        for idx, row in enumerate(rows, start=t_id)
    ]

    t_id += len(rows)

    cx_tasks: list[ContextTask] = await asyncio.gather(*created_tasks)

    random.shuffle(cx_tasks)

    tasks = tr_tasks + sp_tasks + pr_tasks + cx_tasks

    # 4) ── MatchingTask
    mistakes = 2
    if user.cefr == "B":
        mistakes = 1
    elif user.cefr == "C":
        mistakes = 0

    pairs = [Pair(en=r.word.english_word, ru=r.translation.translation) for r in rows]
    tasks.append(MatchingTask(id=f"t{t_id}", pairs=pairs, mistakes=mistakes))
    t_id += 1

    return tasks
