from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import UserService
from ..core.security import ALGORITHM
from ..config import settings
from ..models import User
from ..schemas.user import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 添加调试日志
        print(f"Verifying token: {token}")
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        print(f"Token payload: {payload}")
        
        token_data = TokenPayload(**payload)
        
        # 将字符串ID转换回整数
        user_id = int(token_data.sub)
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise credentials_exception
            
        return user
        
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        raise credentials_exception

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user