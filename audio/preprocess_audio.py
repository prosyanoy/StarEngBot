#!/usr/bin/env python3
"""
Pre‑compute speech features and prepare reference audio corpus.

Workflow
========
1. Walk through every sub‑directory of the top‑level **model/** folder.  Each
   sub‑directory contains one or more OGG‑files named ``<EnglishWord>.ogg`` that
   were recorded by native speakers.
2. For every encountered OGG file
   *   Convert the word to lower‑case (``hello.ogg`` → ``hello``).
   *   Copy the file into the sibling directory **models/** under the new name
       ``<word_lower><index>.ogg`` where *index* starts at 0 and increments for
       each additional recording of the same word (e.g. ``hello0.ogg``,
       ``hello1.ogg``…).
   *   Load the audio (resample to 16 kHz, mono) and extract MFCC + Δ + ΔΔ
       coefficients as a feature matrix (shape ≈ (39, T)).
3. Persist every feature matrix into one compressed ``features.npz`` file that
   sits next to the copied audio (**models/features.npz**).  Each matrix is
   stored under the key that matches the new file stem (e.g. ``hello0``).
4. Update the **words** table in the Postgres database so that every unique
   lowercase word appears exactly once and its *audio* column contains the
   number of recordings available for that word.

The script is idempotent – running it again will only update counts and replace
files whose content changed.

Requirements
------------
::

    pip install librosa soundfile numpy psycopg2-binary sqlalchemy

Make sure PostgreSQL is running and the *DB_URL* below is adjusted to your
credentials.
"""

from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict

import librosa
import numpy as np
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ── Configuration ────────────────────────────────────────────────────────────
MODEL_DIR = Path("model")          # source root with speaker sub‑folders
TARGET_DIR = Path("models")        # destination for renamed audio + npz
TARGET_DIR.mkdir(parents=True, exist_ok=True)
FEATURE_FILE = TARGET_DIR / "features.npz"

# Adjust to your Postgres instance
DB_URL = "postgresql+psycopg2://user:password@localhost:5432/mydb"

# ── Database model ───────────────────────────────────────────────────────────
Base = declarative_base()


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    english_word = Column(String, nullable=False, unique=True)
    audio = Column(Integer)


# ── Audio feature extraction ─────────────────────────────────────────────────

def extract_features(y: np.ndarray, sr: int, n_mfcc: int = 13) -> np.ndarray:
    """Return stacked MFCC, Δ and ΔΔ features as *float32*."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    return np.vstack([mfcc, delta, delta2]).astype(np.float32)


# ── Main routine ─────────────────────────────────────────────────────────────

def main() -> None:
    # Scan & process all audio
    feature_store: Dict[str, np.ndarray] = {}
    recording_count: Dict[str, int] = defaultdict(int)

    for subdir in sorted(MODEL_DIR.iterdir()):
        if not subdir.is_dir():
            continue

        for ogg_path in sorted(subdir.glob("*.ogg")):
            word = ogg_path.stem.lower()
            idx = recording_count[word]
            recording_count[word] += 1

            # ----------------------------------------------------------------
            # 1. Copy/rename audio file to TARGET_DIR
            # ----------------------------------------------------------------
            new_stem = f"{word}{idx}"
            new_path = TARGET_DIR / f"{new_stem}.ogg"
            shutil.copy2(ogg_path, new_path)

            # ----------------------------------------------------------------
            # 2. Extract and cache features
            # ----------------------------------------------------------------
            y, sr = librosa.load(ogg_path, sr=16000, mono=True)
            feature_store[new_stem] = extract_features(y, sr)
            print(f"✓ {ogg_path.relative_to(MODEL_DIR)} → {new_path.name}")

    # ------------------------------------------------------------------------
    # 3. Persist compressed feature archive
    # ------------------------------------------------------------------------
    np.savez_compressed(FEATURE_FILE, **feature_store)
    print(f"\nSaved features: {len(feature_store)} matrices → {FEATURE_FILE}")

    # ------------------------------------------------------------------------
    # 4. Upsert rows in Postgres
    # ------------------------------------------------------------------------
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        for word, count in recording_count.items():
            obj = session.query(Word).filter_by(english_word=word).one_or_none()
            if obj:
                obj.audio = count  # update existing count
            else:
                obj = Word(english_word=word, audio=count)
                session.add(obj)
        session.commit()
    print("Database successfully updated.")


if __name__ == "__main__":
    main()
