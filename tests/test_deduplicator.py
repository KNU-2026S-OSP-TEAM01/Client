"""
Deduplicator 모듈 테스트.

datetime.now()를 직접 호출하지 않고 now 인자로 시각을 주입하여
time.sleep 없이 빠르게 테스트한다.
"""
import os
import sys
from datetime import datetime, timedelta

# src 폴더를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client.deduplicator import Deduplicator


# 테스트용 기준 시각
T0 = datetime(2026, 5, 22, 12, 0, 0)


def test_처음_본_번호판은_송신():
    """처음 보는 번호판은 무조건 송신해야 한다"""
    dedup = Deduplicator(cooldown_seconds=30)
    assert dedup.should_send("12가3456", now=T0) is True


def test_cooldown_안에_들어오면_차단():
    """cooldown 시간 안에 다시 오면 송신하지 않는다"""
    dedup = Deduplicator(cooldown_seconds=30)

    # 첫 송신
    dedup.should_send("12가3456", now=T0)

    # 10초 후 → 차단
    t1 = T0 + timedelta(seconds=10)
    assert dedup.should_send("12가3456", now=t1) is False


def test_cooldown_경계값에서_송신():
    """cooldown 시간 정확히 지나면 송신한다"""
    dedup = Deduplicator(cooldown_seconds=30)
    dedup.should_send("12가3456", now=T0)

    # 30초 후 → 송신 (>= 30이면 통과)
    t1 = T0 + timedelta(seconds=30)
    assert dedup.should_send("12가3456", now=t1) is True


def test_cooldown_지난_후_다시_송신():
    """cooldown 시간 지나면 다시 송신한다"""
    dedup = Deduplicator(cooldown_seconds=30)
    dedup.should_send("12가3456", now=T0)

    # 60초 후 → 송신
    t1 = T0 + timedelta(seconds=60)
    assert dedup.should_send("12가3456", now=t1) is True


def test_서로_다른_번호판은_독립적():
    """다른 번호판은 서로 영향을 주지 않는다"""
    dedup = Deduplicator(cooldown_seconds=30)
    dedup.should_send("12가3456", now=T0)

    # 같은 시각에 다른 번호판 → 송신
    assert dedup.should_send("78바9012", now=T0) is True


def test_연속_차단():
    """cooldown 안에서 여러 번 들어와도 계속 차단"""
    dedup = Deduplicator(cooldown_seconds=30)
    dedup.should_send("12가3456", now=T0)

    # 5초 후, 10초 후, 20초 후 모두 차단
    for sec in [5, 10, 20]:
        t = T0 + timedelta(seconds=sec)
        assert dedup.should_send("12가3456", now=t) is False


def test_reset_후_다시_송신():
    """reset 호출하면 캐시가 비워져 다시 송신한다"""
    dedup = Deduplicator(cooldown_seconds=30)
    dedup.should_send("12가3456", now=T0)

    # 5초 후 → 차단됨
    t1 = T0 + timedelta(seconds=5)
    assert dedup.should_send("12가3456", now=t1) is False

    # reset 후 같은 시각에 다시 → 송신
    dedup.reset()
    assert dedup.should_send("12가3456", now=t1) is True


def test_cooldown_갱신():
    """송신할 때마다 cooldown 시각이 갱신된다"""
    dedup = Deduplicator(cooldown_seconds=30)

    # T0에 송신
    dedup.should_send("12가3456", now=T0)

    # 40초 후 → 송신 (cooldown 지남)
    t1 = T0 + timedelta(seconds=40)
    dedup.should_send("12가3456", now=t1)

    # t1 기준 20초 후 → 차단되어야 함 (t1에서 다시 cooldown 시작)
    t2 = t1 + timedelta(seconds=20)
    assert dedup.should_send("12가3456", now=t2) is False