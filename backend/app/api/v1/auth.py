from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import UserAlreadyExists
from app.schemas.auth import RegisterRequest, TokenResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Register ───────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account."""
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_by_email(request.email)
    if existing_user:
        raise UserAlreadyExists(request.email)

    hashed = hash_password(request.password)
    user = await user_repo.create(
        email=request.email,
        hashed_password=hashed
    )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


# ── Login ──────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # ← changed to form data
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password, returns a JWT token."""
    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(form_data.username)  # ← username field = email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


# ── Me ─────────────────────────────────────────────────────────────

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }