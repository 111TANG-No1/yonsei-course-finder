import os
import re
from pathlib import Path

OCR_DIR = Path("data/plans_pages_ocr")

# 关键词越像“评分/考核方式”，分数越高
KEYWORDS = [
    r"성적", r"평가", r"평가방법", r"평가기준",
    r"중간", r"기말", r"퀴즈", r"과제", r"보고서", r"발표",
    r"팀\s*프로젝트", r"프로젝트", r"출석",
]

# 这些更像“周次/课表/说明/杂讯”，出现越多扣分
NEG_KEYWORDS = [
    r"주차", r"\bPRINT\b", r"학습활동", r"기간",
    r"장애", r"대필", r"지원", r"유의사항", r"복사", r"오류",
]

PCT_RE = re.compile(r"(\d{1,3})(?:\s*[\.,]\s*(\d{1,2}))?\s*%")

def score_text(text: str):
    text = text or ""
    # 统一符号
    t = text.replace("％", "%").replace("﹪", "%")
    # 统计百分比
    pct_hits = PCT_RE.findall(t)
    pct_vals = []
    for a, b in pct_hits:
        try:
            if b:
                pct_vals.append(float(f"{a}.{b}"))
            else:
                pct_vals.append(float(a))
        except:
            pass

    # 关键字命中
    kw_hits = 0
    for pat in KEYWORDS:
        kw_hits += len(re.findall(pat, t))

    neg_hits = 0
    for pat in NEG_KEYWORDS:
        neg_hits += len(re.findall(pat, t))

    # 评分逻辑：百分比越多越好，关键字越多越好，杂讯越多越差
    score = 0
    score += len(pct_vals) * 8
    score += kw_hits * 3
    score -= neg_hits * 2

    # 额外加分：如果出现“多个不同百分比”，更像评分表
    uniq_pcts = sorted(set(pct_vals))
    if len(uniq_pcts) >= 2:
        score += 10
    if len(uniq_pcts) >= 3:
        score += 10

    # 把最有用的信息也返回
    return {
        "score": score,
        "pct_vals": uniq_pcts[:10],
        "kw_hits": kw_hits,
        "neg_hits": neg_hits,
    }

def load_file(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except:
        return ""

def brief_snippet(text: str, max_lines=20):
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    # 只保留含关键字/百分比的行
    kept = []
    for ln in lines:
        if "%" in ln or any(re.search(p, ln) for p in KEYWORDS):
            kept.append(ln)
        if len(kept) >= max_lines:
            break
    if not kept:
        kept = lines[:max_lines]
    return "\n".join(kept)

def pick_for_plan(plan_id: int):
    candidates = []
    for p in [1, 2, 3]:
        f = OCR_DIR / f"plan_{plan_id}_p{p}.txt"
        if not f.exists():
            candidates.append((p, None, None, None))
            continue
        text = load_file(f)
        info = score_text(text)
        candidates.append((p, f, info, text))

    # 过滤存在的
    exist = [c for c in candidates if c[1] is not None]
    if not exist:
        return None, candidates

    best = max(exist, key=lambda x: x[2]["score"])
    return best, candidates

def main():
    for plan_id in [4, 5]:
        best, candidates = pick_for_plan(plan_id)
        print("\n" + "=" * 60)
        print(f"PLAN {plan_id} candidates")
        for (p, f, info, text) in candidates:
            if f is None:
                print(f"  p{p}: (missing)")
                continue
            print(f"  p{p}: score={info['score']}, pcts={info['pct_vals']}, kw={info['kw_hits']}, neg={info['neg_hits']}")
        if best:
            p, f, info, text = best
            print("-" * 60)
            print(f"✅ RECOMMEND: plan_{plan_id}_p{p}  (score={info['score']}, pcts={info['pct_vals']})")
            print("-" * 60)
            print(brief_snippet(text))
        else:
            print("❌ No valid pages found.")

if __name__ == "__main__":
    main()
