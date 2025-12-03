from typing import Type

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_async_session
from backend.app.core.security import decode_token
from backend.app.models import User

security = HTTPBearer()


async def get_current_user(token: str = Depends(security), db: AsyncSession = Depends(get_async_session)) -> Type[User]:
    try:
        payload = decode_token(token.credentials)
        user_id = int(payload.get("sub"))
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
