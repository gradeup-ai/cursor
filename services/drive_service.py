import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from typing import Optional

class GoogleDriveService:
    def __init__(self):
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        
    async def upload_audio(self, audio_data: bytes, interview_id: str) -> Optional[str]:
        """Загрузка аудиозаписи интервью в Google Drive"""
        try:
            file_metadata = {
                'name': f'interview_{interview_id}.mp3',
                'parents': [self.folder_id]
            }
            
            media = MediaIoBaseUpload(
                BytesIO(audio_data),
                mimetype='audio/mp3',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return file.get('webViewLink')
            
        except Exception as e:
            print(f"Error uploading audio: {str(e)}")
            return None
            
    async def delete_audio(self, interview_id: str) -> bool:
        """Удаление аудиозаписи интервью"""
        try:
            # Поиск файла по имени
            results = self.service.files().list(
                q=f"name = 'interview_{interview_id}.mp3' and '{self.folder_id}' in parents",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return False
                
            # Удаление файла
            self.service.files().delete(
                fileId=files[0]['id']
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error deleting audio: {str(e)}")
            return False 