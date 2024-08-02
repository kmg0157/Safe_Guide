import torch
import cv2
import numpy as np

class ObjectDetection:
    def __init__(self):
        # YOLOv5 모델 로드
        self.model = torch.hub.load('/home/jetson/smart/main/yolov5', 'custom', path='/home/jetson/smart/main/best_0.3.0.pt', source='local')

        # 추적 대상 클래스
        self.track_classes = ['car', 'truck', 'van', 'forklift', 'fire', 'smoke']
        self.frame_check_threshold = 3
        self.fire_smoke_frame_check_threshold = 15
        self.alert_threshold = 0.1
        self.warning_ratio = 0.03
        self.danger_ratio = 0.05

        # 경고 상태 관리
        self.tracked_objects = {}

    def plot_one_box(self, x, img, color=(128, 128, 128), label=None, line_thickness=3):
        tl = line_thickness or round(0.002 * max(img.shape[0:2])) + 1
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    def process_image_from_blob(self, image_blob, conf_threshold=0.25):
        # BLOB 데이터를 이미지로 디코딩
        img_array = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print("Image decoding failed.")
            return

        img_height, img_width = img.shape[:2]
        results = self.model(img)

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

                    print(f"Detected: {class_name} with confidence {conf:.2f}, {class_name} ratio in image: {area_ratio:.2f}")

                    if area_ratio >= self.alert_threshold:
                        self.track_object(class_name, area_ratio)

        output_path = os.path.join('/home/jetson/smart/output', 'processed_image.jpg')
        cv2.imwrite(output_path, img)
        print(f"Processed image saved to {output_path}")

    def track_object(self, class_name, area_ratio):
        if class_name not in self.tracked_objects:
            self.tracked_objects[class_name] = {
                'area_ratios': [],
                'alert_level': 'Caution',
                'frames_since_first_detection': 0
            }

        self.tracked_objects[class_name]['area_ratios'].append(area_ratio)
        self.tracked_objects[class_name]['frames_since_first_detection'] += 1

        if self.tracked_objects[class_name]['alert_level'] == 'Caution':
            if len(self.tracked_objects[class_name]['area_ratios']) >= self.frame_check_threshold:
                recent_ratios = self.tracked_objects[class_name]['area_ratios'][-self.frame_check_threshold:]
                ratio_change = recent_ratios[-1] - recent_ratios[0]

                if ratio_change >= self.warning_ratio:
                    self.tracked_objects[class_name]['alert_level'] = 'Danger'
                    print(f"[Danger] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")
                elif ratio_change >= self.danger_ratio:
                    self.tracked_objects[class_name]['alert_level'] = 'Warning'
                    print(f"[Warning] {class_name} detected with area ratio increase to {recent_ratios[-1]:.2f}")

        if class_name in ['fire', 'smoke']:
            if self.tracked_objects[class_name]['frames_since_first_detection'] > self.fire_smoke_frame_check_threshold:
                print(f"[Caution] {class_name} detected for more than {self.fire_smoke_frame_check_threshold} frames")
