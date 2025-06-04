from typing import List, Literal, Union, Optional
from pydantic import BaseModel, Field

class CollectionResponse(BaseModel):
    id: int
    title: str
    wordsToLearn: int
    wordsToRepeat: int
    icon: Optional[str] = None
    total: int

class Context(BaseModel):
    en: str
    ru: str

class WordResponse(BaseModel):
    id: int
    en: str
    ru: str
    transcription: Optional[str] = None
    contexts: Optional[List[Context]] = None

class WordStatusUpdate(BaseModel):
    status: str  # "known" or "learn"

class Task(BaseModel):
    id: str


# ───────── Translation ─────────
class TranslationTask(Task):
    kind: Literal["translation"] = "translation"

    type: Literal["eng-ru", "ru-eng", "audio-ru"]
    audio: Optional[str] = None          # only for audio-ru
    variants: List[str]
    word: str                            # prompt shown to the learner
    correct: int                         # index in variants
    attempts: int                        # by CEFR


# ───────── Pronunciation ─────────
class PronunciationTask(Task):
    kind: Literal["pronunciation"] = "pronunciation"

    # the word to pronounce + link to audio reference
    en: str
    ru: str

# ───────── Spelling ─────────
class SpellingTask(Task):
    kind: Literal["spelling"] = "spelling"

    en: str
    ru: str
    mistakes: int                        # CEFR-dependent number of typos


# ───────── Matching ─────────
class Pair(BaseModel):
    en: str
    ru: str

class ContextTask(Task):
    kind: Literal["context"] = "context"
    level: Literal["A", "B", "C"]

    en: str
    ru: str


class MatchingTask(Task):
    kind: Literal["matching"] = "matching"
    mistakes: int

    pairs: List[Pair]


# ───────── Discriminated-union list ─────────
TaskUnion = Union[
    TranslationTask,
    PronunciationTask,
    SpellingTask,
    ContextTask,
    MatchingTask,
]

TasksResponse = List[TaskUnion]