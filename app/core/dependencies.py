from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    logger.info("=== Token Validation Process Started ===")
    try:
        if token:
            logger.info("Found token in request header")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            if email:
                logger.info(f"Email from header token: {email}")
        else:
            logger.info("No token in request header")
            email = None
    except JWTError as e:
        logger.error(f"Error decoding header token: {str(e)}")
        email = None
    current_time = datetime.utcnow()
    user = db.query(User).filter(
        User.token_expires > current_time
    ).first()
    if not user:
        logger.error("No user found with valid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Found authenticated user: {user.email}")
    logger.info("=== Token Validation Process Completed ===")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user 