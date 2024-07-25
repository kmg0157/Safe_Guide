from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import requests

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.UPLOAD_FOLDER = 'C:/Users/kmg01/smart/uploads'
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        self.JETSON_IP = '192.168.1.42'  # 젯슨 나노의 IP 주소
        self.JETSON_PORT = 5000  # 젯슨 나노의 포트 번호
        self.JETSON_URL = f'http://{self.JETSON_IP}:{self.JETSON_PORT}/receive'
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER

        # 설정 메서드 호출
        self.setup()

    def run(self):
        self.app.run(host='0.0.0.0', port=81)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def setup(self):
        # 업로드 폴더 확인 및 생성
        if not os.path.exists(self.app.config['UPLOAD_FOLDER']):
            os.makedirs(self.app.config['UPLOAD_FOLDER'])

        # '/imageUp' 엔드포인트 등록
        self.app.add_url_rule('/imageUp', 'upload_image', self.upload, methods=['POST'])

        # '/' 루트 엔드포인트 등록
        self.app.add_url_rule('/', 'default', self.index)

    def upload(self):
        image_data = request.data
        if image_data:
            filename = secure_filename('uploaded_image.jpg')
            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            print('Image saved:', file_path)

            # 파일을 젯슨 나노로 전송
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(self.JETSON_URL, files=files)
                if response.status_code == 200:
                    return 'File uploaded and sent to Jetson Nano successfully'
                else:
                    return 'Failed to send file to Jetson Nano', response.status_code
        else:
            return 'No image found in request'

    def index(self):
        return render_template('index.html')