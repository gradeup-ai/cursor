from typing import List, Optional
from datetime import datetime
from models.base import Vacancy, VacancyCreate
from services.sheets_service import GoogleSheetsService

class VacancyService:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        
    async def create_vacancy(self, vacancy: VacancyCreate) -> Vacancy:
        # Получаем текущие вакансии
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # Создаем заголовки, если таблица пуста
            headers = ["ID", "Название", "Уровень", "Hard Skills", "Soft Skills", "Задачи", "Инструменты", "Дата создания"]
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_service.spreadsheet_id,
                range='Вакансии!A1:H1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            values = [headers]
        
        # Создаем новую вакансию
        new_vacancy = Vacancy(
            id=str(len(values)),
            title=vacancy.title,
            level=vacancy.level,
            hard_skills=vacancy.hard_skills,
            soft_skills=vacancy.soft_skills,
            tasks=vacancy.tasks,
            tools=vacancy.tools,
            created_at=datetime.now()
        )
        
        # Подготавливаем данные для записи
        row_data = [
            new_vacancy.id,
            new_vacancy.title,
            new_vacancy.level,
            ",".join(new_vacancy.hard_skills),
            ",".join(new_vacancy.soft_skills),
            ",".join(new_vacancy.tasks),
            ",".join(new_vacancy.tools),
            str(new_vacancy.created_at)
        ]
        
        # Добавляем вакансию в таблицу
        self.sheets_service.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H',
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        return new_vacancy
        
    async def get_vacancy(self, vacancy_id: str) -> Optional[Vacancy]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return None
            
        for row in values[1:]:  # Пропускаем заголовки
            if row[0] == vacancy_id:
                return Vacancy(
                    id=row[0],
                    title=row[1],
                    level=row[2],
                    hard_skills=row[3].split(",") if row[3] else [],
                    soft_skills=row[4].split(",") if row[4] else [],
                    tasks=row[5].split(",") if row[5] else [],
                    tools=row[6].split(",") if row[6] else [],
                    created_at=datetime.fromisoformat(row[7])
                )
        return None
        
    async def get_vacancies(self) -> List[Vacancy]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return []
            
        vacancies = []
        for row in values[1:]:  # Пропускаем заголовки
            vacancy = Vacancy(
                id=row[0],
                title=row[1],
                level=row[2],
                hard_skills=row[3].split(",") if row[3] else [],
                soft_skills=row[4].split(",") if row[4] else [],
                tasks=row[5].split(",") if row[5] else [],
                tools=row[6].split(",") if row[6] else [],
                created_at=datetime.fromisoformat(row[7])
            )
            vacancies.append(vacancy)
        return vacancies
        
    async def update_vacancy(self, vacancy_id: str, vacancy: VacancyCreate) -> Optional[Vacancy]:
        # Получаем текущие вакансии
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        # Ищем вакансию для обновления
        for i, row in enumerate(values[1:], start=2):  # start=2 потому что первая строка - заголовки
            if row[0] == vacancy_id:
                updated_vacancy = Vacancy(
                    id=vacancy_id,
                    title=vacancy.title,
                    level=vacancy.level,
                    hard_skills=vacancy.hard_skills,
                    soft_skills=vacancy.soft_skills,
                    tasks=vacancy.tasks,
                    tools=vacancy.tools,
                    created_at=datetime.fromisoformat(row[7])
                )
                
                # Подготавливаем данные для обновления
                row_data = [
                    updated_vacancy.id,
                    updated_vacancy.title,
                    updated_vacancy.level,
                    ",".join(updated_vacancy.hard_skills),
                    ",".join(updated_vacancy.soft_skills),
                    ",".join(updated_vacancy.tasks),
                    ",".join(updated_vacancy.tools),
                    str(updated_vacancy.created_at)
                ]
                
                # Обновляем вакансию в таблице
                self.sheets_service.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Вакансии!A{i}:H{i}',
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
                
                return updated_vacancy
        return None
        
    async def delete_vacancy(self, vacancy_id: str) -> bool:
        # Получаем текущие вакансии
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Вакансии!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return False
            
        # Ищем вакансию для удаления
        for i, row in enumerate(values[1:], start=2):
            if row[0] == vacancy_id:
                # Удаляем строку с вакансией
                self.sheets_service.service.spreadsheets().values().clear(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Вакансии!A{i}:H{i}'
                ).execute()
                return True
        return False 