from appium.webdriver.common.appiumby import AppiumBy


def input_first_edit(driver, value: str, append: bool = False):
    """
    화면의 첫 번째 EditText에 값 입력.
    append=True 이면 기존 텍스트 뒤에 이어서 입력.
    """
    edits = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
    if not edits:
        raise AssertionError("입력창(EditText)을 찾지 못함")

    edit = edits[0]
    edit.click()

    if not append:
        try:
            edit.clear()
        except Exception:
            pass
        edit.send_keys(value)
    else:
        current = ""
        try:
            current = edit.text or ""
        except Exception:
            pass
        try:
            edit.clear()
        except Exception:
            pass
        edit.send_keys(current + value)
