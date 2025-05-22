from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from starlette.requests import Request

from backend.models import TokenData, Token
from bot.models import User
from bot.config import SECRET_KEY
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

router = APIRouter(prefix="/auth", tags=["Auth"])

# Authentication dependency
async def get_current_user(request: Request, db: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise credentials_exception

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id: int = int(payload.get("sub"))
        if telegram_id is None:
            raise credentials_exception
        token_data = TokenData(telegram_id=telegram_id)
    except jwt.PyJWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.telegram_id == token_data.telegram_id))
    user = result.scalars().first()

    if user is None:
        # Create user if not exists
        user = User(telegram_id=token_data.telegram_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# Authenticate using Telegram data
@router.post("/", response_model=Token)
async def authenticate(telegram_id: int, db: AsyncSession = Depends(get_session)):
    # In a real app, you would verify the Telegram data with Telegram servers
    # For simplicity, we're just creating a token with the telegram_id

    # Get or create user
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user is None:
        user = User(telegram_id=telegram_id)
        db.add(user)
        await db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.telegram_id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Helper function to create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
