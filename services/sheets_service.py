import os
from typing import Dict, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

class GoogleSheetsService:
    def __init__(self):
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
    async def initialize_sheets(self):
        """Инициализация структуры таблицы"""
        sheets = [
            {
                "properties": {
                    "title": "Вакансии"
                }
            },
            {
                "properties": {
                    "title": "Кандидаты"
                }
            },
            {
                "properties": {
                    "title": "Интервью"
                }
            },
            {
                "properties": {
                    "title": "Отчеты"
                }
            },
            {
                "properties": {
                    "title": "HR-менеджеры"
                }
            }
        ]
        
        body = {
            "requests": [{"addSheet": sheet} for sheet in sheets]
        }
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        ).execute()
        
        # Инициализация заголовков для каждого листа
        await self._initialize_headers()
        
    async def _initialize_headers(self):
        """Установка заголовков для каждого листа"""
        headers = {
            "Вакансии": [
                ["ID", "Название", "Уровень", "Hard Skills", "Soft Skills", "Задачи", "Инструменты", "Создано", "Обновлено"]
            ],
            "Кандидаты": [
                ["ID", "Имя", "Email", "Телефон", "Пол", "Создано"]
            ],
            "Интервью": [
                ["ID", "ID Кандидата", "ID Вакансии", "Статус", "Начало", "Конец", "URL записи", "Транскрипт", "Вопросы", "Ответы", "Анализ эмоций"]
            ],
            "Отчеты": [
                ["ID", "ID Интервью", "Оценка Hard Skills", "Оценка Soft Skills", "Анализ эмоций", "Вердикт", "Обратная связь", "Создано"]
            ],
            "HR-менеджеры": [
                ["ID", "Имя", "Email", "Пароль (хеш)", "Создано"]
            ]
        }
        
        for sheet_name, header in headers.items():
            range_name = f"{sheet_name}!A1"
            body = {
                "values": header
            }
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
    async def add_vacancy(self, vacancy_data: Dict) -> str:
        """Добавление новой вакансии"""
        values = [[
            vacancy_data["id"],
            vacancy_data["title"],
            vacancy_data["level"],
            ",".join(vacancy_data["hard_skills"]),
            ",".join(vacancy_data["soft_skills"]),
            ",".join(vacancy_data["tasks"]),
            ",".join(vacancy_data["tools"]),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ]]
        
        body = {
            "values": values
        }
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Вакансии!A:I',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return vacancy_data["id"]
        
    async def add_candidate(self, candidate_data: Dict) -> str:
        """Добавление нового кандидата"""
        values = [[
            candidate_data["id"],
            candidate_data["name"],
            candidate_data["email"],
            candidate_data["phone"],
            candidate_data["gender"],
            datetime.now().isoformat()
        ]]
        
        body = {
            "values": values
        }
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Кандидаты!A:F',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return candidate_data["id"]
        
    async def save_interview(self, interview_data: Dict) -> str:
        """Сохранение данных интервью"""
        values = [[
            interview_data["id"],
            interview_data["candidate_id"],
            interview_data["vacancy_id"],
            interview_data["status"],
            interview_data["start_time"],
            interview_data["end_time"],
            interview_data["recording_url"],
            interview_data["transcript"],
            ",".join(interview_data["questions"]),
            ",".join(interview_data["answers"]),
            ",".join(interview_data["emotions_analysis"])
        ]]
        
        body = {
            "values": values
        }
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Интервью!A:K',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return interview_data["id"]
        
    async def save_report(self, report_data: Dict) -> str:
        """Сохранение отчета об интервью"""
        values = [[
            report_data["id"],
            report_data["interview_id"],
            str(report_data["hard_skills_assessment"]),
            str(report_data["soft_skills_assessment"]),
            str(report_data["emotions_analysis"]),
            str(report_data["verdict"]),
            report_data["feedback"],
            datetime.now().isoformat()
        ]]
        
        body = {
            "values": values
        }
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Отчеты!A:H',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return report_data["id"]
        
    async def get_vacancies(self) -> List[Dict]:
        """Получение списка вакансий"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='Вакансии!A:I'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        vacancies = []
        
        for row in values[1:]:
            vacancy = {
                "id": row[0],
                "title": row[1],
                "level": row[2],
                "hard_skills": row[3].split(","),
                "soft_skills": row[4].split(","),
                "tasks": row[5].split(","),
                "tools": row[6].split(","),
                "created_at": row[7],
                "updated_at": row[8]
            }
            vacancies.append(vacancy)
            
        return vacancies 