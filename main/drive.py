from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = '/home/jetson/smart/main/client_secret_809894108288-9os580gd8pgf37g22e807thllc6ts6d2.apps.googleusercontent.com.json'  # 서비스 계정 JSON 파일 경로
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Google Drive API 클라이언트 서비스 객체 생성
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

# Google Drive 폴더 ID 및 업로드할 파일 경로
folder_id = 'your_folder_id'  # Google Drive 폴더 ID
file_paths = 'file.csv'       # 업로드할 파일 경로

# 파일 메타데이터 정의
file_metadata = {
    'name': 'file.csv',  # 업로드할 파일 이름
    'parents': [folder_id]  # 업로드할 폴더 ID
}

# 파일 업로드를 위한 MediaFileUpload 객체 생성
media = MediaFileUpload(file_paths, mimetype='text/csv')

# 파일 업로드 요청
try:
    file_info = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    # 업로드 성공 시 파일 링크 출력
    print("File webViewLink:", file_info.get('webViewLink'))
except Exception as e:
    print(f"An error occurred: {e}")

