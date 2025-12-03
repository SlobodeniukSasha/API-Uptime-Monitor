from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.auth.utils import get_user_by_email, create_user, verify_password, get_user_by_id
from backend.app.core.security import create_access_token, create_refresh_token, decode_token
from backend.app.schemas.user import UserCreate, UserLogin


class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate):
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = await create_user(
            db,
            user_data.email,
            user_data.password,
            user_data.full_name
        )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id
        }

    @staticmethod
    async def login_user(db: AsyncSession, login_data: UserLogin):
        user = await get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id
        }

    @staticmethod
    async def refresh_tokens(refresh_token: str):
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            user_id = payload.get("sub")

            access_token = create_access_token({"sub": user_id})
            new_refresh_token = create_refresh_token({"sub": user_id})

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

    @staticmethod
    async def logout_user(db: AsyncSession, access_token):
        """
        Базовая реализация logout
        В production нужно добавлять токен в blacklist
        """
        try:
            user_id = await decode_token(access_token).get("sub")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            user = await get_user_by_id(db, user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
