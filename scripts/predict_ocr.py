"""
학습된 YOLO + EasyOCR로 검증 이미지에서 번호판을 인식하는 통합 테스트 스크립트.

사용법:
    python scripts/predict_ocr.py
"""
import os
import sys
import random

import cv2

# 프로젝트 루트를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.recognizer import PlateRecognizer
from src.client.detector import load_image


MODEL_PATH = "models/best.pt"
VAL_IMAGES_DIR = "data/processed/val/images"
OUTPUT_DIR = "runs/predict_ocr"
NUM_SAMPLES = 10


def draw_results(image, results):
    """인식 결과를 이미지에 그린다."""
    for r in results:
        x1, y1, x2, y2 = r.bbox
        # 초록색 박스
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # 인식된 번호판 텍스트 + 신뢰도
        label = f"{r.plate_number} ({r.confidence:.2f})"
        cv2.putText(
            image, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )
    return image


def save_image(image, output_path):
    """이미지 저장 (한글 경로 대응)"""
    success, encoded = cv2.imencode(".jpg", image)
    if success:
        encoded.tofile(output_path)


def main():
    print("=" * 60)
    print("번호판 인식 통합 테스트 (YOLO + EasyOCR)")
    print("=" * 60)
    print(f"  모델: {MODEL_PATH}")
    print(f"  입력: {VAL_IMAGES_DIR}")
    print(f"  출력: {OUTPUT_DIR}")

    # 모델 파일 확인
    if not os.path.exists(MODEL_PATH):
        print(f"\n  ERROR: 모델 파일이 없습니다. 먼저 학습을 진행하세요.")
        return

    print("\n  PlateRecognizer 로드 중... (수 초 소요)")
    recognizer = PlateRecognizer(MODEL_PATH, use_gpu=True)
    print("  로드 완료\n")

    # 출력 폴더 준비
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 검증 이미지 랜덤 샘플링
    all_images = [f for f in os.listdir(VAL_IMAGES_DIR) if f.endswith(".jpg")]
    random.seed(42)
    samples = random.sample(all_images, min(NUM_SAMPLES, len(all_images)))
    print(f"  샘플 {len(samples)}개 추론 시작\n")

    # 추론 + 시각화
    total_recognized = 0
    for image_name in samples:
        image_path = os.path.join(VAL_IMAGES_DIR, image_name)
        image = load_image(image_path)
        if image is None:
            print(f"  이미지 로드 실패: {image_name}")
            continue

        # 인식
        results = recognizer.recognize(image)
        total_recognized += len(results)

        # 박스 + 텍스트 그리기
        result_image = draw_results(image.copy(), results)

        # 저장
        output_path = os.path.join(OUTPUT_DIR, image_name)
        save_image(result_image, output_path)

        # 콘솔 출력
        if results:
            plates_str = ", ".join([f"{r.plate_number}({r.confidence:.2f})" for r in results])
            print(f"  {image_name}: {plates_str}")
        else:
            print(f"  {image_name}: 인식 실패")

    print(f"\n총 인식: {total_recognized}개 / {len(samples)}장")
    print(f"인식률: {total_recognized / len(samples) * 100:.1f}%")
    print(f"결과 이미지: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()