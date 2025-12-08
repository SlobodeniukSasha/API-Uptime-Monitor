from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_async_session
from backend.app.schemas.token import TokenSchema, RefreshSchema
from backend.app.schemas.user import UserCreate, UserLogin
from backend.app.services.auth_services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=TokenSchema)
async def register(
        data: UserCreate,
        db: AsyncSession = Depends(get_async_session)
):
    """
    Registering a new user
    """
    result = await AuthService.register_user(db, data)
    return TokenSchema(**result)


@router.post("/login/", response_model=TokenSchema)
async def login(
        data: UserLogin,
        db: AsyncSession = Depends(get_async_session)
):
    """
    User login
    """
    result = await AuthService.login_user(db, data)
    return TokenSchema(**result)


@router.post("/refresh/", response_model=TokenSchema)
async def refresh_token(data: RefreshSchema):
    """
    Refreshing the access token
    """
    result = await AuthService.refresh_tokens(data.refresh_token)
    return TokenSchema(**result)


@router.post("/logout/")
async def logout(
        authorization: str = None,
        db: AsyncSession = Depends(get_async_session),
):
    """
    User Logout
    The client must delete tokens on its side.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    access_token = authorization.replace("Bearer ", "").strip()

    user = await AuthService.logout_user(db, access_token)

    return {"message": f"User {user.full_name} successfully logged out"}
