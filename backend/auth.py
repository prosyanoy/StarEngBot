import hmac, hashlib, time
import json
from operator import itemgetter
from urllib.parse import parse_qs, unquote, parse_qsl
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import settings
from backend.deps import get_session
from bot.config import BOT_TOKEN
from bot.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

bearer = HTTPBearer(auto_error=False)


def _get_secret_key() -> bytes:
    return hmac.new(key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256).digest()


def verify_init_data(init_data: str):
    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError as err:
        raise Exception("invalid init data") from err
    if "hash" not in parsed_data:
        raise Exception("missing hash")
    hash_ = parsed_data.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0)))
    calculated_hash = hmac.new(
        key=_get_secret_key(), msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    if calculated_hash != hash_:
        raise Exception("invalid hash")
    return int(json.loads(parsed_data["user"])["id"])

def create_jwt(telegram_id: int):
    now = datetime.now(tz=timezone.utc)
    return jwt.encode(
        {"sub": str(telegram_id), "exp": now + timedelta(minutes=settings.JWT_EXP_MIN)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )

async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_session),
) -> User:
    if cred is None:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(cred.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        tg_id = int(payload["sub"])
    except JWTError as e:
        print("JWT decode error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    user = (await db.execute(select(User).where(User.telegram_id == tg_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
