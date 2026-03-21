import re


def extract_quoted_text(s: str):
    """큰따옴표 안 텍스트 추출.  예) '버튼 "확인" 탭' → '확인'"""
    if not isinstance(s, str):
        return None
    m = re.search(r'"([^"]+)"', s)
    return m.group(1).strip() if m else None


def extract_bracket_label(s: str):
    """대괄호 안 텍스트 추출.  예) '[저장] 버튼 탭' → '저장'"""
    if not isinstance(s, str):
        return None
    m = re.search(r"\[([^\]]+)\]", s)
    return m.group(1).strip() if m else None


def extract_primary_text_from_expected(expected: str):
    """
    기대결과에서 검증 대상 텍스트 추출.
    큰따옴표 안 텍스트 → 숫자/분수 패턴 순으로 탐색.
    """
    quoted = extract_quoted_text(expected)
    if quoted:
        return quoted
    m = re.search(r"(\d+\s*/\s*\d+(?:\s*\w+)?)", expected or "")
    return m.group(1) if m else None


def normalize_header(value) -> str:
    """엑셀 컬럼명 정규화 (줄바꿈·BOM·공백 제거)"""
    if value is None:
        return ""
    s = str(value)
    for ch in ("\n", "\r", "\ufeff"):
        s = s.replace(ch, "")
    return s.strip()


def find_header_col(headers: dict, *candidates):
    """헤더 dict에서 후보 컬럼명 중 첫 번째 매칭 열 번호 반환"""
    for cand in candidates:
        if cand in headers:
            return headers[cand]
    return None
