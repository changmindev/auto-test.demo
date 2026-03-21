import datetime
import zipfile
from pathlib import Path
from config import BASE_DIR


def make_run_dir(base: str = "artifacts") -> Path:
    """타임스탬프 기반 실행 결과 디렉터리 생성 (screenshots/pagesource/logs 포함)"""
    ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = BASE_DIR / base / f"run_{ts}"
    for sub in ("screenshots", "pagesource", "logs"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    return run_dir


def zip_artifacts(run_dir: Path) -> Path:
    """run 디렉터리 전체를 ZIP으로 압축"""
    zip_path = run_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in run_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(run_dir.parent))
    return zip_path
