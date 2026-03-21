import re
from appium.webdriver.common.appiumby import AppiumBy


def exists_text_exact(driver, text: str) -> bool:
    """텍스트 정확 일치 요소 존재 여부 확인"""
    try:
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{text}")',
        )
        return True
    except Exception:
        return False


def exists_text_contains(driver, text: str) -> bool:
    """텍스트 부분 일치 요소 존재 여부 확인"""
    try:
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{text}")',
        )
        return True
    except Exception:
        return False


def exists_text(driver, text: str) -> bool:
    """정확 일치 또는 부분 일치로 텍스트 존재 여부 확인"""
    return exists_text_exact(driver, text) or exists_text_contains(driver, text)


def find_text_element(driver, text: str):
    """
    현재 화면에서 텍스트 요소 탐색 (자동 스크롤 없음).
    정확 일치 실패 시 부분 일치로 재시도.
    """
    try:
        return driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{text}")',
        )
    except Exception:
        pass
    return driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        f'new UiSelector().textContains("{text}")',
    )


def tap_text(driver, text: str):
    """텍스트 요소를 찾아 탭"""
    find_text_element(driver, text).click()


def assert_any_text(driver, candidates: list):
    """후보 텍스트 중 하나라도 화면에 존재하면 통과"""
    for t in candidates:
        if exists_text(driver, t):
            return
    raise AssertionError(f"화면 검증 실패: {candidates} 중 어떤 텍스트도 찾지 못함")


def parse_bounds(bounds: str):
    """'[x1,y1][x2,y2]' 형식의 bounds 문자열을 (x1, y1, x2, y2) 튜플로 변환"""
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not m:
        return None
    return tuple(map(int, m.groups()))


def tap_element_center(driver, el):
    """요소의 중앙 좌표를 직접 탭"""
    bounds = el.get_attribute("bounds")
    parsed = parse_bounds(bounds)
    if not parsed:
        raise AssertionError(f"element bounds 파싱 실패: {bounds}")
    x1, y1, x2, y2 = parsed
    driver.tap([((x1 + x2) // 2, (y1 + y2) // 2)])
