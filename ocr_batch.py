import os, glob, subprocess
from PIL import Image
import pytesseract

PDF_DIR = "data/plans_text"
OUT_DIR = "data/ocr_text"
os.makedirs(OUT_DIR, exist_ok=True)

def pdf_to_png_all_pages(pdf_path: str, out_prefix: str):
    # 生成 out_prefix-1.png, out_prefix-2.png, ...
    subprocess.run(["pdftoppm", "-png", "-r", "300", pdf_path, out_prefix], check=True)

pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "plan_*.pdf")))
print(f"Found {len(pdfs)} PDFs")

for pdf in pdfs:
    base = os.path.splitext(os.path.basename(pdf))[0]   # plan_1
    page_prefix = os.path.join(OUT_DIR, f"{base}_page")
    txt_path = os.path.join(OUT_DIR, f"{base}.txt")

    # 1) PDF -> multi-page PNGs
    pdf_to_png_all_pages(pdf, page_prefix)

    # 2) OCR all pages and concat
    page_imgs = sorted(glob.glob(os.path.join(OUT_DIR, f"{base}_page-*.png")))
    print(f"{base}: {len(page_imgs)} pages")

    all_text = []
    for img_path in page_imgs:
        text = pytesseract.image_to_string(Image.open(img_path), lang="kor+eng")
        all_text.append(f"\n\n===== {os.path.basename(img_path)} =====\n")
        all_text.append(text)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("".join(all_text))

    print(f"✅ OCR saved: {txt_path}")
