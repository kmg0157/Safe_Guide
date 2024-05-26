from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
JETSON_IP = '192.168.0.9'  # 젯슨 나노의 IP 주소
JETSON_PORT = 5000  # 젯슨 나노의 포트 번호
JETSON_URL = f'http://{JETSON_IP}:{JETSON_PORT}/receive'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_first_request
def setup():
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 파일을 젯슨 나노로 전송
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(JETSON_URL, files=files)
            if response.status_code == 200:
                return 'File uploaded and sent to Jetson Nano successfully'
            else:
                return 'Failed to send file to Jetson Nano', response.status_code
    else:
        return 'File not allowed'

if __name__ == '__main__':
    app.run(debug=True)
