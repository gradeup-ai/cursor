import os
from typing import Dict, List, Optional
from datetime import datetime
from models.base import Notification, NotificationCreate
from services.sheets_service import GoogleSheetsService
from services.email_service import EmailService

class NotificationService:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.email_service = EmailService()
        
    async def create_notification(self, notification: NotificationCreate) -> Notification:
        # Получаем текущие уведомления
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Уведомления!A:G'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # Создаем заголовки, если таблица пуста
            headers = [
                "ID", "ID HR-менеджера", "Тип", "Текст", 
                "Ссылка", "Дата создания", "Статус"
            ]
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_service.spreadsheet_id,
                range='Уведомления!A1:G1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            values = [headers]
        
        # Создаем новое уведомление
        new_notification = Notification(
            id=str(len(values)),
            hr_manager_id=notification.hr_manager_id,
            type=notification.type,
            text=notification.text,
            link=notification.link,
            created_at=datetime.now(),
            status="new"
        )
        
        # Подготавливаем данные для записи
        row_data = [
            new_notification.id,
            new_notification.hr_manager_id,
            new_notification.type,
            new_notification.text,
            new_notification.link or "",
            str(new_notification.created_at),
            new_notification.status
        ]
        
        # Добавляем уведомление в таблицу
        self.sheets_service.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Уведомления!A:G',
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        # Отправляем уведомление по email
        await self._send_notification_email(new_notification)
        
        return new_notification
        
    async def get_notifications(self, hr_manager_id: str) -> List[Notification]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Уведомления!A:G'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return []
            
        notifications = []
        for row in values[1:]:
            if row[1] == hr_manager_id:  # Фильтруем по ID HR-менеджера
                notification = Notification(
                    id=row[0],
                    hr_manager_id=row[1],
                    type=row[2],
                    text=row[3],
                    link=row[4] if row[4] else None,
                    created_at=datetime.fromisoformat(row[5]),
                    status=row[6]
                )
                notifications.append(notification)
        return notifications
        
    async def update_notification_status(self, notification_id: str, status: str) -> Optional[Notification]:
        # Получаем текущие уведомления
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Уведомления!A:G'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        # Ищем уведомление для обновления
        for i, row in enumerate(values[1:], start=2):
            if row[0] == notification_id:
                # Обновляем статус
                self.sheets_service.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Уведомления!G{i}',
                    valueInputOption='RAW',
                    body={'values': [[status]]}
                ).execute()
                
                return Notification(
                    id=row[0],
                    hr_manager_id=row[1],
                    type=row[2],
                    text=row[3],
                    link=row[4] if row[4] else None,
                    created_at=datetime.fromisoformat(row[5]),
                    status=status
                )
        return None
        
    async def _send_notification_email(self, notification: Notification) -> bool:
        # Получаем email HR-менеджера
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='HR-менеджеры!A:C'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return False
            
        hr_email = None
        for row in values[1:]:
            if row[0] == notification.hr_manager_id:
                hr_email = row[2]  # Предполагаем, что email находится в третьем столбце
                break
                
        if not hr_email:
            return False
            
        # Формируем текст письма
        subject = f"Новое уведомление: {notification.type}"
        body = f"""
        Здравствуйте!
        
        У вас новое уведомление:
        {notification.text}
        
        """
        if notification.link:
            body += f"\nСсылка: {notification.link}"
            
        # Отправляем email
        await self.email_service.send_email(
            to_email=hr_email,
            subject=subject,
            body=body
        )
        
        return True 