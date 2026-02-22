import os
import glob
from PIL import Image
import pytesseract

IMG_DIR = "data/plans_pages"
OUT_DIR = "data/plans_pages_ocr"
os.makedirs(OUT_DIR, exist_ok=True)

# 韩文+英文一起识别（如果你的 tesseract 里没有 kor，也可以先用 eng）
LANG = "kor+eng"

imgs = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
print(f"Found {len(imgs)} images")

for img_path in imgs:
    name = os.path.splitext(os.path.basename(img_path))[0]
    out_txt = os.path.join(OUT_DIR, f"{name}.txt")

    try:
        text = pytesseract.image_to_string(Image.open(img_path), lang=LANG)
    except Exception:
        # 如果 kor 不可用，退回英文
        text = pytesseract.image_to_string(Image.open(img_path), lang="eng")

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ OCR saved: {out_txt}")
