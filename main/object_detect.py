import sqlite3
import io
from PIL import Image
import torch
from matplotlib import pyplot as plt
import numpy as np
from db_manage import ImageDatabase

class ObjectDetector:
    def __init__(self, model_path):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)

    def detect_objects(self, image):
        results = self.model(image)
        return results

def main():
    # Database and Object Detector initialization
    db = ImageDatabase()
    detector = ObjectDetector('/home/jetson/smart/main/best.pt')  # 모델 경로 설정

    # Get the latest image from the database
    image, h, w, c = db.get_latest_image()

    if image is not None:
        # Perform object detection
        results = detector.detect_objects(image)
       
        # Display the results
        results.show()

        # Optionally, you can save the results to an image file
        results.save(save_dir='detections')

    else:
        print("No image found in the database.")

    # Close the database connection
    db.close_db()

if __name__ == '__main__':
    main()

