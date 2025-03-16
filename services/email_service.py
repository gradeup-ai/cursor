import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

class EmailService:
    def __init__(self):
        self.host = os.getenv("EMAIL_HOST")
        self.port = int(os.getenv("EMAIL_PORT", "465"))
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
        
    async def send_interview_link(self, candidate_email: str, interview_link: str) -> bool:
        """Отправка ссылки на интервью кандидату"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = candidate_email
            msg['Subject'] = "Ссылка на интервью с AI-HR"
            
            body = f"""
            Здравствуйте!
            
            Вы можете начать интервью в любое удобное время, перейдя по ссылке:
            {interview_link}
            
            С уважением,
            AI-HR Эмили
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
            
    async def send_interview_report(self, candidate_email: str, report_data: dict) -> bool:
        """Отправка отчета об интервью кандидату"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = candidate_email
            msg['Subject'] = "Результаты интервью"
            
            # Формируем тело письма
            body = f"""
            Здравствуйте!
            
            Спасибо за прохождение интервью. Вот результаты:
            
            Оценка технических навыков:
            {self._format_skills(report_data['hard_skills_assessment'])}
            
            Оценка soft skills:
            {self._format_skills(report_data['soft_skills_assessment'])}
            
            Итоговый вердикт:
            {'Подходит' if report_data['verdict']['is_suitable'] else 'Не подходит'}
            
            Сильные стороны:
            {', '.join(report_data['verdict']['strengths'])}
            
            Зоны роста:
            {', '.join(report_data['verdict']['weaknesses'])}
            
            С уважением,
            AI-HR Эмили
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            print(f"Error sending report: {str(e)}")
            return False
            
    def _format_skills(self, skills: dict) -> str:
        """Форматирование навыков для email"""
        return "\n".join([f"- {skill}: {score}/5" for skill, score in skills.items()]) 