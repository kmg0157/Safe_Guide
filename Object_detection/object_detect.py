import torch
import cv2
import numpy as np
import os
from main.siren import Siren

class ObjectDetection:
    def __init__(self):
        # YOLOv5 모델 로드
        self.model = torch.hub.load('/home/jetson/smart/Object_detection/yolov5', 'custom', path='/home/jetson/smart/Object_detection/best_0.3.0.pt', source='local')

        # 추적 대상 클래스
        # 대상 클래스, 프레임 당 비율 변화, 화재/연기 감지 프레임, 관심/경고/위험 이미지 비율 모두 여기서 조정 가능
        self.track_classes = ['car', 'truck', 'van', 'forklift', 'fire', 'smoke']
        self.frame_check_threshold = 3                   # 이 프레임 당 비율 변화 체크
        self.fire_smoke_frame_check_threshold = 15       # 화재/연기 감지 프레임
        self.alert_threshold = 0.1                       # 관심 단계로 지정되는 이미지 비율
        self.warning_ratio = 0.03                        # 경고 단계로 전환되는 이미지 비율의 증가량
        self.danger_ratio = 0.05                         # 위험 단계로 전환되는 이미지 비율의 증가량


        # 경고 상태 관리
        self.tracked_objects = {}
        self.alert=Siren()


    # 바운딩 박스를 그리는 함수
    def plot_one_box(self, x, img, color=(128, 128, 128), label=None, line_thickness=3):
        tl = line_thickness or round(0.002 * max(img.shape[0:2])) + 1
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    # 이미지 처리
    def process_image(self, image_blob, conf_threshold=0.25):
        # 이미지 로드 
        # BLOB 데이터를 이미지로 디코딩
        img_array = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print("Image decoding failed.")
            return

        img_height, img_width = img.shape[:2]

        # 모델 추론
        results = self.model(img)

        # 결과 처리 및 바운딩 박스 그리기
        for *xyxy, conf, cls in results.xyxy[0]:
            if conf > conf_threshold:
                class_name = self.model.names[int(cls)]
                if class_name in self.track_classes:
                    x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                    box_area = (x2 - x1) * (y2 - y1)
                    image_area = img_width * img_height
                    area_ratio = box_area / image_area

                    label = f'{class_name} {conf:.2f}'
                    self.plot_one_box((x1, y1, x2, y2), img, label=label, color=(255, 0, 0), line_thickness=2)

                    # 객체 인식 메시지 출력
                    print(f"Detected: {class_name} with confidence {conf:.2f} at {img},"
                        f" {class_name} ratio in image: {area_ratio:.2f}")

                    # 관심 수준 이상 감지
                    if area_ratio >= self.alert_threshold:
                        self.track_object(class_name, area_ratio)

        output_path = os.path.join('/home/jetson/smart/output', 'processed_image.jpg')
        cv2.imwrite(output_path, img)
        print(f"Processed image saved to {output_path}")

    # 객체의 상태를 기록 및 추적
    def track_object(self, class_name, area_ratio):
        if class_name not in self.tracked_objects:
            self.tracked_objects[class_name] = {
                'area_ratios': [],
                'alert_level': 'Caution',
                'frames_since_first_detection': 0
            }

        # 바운딩 박스 크기 비율 기록
        self.tracked_objects[class_name]['area_ratios'].append(area_ratio)
        self.tracked_objects[class_name]['frames_since_first_detection'] += 1

        # 관심, 경고, 위험 수준 결정
        if self.tracked_objects[class_name]['alert_level'] == 'Caution':
            if len(self.tracked_objects[class_name]['area_ratios']) >= self.frame_check_threshold:
                # 최근 n개의 프레임에서의 비율 변화 체크
                recent_ratios = self.tracked_objects[class_name]['area_ratios'][-self.frame_check_threshold:]
                ratio_change = recent_ratios[-1] - recent_ratios[0]

                if ratio_change >= self.warning_ratio:
                    self.tracked_objects[class_name]['alert_level'] = 'Danger'
                    self.alert.danger_notice()
                    print(f"[Danger] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")
                
                elif ratio_change >= self.danger_ratio:
                    self.tracked_objects[class_name]['alert_level'] = 'Warning'
                    self.alert.warning_notice()
                    print(f"[Warning] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")

                else:
                    self.alert.default()

        # Fire와 Smoke 클래스는 지정 프레임 횟수가 지나도 감지되면 경고
        if class_name in ['fire', 'smoke']:
            if self.tracked_objects[class_name]['frames_since_first_detection'] > self.fire_smoke_frame_check_threshold:
                self.alert.warning_notice()
                print(f"[Caution] {class_name} detected for more than {self.fire_smoke_frame_check_threshold} frames")
                
