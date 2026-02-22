import glob, os, re
import pandas as pd
from bs4 import BeautifulSoup

IN_DIR = "data/plans_html"
OUT = "data/plans_parsed.csv"

def pick_text(el):
    if not el:
        return ""
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))

rows = []
for path in sorted(glob.glob(os.path.join(IN_DIR, "plan_*.html"))):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    text = soup.get_text("\n", strip=True)

    # 汇总所有表格文本，便于找 “중간시험 25%” 这种
    tables = soup.find_all("table")
    table_text = " | ".join([pick_text(t) for t in tables])

    def find_pct(label):
        # 在整页文本里找
        m = re.search(rf"{re.escape(label)}\s*[:：]?\s*(\d+)\s*%", text)
        if m:
            return int(m.group(1))
        # 在表格汇总文本里找
        m = re.search(rf"{re.escape(label)}\s*(\d+)\s*%", table_text)
        if m:
            return int(m.group(1))
        return None

    # 课程名/教授（尽量抓，不保证每页都能抓到）
    course = None
    m = re.search(r"교과목명\s*([^\n]+)", text)
    if m:
        course = m.group(1).strip()
    if not course:
        course = os.path.basename(path)

    prof = None
    m = re.search(r"담당교수\s*([^\n]+)", text)
    if m:
        prof = m.group(1).strip()

    row = {
        "file": os.path.basename(path),
        "course": course,
        "professor": prof,
        "midterm_pct": find_pct("중간시험"),
        "final_pct": find_pct("기말시험"),
        "quiz_pct": find_pct("퀴즈"),
        "assignment_pct": find_pct("개인과제"),
        "team_project_pct": find_pct("팀과제"),
        "attendance_pct": find_pct("출석"),
        "other_pct": find_pct("기타"),
    }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print("✅ wrote", OUT)
print(df)
