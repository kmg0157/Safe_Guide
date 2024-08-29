from flask import Flask, request
import os, sys
from werkzeug.utils import secure_filename
from db_manage import ImageDatabase
from drive import Cloud
sys.path.append('/home/jetson/smart/Object_Detection')

from object_detect import ObjectDetection

class FileReceiver:
    def __init__(self, receive_folder='received_files'):
        self.app = Flask(__name__) #Initializing app
        self.RECEIVE_FOLDER = receive_folder
        os.makedirs(self.RECEIVE_FOLDER, exist_ok=True)
        self._set_routes() # Setting Flask Route
        self.db = ImageDatabase()  # Create ImageDatabase
        self.detector=ObjectDetection() #Image detector
        self.googledrive=Cloud()

    def _set_routes(self):
        @self.app.route('/receive', methods=['POST'])
        def receive_file():
            if 'file' not in request.files:
                return 'No file part', 400
            
            file = request.files['file']
            
            if file.filename == '':
                return 'No selected file', 400
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.RECEIVE_FOLDER, filename)
            file.save(file_path)

            # read BLOB type
            with open(file_path, 'rb') as image_file:
                image_bytes = image_file.read()
                self.db.save_image(image_bytes, status=0) # save images in DB
                self.detector.process_image(image_bytes) # detecting image
                self.googledrive.upload_to_drive()
                return 'File received successfully', 200

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, threaded=True)
