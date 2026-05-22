"""
학습된 YOLO 모델로 추론 테스트하는 스크립트.

랜덤하게 val 이미지 몇 장을 골라 번호판 검출 결과를 시각화한다.

사용법:
    python scripts/predict_yolo.py
"""
import os
import sys
import random

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.detector import PlateDetector, load_image


MODEL_PATH = "models/best.pt"
VAL_IMAGES_DIR = "data/processed/val/images"
OUTPUT_DIR = "runs/predict"
NUM_SAMPLES = 10   # 테스트할 이미지 개수


def draw_detections(image, detections):
    """검출 결과를 이미지에 그린다."""
    for det in detections:
        x1, y1, x2, y2 = det.bbox
        # 초록색 박스
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # 신뢰도 표시
        label = f"{det.confidence:.2f}"
        cv2.putText(
            image, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )
    return image


def save_image(image, output_path):
    """이미지 저장 (한글 경로 대응)"""
    success, encoded = cv2.imencode(".jpg", image)
    if success:
        encoded.tofile(output_path)


def main():
    print("YOLO 추론 테스트 시작")
    print(f"  모델: {MODEL_PATH}")
    print(f"  입력: {VAL_IMAGES_DIR}")
    print(f"  출력: {OUTPUT_DIR}")

    # 모델 파일 확인
    if not os.path.exists(MODEL_PATH):
        print(f"  ERROR: 모델 파일이 없습니다. 먼저 학습을 진행하세요.")
        return

    # 디텍터 로드
    detector = PlateDetector(MODEL_PATH, conf_threshold=0.5)

    # 출력 폴더 준비
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 검증 이미지 랜덤 샘플링
    all_images = [f for f in os.listdir(VAL_IMAGES_DIR) if f.endswith(".jpg")]
    random.seed(42)
    samples = random.sample(all_images, min(NUM_SAMPLES, len(all_images)))
    print(f"  샘플 {len(samples)}개 추론 시작\n")

    # 추론 + 시각화
    total_detected = 0
    for image_name in samples:
        image_path = os.path.join(VAL_IMAGES_DIR, image_name)
        image = load_image(image_path)
        if image is None:
            print(f"  이미지 로드 실패: {image_name}")
            continue

        detections = detector.detect(image)
        total_detected += len(detections)

        # 박스 그리기
        result_image = draw_detections(image.copy(), detections)

        # 저장
        output_path = os.path.join(OUTPUT_DIR, image_name)
        save_image(result_image, output_path)

        # 콘솔 출력
        print(f"  {image_name}: {len(detections)}개 검출")

    print(f"\n총 검출: {total_detected}개 (평균 {total_detected / len(samples):.2f}개/이미지)")
    print(f"결과 이미지: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()