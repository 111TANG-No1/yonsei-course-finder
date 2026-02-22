import subprocess, os
from PIL import Image
import pytesseract

PDF = "data/plans_text/plan_1.pdf"
OUT_IMG = "data/plans_text/plan_1_page1.png"
TMP_PREFIX = "data/plans_text/plan_1_tmp"

# 1) PDF -> PNG (page 1)
subprocess.run([
    "pdftoppm", "-f", "1", "-l", "1",
    "-png", "-r", "300",
    PDF, TMP_PREFIX
], check=True)

tmp_img = TMP_PREFIX + "-1.png"
os.replace(tmp_img, OUT_IMG)

# 2) OCR
img = Image.open(OUT_IMG)
text = pytesseract.image_to_string(img, lang="kor+eng")

print("===== OCR TEXT (first 2000 chars) =====")
print(text[:2000])
print("===== END =====")
