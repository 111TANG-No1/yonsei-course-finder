import os
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

LIST_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"

OUT_DIR = "data/plans_pages"
os.makedirs(OUT_DIR, exist_ok=True)

# 抓多少门课、每门抓几页（截图）
MAX_COURSES = 5
PAGES_PER_PLAN = 3

# 超时（毫秒）
TIMEOUT = 120_000


def safe_first(locator):
    try:
        if locator.count() > 0:
            return locator.first
    except Exception:
        pass
    return None


def click_next(popup):
    """
    在弹窗里尝试翻到下一页。
    """
    candidates = [
        popup.get_by_role("button", name=re.compile(r"(다음|Next|▶|>|>>)", re.I)),
        popup.get_by_role("link", name=re.compile(r"(다음|Next|▶|>|>>)", re.I)),
        popup.locator("a:has-text('다음')"),
        popup.locator("button:has-text('다음')"),
        popup.locator("a[title*='다음'], button[title*='다음']"),
        popup.locator("a:has-text('▶')"),
        popup.locator("button:has-text('▶')"),
        popup.locator("a:has-text('>')"),
        popup.locator("button:has-text('>')"),
    ]

    for loc in candidates:
        btn = safe_first(loc)
        if not btn:
            continue
        try:
            btn.click()
            return True
        except Exception:
            continue
    return False


def wait_new_page(context, before_pages, timeout_ms=8000):
    """
    有些站点不会触发 expect_popup，但会在 context.pages 里多出一个新 tab。
    """
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        pages = context.pages
        if len(pages) > len(before_pages):
            # 返回新增的那一个
            for p in pages:
                if p not in before_pages:
                    return p
        time.sleep(0.2)
    return None


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.set_default_timeout(TIMEOUT)
        page.set_default_navigation_timeout(TIMEOUT)

        print("🌐 正在打开课程列表页…")
        page.goto(LIST_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        print("✅ 浏览器已打开。请你在页面里：")
        print("   1) 选择学期/筛选条件")
        print("   2) 点一次「조회」让列表出现（你只需要做到这里）")
        print("   3) 列表出现后，回到终端按一次回车继续")
        input()

        # 关键：找“计划/계획”所在列的按钮（通常是 ‘xx행 11열’）
        # 你之前成功抓到就是这个策略
        COL = 11
        pattern = rf"^\d+행\s+{COL}열$"
        plan_buttons = page.get_by_role("button", name=re.compile(pattern))
        btn_count = plan_buttons.count()

        print(f"Detected plan buttons (행 {COL}열): {btn_count}")
        if btn_count == 0:
            print("❌ 没找到任何 ‘xx행 11열’ 按钮。")
            print("   你需要确认：你确实点了「조회」且列表已经出现。")
            browser.close()
            return

        to_fetch = min(MAX_COURSES, btn_count)

        for i in range(to_fetch):
            print(f"\n===== Course {i+1}/{to_fetch} =====")
            btn = plan_buttons.nth(i)

            # 记录点击前已经存在的页面（用于兜底抓新 tab）
            before_pages = list(context.pages)

            popup = None

            # 方案A：正常 expect_popup
            try:
                with page.expect_popup(timeout=6000) as pop:
                    btn.click()
                popup = pop.value
            except PWTimeout:
                # 方案B：有时不会被识别为 popup，但会新开一个 tab
                try:
                    btn.click()
                except Exception:
                    pass
                popup = wait_new_page(context, before_pages, timeout_ms=8000)

            if popup is None:
                print("⚠️ 没等到弹窗(tab)。可能被当成同页弹层/或站点没打开新页。跳过这一门…")
                continue

            try:
                popup.set_default_timeout(TIMEOUT)
                popup.set_default_navigation_timeout(TIMEOUT)

                # 等页面内容稳定一点
                try:
                    popup.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
                except Exception:
                    pass
                popup.wait_for_timeout(900)

                # 截图多页（p1/p2/p3）
                for pageno in range(1, PAGES_PER_PLAN + 1):
                    out_path = os.path.join(OUT_DIR, f"plan_{i+1}_p{pageno}.png")
                    popup.set_viewport_size({"width": 1200, "height": 1600})
                    popup.wait_for_timeout(300)
                    popup.screenshot(path=out_path, full_page=True)
                    print(f"✅ saved {out_path}")

                    if pageno < PAGES_PER_PLAN:
                        ok = click_next(popup)
                        popup.wait_for_timeout(900)
                        if not ok:
                            print("⚠️ 没找到下一页按钮，提前停止翻页。")
                            break

            finally:
                try:
                    popup.close()
                except Exception:
                    pass
                page.wait_for_timeout(300)

        browser.close()
        print("\n✅ 完成。截图在：data/plans_pages/")


if __name__ == "__main__":
    main()
