import os
from elevenlabs import generate, set_api_key
from typing import Optional

class ElevenLabsService:
    def __init__(self):
        set_api_key(os.getenv("ELEVENLABS_API_KEY"))
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # ID голоса Emily
        
    async def generate_speech(self, text: str) -> bytes:
        """Генерирует речь из текста используя ElevenLabs"""
        try:
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2"
            )
            return audio
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return None 