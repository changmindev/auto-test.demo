import re
from appium.webdriver.common.appiumby import AppiumBy
from actions.elements import find_text_element, tap_element_center, parse_bounds
from utils.timing import wait_ms
from config import APP_PACKAGE


# ─── 인덱스 추출 ─────────────────────────────────────────────────────────────

def extract_radio_index(text: str):
    """테스트 항목 텍스트에서 라디오 버튼 순번(1/2/3) 추출"""
    s = (text or "").strip().lower()
    patterns = [
        (r"1\s*번째|첫\s*번째|첫째|radio\s*1|1번", 1),
        (r"2\s*번째|두\s*번째|둘째|radio\s*2|2번", 2),
        (r"3\s*번째|세\s*번째|셋째|radio\s*3|3번", 3),
    ]
    for pattern, idx in patterns:
        if re.search(pattern, s):
            return idx
    return None


def _parse_radio_index_from_label(label: str):
    """레이블 텍스트에서 라디오 버튼 순번 추출"""
    s = (label or "").strip().lower()
    patterns = [
        (r"(?:^|\s)1\s*번째|1번|첫\s*번째", 1),
        (r"(?:^|\s)2\s*번째|2번|두\s*번째", 2),
        (r"(?:^|\s)3\s*번째|3번|세\s*번째", 3),
    ]
    for pat, idx in patterns:
        if re.search(pat, s):
            return idx
    return None


# ─── resource-id 후보 생성 ───────────────────────────────────────────────────

def get_radio_id_candidates(label: str) -> list:
    """레이블 기반으로 시도할 radio resource-id 후보 목록 반환"""
    idx = _parse_radio_index_from_label(label)
    candidates = []
    if idx:
        candidates += [f"{APP_PACKAGE}:id/radio{idx}", f"radio{idx}"]
    # fallback: 마지막으로 확인된 실제 id
    candidates += [f"{APP_PACKAGE}:id/radio3", "radio3"]
    seen, out = set(), []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _find_by_any_id(driver, id_candidates: list):
    """id 후보 목록을 순서대로 시도해 첫 번째 성공한 요소 반환"""
    for rid in id_candidates:
        if not rid:
            continue
        try:
            return driver.find_element(AppiumBy.ID, rid)
        except Exception:
            pass
    return None


# ─── 라디오 요소 + 컨테이너 탐색 ─────────────────────────────────────────────

def _find_radio_and_container(driver, label: str):
    """레이블과 인접한 RadioButton·컨테이너 요소를 다단계로 탐색"""
    label_el = None
    try:
        if label:
            label_el = find_text_element(driver, label)
    except Exception:
        pass

    radio = _find_by_any_id(driver, get_radio_id_candidates(label))
    container = None

    if label:
        strategies = [
            f'new UiSelector().textContains("{label}").fromParent(new UiSelector().resourceId("{APP_PACKAGE}:id/radio3"))',
            f'new UiSelector().textContains("{label}").fromParent(new UiSelector().className("android.widget.RadioButton"))',
            f'new UiSelector().text("{label}").fromParent(new UiSelector().className("android.widget.RadioButton"))',
            f'new UiSelector().textContains("{label}").fromParent(new UiSelector().checkable(true))',
            f'new UiSelector().textContains("{label}").fromParent(new UiSelector().clickable(true))',
        ]
        for ui in strategies:
            try:
                el = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                cls = ((el.get_attribute("className") or "") + " " + (el.tag_name or "")).lower()
                rid = (el.get_attribute("resourceId") or "").lower()
                if "radiobutton" in cls or "radio" in rid:
                    radio = radio or el
                else:
                    container = container or el
            except Exception:
                pass

    return label_el, radio, container


# ─── 선택 상태 검증 ───────────────────────────────────────────────────────────

def assert_radio_selected(driver, label: str):
    """라디오 버튼 선택 상태 검증 (checked/selected 속성 또는 page source 확인)"""
    label_el, radio, container = _find_radio_and_container(driver, label)
    direct_radio = _find_by_any_id(driver, get_radio_id_candidates(label))

    for el in [direct_radio, radio, container, label_el]:
        if not el:
            continue
        for attr in ["checked", "selected"]:
            try:
                if (el.get_attribute(attr) or "").lower() == "true":
                    return
            except Exception:
                pass

    src = driver.page_source
    if any(s in src for s in [
        f'text="{label}" checked="true"',
        f'text="{label}" selected="true"',
        f'resource-id="{APP_PACKAGE}:id/radio3" checked="true"',
        f'resource-id="{APP_PACKAGE}:id/radio3" selected="true"',
        f">{label}<",
    ]):
        return

    raise AssertionError(f'라디오 버튼 선택 검증 실패: "{label}"')


def assert_radio_selected_by_index(driver, idx: int):
    """인덱스로 라디오 버튼 선택 상태 검증"""
    radio = _find_by_any_id(driver, [f"{APP_PACKAGE}:id/radio{idx}", f"radio{idx}"])

    if radio is None:
        try:
            radios = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.RadioButton")
            if len(radios) >= idx:
                radio = radios[idx - 1]
        except Exception:
            pass

    if radio is None:
        raise AssertionError(f"라디오 검증 - 요소를 찾지 못함 (index={idx})")

    checked  = (radio.get_attribute("checked") or "").lower()
    selected = (radio.get_attribute("selected") or "").lower()
    if checked == "true" or selected == "true":
        return

    desc     = (radio.get_attribute("contentDescription") or radio.get_attribute("content-desc") or "").lower()
    text_val = (radio.text or "").lower()
    if any(k in desc or k in text_val for k in ["selected", "checked", "선택"]):
        return

    raise AssertionError(
        f"라디오 선택 검증 실패 (index={idx}) checked={checked}, selected={selected}"
    )


# ─── 탭 액션 ─────────────────────────────────────────────────────────────────

def tap_radio_by_index(driver, idx: int):
    """인덱스(1/2/3)로 라디오 버튼 탭 (resource-id → RadioButton class 순 fallback)"""
    radio = _find_by_any_id(driver, [f"{APP_PACKAGE}:id/radio{idx}", f"radio{idx}"])

    if radio is None:
        try:
            radios = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.RadioButton")
            if len(radios) >= idx:
                radio = radios[idx - 1]
                print(f"[RADIO] fallback by RadioButton class index {idx}")
        except Exception:
            pass

    if radio is None:
        raise AssertionError(f"라디오 버튼을 찾지 못함 (index={idx})")

    last_error = None

    # 1) 직접 click
    try:
        radio.click()
        wait_ms(800)
        return
    except Exception as e:
        last_error = e

    # 2) 좌표 중앙 탭
    try:
        tap_element_center(driver, radio)
        wait_ms(800)
        return
    except Exception as e:
        last_error = e

    # 3) 라디오 오른쪽(텍스트 영역) 탭
    try:
        r = radio.rect
        x = min(int(r["x"] + r["width"] + 60), driver.get_window_size()["width"] - 10)
        y = int(r["y"] + r["height"] / 2)
        driver.tap([(x, y)])
        wait_ms(800)
        return
    except Exception as e:
        last_error = e

    raise AssertionError(f"라디오 버튼 클릭 실패 (index={idx}) / last_error={last_error}")


def tap_radio_by_label(driver, label: str):
    """레이블 텍스트 기준으로 라디오 버튼 탭 (다단계 fallback)"""
    label_el, radio, container = _find_radio_and_container(driver, label)
    direct_radio = _find_by_any_id(driver, get_radio_id_candidates(label))

    actions = []
    if direct_radio:
        actions.append(lambda: direct_radio.click())
        actions.append(lambda: tap_element_center(driver, direct_radio))
    if label_el:
        actions.append(lambda: label_el.click())
        actions.append(lambda: tap_element_center(driver, label_el))
    if radio:
        actions.append(lambda: radio.click())
        actions.append(lambda: tap_element_center(driver, radio))
    if container:
        actions.append(lambda: container.click())
        actions.append(lambda: tap_element_center(driver, container))

    if direct_radio:
        def _tap_right_of_radio():
            bounds = direct_radio.get_attribute("bounds")
            parsed = parse_bounds(bounds)
            if not parsed:
                raise AssertionError("radio bounds 파싱 실패")
            x1, y1, x2, y2 = parsed
            x = min(x2 + 120, driver.get_window_size()["width"] - 5)
            driver.tap([(x, (y1 + y2) // 2)])
        actions.append(_tap_right_of_radio)

    last_error = None
    for action in actions:
        try:
            action()
            wait_ms(700)
            try:
                assert_radio_selected(driver, label)
                return
            except Exception:
                pass
        except Exception as e:
            last_error = e

    raise AssertionError(f'라디오 버튼 선택 실패: "{label}" / last_error={last_error}')
