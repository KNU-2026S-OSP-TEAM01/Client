"""
PlateDetector 모듈 테스트.

학습된 모델 파일(models/best.pt)이 필요하므로,
모델이 없는 경우 자동으로 skip한다.

실행 방법:
    pytest tests/test_detector.py -v
"""
import os
import sys
import numpy as np
import pytest

# src 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.detector import PlateDetector
from src.client.models import PlateDetection


MODEL_PATH = "models/best.pt"

# 모델 파일이 없으면 모든 테스트 skip
pytestmark = pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="학습된 모델(models/best.pt)이 없어서 테스트 skip"
)


def test_detector_초기화():
    """모델 로드가 정상적으로 동작하는지"""
    detector = PlateDetector(MODEL_PATH)
    assert detector is not None
    assert detector.conf_threshold == 0.5


def test_detect_빈_이미지에서는_빈_리스트_반환():
    """검은 이미지에는 번호판이 없으므로 빈 리스트가 나와야 한다"""
    detector = PlateDetector(MODEL_PATH)
    black_image = np.zeros((640, 640, 3), dtype=np.uint8)

    result = detector.detect(black_image)
    assert isinstance(result, list)
    assert len(result) == 0


def test_detect_반환_타입_확인():
    """detect()는 PlateDetection 객체 리스트를 반환해야 한다"""
    detector = PlateDetector(MODEL_PATH)
    # 실제 번호판이 있는 이미지 사용
    test_image_path = "data/processed/val/images"
    if not os.path.exists(test_image_path):
        pytest.skip("검증 이미지가 없음")

    # val 이미지 하나 골라서 테스트
    from src.client.detector import load_image
    image_files = [f for f in os.listdir(test_image_path) if f.endswith(".jpg")]
    if not image_files:
        pytest.skip("검증 이미지가 없음")

    image_path = os.path.join(test_image_path, image_files[0])
    image = load_image(image_path)
    if image is None:
        pytest.skip("이미지 로드 실패")

    result = detector.detect(image)
    assert isinstance(result, list)

    # 검출된 게 있으면 PlateDetection 타입인지 확인
    for detection in result:
        assert isinstance(detection, PlateDetection)
        assert len(detection.bbox) == 4
        assert 0 <= detection.confidence <= 1