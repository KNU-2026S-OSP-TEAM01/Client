"""RecognitionBuffer — OCR 오탐 줄이기용 다수결 + 유사도 그룹화 + suppress.

흐름:
1. add(): 새 OCR 결과를 누적. suppress 중인 plate(또는 유사 plate)는 무시.
2. get_consensus(): 편집거리 ≤ threshold 인 plate끼리 그룹화 →
   가장 큰 그룹이 min_count/min_avg_conf 만족하면 그룹 내 최빈 plate 반환.
3. mark_sent(): 송신 직후 호출. 해당 plate를 suppress_seconds 동안 거부 +
   현재 버퍼에서 유사 plate 모두 제거.
"""
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class _Entry:
    plate: str
    confidence: float


def _levenshtein(a: str, b: str) -> int:
    """편집거리 (삽입/삭제/치환 횟수)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            insert = curr[-1] + 1
            delete = prev[j] + 1
            replace = prev[j - 1] + (ca != cb)
            curr.append(min(insert, delete, replace))
        prev = curr
    return prev[-1]


class RecognitionBuffer:
    """OCR 결과 누적 + 유사도 그룹 다수결 + 송신 후 suppress."""

    def __init__(
        self,
        window_size: int = 10,
        min_count: int = 5,
        min_avg_conf: float = 0.7,
        similarity_threshold: int = 1,
        suppress_seconds: int = 30,
    ):
        self._window_size = window_size
        self._min_count = min_count
        self._min_avg_conf = min_avg_conf
        self._similarity_threshold = similarity_threshold
        self._suppress_seconds = suppress_seconds
        self._buffer: deque[_Entry] = deque(maxlen=window_size)
        self._suppressed: dict[str, datetime] = {}

    def _is_similar(self, a: str, b: str) -> bool:
        return _levenshtein(a, b) <= self._similarity_threshold

    def _purge_expired_suppress(self, now: datetime) -> None:
        expired = [p for p, until in self._suppressed.items() if now >= until]
        for p in expired:
            del self._suppressed[p]

    def add(self, plate: str, confidence: float, now: Optional[datetime] = None) -> None:
        """새 OCR 결과를 추가. suppress 중인 plate와 유사하면 무시."""
        now = now or datetime.now()
        self._purge_expired_suppress(now)
        for sup_plate in self._suppressed:
            if self._is_similar(plate, sup_plate):
                return
        self._buffer.append(_Entry(plate=plate, confidence=confidence))

    def get_consensus(self) -> Optional[str]:
        """편집거리 그룹 다수결 + 평균 신뢰도 조건 만족하는 대표 plate 반환."""
        if not self._buffer:
            return None

        # 그룹화: 첫 entry의 plate를 기준으로 유사 plate 묶음
        groups: list[list[_Entry]] = []
        for entry in self._buffer:
            placed = False
            for group in groups:
                if self._is_similar(entry.plate, group[0].plate):
                    group.append(entry)
                    placed = True
                    break
            if not placed:
                groups.append([entry])

        winner = max(groups, key=len)
        if len(winner) < self._min_count:
            return None

        avg_conf = sum(e.confidence for e in winner) / len(winner)
        if avg_conf < self._min_avg_conf:
            return None

        # 그룹 내 가장 자주 나온 plate (정확한 인식 우선)
        plate_counts = Counter(e.plate for e in winner)
        return plate_counts.most_common(1)[0][0]

    def mark_sent(self, plate: str, now: Optional[datetime] = None) -> None:
        """송신 직후 호출. suppress 시작 + 버퍼에서 유사 plate 제거."""
        now = now or datetime.now()
        self._suppressed[plate] = now + timedelta(seconds=self._suppress_seconds)
        self._buffer = deque(
            (e for e in self._buffer if not self._is_similar(e.plate, plate)),
            maxlen=self._window_size,
        )

    def reset(self) -> None:
        """모든 기록 초기화."""
        self._buffer.clear()
        self._suppressed.clear()