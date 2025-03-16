import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Response
from jose import JWTError, jwt
from passlib.context import CryptContext

class SecurityService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
        
    def set_auth_cookie(self, response: Response, token: str) -> None:
        """Устанавливает HttpOnly куку с токеном"""
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=True,  # Только для HTTPS
            samesite="lax",  # Защита от CSRF
            max_age=self.access_token_expire_minutes * 60  # Время жизни в секундах
        )
        
    def remove_auth_cookie(self, response: Response) -> None:
        """Удаляет куку с токеном"""
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
    def verify_token(self, token: str) -> Optional[dict]:
        """Проверяет токен и возвращает данные"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None 