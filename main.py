from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from routes import auth, vacancies, candidates, interviews, reports, notifications, livekit

from services.interview_service import InterviewService
from services.sheets_service import GoogleSheetsService
from services.voice_service import ElevenLabsService
from services.livekit_service import LiveKitService

load_dotenv()

app = FastAPI(title="AI-HR Bot API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL фронтенда
    allow_credentials=True,  # Разрешаем куки
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
app.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
app.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(livekit.router, prefix="/livekit", tags=["livekit"])

class InterviewRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    job_title: str
    job_level: str

@app.post("/start-interview")
async def start_interview(request: InterviewRequest):
    try:
        interview_service = InterviewService()
        session_id = await interview_service.create_session(
            request.candidate_name,
            request.candidate_email,
            request.job_title,
            request.job_level
        )
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    interview_service = InterviewService()
    voice_service = ElevenLabsService()
    sheets_service = GoogleSheetsService()
    
    try:
        while True:
            # Получаем ответ от кандидата
            response = await websocket.receive_text()
            
            # Анализируем ответ и генерируем следующий вопрос
            next_question = await interview_service.process_response(session_id, response)
            
            # Генерируем голосовой ответ
            audio = await voice_service.generate_speech(next_question)
            
            # Отправляем ответ клиенту
            await websocket.send_json({
                "question": next_question,
                "audio": audio
            })
            
            # Если интервью завершено, сохраняем результаты
            if interview_service.is_interview_complete(session_id):
                report = interview_service.generate_report(session_id)
                await sheets_service.save_report(report)
                await websocket.close()
                break
                
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to AI-HR Bot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 