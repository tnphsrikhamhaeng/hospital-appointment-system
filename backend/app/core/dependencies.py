import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.utils.security import decode_access_token
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.repositories.user_repository import UserRepository




# ==========================================
# JWT Configuration
# ==========================================

# HTTPBearer ทำหน้าที่ดึง JWT Token
# จาก Authorization Header
#
# Authorization: Bearer <token>
#
# Swagger UI จะมีปุ่ม Authorize
# สำหรับใส่ JWT Token โดยตรง
bearer_scheme = HTTPBearer()


# ==========================================
# Get Current User
# ==========================================


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:

    try:

        # ดึง JWT Token จาก Authorization Header
        token = credentials.credentials

        # ถอดรหัส JWT
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user_repository = UserRepository(db)

        user = user_repository.get_by_id(
            uuid.UUID(user_id),
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user

    # Token ไม่ถูกต้อง
    # เช่น หมดอายุ หรือถูกแก้ไข
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
        
def require_roles(*allowed_roles: UserRoleEnum):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )

        return current_user

    return role_checker