import os
from typing import Optional, Dict
from datetime import datetime, timedelta
from livekit import api
from livekit.rtc import Room, RoomEvent, RemoteParticipant, RemoteTrack

class LiveKitService:
    def __init__(self):
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.host = os.getenv("LIVEKIT_HOST")
        self.port = int(os.getenv("LIVEKIT_PORT", "7880"))
        
        if not all([self.api_key, self.api_secret, self.host]):
            raise ValueError("Missing LiveKit configuration")
            
        self.client = api.LiveKitAPI(
            self.host,
            self.api_key,
            self.api_secret,
            port=self.port
        )
        
    async def create_room(self, room_name: str) -> Dict[str, str]:
        """Создает новую комнату в LiveKit и возвращает токены для участников"""
        try:
            # Создаем комнату
            room = await self.client.create_room(
                name=room_name,
                empty_timeout=300,  # 5 минут
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "type": "interview"
                }
            )
            
            # Генерируем токены для участников
            interviewer_token = self.client.generate_token(
                room_name=room_name,
                identity="interviewer",
                name="AI Interviewer",
                metadata={"role": "interviewer"},
                expires_in=3600  # 1 час
            )
            
            candidate_token = self.client.generate_token(
                room_name=room_name,
                identity="candidate",
                name="Candidate",
                metadata={"role": "candidate"},
                expires_in=3600  # 1 час
            )
            
            return {
                "room_name": room_name,
                "interviewer_token": interviewer_token,
                "candidate_token": candidate_token,
                "ws_url": f"wss://{self.host}:{self.port}/rtc"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create LiveKit room: {str(e)}")
            
    async def delete_room(self, room_name: str) -> bool:
        """Удаляет комнату в LiveKit"""
        try:
            await self.client.delete_room(room_name)
            return True
        except Exception as e:
            print(f"Failed to delete LiveKit room: {str(e)}")
            return False
            
    async def get_room_info(self, room_name: str) -> Optional[Dict]:
        """Получает информацию о комнате"""
        try:
            room = await self.client.get_room(room_name)
            return {
                "name": room.name,
                "num_participants": room.num_participants,
                "created_at": room.metadata.get("created_at"),
                "type": room.metadata.get("type")
            }
        except Exception:
            return None
            
    async def get_participant_token(
        self,
        room_name: str,
        identity: str,
        name: str,
        role: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        """Генерирует токен для нового участника"""
        try:
            return self.client.generate_token(
                room_name=room_name,
                identity=identity,
                name=name,
                metadata={"role": role},
                expires_in=expires_in
            )
        except Exception:
            return None
            
    async def list_rooms(self) -> list:
        """Получает список всех активных комнат"""
        try:
            rooms = await self.client.list_rooms()
            return [
                {
                    "name": room.name,
                    "num_participants": room.num_participants,
                    "created_at": room.metadata.get("created_at"),
                    "type": room.metadata.get("type")
                }
                for room in rooms
            ]
        except Exception:
            return [] 