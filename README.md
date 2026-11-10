# auto-test.demo

Android 앱을 대상으로 한 Appium(UiAutomator2) 기반 Excel-Driven 자동화 도구입니다.
엑셀에 적은 TC 문장(`테스트 항목`)을 읽어 동작을 고르고, `기대결과` 를 화면과 대조한 뒤
결과를 HTML 리포트 · JSON · 실패 시 스크린샷으로 남깁니다.

---

## 요구사항

| 항목 | 버전 / 조건 |
|------|-------------|
| Python | 3.10 이상 |
| Node.js / npm | Appium 2.x 설치용 |
| Appium | 2.x (UiAutomator2 드라이버 포함) — 작성 기준 버전 |
| Android SDK | ADB 설치 필요 |
| 테스트 단말 | USB 디버깅 활성화된 Android 기기 |

---

## 프로젝트 구조

```
auto-test.demo/
│
├── main.py                  # 실행 진입점
├── config.py                # 설정값·매핑 (앱이 바뀌면 여기를 고침)
├── driver.py                # Appium 드라이버 초기화
├── requirements.txt         # 의존성 목록
├── testcases.sample.xlsx    # TC 형식 견본 (10건)
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
│   └── switch.py            # 토글 스위치 상태 변경·검증 (runner 에는 아직 연결 안 됨)
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
# 최초 1회 설치 — 요구사항의 2.x 에 맞춘다 (버전 없이 설치하면 현재 3.x 가 깔린다)
npm install -g appium@2
appium driver install uiautomator2

# 별도 터미널에서 실행
appium
```

### 3. Android 기기 연결 확인

```bash
adb devices
```

### 4. 테스트케이스 파일 준비

`config.py` 의 `EXCEL_PATH` 는 `testcases.xlsx` 를 가리키는데, **이 파일은 저장소에 없습니다.**
실제 TC 에는 앱 정보가 섞이기 쉬워 `.gitignore` 로 막아두었기 때문입니다.

대신 같은 형식의 `testcases.sample.xlsx` (10건)가 들어 있습니다. 예시 앱(LearnApp) 기준 문장이라
실제 앱에 돌리려면 화면 문구에 맞게 고쳐야 합니다. 형식은 기기 없이도 확인할 수 있습니다.

```bash
cp testcases.sample.xlsx testcases.xlsx

# 기기 없이 파싱만 확인 — 헤더 목록과 10 이 출력된다
python -c "from pathlib import Path; from core.loader import load_cases; print(len(load_cases(Path('testcases.sample.xlsx'), 'automation_TC')))"
```

시트명은 `automation_TC`, 1행이 헤더입니다.

| 컬럼 | 필수 | 설명 |
|---|:---:|---|
| `No.` | O | `TC-001` 형식. `config.py` 의 `START_TC_ID`~`END_TC_ID` 로 실행 범위를 자릅니다 |
| `전제조건` | O | 이 TC 가 시작되는 화면 |
| `테스트 항목` | O | 수행할 동작. 이 문장을 파싱해 액션을 고릅니다 (아래 참고) |
| `기대결과` | O | 검증 기준. `"큰따옴표"` 안 텍스트나 `1/10` 형태를 뽑아 대조합니다 |
| `자동화실행` | | `AUTO`(기본) · `MANUAL` · `SKIP`. `MANUAL`·`SKIP` 은 실행하지 않고 SKIP 으로 기록 |
| `자동화사유` | | 자동화하지 않은 이유 |
| `자동화메모` | | 비고 |

`테스트 항목` 문장이 곧 명령입니다. `[저장] 버튼 탭` · `입력창에 "TestUser" 입력` ·
`OS Back Key 수행` · `라디오 버튼 선택 - 첫 번째` 처럼 씁니다.
대괄호·큰따옴표 안의 값이 대상 요소로 추출되고, 어느 패턴에도 맞지 않는 문장은 `미구현 패턴` 으로 SKIP 됩니다.
`기대결과` 의 숫자는 `"1/10"` 처럼 큰따옴표로 감싸 두는 편이 안전합니다(감싸지 않으면 뒤 단어까지 붙어 추출됩니다).

### 5. 앱을 시작 화면에 띄운 뒤 실행

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
| `KEEP_SKIP_IN_REPORT` | SKIP 결과를 리포트에 남길지 여부 |
| `START_SCREEN_TEXTS` | 시작 화면 검증 텍스트 목록 |
| `DESTINATION_ASSERT` | 화면 이동 검증 매핑 |
| `RADIO_TC_MAP` | TC ID → 라디오 버튼 인덱스 고정 매핑 |

---

## 지원 액션 목록

| 테스트 항목 키워드 | 동작 |
|-------------------|------|
| `노출된 키보드 "버튼명" 탭` | 소프트 키보드의 해당 버튼 탭 (기본 `Dismiss`) |
| `키패드 Enter 수행` | IME Enter 키 입력 |
| `키패드 완료 버튼 탭` | 완료/Done/OK 버튼 탭 |
| `라디오 버튼 선택` | 라디오 버튼 탭 + 선택 상태 검증. 순번은 `RADIO_TC_MAP` → 문장의 `첫 번째`·`2번` → `Child`·`Male`·`Female` 순으로 정함 |
| `OS Back Key 수행` | 시스템 Back 키 입력 |
| `환경설정 아이콘 탭` / `우측 상단 환경설정 버튼 탭` | 우측 상단 좌표 탭 |
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
artifacts/run_YYYYMMDD_HHMMSS/      # 정상 종료 시 같은 이름의 .zip 도 생성
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
  ├── driver.py            ← Appium 세션 (현재 화면에 붙음)
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

의존은 `main` → `core` → `actions` → `utils` 한 방향이고, 거꾸로 올라가는 import 는 없습니다(설정값은 모두 `config.py` 에서 읽음).
새 액션은 `actions/` 에 함수를 만들고 `core/runner.py` 의 `run_step()` 에 문장 패턴 분기를 하나 추가하면 됩니다.

---

## 기술 스택

- Python 3.10+
- Appium 2.x + UiAutomator2 · appium-python-client
- openpyxl — Excel TC 파싱
- ADB — logcat 수집 / keyevent 입력

---

## 주의사항

- `testcases.xlsx` 는 민감 데이터가 섞일 수 있어 커밋하지 않습니다 (`.gitignore` 처리됨).
  저장소에 올라가는 건 익명화된 `testcases.sample.xlsx` 뿐입니다.
- 앱 패키지명(`APP_PACKAGE`)·시작 화면 검증 텍스트는 `config.py` 에서 바꿉니다.
  기본값은 실제 앱이 아닌 예시(`com.example.learningapp` · `LearnApp`)입니다.
