from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from models.auth import TokenData
from services.livekit_service import LiveKitService
from dependencies.auth import get_current_user

router = APIRouter()
livekit_service = LiveKitService()

@router.post("/rooms")
async def create_room(
    room_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Создает новую комнату для интервью"""
    try:
        room_data = await livekit_service.create_room(room_name)
        return room_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/rooms/{room_name}")
async def delete_room(
    room_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Удаляет комнату"""
    success = await livekit_service.delete_room(room_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return {"message": "Room deleted successfully"}

@router.get("/rooms/{room_name}")
async def get_room_info(
    room_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Получает информацию о комнате"""
    room_info = await livekit_service.get_room_info(room_name)
    if not room_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room_info

@router.get("/rooms")
async def list_rooms(
    current_user: TokenData = Depends(get_current_user)
):
    """Получает список всех активных комнат"""
    return await livekit_service.list_rooms()

@router.post("/rooms/{room_name}/tokens")
async def get_participant_token(
    room_name: str,
    identity: str,
    name: str,
    role: str,
    expires_in: int = 3600,
    current_user: TokenData = Depends(get_current_user)
):
    """Генерирует токен для нового участника"""
    token = await livekit_service.get_participant_token(
        room_name=room_name,
        identity=identity,
        name=name,
        role=role,
        expires_in=expires_in
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return {"token": token} 