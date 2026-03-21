import time
from appium.webdriver.common.appiumby import AppiumBy
from config import CHECK_ICON_GROUPS


def get_switch_checked_by_label(driver, label_text: str) -> bool:
    """레이블 텍스트로 Switch 요소를 찾아 현재 ON/OFF 상태 반환"""
    ui = (
        f'new UiSelector().textContains("{label_text}")'
        '.fromParent(new UiSelector().className("android.widget.Switch"))'
    )
    sw = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
    return (sw.get_attribute("checked") or "").lower() == "true"


def set_switch_by_label(driver, label_text: str, to_on: bool):
    """레이블 텍스트로 Switch를 찾아 원하는 상태로 변경 후 검증"""
    ui = (
        f'new UiSelector().textContains("{label_text}")'
        '.fromParent(new UiSelector().className("android.widget.Switch"))'
    )
    sw = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
    current = (sw.get_attribute("checked") or "").lower() == "true"

    if current != to_on:
        sw.click()
        time.sleep(0.4)

    checked_after = (sw.get_attribute("checked") or "").lower() == "true"
    if checked_after != to_on:
        raise AssertionError(
            f'토글 변경 실패: "{label_text}" expected={to_on}, actual={checked_after}'
        )


def read_check_group(driver, key: str) -> list:
    """체크 아이콘 그룹의 선택 상태 목록 반환"""
    from core.runner import UnsupportedStep  # 순환 방지용 지연 import

    if key not in CHECK_ICON_GROUPS:
        raise UnsupportedStep(f"체크 그룹 미정의: {key}")

    states = []
    for aid in CHECK_ICON_GROUPS[key]:
        try:
            el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, aid)
        except Exception:
            raise UnsupportedStep(
                f"체크 아이콘 accessibility id 미존재: {aid} (앱에 selector 추가 필요)"
            )

        found = False
        for attr_name in ("selected", "checked", "enabled"):
            val = (el.get_attribute(attr_name) or "").lower()
            if val in ("true", "false"):
                states.append(val == "true")
                found = True
                break

        if not found:
            states.append(False)

    return states
