from playwright.sync_api import sync_playwright

LOGIN_URL = "https://ysweb.yonsei.ac.kr/com/lgin/SsoCtr/initPageWork.do?univDivCd=gsch&requestTimeStr=1771055255172"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.bring_to_front()

        print("✅ 浏览器已启动。请在弹出的浏览器里手动登录。")
        print("登录成功并进入登录后页面后，回到终端按回车继续保存登录态。")
        input()

        context.storage_state(path="storage_state.json")
        print("✅ 已保存登录态到 storage_state.json")

        browser.close()

if __name__ == "__main__":
    main()
