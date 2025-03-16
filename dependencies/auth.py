from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.auth import TokenData
from services.security_service import SecurityService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security_service = SecurityService()

async def get_current_user(request: Request) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Получаем токен из куки
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
        
    # Проверяем токен
    payload = security_service.verify_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    return TokenData(email=email) 