import torch
import cv2
import numpy as np
import os,sys
from deep_sort_realtime.deepsort_tracker import DeepSort # type: ignore
sys.path.append('/home/jetson/smart/send_to_led')
from control_led import ControlLED

class ObjectDetection:
    def __init__(self):
        # YOLOv5 모델 로드
        self.model = torch.hub.load('/home/jetson/smart/Object_Detection/yolov5', 'custom', path='Object_Detection/best_0.3.1.pt', source='local')

        # 추적 대상 클래스
        self.track_classes = ['car', 'truck', 'van', 'forklift', 'fire', 'smoke']
        self.frame_check_threshold = 2                   # 이 프레임 당 비율 변화 체크
        self.alert_threshold = 0.01                       # 관심 단계로 지정되는 이미지 비율
        self.warning_ratio = 0.01                        # 경고 단계로 전환되는 이미지 비율의 증가량
        self.danger_ratio = 0.03                         # 위험 단계로 전환되는 이미지 비율의 증가량
        self.conf_threshold=0.25

        # 경고 상태 관리
        self.deepsort=DeepSort(max_age=30,n_init=3, nms_max_overlap=1.0, max_cosine_distance=0.2, nn_budget=100)
        self.tracked_objects = {}
        self.cl = ControlLED()

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
    def process_image(self, image_blob):
        # 이미지 로드
        img_array = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print("Image decoding failed.")
            return

        img_height, img_width = img.shape[:2]

        # 모델 추론
        results = self.model(img)
        detections=[]

        for *xyxy,conf,cls in results.xyxy[0]:
            if conf > self.conf_threshold:
                class_name=self.model.names[int(cls)]
                if class_name in self.track_classes:
                    x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                    bbox_xywh=[x1,y1,x2-x1,y2-y1]
                    detections.append((bbox_xywh,conf.item(),class_name))

        tracks=self.deepsort.update_tracks(detections, frame=img)

        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id=track.track_id
            bbox=track.to_ltwh()
            class_name=track.get_det_class()
            x1,y1,w,h=bbox
            x2,y2=x1+w,y1+h
            label=f'{class_name} {track_id}'
            self.plot_one_box([x1, y1, x2, y2], img, label=label, color=(255, 0, 0), line_thickness=2)
            box_area = (x2 - x1) * (y2 - y1)
            image_area = img_width * img_height
            area_ratio = box_area / image_area

            det_conf=track.get_det_conf()
            if det_conf is not None:
                 print(f"Detected: {class_name} with confidence {det_conf:.2f},"
                          f" {class_name} ratio in image: {area_ratio:.2f}")
            else:
                 print(f"No Detection")

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
        else:
            self.tracked_objects[class_name]['alert_level']='Caution'

        self.tracked_objects[class_name]['area_ratios'].append(area_ratio)
        self.tracked_objects[class_name]['frames_since_first_detection'] += 1

        recent_ratios = self.tracked_objects[class_name]['area_ratios'][-self.frame_check_threshold:]
        ratio_change = recent_ratios[-1] - recent_ratios[0] if len(recent_ratios) > 1 else 0

        current_alert_level = self.tracked_objects[class_name]['alert_level']

        if current_alert_level == 'Caution':
            if ratio_change >= self.danger_ratio:
                self.tracked_objects[class_name]['alert_level'] = 'Danger'
                self.cl.request_on()  # LED 켜기
                print(f"[Danger] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")
            elif ratio_change >= self.warning_ratio:
                self.tracked_objects[class_name]['alert_level'] = 'Warning'
                self.cl.request_on()  # LED 켜기
                print(f"[Warning] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")
        elif current_alert_level in ['Warning', 'Danger']:
            if ratio_change < self.warning_ratio:
                self.tracked_objects[class_name]['alert_level'] = 'Caution'
                self.cl.request_off()  # LED 끄기
                print(f"[Caution] {class_name} detected with area ratio stabilized at {recent_ratios[-1]:.2f}")