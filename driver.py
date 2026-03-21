from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import APPIUM_SERVER


def build_driver():
    """
    현재 실행 중인 앱 화면에 attach.
    app_package / app_activity 미지정 → 앱 재시작 없이 현재 화면 그대로 유지.
    """
    opts = UiAutomator2Options()
    opts.platform_name        = "Android"
    opts.automation_name      = "UiAutomator2"
    opts.device_name          = "Android"
    opts.no_reset             = True
    opts.dont_stop_app_on_reset = True
    opts.full_reset           = False

    driver = webdriver.Remote(APPIUM_SERVER, options=opts)
    driver.implicitly_wait(2)
    return driver
