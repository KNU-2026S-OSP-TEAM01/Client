"""RecognitionBuffer 단위 테스트."""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.client.buffer import RecognitionBuffer


def test_빈_버퍼는_None_반환():
    buf = RecognitionBuffer()
    assert buf.get_consensus() is None


def test_min_count_미달이면_None():
    buf = RecognitionBuffer(min_count=5)
    for _ in range(4):
        buf.add("12가3456", 0.9)
    assert buf.get_consensus() is None


def test_min_count_충족하고_신뢰도_충분하면_반환():
    buf = RecognitionBuffer(min_count=5, min_avg_conf=0.7)
    for _ in range(5):
        buf.add("12가3456", 0.9)
    assert buf.get_consensus() == "12가3456"


def test_min_count_충족해도_평균_신뢰도_부족하면_None():
    buf = RecognitionBuffer(min_count=5, min_avg_conf=0.7)
    for _ in range(5):
        buf.add("12가3456", 0.5)
    assert buf.get_consensus() is None


def test_window_초과시_오래된_것_떨어짐():
    """전혀 다른 plate는 다른 그룹으로 분리."""
    buf = RecognitionBuffer(window_size=5, min_count=3, similarity_threshold=1)
    for _ in range(5):
        buf.add("11가1111", 0.9)
    for _ in range(3):
        buf.add("99나9999", 0.9)
    assert buf.get_consensus() == "99나9999"


def test_reset_후_None():
    buf = RecognitionBuffer(min_count=2)
    buf.add("12가3456", 0.9)
    buf.add("12가3456", 0.9)
    assert buf.get_consensus() == "12가3456"
    buf.reset()
    assert buf.get_consensus() is None


def test_평균_신뢰도_경계값():
    buf = RecognitionBuffer(min_count=3, min_avg_conf=0.7)
    buf.add("12가3456", 0.7)
    buf.add("12가3456", 0.8)
    buf.add("12가3456", 0.9)
    assert buf.get_consensus() == "12가3456"


# === Levenshtein 그룹화 ===

def test_유사도_그룹화_정확_plate_우선():
    """편집거리 1 이내는 같은 그룹. 그룹 내 빈도 높은 plate 반환."""
    buf = RecognitionBuffer(min_count=5, similarity_threshold=1, min_avg_conf=0.7)
    for _ in range(4):
        buf.add("381어7717", 0.9)
    buf.add("38어7717", 0.78)  # 한 글자 누락 오탐
    # 그룹 크기 5, 빈도 높은 381어7717 반환
    assert buf.get_consensus() == "381어7717"


def test_그룹_내_빈도_낮은_오탐_여러개():
    """오탐이 여러 번 섞여도 정확 plate 빈도가 더 높으면 정확 plate 반환."""
    buf = RecognitionBuffer(window_size=15, min_count=5, similarity_threshold=1, min_avg_conf=0.7)
    for _ in range(3):
        buf.add("38어7717", 0.8)
    for _ in range(7):
        buf.add("381어7717", 0.9)
    assert buf.get_consensus() == "381어7717"


def test_similarity_threshold_0_엄격_매칭():
    """threshold 0이면 정확 일치만 같은 그룹."""
    buf = RecognitionBuffer(min_count=5, similarity_threshold=0, min_avg_conf=0.7)
    for _ in range(3):
        buf.add("38어7717", 0.9)
    for _ in range(3):
        buf.add("381어7717", 0.9)
    # 각각 3개라 min_count 5 못 채움
    assert buf.get_consensus() is None


# === mark_sent / suppress ===

def test_mark_sent_후_같은_plate_거부():
    buf = RecognitionBuffer(min_count=3, suppress_seconds=30)
    buf.mark_sent("12가3456")
    for _ in range(5):
        buf.add("12가3456", 0.9)
    assert buf.get_consensus() is None


def test_mark_sent_후_유사_plate도_거부():
    buf = RecognitionBuffer(min_count=3, similarity_threshold=1, suppress_seconds=30)
    buf.mark_sent("381어7717")
    for _ in range(5):
        buf.add("38어7717", 0.9)
    assert buf.get_consensus() is None


def test_mark_sent은_버퍼에_쌓인_유사_plate도_제거():
    buf = RecognitionBuffer(min_count=3, similarity_threshold=1, min_avg_conf=0.7)
    for _ in range(5):
        buf.add("381어7717", 0.9)
    for _ in range(3):
        buf.add("99나9999", 0.9)
    buf.mark_sent("381어7717")
    assert buf.get_consensus() == "99나9999"


def test_suppress_만료_후_다시_받음():
    buf = RecognitionBuffer(min_count=3, suppress_seconds=30, min_avg_conf=0.7)
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    buf.mark_sent("12가3456", now=t0)
    t_after = t0 + timedelta(seconds=31)
    for _ in range(3):
        buf.add("12가3456", 0.9, now=t_after)
    assert buf.get_consensus() == "12가3456"


def test_다른_차는_suppress_영향_안받음():
    buf = RecognitionBuffer(min_count=3, similarity_threshold=1, suppress_seconds=30, min_avg_conf=0.7)
    buf.mark_sent("12가3456")
    for _ in range(5):
        buf.add("99나9999", 0.9)
    assert buf.get_consensus() == "99나9999"