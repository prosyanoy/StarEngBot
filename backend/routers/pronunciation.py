from typing import Union
from pathlib import Path
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.deps import get_session
from bot.models import User, CEFR               # CEFR enum is already declared by you
from backend.auth import get_current_user           # same dependency we used earlier

import numpy as np

from audio.analyze import compute_dtw, analyse

FEATURES_NPZ = Path(__file__).resolve().parent.parent.parent/"audio"/"features.npz"

def evaluate_pronunciation(
    word: str,
    webm_path: Union[str, Path],
    features_npz_path: Union[str, Path] = FEATURES_NPZ,
    strategy: str = "min",  # "min" | "mean"
) -> float:
    """Возвращает score.

    * ``word`` – английское слово (регистр игнорируется)
    * ``webm_path`` – путь к записи учащегося (.webm, .wav, …)
    * ``features.npz`` должен содержать ключи ``<word>_<idx>.ogg``
    """
    word = word.lower()
    data = np.load(features_npz_path, allow_pickle=True)
    ref_keys = [k for k in data.files if k.split('_')[0] == word]
    if not ref_keys:
        raise KeyError(f"В архиве {features_npz_path} нет эталонов для слова `{word}`.")
    ref_features = [data[k] for k in ref_keys]

    test_feat = analyse(webm_path)
    costs = [compute_dtw(ref, test_feat)[0] for ref in ref_features]
    score = float(np.mean(costs) if strategy == "mean" else np.min(costs))
    return score

# ─────────────────────────────────────────────────────────────
class PronResp(BaseModel):
    ok: bool
    points: int
    dtw: float

# DTW thresholds table
DTW_LIMIT = {
    CEFR.A: 130,
    CEFR.B: 120,
    CEFR.C: 110,
}

# ─────────────────────────────────────────────────────────────
router = APIRouter(prefix="/pronunciation", tags=["pronunciation"])

@router.post("/{task_id}", response_model=PronResp)
async def check_pronunciation(
    task_id: str,
    word: str = Form(...),
    audio: UploadFile = File(..., description="webm audio recorded in browser"),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Evaluate user's pronunciation with DTW and award 3 % or 0 % according to CEFR level:

    * A-level  – cost < 130 → 3 %; otherwise 0
    * B-level  – cost < 120 → 3 %; otherwise 0
    * C-level  – cost < 110 → 3 %; otherwise 0
    """
    # 1) save the uploaded webm to a temp file
    try:
        tmp = Path(tempfile.mkstemp(suffix=".webm")[1])
        tmp.write_bytes(await audio.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Audio save failed: {e}")

    # 2) run evaluator
    try:
        dtw_cost: float = evaluate_pronunciation(word, tmp)
    finally:
        tmp.unlink(missing_ok=True)  # cleanup

    # 3) decide points by CEFR level
    cefr_level: CEFR = user.cefr or CEFR.A     # default to A if null
    limit = DTW_LIMIT[cefr_level]

    points = 3 if dtw_cost < limit else 0
    return PronResp(ok=points > 0, points=points, dtw=dtw_cost)
