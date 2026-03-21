import re
import time

# 화면 전환·애니메이션이 느린 케이스에서 추가 대기가 필요한 키워드
_ANIMATION_KEYWORDS = [
    "학습 시작", "인트로", "quiz", "퀴즈", "practice", "writing",
    "start", "complete", "animation", "애니메이션",
]


def wait_ms(ms: int):
    """밀리초 단위 대기"""
    time.sleep(max(ms, 0) / 1000.0)


def get_tc_number(tc_id: str) -> int:
    """TC ID에서 숫자 추출.  예) 'TC-023' → 23"""
    m = re.search(r"(\d+)", tc_id or "")
    return int(m.group(1)) if m else -1


def needs_extra_animation_wait(row: dict) -> bool:
    """TC 번호 또는 내용 기반으로 애니메이션 추가 대기 필요 여부 결정"""
    tc_num = get_tc_number(row.get("tc_id", ""))
    text = " ".join([
        row.get("state", ""),
        row.get("test_item", ""),
        row.get("expected", ""),
    ]).lower()
    return tc_num >= 30 or any(k.lower() in text for k in _ANIMATION_KEYWORDS)


def step_sleep(row: dict, base_ms: int = 800, extra_ms: int = 0):
    """
    액션 후 대기.
    애니메이션이 예상되는 화면이면 1400ms 추가 대기 적용.
    """
    ms = base_ms + extra_ms
    if needs_extra_animation_wait(row):
        ms += 1400
    wait_ms(ms)
