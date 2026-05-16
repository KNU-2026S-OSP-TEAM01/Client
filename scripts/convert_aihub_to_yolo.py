"""
AI Hub JSON 어노테이션을 YOLO 형식으로 변환하는 스크립트.

사용법:
    python scripts/convert_aihub_to_yolo.py
"""
import os
import json
import shutil
import random

import cv2
import numpy as np

# 경로 설정
RAW_DIR = "data/raw/aihub-vehicle-plate"
IMAGE_DIR = os.path.join(RAW_DIR, "원천데이터")
LABEL_DIR = os.path.join(RAW_DIR, "라벨링데이터")
OUTPUT_DIR = "data/processed"

# 학습/검증 비율
TRAIN_RATIO = 0.8

# YOLO 클래스 ID (번호판 하나만 사용)
CLASS_ID = 0


def bbox_to_yolo(bbox, img_width, img_height):
    """
    AI Hub bbox를 YOLO 형식으로 변환한다.
    bbox는 [[x1, y1], [x2, y2]] 형태이고,
    YOLO는 (x_center, y_center, width, height)를 0~1로 정규화한 값을 쓴다.
    """
    x1, y1 = bbox[0]
    x2, y2 = bbox[1]

    x_center = (x1 + x2) / 2 / img_width
    y_center = (y1 + y2) / 2 / img_height
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height

    return x_center, y_center, width, height


def find_image_for_json(json_path):
    """
    JSON 파일에 대응하는 이미지 경로를 찾는다.
    못 찾으면 None 반환.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 예: "SUV/현대자동차/SUV_팰리세이드-876.jpg"
    rel_path = data.get("car", {}).get("imagePath")
    if not rel_path:
        return None

    # 원천데이터/차종분류데이터/SUV/SUV/현대자동차/...jpg 구조
    car_type = rel_path.split("/")[0]  # "SUV"
    image_path = os.path.join(IMAGE_DIR, "차종분류데이터", car_type, rel_path)

    if os.path.exists(image_path):
        return image_path
    return None


def convert_one(json_path):
    """
    JSON 하나를 읽어서 YOLO 한 줄로 변환한다.
    실패하면 (None, None) 반환.

    AI Hub plate.bbox는 원본 영상 좌표 기준이지만,
    우리가 가진 이미지는 차량만 크롭한 작은 이미지다.
    따라서 차량 bbox를 기준으로 좌표를 보정한 뒤 정규화한다.
    """
    image_path = find_image_for_json(json_path)
    if image_path is None:
        return None, None

    # 이미지 크기 읽기 (한글 경로 대응)
    image_array = np.fromfile(image_path, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return None, None
    h, w = image.shape[:2]

    # JSON 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    car_bbox = data.get("car", {}).get("bbox")
    plate_bbox = data.get("plate", {}).get("bbox")
    if not car_bbox or not plate_bbox:
        return None, None

    # 차량 bbox 왼쪽 위 좌표를 기준점으로 사용
    car_x1, car_y1 = car_bbox[0]
    # 번호판 좌표를 크롭 이미지 기준으로 보정
    plate_x1 = plate_bbox[0][0] - car_x1
    plate_y1 = plate_bbox[0][1] - car_y1
    plate_x2 = plate_bbox[1][0] - car_x1
    plate_y2 = plate_bbox[1][1] - car_y1

    # 보정된 좌표로 YOLO 형식 변환
    corrected_bbox = [[plate_x1, plate_y1], [plate_x2, plate_y2]]
    x_c, y_c, bw, bh = bbox_to_yolo(corrected_bbox, w, h)

    # 0~1 범위 벗어나면 실패 처리 (잘못된 좌표 거르기)
    if not (0 <= x_c <= 1 and 0 <= y_c <= 1):
        return None, None

    yolo_line = f"{CLASS_ID} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}"
    return yolo_line, image_path


def save_samples(samples, split_name):
    """
    변환된 데이터를 train/ 또는 val/ 폴더에 저장한다.
    samples: [(yolo_line, image_path), ...]
    """
    images_dir = os.path.join(OUTPUT_DIR, split_name, "images")
    labels_dir = os.path.join(OUTPUT_DIR, split_name, "labels")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    for yolo_line, image_path in samples:
        # 이미지 복사
        image_name = os.path.basename(image_path)
        shutil.copy(image_path, os.path.join(images_dir, image_name))

        # 라벨 저장 (이미지와 같은 이름, 확장자 .txt)
        label_name = os.path.splitext(image_name)[0] + ".txt"
        label_path = os.path.join(labels_dir, label_name)
        with open(label_path, "w", encoding="utf-8") as f:
            f.write(yolo_line + "\n")


def write_dataset_yaml():
    """YOLO 학습용 dataset.yaml 파일을 만든다.
    YOLO는 어디서 실행되든 데이터를 찾을 수 있어야 하므로 절대 경로를 사용한다.
    """
    abs_path = os.path.abspath(OUTPUT_DIR).replace("\\", "/")
    yaml_content = f"""path: {abs_path}
train: train/images
val: val/images

names:
  0: license_plate

nc: 1
"""
    yaml_path = os.path.join(OUTPUT_DIR, "dataset.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print(f"  dataset.yaml 생성: {yaml_path}")

def find_all_json_files(root_dir):
    """root_dir 아래의 모든 .json 파일 경로를 리스트로 반환"""
    json_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            if name.endswith(".json"):
                json_files.append(os.path.join(dirpath, name))
    return json_files


def main():
    print("AI Hub -> YOLO 변환 시작")
    print(f"  입력: {LABEL_DIR}")
    print(f"  출력: {OUTPUT_DIR}")

    # 모든 JSON 파일 찾기
    json_files = find_all_json_files(LABEL_DIR)
    print(f"  발견된 JSON: {len(json_files)}개")

    # 하나씩 변환
    success = []
    failed = 0
    for json_path in json_files:
        yolo_line, image_path = convert_one(json_path)
        if yolo_line is None:
            failed += 1
            continue
        success.append((yolo_line, image_path))

    print(f"  변환 성공: {len(success)}개")
    print(f"  변환 실패: {failed}개")

    # train/val 분할 (8:2)
    random.seed(42)
    random.shuffle(success)
    split_idx = int(len(success) * TRAIN_RATIO)
    train_samples = success[:split_idx]
    val_samples = success[split_idx:]

    print(f"  train: {len(train_samples)}개")
    print(f"  val: {len(val_samples)}개")

    # 저장
    print("저장 중...")
    save_samples(train_samples, "train")
    save_samples(val_samples, "val")
    write_dataset_yaml()

    print("완료!")


if __name__ == "__main__":
    main()