from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.notification import Notification, NotificationCreate
from models.auth import TokenData
from services.notification_service import NotificationService
from dependencies.auth import get_current_user

router = APIRouter()
notification_service = NotificationService()

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    current_user: TokenData = Depends(get_current_user)
):
    return await notification_service.create_notification(notification)

@router.get("/", response_model=List[Notification])
async def get_notifications(
    current_user: TokenData = Depends(get_current_user)
):
    return await notification_service.get_notifications(current_user.id)

@router.put("/{notification_id}/status")
async def update_notification_status(
    notification_id: str,
    status: str,
    current_user: TokenData = Depends(get_current_user)
):
    notification = await notification_service.update_notification_status(notification_id, status)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification 