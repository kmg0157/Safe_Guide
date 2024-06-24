from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import requests

class FlaskServer:
    def __init__(self):
        self.app=Flask(__name__)
        self.UPLOAD_FOLDER = 'uploads'
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        self.JETSON_IP = '192.168.0.9'  # 젯슨 나노의 IP 주소
        self.JETSON_PORT = 5000  # 젯슨 나노의 포트 번호
        self.JETSON_URL = f'http://{self.JETSON_IP}:{self.JETSON_PORT}/receive'
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER

    def run(self):
        self.app.run(debug=True)

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def setup(self):
        @self.app.before_first_request
        def ensure_upload_folder():
            if not os.path.exists(self.app.config['UPLOAD_FOLDER']):
                os.makedirs(self.app.config['UPLOAD_FOLDER'])
    
    def index(self):
        @self.app.route('/')
        def defalt():
            return render_template('index.html')
        
    def upload(self):
        @self.app.route('/upload',methods=['POST'])
        def upload_image():
            if 'file' not in request.files:
                return 'No file part'
            file = request.files['file']
            if file.filename == '':
                return 'No selected file'
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 파일을 젯슨 나노로 전송
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(self.JETSON_URL, files=files)
                    if response.status_code == 200:
                        return 'File uploaded and sent to Jetson Nano successfully'
                    else:
                        return 'Failed to send file to Jetson Nano', response.status_code
            else:
                return 'File not allowed'
