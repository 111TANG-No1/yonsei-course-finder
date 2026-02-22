import os, re, glob
import pandas as pd

# OCR txt 来源目录（你的截图里就是这个）
IN_DIR = "data/plans_pages_ocr"
OUT_CSV = "data/plans_pages_parsed.csv"

os.makedirs("data", exist_ok=True)

# 关键字：把 OCR 里可能出现的中文/韩文关键词都尽量覆盖
KEYS = {
    "midterm_pct": ["중간", "중간시험", "중간고사", "中间", "期中", "midterm"],
    "final_pct":   ["기말", "기말시험", "기말고사", "期末", "final"],
    "quiz_pct":    ["퀴즈", "쪽지시험", "quiz"],
    "assignment_pct": ["과제", "리포트", "보고서", "assignment", "report"],
    "presentation_pct": ["발표", "presentation"],
    "attendance_pct": ["출석", "attendance"],
    "team_project_pct": ["팀프로젝트", "팀 프로젝트", "프로젝트", "project", "team"],
}

# 匹配百分比：10%, 16%, 16.0%, 16,7%（韩式小数逗号）
PCT_RE = re.compile(r"(\d{1,3}(?:[.,]\d{1,2})?)\s*%")

def normalize_text(t: str) -> str:
    if not t:
        return ""
    t = t.replace("％", "%").replace("﹪", "%")
    # OCR 常见：把全角逗号句号统一一下
    t = t.replace("，", ",").replace("．", ".")
    return t

def find_first_pct_near(lines, idx, col):
    """
    在关键词所在行附近（当前行 +/- 2 行）找第一个百分比
    """
    start = max(0, idx - 2)
    end = min(len(lines), idx + 3)
    block = "\n".join(lines[start:end])

    m = PCT_RE.search(block)
    if not m:
        return None

    s = m.group(1).replace(",", ".")
    try:
        return float(s)
    except:
        return None

def extract_pcts(text: str):
    text = normalize_text(text)
    lines = text.splitlines()

    result = {k: None for k in KEYS.keys()}

    for key, patterns in KEYS.items():
        found = None
        for pat in patterns:
            # 找到包含关键词的行
            for i, line in enumerate(lines):
                if pat.lower() in line.lower():
                    col = line.lower().find(pat.lower())
                    pct = find_first_pct_near(lines, i, col)
                    if pct is not None:
                        found = pct
                        break
            if found is not None:
                break

        result[key] = found

    return result

def guess_course_title(text: str):
    """
    可选：从前几行猜课程名（你现在网页显示“未解析到课程名”，先让它尽量能显示）
    规则：优先找英文较长的一行；否则返回 None
    """
    lines = [ln.strip() for ln in normalize_text(text).splitlines() if ln.strip()]
    head = lines[:25]
    # 英文比例较高且长度较长
    best = None
    for ln in head:
        eng = sum(ch.isalpha() for ch in ln)
        if eng >= 10 and len(ln) >= 12:
            best = ln
            break
    return best

def main():
    txts = sorted(glob.glob(os.path.join(IN_DIR, "plan_*.txt")))
    if not txts:
        print(f"❌ 没找到任何 txt：{IN_DIR}/plan_*.txt")
        return

    rows = []
    for path in txts:
        base = os.path.basename(path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        pcts = extract_pcts(text)

        # 从文件名提取 course_id（plan_3_p2.txt -> 3）
        m = re.search(r"plan_(\d+)_p\d+\.txt", base)
        course_id = int(m.group(1)) if m else None

        course_title = guess_course_title(text)

        row = {
            "file": base,
            "course_id": course_id,
            "course": course_title,
            "professor": None,
            **pcts,
            "raw_excerpt": (normalize_text(text)[:300].replace("\n", " ") + "...") if text else "",
        }
        rows.append(row)

    df = pd.DataFrame(rows).sort_values(["course_id", "file"], na_position="last")
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"✅ wrote {OUT_CSV}")
    print(df[["file","course_id","midterm_pct","final_pct","quiz_pct","assignment_pct","attendance_pct","team_project_pct"]].head(20))

if __name__ == "__main__":
    main()
