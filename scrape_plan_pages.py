import os, re, time
from playwright.sync_api import sync_playwright

LIST_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"
OUT_DIR = "data/plans_pages"
os.makedirs(OUT_DIR, exist_ok=True)

# 你之前验证过 “계획” 在第 11 列（11열）。如果以后不对，改这里。
COL = 11
MAX_COURSES = 5
PAGES_PER_PLAN = 3  # 1/3,2/3,3/3

def click_next(popup):
    # 尝试各种常见“下一页”控件
    candidates = [
        popup.get_by_role("button", name=re.compile(r"(다음|다음페이지|Next|▶|>|>>)", re.I)),
        popup.get_by_role("link", name=re.compile(r"(다음|Next|▶|>|>>)", re.I)),
        popup.locator("a:has-text('다음')"),
        popup.locator("button:has-text('다음')"),
        popup.locator("a[title*='다음'], button[title*='다음']"),
    ]
    for c in candidates:
        try:
            if c.count() > 0:
                c.first.click()
                return True
        except Exception:
            pass
    # 如果找不到，就返回 False
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LIST_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)

        print("✅ 浏览器已打开。请你在页面里选好筛选条件并点一次 ‘조회’。列表出来后回终端按回车继续。")
        input()

        # 获取表格行
        rows = page.locator("table tbody tr")
        n = rows.count()
        print(f"Detected rows: {n}")
        if n == 0:
            print("❌ 没检测到表格行。可能表格选择器不对。")
            return

        to_fetch = min(MAX_COURSES, n)
        print(f"Will fetch first {to_fetch} courses, {PAGES_PER_PLAN} pages each.")

        for i in range(to_fetch):
            row = rows.nth(i)
            cell = row.locator("td").nth(COL - 1)  # 11열 -> index 10
            btn = cell.locator("button, a").first

            with page.expect_popup() as pop:
                btn.click()
            popup = pop.value
            popup.wait_for_load_state("domcontentloaded")
            popup.wait_for_timeout(800)

            # 截图 1~3 页
            for pageno in range(1, PAGES_PER_PLAN + 1):
                out_path = os.path.join(OUT_DIR, f"plan_{i+1}_p{pageno}.png")
                popup.set_viewport_size({"width": 1200, "height": 1600})
                popup.wait_for_timeout(300)
                popup.screenshot(path=out_path, full_page=True)
                print(f"✅ saved {out_path}")

                if pageno < PAGES_PER_PLAN:
                    ok = click_next(popup)
                    popup.wait_for_timeout(800)
                    if not ok:
                        print("⚠️ 没找到下一页按钮，提前停止翻页。")
                        break

            popup.close()
            page.wait_for_timeout(300)

        browser.close()

if __name__ == "__main__":
    main()
