from pathlib import Path
from config import EXCEL_PATH, EXCEL_SHEET, START_TC_ID, END_TC_ID

_STATUS_COLOR = {"PASS": "#2e7d32", "FAIL": "#c62828", "SKIP": "#f57f17"}


def _esc(s) -> str:
    return (str(s) if s else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_html_report(run_dir: Path, results: list) -> Path:
    """결과 리스트를 받아 HTML 리포트 파일 생성 후 경로 반환"""
    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    total   = len(results)

    rows_html = []
    for r in results:
        ss = r.get("screenshot", "")
        ps = r.get("pagesource", "")
        links = " ".join(filter(None, [
            f'<a href="{_esc(ss)}">screenshot</a>' if ss else "",
            f'<a href="{_esc(ps)}">pageSource</a>'  if ps else "",
        ]))
        color = _STATUS_COLOR.get(r.get("status", ""), "#333")
        rows_html.append(f"""
            <tr>
              <td>{_esc(r.get("tc_id"))}</td>
              <td>{_esc(r.get("state"))}</td>
              <td>{_esc(r.get("test_item"))}</td>
              <td>{_esc(r.get("expected"))}</td>
              <td style="color:{color};font-weight:bold;text-align:center">{_esc(r.get("status"))}</td>
              <td style="text-align:right">{_esc(str(r.get("duration_ms", "")))}</td>
              <td>{links}</td>
              <td style="white-space:pre-wrap;max-width:560px;font-size:11px">{_esc(r.get("error", ""))}</td>
            </tr>""")

    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <title>Automation Report</title>
  <style>
    body  {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
    h2   {{ color: #1a237e; }}
    .meta {{ font-size: 13px; color: #555; margin-bottom: 12px; }}
    .summary {{ font-size: 15px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff;
             box-shadow: 0 1px 3px rgba(0,0,0,.12); }}
    th, td {{ border: 1px solid #e0e0e0; padding: 8px 10px; vertical-align: top; font-size: 13px; }}
    th   {{ background: #e8eaf6; text-align: center; }}
    tr:hover {{ background: #f3f3f3; }}
  </style>
</head>
<body>
  <h2>📋 Automation Report</h2>
  <div class="meta">
    파일: <code>{_esc(EXCEL_PATH.name)}</code> &nbsp;|&nbsp;
    시트: <code>{_esc(EXCEL_SHEET)}</code> &nbsp;|&nbsp;
    범위: <code>{_esc(START_TC_ID)}</code> ~ <code>{_esc(END_TC_ID)}</code>
  </div>
  <div class="summary">
    전체: <b>{total}</b> &nbsp;|&nbsp;
    <span style="color:#2e7d32">PASS <b>{passed}</b></span> &nbsp;|&nbsp;
    <span style="color:#c62828">FAIL <b>{failed}</b></span> &nbsp;|&nbsp;
    <span style="color:#f57f17">SKIP <b>{skipped}</b></span>
  </div>
  <table>
    <thead>
      <tr>
        <th>TC ID</th><th>전제조건</th><th>테스트 항목</th><th>기대결과</th>
        <th>결과</th><th>소요(ms)</th><th>첨부파일</th><th>오류 내용</th>
      </tr>
    </thead>
    <tbody>{''.join(rows_html)}</tbody>
  </table>
</body>
</html>"""

    report_path = run_dir / "report.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path
