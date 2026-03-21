from appium.webdriver.common.appiumby import AppiumBy
from actions.elements import tap_element_center


def tap_top_right(driver):
    """우측 상단 아이콘(환경설정 등) 좌표 탭"""
    size = driver.get_window_size()
    driver.tap([(int(size["width"] * 0.93), int(size["height"] * 0.07))])


def tap_first_clickable(driver):
    """화면에서 첫 번째 클릭 가능한 요소 탭"""
    elems = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR,
        "new UiSelector().clickable(true)",
    )
    if not elems:
        raise AssertionError("첫 번째 클릭 가능한 요소를 찾지 못함")
    elems[0].click()


def tap_nth_image(driver, n: int):
    """화면의 n번째 ImageView 탭"""
    imgs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageView")
    if len(imgs) < n:
        raise AssertionError(f"ImageView 개수 부족: expected>={n}, actual={len(imgs)}")
    imgs[n - 1].click()


def tap_outside_for_keyboard(driver):
    """키보드 닫기용 화면 상단 빈 영역 탭"""
    size = driver.get_window_size()
    driver.tap([(int(size["width"] * 0.5), int(size["height"] * 0.18))])
