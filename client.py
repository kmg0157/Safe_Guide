from flask import Flask, request
import os
from werkzeug.utils import secure_filename


class FlaskClient:
    def __init__(self, receive_folder='received_files'):
        self.app = Flask(__name__)
        self.RECEIVE_FOLDER = receive_folder
        os.makedirs(self.RECEIVE_FOLDER, exist_ok=True)
        self._set_routes()

    def _set_routes(self):
        @self.app.route('/receive', methods=['POST'])
        def receive_file():
            if 'file' not in request.files:
                return 'No file part', 400
            file = request.files['file']
            if file.filename == '':
                return 'No selected file', 400
            file_path = os.path.join(self.RECEIVE_FOLDER, secure_filename(file.filename))
            file.save(file_path)
            return 'File received successfully', 200

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)
