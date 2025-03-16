from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from models.auth import Token, TokenData, LoginRequest, RegisterRequest
from services.auth_service import AuthService
from services.sheets_service import GoogleSheetsService
from services.security_service import SecurityService
from dependencies.auth import get_current_user

router = APIRouter()
auth_service = AuthService()
sheets_service = GoogleSheetsService()
security_service = SecurityService()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = security_service.create_access_token(
        data={"sub": user.email}
    )
    
    # Устанавливаем HttpOnly куку
    security_service.set_auth_cookie(response, access_token)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(register_data: RegisterRequest):
    user = await auth_service.create_user(register_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return {"message": "User created successfully"}

@router.post("/logout")
async def logout(
    response: Response = None,
    current_user: TokenData = Depends(get_current_user)
):
    # Удаляем куку с токеном
    security_service.remove_auth_cookie(response)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=TokenData)
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = await auth_service.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_user(register_data: RegisterRequest):
    # Проверяем, существует ли пользователь
    result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=sheets_service.spreadsheet_id,
        range='HR-менеджеры!A:E'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        headers = ["ID", "Имя", "Email", "Пароль", "Дата создания"]
        sheets_service.service.spreadsheets().values().update(
            spreadsheetId=sheets_service.spreadsheet_id,
            range='HR-менеджеры!A1:E1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        values = [headers]
    
    for row in values[1:]:
        if row[2] == register_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Создаем нового пользователя
    hashed_password = auth_service.get_password_hash(register_data.password)
    new_user = [
        str(len(values)),  # ID
        register_data.name,
        register_data.email,
        hashed_password,
        str(datetime.now())
    ]
    
    sheets_service.service.spreadsheets().values().append(
        spreadsheetId=sheets_service.spreadsheet_id,
        range='HR-менеджеры!A:E',
        valueInputOption='RAW',
        body={'values': [new_user]}
    ).execute()
    
    return {"message": "User registered successfully"} 