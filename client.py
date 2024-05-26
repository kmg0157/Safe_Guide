from flask import Flask, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

RECEIVE_FOLDER = 'received_files'
os.makedirs(RECEIVE_FOLDER, exist_ok=True)

@app.route('/receive', methods=['POST'])
def receive_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    file_path = os.path.join(RECEIVE_FOLDER, secure_filename(file.filename))
    file.save(file_path)
    return 'File received successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
