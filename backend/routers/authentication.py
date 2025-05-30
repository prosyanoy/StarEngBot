from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import verify_init_data, create_jwt
from backend.deps import get_session
from bot.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/", summary="Authenticate", response_model=dict)
async def auth(initData: str = Body(..., embed=True), db: AsyncSession = Depends(get_session)):
    telegram_id = verify_init_data(initData)
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="Bad initData")
    # create user row if first login
    user = (await db.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        await db.commit()

    token = create_jwt(telegram_id)
    return {"access_token": token, "token_type": "bearer"}
