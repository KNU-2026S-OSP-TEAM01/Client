"""
PlateOCR 모듈 테스트.

EasyOCR 모델 로드는 무거우므로 (수 초 소요),
순수 함수(clean_text, is_valid_korean_plate)만 테스트한다.
실제 OCR 통합 테스트는 scripts/predict_ocr.py로 진행.
"""
import os
import sys

# src 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.ocr import clean_text, is_valid_korean_plate


# ===== clean_text 테스트 =====

def test_clean_text_공백_제거():
    """공백이 제거되어야 한다"""
    assert clean_text("12 가 3456") == "12가3456"


def test_clean_text_특수문자_제거():
    """특수문자가 제거되어야 한다"""
    assert clean_text("12-가.3456!") == "12가3456"


def test_clean_text_빈_문자열():
    """빈 문자열은 그대로 빈 문자열"""
    assert clean_text("") == ""


def test_clean_text_한글_영문_숫자만_남김():
    """한글, 영문, 숫자만 남고 나머지는 제거"""
    assert clean_text("한국ABC123!@#$") == "한국ABC123"


# ===== is_valid_korean_plate 테스트 =====

def test_구형_자가용_번호판():
    """숫자 2자리 + 한글 1자 + 숫자 4자리 (구형)"""
    assert is_valid_korean_plate("12가3456") is True


def test_신형_자가용_번호판():
    """숫자 3자리 + 한글 1자 + 숫자 4자리 (신형)"""
    assert is_valid_korean_plate("123가4567") is True


def test_영업용_번호판():
    """영업용도 같은 형식"""
    assert is_valid_korean_plate("78바9012") is True


def test_숫자_부족():
    """숫자가 부족하면 안 됨"""
    assert is_valid_korean_plate("1가234") is False


def test_한글_없음():
    """한글이 없으면 안 됨"""
    assert is_valid_korean_plate("1234567") is False


def test_영어_포함():
    """영어는 한국 번호판 아님"""
    assert is_valid_korean_plate("12A3456") is False


def test_공백_포함():
    """공백 있으면 안 됨 (clean_text 거쳐야 함)"""
    assert is_valid_korean_plate("12 가 3456") is False


def test_빈_문자열():
    """빈 문자열은 무효"""
    assert is_valid_korean_plate("") is False


def test_None_처리():
    """None도 무효"""
    assert is_valid_korean_plate(None) is False