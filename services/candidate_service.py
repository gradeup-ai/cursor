from typing import List, Optional
from datetime import datetime
from models.base import Candidate, CandidateCreate
from services.sheets_service import GoogleSheetsService

class CandidateService:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        
    async def create_candidate(self, candidate: CandidateCreate) -> Candidate:
        # Получаем текущих кандидатов
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:E'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # Создаем заголовки, если таблица пуста
            headers = ["ID", "Имя", "Email", "Телефон", "Пол", "Дата создания"]
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_service.spreadsheet_id,
                range='Кандидаты!A1:F1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            values = [headers]
        
        # Создаем нового кандидата
        new_candidate = Candidate(
            id=str(len(values)),
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            gender=candidate.gender,
            created_at=datetime.now()
        )
        
        # Подготавливаем данные для записи
        row_data = [
            new_candidate.id,
            new_candidate.name,
            new_candidate.email,
            new_candidate.phone,
            new_candidate.gender,
            str(new_candidate.created_at)
        ]
        
        # Добавляем кандидата в таблицу
        self.sheets_service.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:F',
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        return new_candidate
        
    async def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:F'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return None
            
        for row in values[1:]:  # Пропускаем заголовки
            if row[0] == candidate_id:
                return Candidate(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    phone=row[3],
                    gender=row[4],
                    created_at=datetime.fromisoformat(row[5])
                )
        return None
        
    async def get_candidates(self) -> List[Candidate]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:F'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return []
            
        candidates = []
        for row in values[1:]:  # Пропускаем заголовки
            candidate = Candidate(
                id=row[0],
                name=row[1],
                email=row[2],
                phone=row[3],
                gender=row[4],
                created_at=datetime.fromisoformat(row[5])
            )
            candidates.append(candidate)
        return candidates
        
    async def update_candidate(self, candidate_id: str, candidate: CandidateCreate) -> Optional[Candidate]:
        # Получаем текущих кандидатов
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:F'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        # Ищем кандидата для обновления
        for i, row in enumerate(values[1:], start=2):  # start=2 потому что первая строка - заголовки
            if row[0] == candidate_id:
                updated_candidate = Candidate(
                    id=candidate_id,
                    name=candidate.name,
                    email=candidate.email,
                    phone=candidate.phone,
                    gender=candidate.gender,
                    created_at=datetime.fromisoformat(row[5])
                )
                
                # Подготавливаем данные для обновления
                row_data = [
                    updated_candidate.id,
                    updated_candidate.name,
                    updated_candidate.email,
                    updated_candidate.phone,
                    updated_candidate.gender,
                    str(updated_candidate.created_at)
                ]
                
                # Обновляем кандидата в таблице
                self.sheets_service.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Кандидаты!A{i}:F{i}',
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
                
                return updated_candidate
        return None
        
    async def delete_candidate(self, candidate_id: str) -> bool:
        # Получаем текущих кандидатов
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Кандидаты!A:F'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return False
            
        # Ищем кандидата для удаления
        for i, row in enumerate(values[1:], start=2):
            if row[0] == candidate_id:
                # Удаляем строку с кандидатом
                self.sheets_service.service.spreadsheets().values().clear(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Кандидаты!A{i}:F{i}'
                ).execute()
                return True
        return False 