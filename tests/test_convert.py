"""
convert_aihub_to_yolo.py의 좌표 변환 함수 테스트.

실행 방법:
    pytest tests/test_convert.py -v
"""
import sys
import os

# scripts 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from convert_aihub_to_yolo import bbox_to_yolo


def test_bbox_가운데에_있을때():
    """이미지 정중앙에 있는 bbox는 (0.5, 0.5)가 되어야 한다."""
    # 1000x1000 이미지의 정중앙에 100x100 bbox
    bbox = [[450, 450], [550, 550]]
    x_c, y_c, w, h = bbox_to_yolo(bbox, 1000, 1000)

    assert x_c == 0.5
    assert y_c == 0.5
    assert w == 0.1
    assert h == 0.1


def test_bbox_왼쪽위_모서리():
    """이미지 왼쪽 위에 있는 bbox 변환"""
    # 1000x500 이미지의 왼쪽 위에 200x100 bbox
    bbox = [[0, 0], [200, 100]]
    x_c, y_c, w, h = bbox_to_yolo(bbox, 1000, 500)

    # x_center = 100/1000 = 0.1
    # y_center = 50/500 = 0.1
    assert x_c == 0.1
    assert y_c == 0.1
    assert w == 0.2
    assert h == 0.2


def test_bbox_오른쪽아래_모서리():
    """이미지 오른쪽 아래에 딱 붙은 bbox 변환"""
    bbox = [[800, 400], [1000, 500]]
    x_c, y_c, w, h = bbox_to_yolo(bbox, 1000, 500)

    # x_center = 900/1000 = 0.9
    # y_center = 450/500 = 0.9
    assert x_c == 0.9
    assert y_c == 0.9


def test_값이_0과_1_사이():
    """변환된 값은 항상 0 ~ 1 사이여야 한다."""
    bbox = [[1317.59, 887.01], [1374.62, 903.41]]
    img_w, img_h = 1920, 1080  # FHD 가정

    x_c, y_c, w, h = bbox_to_yolo(bbox, img_w, img_h)

    assert 0 <= x_c <= 1
    assert 0 <= y_c <= 1
    assert 0 <= w <= 1
    assert 0 <= h <= 1


def test_실제_aihub_데이터_샘플():
    """실제 AI Hub 데이터 예시 변환이 정상 동작하는지"""
    # 실제 SUV_팰리세이드-876.json의 plate.bbox
    bbox = [[1317.5888671875, 887.00732421875],
            [1374.624267578125, 903.405029296875]]
    img_w, img_h = 1920, 1080

    x_c, y_c, w, h = bbox_to_yolo(bbox, img_w, img_h)

    # 작은 번호판이라 width, height는 작아야 함
    assert w < 0.1
    assert h < 0.1
    # 중심점은 이미지 안에 있어야 함
    assert 0 < x_c < 1
    assert 0 < y_c < 1

def test_좌표가_이미지_밖이면_큰값_반환():
    """bbox가 이미지 크기 밖이면 정규화 값이 1을 넘어야 한다.
    이런 경우는 convert_one에서 걸러진다."""
    bbox = [[500, 500], [600, 600]]
    x_c, y_c, w, h = bbox_to_yolo(bbox, 200, 200)

    # 결과가 1을 넘어야 정상 (이런 경우 convert_one에서 걸러야 함)
    assert x_c > 1 or y_c > 1