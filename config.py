import sys
from pathlib import Path

# stdout UTF-8 강제 (Windows 대응)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─── Appium 서버 ────────────────────────────────────────────────────────────────
APPIUM_SERVER = "http://127.0.0.1:4723"

# ─── 파일 경로 ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
EXCEL_PATH  = BASE_DIR / "testcases.xlsx"
EXCEL_SHEET = "automation_TC"

# ─── 실행 TC 범위 ────────────────────────────────────────────────────────────────
START_TC_ID = "TC-001"
END_TC_ID   = "TC-050"

# ─── 앱 패키지명 ─────────────────────────────────────────────────────────────────
APP_PACKAGE = "com.example.learningapp"

# ─── 실행 옵션 ──────────────────────────────────────────────────────────────────
CONTINUE_ON_FAIL    = True   # FAIL 발생 시 계속 진행 여부
KEEP_SKIP_IN_REPORT = True   # SKIP 결과를 리포트에 포함 여부

# ─── 시작 화면 검증 텍스트 (앱 실행 시 화면에 있어야 할 텍스트) ────────────────
START_SCREEN_TEXTS = [
    "LearnApp",
    "Personal Settings",
    "Environment Settings",
    "My Quiz Score",
    "Listen carefully and select the correct answer.",
]

# ─── 화면 이동 검증 매핑 {화면명: [필수 텍스트 후보]} ───────────────────────────
DESTINATION_ASSERT = {
    "LearnApp 메인 화면":          ["LearnApp", "LEARNAPP"],
    "메인 화면":                   ["LearnApp", "LEARNAPP"],
    "개인설정 페이지":             ["Personal Settings"],
    "코스 선택 페이지":            ["Please select a course to start."],
    "레슨 인트로 화면":   ["Congratulations on starting your first lesson."],
    "레슨 요약 화면": ["Basic Course | Learn Sentences", "Greetings and Basic Expressions"],
    "익히기 인트로 화면":          ["Practice"],
    "쓰기 인트로 화면":            ["Writing"],
    "Quiz 인트로 화면":            ["Quiz"],
    "Quiz 학습 화면":              [
        "Listen carefully and select the correct answer.",
        "Listen and write the matching character.",
    ],
    "기초 Quiz 학습 화면":     ["Listen carefully and select the correct answer."],
    "답 비교 화면":         ["Correct Answer", "Rewrite"],
    "학습 결과 화면":              ["My Quiz Score", "You have completed the lesson."],
    "환경설정 팝업":               ["Environment Settings"],
    "업데이트 확인 팝업":          ["Do you want to check for updates?"],
    "업데이트 결과 팝업":          ["No new updates available."],
    "앱 종료 확인 팝업":           ["Do you want to exit and return to the Manager screen?"],
    "매니저 메인화면":         ["Manager"],
}

# ─── 체크 아이콘 그룹 accessibility ID 매핑 ─────────────────────────────────────
CHECK_ICON_GROUPS = {
    "최근 학습": ["recent_lesson_check_1", "recent_lesson_check_2", "recent_lesson_check_3"],
    "카드 #1":   ["card1_check_1", "card1_check_2", "card1_check_3"],
    "카드 #2":   ["card2_check_1", "card2_check_2", "card2_check_3"],
}

# ─── TC ID → 라디오 버튼 인덱스 고정 매핑 (1=Child, 2=Male, 3=Female) ──────────
RADIO_TC_MAP = {
    "TC-011": 1,   # Child (under 14)
    "TC-012": 2,   # Male (15+)
    "TC-013": 3,   # Female (15+)
    "TC-019": 2,   # 2nd profile creation - Male
}

# ─── 라디오 버튼 resource-id 접두사 ─────────────────────────────────────────────
RADIO_RESOURCE_ID_PREFIX = f"{APP_PACKAGE}:id/radio"
