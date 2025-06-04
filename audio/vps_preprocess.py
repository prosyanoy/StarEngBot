from __future__ import annotations

import asyncio
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional

project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from bot.models import Word
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

MODELS_DIR = Path("/srv/audio/models")

_filename_re = re.compile(r"^([A-Za-z][A-Za-z0-9]*?)(\d+)$")


def _collect_audio_counts() -> Dict[str, int]:
    """
    Перебираем все .ogg в /srv/audio и считаем
    для каждого слова (в нижнем регистре) max(idx) + 1.
    """
    counts: Dict[str, int] = defaultdict(int)

    # DEBUG: выведите список реально найденных ogg-файлов
    found = list(MODELS_DIR.glob("*.ogg"))
    print(f"DEBUG: Нашли {len(found)} .ogg в {MODELS_DIR}:")
    for p in found:
        print("  ", p.name)

    for ogg_path in found:
        m = _filename_re.match(ogg_path.stem)
        if not m:
            # пропускаем, если имя вида «foo_bar.ogg» или «123.ogg» и т.п.
            print(f"  SKIP (не match): {ogg_path.name}")
            continue

        raw_word, idx_str = m.groups()
        word = raw_word.lower()
        idx = int(idx_str)
        # сохраняем максимум:
        counts[word] = max(counts[word], idx + 1)

    print("DEBUG: counts =", counts)
    return counts


async def update_db_with_counts() -> None:
    from bot.config import DATABASE_URL

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    counts = await asyncio.to_thread(_collect_audio_counts)

    async with AsyncSessionLocal() as session:
        for word, max_count in counts.items():
            stmt = select(Word).where(Word.english_word == word)
            obj: Optional[Word] = await session.scalar(stmt)
            if obj:
                if obj.audio is None or obj.audio < max_count:
                    print(f"  UPDATE word={word!r}: audio {obj.audio} → {max_count}")
                    obj.audio = max_count
            else:
                print(f"  INSERT word={word!r}, audio={max_count}")
                session.add(Word(english_word=word, audio=max_count))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(update_db_with_counts())
