import os
import openai
from typing import Dict, List, Optional
import uuid
import json
from datetime import datetime
from models.base import Interview, InterviewCreate, Report, ReportCreate
from services.sheets_service import GoogleSheetsService
from services.whisper_service import WhisperService
from services.drive_service import GoogleDriveService
from services.livekit_service import LiveKitService

class InterviewService:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        self.sessions: Dict[str, Dict] = {}
        self.sheets_service = GoogleSheetsService()
        self.whisper_service = WhisperService()
        self.drive_service = GoogleDriveService()
        self.livekit_service = LiveKitService()
        
    async def create_interview(self, interview: InterviewCreate) -> Interview:
        # Получаем текущие интервью
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:J'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # Создаем заголовки, если таблица пуста
            headers = [
                "ID", "ID кандидата", "ID вакансии", "Статус", 
                "Время начала", "Время окончания", "URL записи", 
                "Транскрипт", "Вопросы", "Ответы", "Анализ эмоций"
            ]
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_service.spreadsheet_id,
                range='Интервью!A1:K1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            values = [headers]
        
        # Создаем новое интервью
        new_interview = Interview(
            id=str(len(values)),
            candidate_id=interview.candidate_id,
            vacancy_id=interview.vacancy_id,
            status=interview.status,
            start_time=interview.start_time,
            end_time=interview.end_time,
            recording_url=interview.recording_url,
            transcript=interview.transcript,
            questions=interview.questions,
            answers=interview.answers,
            emotions_analysis=interview.emotions_analysis
        )
        
        # Подготавливаем данные для записи
        row_data = [
            new_interview.id,
            new_interview.candidate_id,
            new_interview.vacancy_id,
            new_interview.status,
            str(new_interview.start_time),
            str(new_interview.end_time) if new_interview.end_time else "",
            new_interview.recording_url or "",
            new_interview.transcript or "",
            ",".join(new_interview.questions),
            ",".join(new_interview.answers),
            str(new_interview.emotions_analysis)
        ]
        
        # Добавляем интервью в таблицу
        self.sheets_service.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:K',
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        return new_interview
        
    async def get_interview(self, interview_id: str) -> Optional[Interview]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:K'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return None
            
        for row in values[1:]:  # Пропускаем заголовки
            if row[0] == interview_id:
                return Interview(
                    id=row[0],
                    candidate_id=row[1],
                    vacancy_id=row[2],
                    status=row[3],
                    start_time=datetime.fromisoformat(row[4]),
                    end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                    recording_url=row[6] if row[6] else None,
                    transcript=row[7] if row[7] else None,
                    questions=row[8].split(",") if row[8] else [],
                    answers=row[9].split(",") if row[9] else [],
                    emotions_analysis=eval(row[10]) if row[10] else []
                )
        return None
        
    async def get_interviews(self) -> List[Interview]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:K'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Проверяем наличие заголовков и данных
            return []
            
        interviews = []
        for row in values[1:]:  # Пропускаем заголовки
            interview = Interview(
                id=row[0],
                candidate_id=row[1],
                vacancy_id=row[2],
                status=row[3],
                start_time=datetime.fromisoformat(row[4]),
                end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                recording_url=row[6] if row[6] else None,
                transcript=row[7] if row[7] else None,
                questions=row[8].split(",") if row[8] else [],
                answers=row[9].split(",") if row[9] else [],
                emotions_analysis=eval(row[10]) if row[10] else []
            )
            interviews.append(interview)
        return interviews
        
    async def update_interview(self, interview_id: str, interview: InterviewCreate) -> Optional[Interview]:
        # Получаем текущие интервью
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:K'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        # Ищем интервью для обновления
        for i, row in enumerate(values[1:], start=2):  # start=2 потому что первая строка - заголовки
            if row[0] == interview_id:
                updated_interview = Interview(
                    id=interview_id,
                    candidate_id=interview.candidate_id,
                    vacancy_id=interview.vacancy_id,
                    status=interview.status,
                    start_time=interview.start_time,
                    end_time=interview.end_time,
                    recording_url=interview.recording_url,
                    transcript=interview.transcript,
                    questions=interview.questions,
                    answers=interview.answers,
                    emotions_analysis=interview.emotions_analysis
                )
                
                # Подготавливаем данные для обновления
                row_data = [
                    updated_interview.id,
                    updated_interview.candidate_id,
                    updated_interview.vacancy_id,
                    updated_interview.status,
                    str(updated_interview.start_time),
                    str(updated_interview.end_time) if updated_interview.end_time else "",
                    updated_interview.recording_url or "",
                    updated_interview.transcript or "",
                    ",".join(updated_interview.questions),
                    ",".join(updated_interview.answers),
                    str(updated_interview.emotions_analysis)
                ]
                
                # Обновляем интервью в таблице
                self.sheets_service.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Интервью!A{i}:K{i}',
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
                
                return updated_interview
        return None
        
    async def delete_interview(self, interview_id: str) -> bool:
        # Получаем текущие интервью
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Интервью!A:K'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return False
            
        # Ищем интервью для удаления
        for i, row in enumerate(values[1:], start=2):
            if row[0] == interview_id:
                # Удаляем строку с интервью
                self.sheets_service.service.spreadsheets().values().clear(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Интервью!A{i}:K{i}'
                ).execute()
                return True
        return False
        
    async def create_session(self, candidate_name: str, candidate_email: str, job_title: str, job_level: str) -> str:
        # Создаем новую сессию в LiveKit
        room_name = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        token = await self.livekit_service.create_room(room_name)
        
        # Создаем запись интервью
        interview = InterviewCreate(
            candidate_id="",  # Будет заполнено позже
            vacancy_id="",    # Будет заполнено позже
            status="in_progress",
            start_time=datetime.now(),
            recording_url=f"https://drive.google.com/recordings/{room_name}"
        )
        
        created_interview = await self.create_interview(interview)
        return created_interview.id
        
    async def process_response(self, session_id: str, response: str) -> str:
        # Получаем интервью
        interview = await self.get_interview(session_id)
        if not interview:
            raise ValueError("Interview not found")
            
        # Транскрибируем ответ
        transcript = await self.whisper_service.transcribe_audio(response)
        
        # Анализируем ответ
        analysis = await self.whisper_service.analyze_response(transcript, interview)
        
        # Обновляем интервью
        interview.answers.append(transcript)
        interview.emotions_analysis.append(analysis)
        
        await self.update_interview(session_id, interview)
        
        # Генерируем следующий вопрос
        return await self._generate_next_question(interview)
        
    async def _generate_next_question(self, interview: Interview) -> str:
        # TODO: Реализовать генерацию следующего вопроса на основе предыдущих ответов
        return "Расскажите о вашем опыте работы"
        
    def is_interview_complete(self, session_id: str) -> bool:
        # TODO: Реализовать проверку завершения интервью
        return False
        
    def generate_report(self, session_id: str) -> Report:
        # TODO: Реализовать генерацию отчета
        return Report(
            interview_id=session_id,
            hard_skills_assessment={},
            soft_skills_assessment={},
            emotions_analysis={},
            verdict={}
        ) 