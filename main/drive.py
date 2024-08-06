from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os, time


class Cloud:
    def __init__(self):    
        # 서비스 계정 파일 경로
        self.SERVICE_ACCOUNT_FILE = '/home/jetson/smart/safe-guide-manager-431512-9e05ded22b73.json'

        # 인증 및 API 클라이언트 생성
        self.credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        # 폴더 경로와 폴더 ID 설정
        self.folder_path = '/home/jetson/smart/output'
        self.folder_id = '15G8-Cqv3HraAmtLiaqU6HYmoG328COUm'


    def upload_to_drive(self):
        # 폴더 내 모든 파일 경로 가져오기
        file_paths = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
    
        for index, file_path in enumerate(file_paths):
            # 파일 이름 생성
            file_name = f'image_{time.time():.0f}_{index}{os.path.splitext(file_path)[1]}'
            file_metadata = {
                'name': file_name,  # 업로드될 파일의 이름
                'parents': [self.folder_id]  # 업로드될 폴더 ID
            }
            media = MediaFileUpload(file_path, mimetype='image/jpeg')

            try:
                # 파일 업로드
                file = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"Uploaded {file_name} with File ID: {file.get('id')}")
            except Exception as e:
                print(f"Failed to upload {file_name}. Error: {str(e)}")