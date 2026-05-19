"""
번호판 이미지에서 글자를 읽어 한국 번호판 문자열을 추출하는 모듈.
EasyOCR 한국어 모델을 사용한다.
"""
import re

import easyocr


# 한국 번호판 정규식
# - 구형 자가용/영업용: 12가3456 (숫자 2자리 + 한글 1자 + 숫자 4자리)
# - 신형 자가용: 123가4567 (숫자 3자리 + 한글 1자 + 숫자 4자리)
PLATE_PATTERN = re.compile(r"^\d{2,3}[가-힣]\d{4}$")


class PlateOCR:
    """EasyOCR로 번호판 이미지에서 글자를 읽는 클래스."""

    def __init__(self, use_gpu=True):
        """
        Args:
            use_gpu: GPU 사용 여부 (CUDA 가능하면 True)
        """
        # 한국어 + 영어 (번호판에 영문 섞이는 경우 대비)
        self.reader = easyocr.Reader(["ko", "en"], gpu=use_gpu)

    def read(self, plate_image):
        """
        번호판 이미지에서 글자를 읽는다.

        Args:
            plate_image: 번호판 영역 이미지 (numpy array, BGR)

        Returns:
            (plate_text, confidence) 튜플
            - plate_text: 정규화된 번호판 문자열 (실패 시 빈 문자열)
            - confidence: OCR 신뢰도 (실패 시 0.0)
        """
        # EasyOCR 추론
        results = self.reader.readtext(plate_image)

        if not results:
            return "", 0.0

        # 검출된 모든 텍스트를 합쳐서 번호판 후보 만들기
        # (번호판이 두 줄로 인식될 수 있어서)
        merged_text = ""
        total_confidence = 0.0
        for (_, text, conf) in results:
            merged_text += text
            total_confidence += conf

        # 후처리: 공백/특수문자 제거
        cleaned = clean_text(merged_text)

        # 정규식 검증
        if PLATE_PATTERN.match(cleaned):
            avg_confidence = total_confidence / len(results)
            return cleaned, avg_confidence

        return "", 0.0


def clean_text(text):
    """
    OCR 결과를 정리한다.
    - 공백 제거
    - 특수문자 제거
    - 알파벳/숫자/한글만 남김
    """
    # 공백, 특수문자 제거 (한글, 영문, 숫자만 남김)
    cleaned = re.sub(r"[^가-힣A-Za-z0-9]", "", text)
    return cleaned


def is_valid_korean_plate(text):
    """문자열이 한국 번호판 형식에 맞는지 확인한다."""
    if not text:
        return False
    return bool(PLATE_PATTERN.match(text))