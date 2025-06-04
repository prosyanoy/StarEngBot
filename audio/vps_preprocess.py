from __future__ import annotations

import asyncio
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional

project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import select
from backend.deps import get_session

from bot.models import Word
from db import init_db

# ────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent
MODELS_DIR = "srv/audio/models"
FEATURES_NPZ = BASE_DIR / "features.npz"  # pre‑computed features
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:pass@localhost:5432/english",
)

_filename_re = re.compile(r"^([a-z][a-z0-9]*?)(\d+)$", re.ASCII)

def _collect_audio_counts() -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for ogg in MODELS_DIR.glob("*.ogg"):
        m = _filename_re.match(ogg.stem)
        if not m:
            continue  # пропускаем странные имена
        word, idx = m.groups()
        counts[word] = max(counts[word], int(idx) + 1)
    return counts

async def update_db_with_counts() -> None:
    await init_db()
    # собираем данные в пуле потоков (чтение файлов – I/O)
    counts = await asyncio.to_thread(_collect_audio_counts)

    async with get_session() as session:
        for word, max_count in counts.items():
            stmt = select(Word).where(Word.english_word == word)
            obj: Optional[Word] = await session.scalar(stmt)
            if obj:
                if obj.audio is None or obj.audio < max_count:
                    obj.audio = max_count
            else:
                session.add(Word(english_word=word, audio=max_count))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(update_db_with_counts())
