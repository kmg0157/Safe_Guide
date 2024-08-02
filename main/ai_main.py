import os
from object_detect import ObjectDetection

def main():
    # 데이터셋 디렉토리 경로
    dataset_dir = '/home/jetson/smart/input'  # 이미지가 있는 디렉토리 경로를 설정하세요

    # ObjectDetection 인스턴스 생성
    detector = ObjectDetection()

    # 데이터셋 디렉토리 내의 모든 이미지 파일을 처리
    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # 지원하는 이미지 형식
            image_path = os.path.join(dataset_dir, filename)
            detector.process_image(image_path)

if __name__ == "__main__":
    main()
