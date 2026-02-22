import os, re, glob

IN_DIR = "data/plans_pages_ocr"
OUT_DIR = "data/merged"
os.makedirs(OUT_DIR, exist_ok=True)

# plan_3_p2.txt -> course 3, page 2
pat = re.compile(r"plan_(\d+)_p(\d+)\.txt$")

groups = {}
for fp in glob.glob(os.path.join(IN_DIR, "plan_*_p*.txt")):
    m = pat.search(fp)
    if not m:
        continue
    cid = int(m.group(1))
    page = int(m.group(2))
    groups.setdefault(cid, []).append((page, fp))

for cid, items in sorted(groups.items()):
    items.sort(key=lambda x: x[0])  # by page
    out = os.path.join(OUT_DIR, f"course_{cid}.txt")
    with open(out, "w", encoding="utf-8") as w:
        for page, fp in items:
            w.write(f"\n\n===== course {cid} page {page} =====\n")
            with open(fp, "r", encoding="utf-8", errors="ignore") as r:
                w.write(r.read())
    print("✅ merged:", out, "| pages:", [p for p, _ in items])
