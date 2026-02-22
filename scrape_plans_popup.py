import os
from playwright.sync_api import sync_playwright

LIST_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"
OUT_DIR = "data/plans_html"
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LIST_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)

        print("请在浏览器页面上把筛选条件选好并点击一次 ‘조회’，列表出现后回终端按回车继续。")
        input()

        # 抓表格所有行
        rows = page.locator("table tbody tr")
        n = rows.count()
        print(f"Detected rows: {n}")
        if n == 0:
            print("❌ 没检测到表格行。可能页面表格不是 table/tbody/tr 结构。我们需要根据页面结构调整 selector。")
            browser.close()
            return

        # 先抓前 5 行验证
        max_to_fetch = min(5, n)

        for i in range(max_to_fetch):
            row = rows.nth(i)

            # 计划书按钮大概率在某一列：先用第11列（nth(10)）尝试
            cell = row.locator("td").nth(10)
            btn = cell.locator("button, a").first

            with page.expect_popup() as popup_info:
                btn.click()

            popup = popup_info.value
            popup.wait_for_load_state("domcontentloaded")
            html = popup.content()

            out_path = os.path.join(OUT_DIR, f"row_{i+1}.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"✅ saved {out_path} | popup url: {popup.url}")
            popup.close()

        browser.close()

if __name__ == "__main__":
    main()
