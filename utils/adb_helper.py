import subprocess
from pathlib import Path


def adb(*args, timeout: int = 20) -> subprocess.CompletedProcess:
    """adb 명령어 실행"""
    return subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def adb_keyevent(key_code: int):
    """adb shell input keyevent 실행"""
    adb("shell", "input", "keyevent", str(key_code), timeout=10)


def is_keyboard_shown() -> bool:
    """소프트 키보드 노출 여부 확인"""
    try:
        out = adb("shell", "dumpsys", "input_method", timeout=10)
        txt = (out.stdout or "") + "\n" + (out.stderr or "")
        return any(p in txt for p in [
            "mInputShown=true",
            "mIsInputViewShown=true",
            "isInputViewShown=true",
            "mImeWindowVis=0x1",
            "mImeWindowVis=0x3",
        ])
    except Exception:
        return False


def start_logcat(run_dir: Path):
    """logcat 수집 시작 → (process, log_path) 반환"""
    log_path = run_dir / "logs" / "adb_logcat.txt"
    try:
        adb("logcat", "-c")
    except Exception:
        pass
    proc = subprocess.Popen(
        ["adb", "logcat", "-v", "time"],
        stdout=open(log_path, "w", encoding="utf-8", errors="ignore"),
        stderr=subprocess.STDOUT,
    )
    return proc, log_path


def stop_logcat(proc):
    """logcat 수집 종료"""
    try:
        proc.terminate()
    except Exception:
        pass
