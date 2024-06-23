from flask import jsonify, request
from db_manage import ImageDatabase

def receive_file(app, db):
    @app.route('/receive', methods=['POST'])
    def receive_file_route():
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400
        try:
            image_bytes = file.read()
            db.save_image(image_bytes, 0)  # 초기 상태는 0으로 저장
            return jsonify({"message": "File successfully uploaded"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def update_status(app, db):
    @app.route('/update_status/<int:image_id>', methods=['POST'])
    def update_status_route(image_id):
        try:
            new_status = request.json['status']
            db.update_image_status(image_id, new_status)
            return jsonify({"message": "Status updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def get_images(app, db):
    @app.route('/images', methods=['GET'])
    def get_images_route():
        try:
            images = db.fetch_images()
            return jsonify(images), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
