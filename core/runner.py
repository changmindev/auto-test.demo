import re
import time
from pathlib import Path

from config import START_SCREEN_TEXTS, DESTINATION_ASSERT, RADIO_TC_MAP
from utils.parsers import (
    extract_quoted_text, extract_bracket_label,
    extract_primary_text_from_expected,
)
from utils.timing import step_sleep
from actions.elements import exists_text, assert_any_text, tap_text
from actions.tap import tap_top_right, tap_first_clickable, tap_nth_image
from actions.input_actions import input_first_edit
from actions.keyboard import (
    tap_keyboard_button, press_enter_key, hide_keyboard_aggressively,
)
from actions.radio import (
    extract_radio_index,
    tap_radio_by_index, assert_radio_selected_by_index,
)


class UnsupportedStep(Exception):
    """자동화 대상(AUTO)이지만 아직 구현되지 않은 액션"""
    pass


# ─── 시작 화면 검증 ──────────────────────────────────────────────────────────

def assert_start_screen(driver):
    """앱 시작 화면이 예상대로 열려 있는지 확인"""
    for text in START_SCREEN_TEXTS:
        if exists_text(driver, text):
            print(f"[START OK] 시작 화면 텍스트 확인: {text}")
            return
    raise AssertionError(
        f"시작 화면이 예상과 다릅니다. expected one of: {START_SCREEN_TEXTS}"
    )


# ─── 실패 증거 수집 ──────────────────────────────────────────────────────────

def collect_failure_artifacts(driver, run_dir: Path, tc_id: str, step_name: str):
    """FAIL 발생 시 스크린샷과 page source 저장"""
    safe_id   = re.sub(r"[^A-Za-z0-9_.-]+", "_", tc_id or "unknown")
    safe_step = re.sub(r"[^A-Za-z0-9_.-]+", "_", step_name or "step")

    png_path = run_dir / "screenshots" / f"{safe_id}__{safe_step}.png"
    try:
        driver.save_screenshot(str(png_path))
    except Exception:
        pass

    xml_path = run_dir / "pagesource" / f"{safe_id}__{safe_step}.xml"
    try:
        xml_path.write_text(driver.page_source, encoding="utf-8", errors="ignore")
    except Exception:
        pass

    return png_path, xml_path


# ─── 기대결과 검증 ───────────────────────────────────────────────────────────

def _assert_destination(driver, expected: str) -> bool:
    """화면 이동 기대결과 검증 (DESTINATION_ASSERT 매핑 기반)"""
    for dest, must_have in DESTINATION_ASSERT.items():
        if dest in (expected or ""):
            time.sleep(0.6)
            assert_any_text(driver, must_have)
            return True
    return False


def _assert_expected_text(driver, expected: str) -> bool:
    """기대결과에서 텍스트를 추출해 화면 노출 여부 검증"""
    text = extract_primary_text_from_expected(expected)
    if text:
        assert exists_text(driver, text), f'기대 텍스트 미노출: "{text}"'
        return True
    return False


def _assert_correct_wrong_sum(driver, expected: str):
    """퀴즈 정답/오답 합계 검증 (정답+오답 = 10)"""
    nums = re.findall(r"\((\d+)\)", expected or "")
    if len(nums) < 2:
        raise AssertionError(f"정답/오답 숫자 파싱 실패: {expected}")

    correct = int(nums[0])
    wrong   = int(nums[1])

    if correct + wrong != 10:
        raise AssertionError(f"정답+오답 합 불일치: {correct}+{wrong} != 10")

    if exists_text(driver, "Correct"):
        assert exists_text(driver, str(correct)), f'정답 개수 "{correct}" 미노출'
    if exists_text(driver, "Incorrect"):
        assert exists_text(driver, str(wrong)), f'오답 개수 "{wrong}" 미노출'


def post_assert(driver, expected: str):
    """액션 수행 후 공통 기대결과 검증"""
    if not expected:
        return

    if "정답(" in expected and "오답(" in expected and "합" in expected:
        _assert_correct_wrong_sum(driver, expected)
        return

    if _assert_destination(driver, expected):
        return

    if _assert_expected_text(driver, expected):
        return

    if "닫힌다" in expected:
        return


# ─── TC 1개 실행 ─────────────────────────────────────────────────────────────

def run_step(driver, row: dict):
    """
    TC 행 하나를 읽어 액션을 실행하고 기대결과를 검증.
    SKIP 플래그가 있으면 UnsupportedStep 예외 발생.
    """
    test_item = row["test_item"]
    expected  = row["expected"]

    if row["auto_flag"] == "SKIP":
        raise UnsupportedStep(row["reason"] or "SKIP으로 표시됨")

    # 0) 키보드 닫기 버튼 탭
    if "노출된 키보드" in test_item and "탭" in test_item:
        label = extract_quoted_text(test_item) or "Dismiss"
        tap_keyboard_button(driver, label)
        step_sleep(row, base_ms=700)
        post_assert(driver, expected)
        return

    # 1) 키패드 Enter
    if "키패드 Enter 수행" in test_item:
        press_enter_key(driver)
        step_sleep(row, base_ms=700)
        post_assert(driver, expected)
        return

    # 2) 키패드 완료 버튼
    if "키패드 완료 버튼 탭" in test_item:
        for label in ["완료", "Done", "done", "DONE", "확인", "OK", "ok", "Enter"]:
            try:
                tap_keyboard_button(driver, label)
                step_sleep(row, base_ms=700)
                post_assert(driver, expected)
                return
            except Exception:
                pass
        press_enter_key(driver)
        hide_keyboard_aggressively(driver)
        step_sleep(row, base_ms=700)
        post_assert(driver, expected)
        return

    # 3) 라디오 버튼 선택 (TC 고정 매핑 → 텍스트 추출 → 레이블 순)
    if "라디오 버튼 선택" in test_item:
        hide_keyboard_aggressively(driver)
        step_sleep(row, base_ms=400)

        idx = RADIO_TC_MAP.get(row["tc_id"])

        if idx is None:
            idx = extract_radio_index(test_item)

        if idx is None:
            for label, radio_idx in [("Child", 1), ("Male", 2), ("Female", 3)]:
                if label in test_item:
                    idx = radio_idx
                    break

        if idx is not None:
            print(f"[RADIO] TC={row['tc_id']} → index={idx}")
            tap_radio_by_index(driver, idx)
            step_sleep(row, base_ms=700)
            assert_radio_selected_by_index(driver, idx)
            post_assert(driver, expected)
            return

        raise AssertionError(f"라디오 인덱스 결정 실패: {test_item}")

    # 4) OS Back Key
    if "OS Back Key 수행" in test_item or "OS Back Key 탭" in test_item:
        driver.back()
        step_sleep(row, base_ms=800)
        post_assert(driver, expected)
        return

    # 5) 환경설정 아이콘 탭
    if test_item in ["환경설정 아이콘 탭", "우측 상단 환경설정 버튼 탭"]:
        tap_top_right(driver)
        step_sleep(row, base_ms=800)
        post_assert(driver, expected)
        return

    # 6) 첫 번째 학습 항목 탭
    if "화면 내 첫 번째 학습 항목 탭" in test_item:
        tap_first_clickable(driver)
        step_sleep(row, base_ms=800)
        post_assert(driver, expected)
        return

    # 7) N번째 이미지 선택
    m = re.search(r"9개 이미지 중\s*(\d+)번째 이미지 선택", test_item)
    if m:
        tap_nth_image(driver, int(m.group(1)))
        step_sleep(row, base_ms=800)
        post_assert(driver, expected)
        return

    # 8) 입력창 텍스트 입력
    if "입력창에" in test_item and "입력" in test_item:
        value = extract_quoted_text(test_item)
        if not value:
            raise AssertionError(f"입력값 추출 실패: {test_item}")
        input_first_edit(driver, value, append="기존 닉네임 끝에" in test_item)
        step_sleep(row, base_ms=500)
        post_assert(driver, expected)
        return

    # 9) 버튼 탭
    if "버튼 탭" in test_item:
        label = extract_bracket_label(test_item)
        if not label:
            raise AssertionError(f"버튼 라벨 추출 실패: {test_item}")
        tap_text(driver, label)
        step_sleep(row, base_ms=800)
        post_assert(driver, expected)
        return

    # 10) 버튼 노출 확인
    if "버튼 확인" in test_item:
        label = (
            extract_bracket_label(test_item)
            or extract_bracket_label(expected)
            or extract_quoted_text(expected)
        )
        if not label:
            raise AssertionError(f"버튼 확인 라벨 추출 실패: {test_item} / {expected}")
        assert exists_text(driver, label), f'버튼 미노출: "{label}"'
        return

    # 11) 텍스트 확인
    TEXT_CHECK_KEYWORDS = [
        "텍스트 확인", "문장 확인", "라벨 확인", "타이틀 확인", "레슨명 확인",
        "과정명 텍스트 확인", "학습 통계 텍스트 확인", "진도 안내 텍스트 확인",
    ]
    if any(k in test_item for k in TEXT_CHECK_KEYWORDS):
        target = extract_quoted_text(test_item) or extract_primary_text_from_expected(expected)
        if not target:
            raise AssertionError(f"텍스트 확인 대상 추출 실패: {test_item} / {expected}")
        assert exists_text(driver, target), f'텍스트 미노출: "{target}"'
        return

    # 12) 진행도 / 번호 확인
    PROGRESS_KEYWORDS = [
        "진행도 확인", "진행 번호 확인", "현재 진행 번호 확인", "문제 번호 확인",
        "현재 문제 순서 확인", "레슨 번호 확인", "문제 수 확인",
        "전체 레슨 대비 진행도 확인", "상단 우측 진행 표시 확인", "진도 퍼센트 값 확인",
    ]
    if any(k in test_item for k in PROGRESS_KEYWORDS):
        target = extract_primary_text_from_expected(expected)
        if not target:
            raise AssertionError(f"진행/번호 기대값 추출 실패: {expected}")
        assert exists_text(driver, target), f'기대 텍스트 미노출: "{target}"'
        return

    raise UnsupportedStep(f"미구현 패턴: {test_item}")
