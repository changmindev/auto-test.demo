from appium.webdriver.common.appiumby import AppiumBy
from actions.elements import tap_element_center
from actions.tap import tap_outside_for_keyboard
from utils.adb_helper import adb_keyevent, is_keyboard_shown
from utils.timing import wait_ms

# 키보드를 닫는 버튼 레이블 목록
_DISMISS_LABELS = {"dismiss", "done", "ok", "확인", "완료", "enter"}


def press_enter_key(driver):
    """IME EditorAction → ADB keyevent 순서로 Enter 키 수행"""
    last_error = None
    for action_name in ["done", "go", "next", "search", "send"]:
        try:
            driver.execute_script("mobile: performEditorAction", {"action": action_name})
            wait_ms(500)
            return
        except Exception as e:
            last_error = e

    for key_code in [66, 160]:
        try:
            adb_keyevent(key_code)
            wait_ms(500)
            return
        except Exception as e:
            last_error = e

    if last_error:
        raise AssertionError(f"Enter 키 수행 실패: {last_error}")


def hide_keyboard_aggressively(driver):
    """여러 방법을 순차 시도하여 소프트 키보드 닫기"""
    attempts = [
        lambda: driver.hide_keyboard(),
        lambda: driver.execute_script("mobile: performEditorAction", {"action": "done"}),
        lambda: adb_keyevent(66),    # ENTER
        lambda: adb_keyevent(111),   # ESCAPE
        lambda: tap_outside_for_keyboard(driver),
        lambda: adb_keyevent(4),     # BACK
    ]
    for fn in attempts:
        try:
            fn()
        except Exception:
            pass
        wait_ms(450)
        if not is_keyboard_shown():
            return
    wait_ms(300)


def tap_keyboard_button(driver, label: str):
    """키보드 위의 버튼(완료·확인 등)을 텍스트/description으로 탭"""
    candidates = [label, label.strip(), label.lower(), label.upper(), label.capitalize()]

    for cand in filter(None, candidates):
        selectors = [
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{cand}")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{cand}")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{cand}")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().descriptionContains("{cand}")'),
        ]
        for by, value in selectors:
            try:
                el = driver.find_element(by, value)
                try:
                    el.click()
                except Exception:
                    tap_element_center(driver, el)
                wait_ms(500)
                if label.lower() in _DISMISS_LABELS:
                    hide_keyboard_aggressively(driver)
                return
            except Exception:
                pass

    if label.lower() in _DISMISS_LABELS:
        hide_keyboard_aggressively(driver)
        return

    raise AssertionError(f'키보드 버튼 탭 실패: "{label}"')
