from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.core.exceptions import InvalidToken
from app.db.session import get_db
from app.db.repositories.user_repository import UserRepository
from app.models.user import User

# tells FastAPI where to look for the token in the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Runs on every protected endpoint.
    Decodes the JWT, finds the user, returns them.
    Raises 401 if anything is wrong.
    """
    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise InvalidToken()

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise InvalidToken()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated."
        )

    return user