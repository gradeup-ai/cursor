import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.auth import TokenData
from services.sheets_service import GoogleSheetsService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = os.getenv("JWT_ALGORITHM")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.sheets_service = GoogleSheetsService()
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
        
    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
        
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        # Получаем пользователя из Google Sheets
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='HR-менеджеры!A:E'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return None
            
        headers = values[0]
        for row in values[1:]:
            if row[2] == email:  # Проверяем email
                if self.verify_password(password, row[3]):  # Проверяем пароль
                    return {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "hashed_password": row[3],
                        "created_at": row[4]
                    }
        return None
        
    async def get_current_user(self, token: str) -> Optional[TokenData]:
        credentials_exception = ValueError("Could not validate credentials")
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
            
        # Получаем пользователя из Google Sheets
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='HR-менеджеры!A:E'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return None
            
        for row in values[1:]:
            if row[2] == token_data.email:
                return TokenData(email=row[2])
        return None 