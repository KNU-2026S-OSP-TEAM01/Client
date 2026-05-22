"""
실제 한국 번호판 사진으로 OCR 단독 검증.
AI Hub 데이터는 블러 처리되어 OCR이 못 읽는데,
EasyOCR 자체는 잘 동작하는지 선명한 사진으로 확인한다.

사용법:
    python scripts/test_ocr_real.py
"""
import os
import sys

# 프로젝트 루트를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.ocr import PlateOCR, clean_text, PLATE_PATTERN
from src.client.detector import load_image


TEST_IMAGES_DIR = "data/test_real"


def main():
    print("=" * 60)
    print("EasyOCR 단독 검증 (실제 번호판 사진)")
    print("=" * 60)

    if not os.path.exists(TEST_IMAGES_DIR):
        print(f"  ERROR: {TEST_IMAGES_DIR} 폴더가 없습니다.")
        return

    images = [f for f in os.listdir(TEST_IMAGES_DIR)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if not images:
        print(f"  ERROR: {TEST_IMAGES_DIR} 폴더에 이미지가 없습니다.")
        return

    print(f"\n  PlateOCR 로드 중...")
    ocr = PlateOCR(use_gpu=True)
    print(f"  로드 완료\n")

    print(f"  검증 이미지 {len(images)}장\n")

    for image_name in images:
        image_path = os.path.join(TEST_IMAGES_DIR, image_name)
        image = load_image(image_path)
        if image is None:
            print(f"  {image_name}: 이미지 로드 실패")
            continue

        print(f"  [{image_name}] (크기: {image.shape[1]}x{image.shape[0]})")

        # 1. EasyOCR 원본 결과 (디버깅용)
        raw_results = ocr.reader.readtext(image)
        print(f"    EasyOCR 원본 결과:")
        for (_, text, conf) in raw_results:
            print(f"      '{text}' (신뢰도 {conf:.3f})")

        # 2. 정리된 결과 (정규식 통과한 것만)
        plate_text, plate_conf = ocr.read(image)
        if plate_text:
            print(f"    [OK] 한국 번호판 인식: {plate_text} (신뢰도 {plate_conf:.3f})")
        else:
            # 합쳐서 보면 어떻게 되는지도 보여줌
            merged = "".join([t for (_, t, _) in raw_results])
            cleaned = clean_text(merged)
            print(f"    [FAIL] 한국 번호판 패턴 불일치")
            print(f"      합친 결과: '{merged}' → 정리: '{cleaned}'")

        print()


if __name__ == "__main__":
    main()