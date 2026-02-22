import pdfplumber

path = "data/plans_text/plan_1.pdf"

with pdfplumber.open(path) as pdf:
    for i, page in enumerate(pdf.pages[:2]):  # 先看前两页
        text = page.extract_text() or ""
        print("=== page", i+1, "===")
        print(text[:1500])
