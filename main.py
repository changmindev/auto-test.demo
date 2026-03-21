import os
import json
import time
from pathlib import Path

from config import EXCEL_PATH, EXCEL_SHEET, CONTINUE_ON_FAIL, KEEP_SKIP_IN_REPORT
from driver import build_driver
from core.artifacts import make_run_dir, zip_artifacts
from core.loader import load_cases
from core.reporter import make_html_report
from core.runner import UnsupportedStep, assert_start_screen, collect_failure_artifacts, run_step
from utils.adb_helper import start_logcat, stop_logcat


def main():
    run_dir = make_run_dir()
    print(f"[RUN DIR] {run_dir}")

    logcat_proc, _ = start_logcat(run_dir)
    driver = build_driver()
    results = []

    try:
        assert_start_screen(driver)
        cases = load_cases(EXCEL_PATH, EXCEL_SHEET)

        if not cases:
            raise RuntimeError(
                "실행할 TC가 없습니다. config.py의 START_TC_ID / END_TC_ID 또는 엑셀 파일을 확인하세요."
            )

        for i, row in enumerate(cases, start=1):
            tc_id     = row["tc_id"]
            step_name = f"{i}_{row['test_item'][:30]}"
            print(f"[{i:03}] {tc_id} | {row['test_item']} => {row['expected']}")

            record = {
                "tc_id":       tc_id,
                "state":       row["state"],
                "test_item":   row["test_item"],
                "expected":    row["expected"],
                "status":      "PASS",
                "error":       "",
                "screenshot":  "",
                "pagesource":  "",
                "duration_ms": 0,
            }

            start_ts = time.time()
            try:
                run_step(driver, row)

            except UnsupportedStep as e:
                record["status"] = "SKIP"
                record["error"]  = str(e)

            except Exception as e:
                record["status"] = "FAIL"
                record["error"]  = repr(e)
                png_path, xml_path = collect_failure_artifacts(driver, run_dir, tc_id, step_name)
                record["screenshot"] = os.path.relpath(png_path, run_dir)
                record["pagesource"] = os.path.relpath(xml_path, run_dir)

                if not CONTINUE_ON_FAIL:
                    record["duration_ms"] = int((time.time() - start_ts) * 1000)
                    results.append(record)
                    raise

            record["duration_ms"] = int((time.time() - start_ts) * 1000)

            if record["status"] != "SKIP" or KEEP_SKIP_IN_REPORT:
                results.append(record)

        (run_dir / "results.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        report_path = make_html_report(run_dir, results)
        print(f"[REPORT] {report_path}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        stop_logcat(logcat_proc)

    zip_path = zip_artifacts(run_dir)
    print(f"[ZIP]    {zip_path}")


if __name__ == "__main__":
    main()
