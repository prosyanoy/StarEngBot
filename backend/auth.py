import hmac, hashlib, time
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import settings
from backend.deps import get_session
from bot.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

bearer = HTTPBearer(auto_error=False)

def verify_init_data(init_data: str) -> Optional[int]:
    """
    Returns Telegram user_id if init_data signature is valid, else None.
    """
    parts = dict(i.split('=') for i in init_data.split('&'))
    hash_ = parts.pop('hash', None)
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parts.items()))
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return int(parts.get('user', '0')) if h == hash_ else None

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
