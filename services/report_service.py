import os
from typing import Dict, List, Optional
from datetime import datetime
from models.base import Report, ReportCreate
from services.sheets_service import GoogleSheetsService
from services.email_service import EmailService

class ReportService:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.email_service = EmailService()
        
    async def create_report(self, report: ReportCreate) -> Report:
        # Получаем текущие отчеты
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Отчеты!A:J'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # Создаем заголовки, если таблица пуста
            headers = [
                "ID", "ID интервью", "ID кандидата", "ID вакансии",
                "Оценка hard skills", "Оценка soft skills", "Анализ эмоций",
                "Вердикт", "Дата создания", "Статус"
            ]
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_service.spreadsheet_id,
                range='Отчеты!A1:J1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            values = [headers]
        
        # Создаем новый отчет
        new_report = Report(
            id=str(len(values)),
            interview_id=report.interview_id,
            candidate_id=report.candidate_id,
            vacancy_id=report.vacancy_id,
            hard_skills_assessment=report.hard_skills_assessment,
            soft_skills_assessment=report.soft_skills_assessment,
            emotions_analysis=report.emotions_analysis,
            verdict=report.verdict,
            created_at=datetime.now(),
            status="new"
        )
        
        # Подготавливаем данные для записи
        row_data = [
            new_report.id,
            new_report.interview_id,
            new_report.candidate_id,
            new_report.vacancy_id,
            str(new_report.hard_skills_assessment),
            str(new_report.soft_skills_assessment),
            str(new_report.emotions_analysis),
            str(new_report.verdict),
            str(new_report.created_at),
            new_report.status
        ]
        
        # Добавляем отчет в таблицу
        self.sheets_service.service.spreadsheets().values().append(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Отчеты!A:J',
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        return new_report
        
    async def get_report(self, report_id: str) -> Optional[Report]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Отчеты!A:J'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        for row in values[1:]:
            if row[0] == report_id:
                return Report(
                    id=row[0],
                    interview_id=row[1],
                    candidate_id=row[2],
                    vacancy_id=row[3],
                    hard_skills_assessment=eval(row[4]),
                    soft_skills_assessment=eval(row[5]),
                    emotions_analysis=eval(row[6]),
                    verdict=eval(row[7]),
                    created_at=datetime.fromisoformat(row[8]),
                    status=row[9]
                )
        return None
        
    async def get_reports(self) -> List[Report]:
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Отчеты!A:J'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return []
            
        reports = []
        for row in values[1:]:
            report = Report(
                id=row[0],
                interview_id=row[1],
                candidate_id=row[2],
                vacancy_id=row[3],
                hard_skills_assessment=eval(row[4]),
                soft_skills_assessment=eval(row[5]),
                emotions_analysis=eval(row[6]),
                verdict=eval(row[7]),
                created_at=datetime.fromisoformat(row[8]),
                status=row[9]
            )
            reports.append(report)
        return reports
        
    async def update_report_status(self, report_id: str, status: str) -> Optional[Report]:
        report = await self.get_report(report_id)
        if not report:
            return None
            
        report.status = status
        
        # Получаем текущие отчеты
        result = self.sheets_service.service.spreadsheets().values().get(
            spreadsheetId=self.sheets_service.spreadsheet_id,
            range='Отчеты!A:J'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return None
            
        # Ищем отчет для обновления
        for i, row in enumerate(values[1:], start=2):
            if row[0] == report_id:
                # Обновляем статус
                self.sheets_service.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_service.spreadsheet_id,
                    range=f'Отчеты!J{i}',
                    valueInputOption='RAW',
                    body={'values': [[status]]}
                ).execute()
                break
                
        return report
        
    async def send_report(self, report_id: str, hr_email: str) -> bool:
        report = await self.get_report(report_id)
        if not report:
            return False
            
        # Отправляем отчет по email
        await self.email_service.send_interview_report(
            hr_email=hr_email,
            candidate_name="",  # TODO: Получить имя кандидата
            vacancy_title="",   # TODO: Получить название вакансии
            hard_skills=report.hard_skills_assessment,
            soft_skills=report.soft_skills_assessment,
            emotions=report.emotions_analysis,
            verdict=report.verdict
        )
        
        # Обновляем статус отчета
        await self.update_report_status(report_id, "sent")
        
        return True 