import os, re
from playwright.sync_api import sync_playwright

LIST_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"
OUT_DIR = "data/plans_html"
os.makedirs(OUT_DIR, exist_ok=True)

COL = 11  # codegen 看到的是 “26행 11열”

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
            popup.wait_for_load_state("domcontentloaded")

            out = os.path.join(OUT_DIR, f"plan_{i+1}.html")
            with open(out, "w", encoding="utf-8") as f:
                f.write(popup.content())

            print("saved", out, "|", popup.url)
            popup.close()

        browser.close()

if __name__ == "__main__":
    main()

