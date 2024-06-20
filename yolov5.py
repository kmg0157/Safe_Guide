import torch
from PIL import Image
import matplotlib.pyplot as plt

# YOLOv5 모델을 위한 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# 예측할 이미지 파일 경로
img_path = '/home/jetson/smart/received_files/dog.jpg'

# 이미지 불러오기
img = Image.open(img_path)

# 객체 검출 수행
results = model(img)

# 결과 출력
results.show()  # 결과 이미지를 시각화해서 보여줍니다.

# 각 객체의 클래스와 신뢰도 출력
for detection in results.pandas().xyxy[0].iterrows():
    print(detection)
