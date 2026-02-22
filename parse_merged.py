#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MERGED_DIR = ROOT / "data" / "merged"
OUT_CSV = ROOT / "data" / "course_grading.csv"

# 你最终想要的字段
FIELDS = [
    ("midterm_pct", "期中"),
    ("final_pct", "期末"),
    ("quiz_pct", "小测/퀴즈"),
    ("assignment_pct", "作业/과제/报告"),
    ("presentation_pct", "发表/발표"),
    ("attendance_pct", "出勤/출석"),
    ("team_project_pct", "团队项目/프로젝트"),
]

# 把各种语言/写法归一
KEY_PATTERNS = {
    "midterm_pct": [
        r"\bmid\s*term\b", r"\bmidterm\b",
        r"중간\s*고사", r"중간\s*시험", r"중간",
        r"期中",
    ],
    "final_pct": [
        r"\bfinal\b",
        r"기말\s*고사", r"기말\s*시험", r"기말",
        r"期末",
    ],
    "quiz_pct": [
        r"\bquiz\b", r"\bquizz\b", r"\btest\b",
        r"퀴즈", r"쪽지\s*시험", r"수시\s*시험", r"소\s*테스트",
        r"小测", r"测验",
    ],
    "assignment_pct": [
        r"\bassignment\b", r"\breport\b", r"\bpaper\b",
        r"과제", r"리포트", r"보고서",
        r"作业", r"报告",
    ],
    "presentation_pct": [
        r"\bpresentation\b", r"\bpresent\b",
        r"발표",
        r"发表", r"展示",
    ],
    "attendance_pct": [
        r"\battendance\b",
        r"출석",
        r"出勤",
    ],
    "team_project_pct": [
        r"\bteam\s*project\b", r"\bproject\b",
        r"팀\s*프로젝트", r"프로젝트", r"조별\s*과제",
        r"团队项目", r"小组项目",
    ],
}

PCT_RE = re.compile(r"(?<!\d)(\d{1,3})\s*%")

def normalize_text(s: str) -> str:
    # 统一空白 & 降噪（OCR 会有奇怪符号）
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[|•·■◆◇●◯◎▶▷▸▹※]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def find_pct_near_keywords(text: str, key: str):
    """
    在关键词附近找百分比：优先取“同一行/附近一小段”的数字。
    """
    pats = KEY_PATTERNS[key]
    # 把文本按行处理更稳
    lines = [normalize_text(x) for x in text.splitlines()]
    candidates = []

    for i, line in enumerate(lines):
        if not line:
            continue
        hit = any(re.search(p, line, flags=re.I) for p in pats)
        if not hit:
            continue

        # 在该行找%
        for m in PCT_RE.finditer(line):
            v = int(m.group(1))
            if 0 <= v <= 100:
                candidates.append(v)

        # 若该行没找到，看看上下各 1 行（OCR 常把 % 跑到隔壁）
        if not candidates:
            for j in (i-1, i+1):
                if 0 <= j < len(lines):
                    for m in PCT_RE.finditer(lines[j]):
                        v = int(m.group(1))
                        if 0 <= v <= 100:
                            candidates.append(v)

    if not candidates:
        return None

    # 如果多个：一般取最大更合理（比如 “출석 10% / 과제 30%” 这种不会串）
    return float(max(candidates))

def extract_all(text: str):
    out = {}
    for field, _label in FIELDS:
        out[field] = find_pct_near_keywords(text, field)
    return out

def main():
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    files = sorted(MERGED_DIR.glob("course_*.txt"))
    if not files:
        print(f"[ERROR] no merged files found in {MERGED_DIR}")
        return

    for f in files:
        m = re.search(r"course_(\d+)\.txt$", f.name)
        if not m:
            continue
        course_id = int(m.group(1))

        text = f.read_text(encoding="utf-8", errors="ignore")
        parsed = extract_all(text)

        row = {
            "course_id": course_id,
            "file": f.name,
            **parsed
        }
        rows.append(row)

    # 写 CSV（空值写空）
    cols = ["course_id", "file"] + [k for k, _ in FIELDS]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as wf:
        w = csv.DictWriter(wf, fieldnames=cols)
        w.writeheader()
        for r in rows:
            # 把 None 转空
            rr = {k: ("" if r.get(k) is None else r.get(k)) for k in cols}
            w.writerow(rr)

    print(f"✅ wrote {OUT_CSV}")

    # 打印预览
    for r in rows:
        brief = {k: r[k] for k, _ in FIELDS if r.get(k) is not None}
        print(f"course_{r['course_id']}: {brief if brief else '(no pct found)'}")

if __name__ == "__main__":
    main()
