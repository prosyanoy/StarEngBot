from __future__ import annotations

import asyncio
import shutil
from collections import defaultdict
from pathlib import Path
import numpy as np
from sqlalchemy import select

from audio.analyze import analyse
from db import init_db
from bot.models import Word

# ── Configuration ────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"         # исходные подпапки с OGG
TARGET_DIR = BASE_DIR / "models"       # куда копируем переименованные файлы
TARGET_DIR.mkdir(exist_ok=True)
FEATURES_FILE = BASE_DIR / "features.npz"

async def process_subdir(subdir: Path) -> tuple[dict[str, int], list[tuple[str, np.ndarray]]]:
    """Асинхронно обрабатывает одну подпапку *subdir*.

    * копирует файлы в TARGET_DIR,
    * извлекает признаки (в to_thread),
    * возвращает (word → count) и список (имя_файла, features).
    """
    counts: dict[str, int] = defaultdict(int)
    features: list[tuple[str, np.ndarray]] = []

    for f in sorted(subdir.glob("*.ogg")):
        name = f.stem.lower()
        word = ''.join([i for i in name if i.isalpha()])
        if word == "":
            continue
        idx = counts[word]
        new_name = f"{word}_{idx}.ogg"
        dest = TARGET_DIR / new_name

        # I/O операции в отдельном потоке, чтобы не блокировать event‑loop
        await asyncio.to_thread(shutil.copy2, f, dest)

        # Извлечение MFCC также в другом потоке
        feat = await asyncio.to_thread(analyse, dest)
        features.append((new_name, feat))

        counts[word] += 1

    return counts, features

async def main() -> None:
    subdirs = [d for d in sorted(MODEL_DIR.iterdir()) if d.is_dir()]
    if not subdirs:
        print("No sub‑directories found in", MODEL_DIR)
        return

    # Параллельно обрабатываем все папки (по умолч. неограниченное число задач).
    results = await asyncio.gather(*(process_subdir(sd) for sd in subdirs))

    # ───── агрегируем результаты ──────────────────────────────────
    total_counts: dict[str, int] = defaultdict(int)
    all_features: dict[str, np.ndarray] = {}

    for counts, feats in results:
        for w, c in counts.items():
            total_counts[w] += c
        for name, feat in feats:
            all_features[name] = feat.astype(np.float32)

    # ───── сохраняем feature‑банк ─────────────────────────────────
    np.savez_compressed(FEATURES_FILE, **all_features)
    print("Saved", FEATURES_FILE.relative_to(BASE_DIR))

    # ───── обновляем БД ───────────────────────────────────────────
    await init_db()

    from db import async_session_maker

    async with async_session_maker() as session:
        for word, cnt in total_counts.items():
            stmt = select(Word).where(Word.english_word == word)
            obj = await session.scalar(stmt)
            if obj:
                obj.audio = cnt
            else:
                obj = Word(english_word=word, audio=cnt)
                session.add(obj)
        await session.commit()
    print("Database updated:", len(total_counts), "words")

if __name__ == "__main__":
    asyncio.run(main())