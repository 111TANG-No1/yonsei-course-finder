import os, re
from playwright.sync_api import sync_playwright

LIST_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"
OUT_DIR = "data/plans_text"
os.makedirs(OUT_DIR, exist_ok=True)

COL = 11  # “xx행 11열”

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(LIST_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)

        print("在浏览器里点一次‘조회’，列表出来后回终端按回车。")
        input()

        pattern = rf"^\d+행\s+{COL}열$"
        btns = page.get_by_role("button", name=re.compile(pattern))
        print("Detected plan buttons:", btns.count())

        for i in range(min(5, btns.count())):
            with page.expect_popup() as pop:
                btns.nth(i).click()
            popup = pop.value
            popup.wait_for_load_state("networkidle")  # 等动态内容更充分加载

            # 1) 保存“可见文本”
            text = popup.inner_text("body")
            txt_path = os.path.join(OUT_DIR, f"plan_{i+1}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            # 2) 保存截图（备用）
            png_path = os.path.join(OUT_DIR, f"plan_{i+1}.png")
            popup.set_viewport_size({"width": 1200, "height": 1600})
            popup.wait_for_timeout(500)
            popup.screenshot(path=png_path, full_page=True)
            pdf_path = os.path.join(OUT_DIR, f"plan_{i+1}.pdf")
            popup.pdf(path=pdf_path, format="A4", print_background=True)
            print("✅ saved PDF", pdf_path)
            print("✅ saved", txt_path, "and", png_path, "|", popup.url)
            popup.close()

        browser.close()

if __name__ == "__main__":
    main()

