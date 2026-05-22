"""
번호판 이미지에서 글자를 인식하는 모듈.
EasyOCR 또는 PaddleOCR 등 사용 예정.
"""
import numpy as np


class PlateOCR:
    """번호판 OCR"""

    def __init__(self):
        # TODO: OCR 엔진 초기화 (EasyOCR / PaddleOCR 중 선택)
        pass

    def read(self, plate_image: np.ndarray) -> tuple:
        """
        번호판 이미지에서 글자를 읽는다.

        Args:
            plate_image: 잘라낸 번호판 영역 이미지

        Returns:
            (번호판 문자열, 신뢰도) 튜플. 인식 실패 시 (None, 0.0)
        """
        # TODO: 다음 sub-issue에서 구현
        # 1. OCR 엔진으로 텍스트 추출
        # 2. 공백 제거 (예: "12 가 3456" → "12가3456")
        # 3. 한국 번호판 형식 검증 (선택)
        raise NotImplementedError("다음 sub-issue에서 구현")