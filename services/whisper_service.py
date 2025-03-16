import os
import openai
from typing import Optional, Dict
import json

class WhisperService:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Транскрибация аудио в текст"""
        try:
            response = await self.openai.audio.transcriptions.create(
                file=("audio.mp3", audio_data),
                model="whisper-1",
                language="ru"
            )
            return response.text
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None
            
    async def analyze_response(self, text: str, vacancy_data: Dict) -> Dict:
        """Анализ ответа кандидата"""
        try:
            # Формируем контекст для анализа
            context = {
                "text": text,
                "vacancy": {
                    "title": vacancy_data["title"],
                    "level": vacancy_data["level"],
                    "hard_skills": vacancy_data["hard_skills"],
                    "soft_skills": vacancy_data["soft_skills"]
                }
            }
            
            # Анализируем ответ с помощью GPT-4
            response = await self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Вы — HR-специалист, анализирующий ответ кандидата на собеседовании. Оцените технические знания и soft skills кандидата."},
                    {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
                ]
            )
            
            # Парсим ответ
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "hard_skills_assessment": analysis.get("hard_skills", {}),
                "soft_skills_assessment": analysis.get("soft_skills", {}),
                "emotions_analysis": analysis.get("emotions", []),
                "verdict": analysis.get("verdict", {})
            }
            
        except Exception as e:
            print(f"Error analyzing response: {str(e)}")
            return None 