from flask import Flask
import os
from db_manage import ImageDatabase
from route import receive_file, update_status, get_images

class FlaskClient:
    def __init__(self, receive_folder='received_files'):
        self.app = Flask(__name__)
        self.RECEIVE_FOLDER = receive_folder
        os.makedirs(self.RECEIVE_FOLDER, exist_ok=True)
        self.db = ImageDatabase()
        self._set_routes()

    def _set_routes(self):
        receive_file(self.app, self.db)
        update_status(self.app, self.db)
        get_images(self.app, self.db)

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

    def close(self):
        self.db.close_db()

if __name__ == '__main__':
    client = FlaskClient()
    try:
        client.run()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
