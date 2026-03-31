# 📱 auto-test.demo

Android 앱을 대상으로 한 **Appium(UiAutomator2) 기반 Excel-Driven 자동화 프레임워크**입니다.
Excel로 TC를 관리하고, 실행 결과를 HTML 리포트 + JSON + 스크린샷으로 저장합니다.

---

## 요구사항

| 항목 | 버전 / 조건 |
|------|-------------|
| Python | 3.10 이상 |
| Node.js / npm | Appium 2.x 설치용 |
| Appium | 2.x (UiAutomator2 드라이버 포함) |
| Android SDK | ADB 설치 필요 |
| 테스트 단말 | USB 디버깅 활성화된 Android 기기 |

---

## 프로젝트 구조

```
auto-test.demo/
│
├── main.py                  # 실행 진입점
├── config.py                # 모든 설정값·매핑 (여기만 수정하면 됨)
├── driver.py                # Appium 드라이버 초기화
├── requirements.txt         # 의존성 목록
├── .gitignore
│
├── core/                    # 실행 흐름 제어
│   ├── loader.py            # Excel TC 파싱 및 범위 필터링
│   ├── runner.py            # TC 실행 엔진 + 기대결과 검증
│   ├── reporter.py          # HTML 결과 리포트 생성
│   └── artifacts.py         # 결과 디렉터리 생성 / ZIP 압축
│
├── actions/                 # UI 조작 액션
│   ├── elements.py          # 요소 탐색·존재 확인 헬퍼
│   ├── tap.py               # 탭·클릭 액션
│   ├── input_actions.py     # EditText 텍스트 입력
│   ├── keyboard.py          # 소프트 키보드 처리
│   ├── radio.py             # 라디오 버튼 탭·선택 검증
│   └── switch.py            # 토글 스위치 상태 변경·검증
│
└── utils/                   # 공통 유틸리티
    ├── adb_helper.py        # ADB 명령어 / logcat 수집
    ├── parsers.py           # 문자열·헤더 파싱
    └── timing.py            # wait / 애니메이션 대기
```

---

## 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Appium 서버 설치 및 실행

```bash
# 최초 1회 설치
npm install -g appium
appium driver install uiautomator2

# 별도 터미널에서 실행
appium
```

### 3. Android 기기 연결 확인

```bash
adb devices
```

### 4. 앱을 원하는 시작 화면에 띄운 뒤 실행

```bash
python main.py
```

---

## 설정 변경 (config.py)

| 항목 | 설명 |
|------|------|
| `APPIUM_SERVER` | Appium 서버 주소 |
| `EXCEL_PATH` | TC 엑셀 파일 경로 |
| `EXCEL_SHEET` | 읽을 시트 이름 |
| `START_TC_ID` / `END_TC_ID` | 실행 TC 범위 |
| `APP_PACKAGE` | 앱 패키지명 (라디오 버튼 resource-id에 사용) |
| `CONTINUE_ON_FAIL` | FAIL 발생 시 계속 진행 여부 |
| `START_SCREEN_TEXTS` | 시작 화면 검증 텍스트 목록 |
| `DESTINATION_ASSERT` | 화면 이동 검증 매핑 |
| `RADIO_TC_MAP` | TC ID → 라디오 버튼 인덱스 고정 매핑 |

---

## TC 엑셀 컬럼 구조

| 컬럼 | 필수 | 설명 |
|------|:----:|------|
| `No.` | ✅ | TC ID (예: TC-001) |
| `전제조건` | ✅ | 시작 화면 상태 |
| `테스트 항목` | ✅ | 수행 액션 |
| `기대결과` | ✅ | 검증 기준 |
| `자동화실행` | ⬜ | `AUTO` / `SKIP` |
| `자동화사유` | ⬜ | SKIP 사유 |
| `자동화메모` | ⬜ | 기타 메모 |

---

## 지원 액션 목록

| 테스트 항목 키워드 | 동작 |
|-------------------|------|
| `키패드 Enter 수행` | IME Enter 키 입력 |
| `키패드 완료 버튼 탭` | 완료/Done/OK 버튼 탭 |
| `라디오 버튼 선택` | 라디오 버튼 탭 + 선택 상태 검증 |
| `OS Back Key 수행` | 시스템 Back 키 입력 |
| `환경설정 아이콘 탭` | 우측 상단 좌표 탭 |
| `화면 내 첫 번째 학습 항목 탭` | 첫 번째 클릭 가능 요소 탭 |
| `9개 이미지 중 N번째 이미지 선택` | N번째 ImageView 탭 |
| `입력창에 "값" 입력` | EditText에 텍스트 입력 |
| `[버튼명] 버튼 탭` | 텍스트로 버튼 탭 |
| `버튼 확인` | 버튼 노출 여부 검증 |
| `텍스트 확인` / `문장 확인` 등 | 텍스트 노출 여부 검증 |
| `진행도 확인` / `문제 번호 확인` 등 | 진행 번호 검증 |

---

## 실행 결과물 구조

```
artifacts/run_YYYYMMDD_HHMMSS/
├── report.html        # HTML 테스트 리포트
├── results.json       # JSON 원시 결과
├── screenshots/       # FAIL 발생 시 스크린샷 (.png)
├── pagesource/        # FAIL 발생 시 XML page source
└── logs/
    └── adb_logcat.txt # ADB logcat 전체 로그
```

---

## 아키텍처 의존 방향

```
main.py
  ├── core/loader.py       ← Excel 파싱
  ├── core/runner.py       ← TC 실행 + 검증
  │     ├── actions/elements.py
  │     ├── actions/tap.py
  │     ├── actions/input_actions.py
  │     ├── actions/keyboard.py
  │     └── actions/radio.py
  ├── core/reporter.py     ← HTML 리포트
  ├── core/artifacts.py    ← 파일 관리
  └── utils/               ← 공통 유틸 (단방향, 순환 없음)
```

> `utils` → `actions` → `core` → `main` 단방향 의존 구조.
> 새 액션 추가 시 `actions/` 파일과 `core/runner.py`에 패턴 한 줄만 추가하면 됩니다.

---

## 기술 스택

- **Python 3.10+**
- **Appium 2.x** + UiAutomator2
- **openpyxl** — Excel TC 파싱
- **ADB** — logcat 수집 / keyevent 입력

---

## 주의사항

- `testcases.xlsx`는 민감 데이터가 포함될 수 있으므로 **절대 저장소에 커밋하지 마세요** (`.gitignore` 처리됨).
- 실제 앱 패키지명은 `config.py`의 `APP_PACKAGE`에서 직접 수정하세요.
