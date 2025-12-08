from typing import Type

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_async_session
from backend.app.core.security import decode_token
from backend.app.models import User

security = HTTPBearer()


async def get_current_user(token: str = Depends(security), db: AsyncSession = Depends(get_async_session)) -> Type[User]:
    credentials = token.credentials

    try:
        payload = decode_token(credentials)

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Token payload missing 'sub'")

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid user ID inside token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
