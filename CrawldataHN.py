from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import pandas as pd
import time
import random

# Tạo Chrome headless
def create_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 🖥️ Chạy ẩn trình duyệt
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    service = Service(r"E:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    browser = webdriver.Chrome(service=service, options=chrome_options)

    stealth(browser,
        languages=["vi-VN", "vi"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return browser

# Lưu kết quả
data = []

# Crawl 20 trang
for page in range(1, 1023):
    print(f"📄 Đang xử lý trang {page}...")

    url = f"https://batdongsan.com.vn/ban-nha-rieng-ha-noi/p{page}"
    browser = create_browser()
    browser.get(url)
    time.sleep(random.uniform(6, 9))

    # Scroll như người dùng
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
    time.sleep(random.uniform(1, 2))
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))

    cards = browser.find_elements(By.XPATH, '//div[@class="re__card-info-content"]')

    for ele in cards:
        try:
            name_project = ele.find_element(By.XPATH, './/span[contains(@class, "js__card-title")]').text
            price_project = ele.find_element(By.XPATH, './/span[contains(@class, "re__card-config-price")]').text
            area_project = ele.find_element(By.XPATH, './/span[contains(@class, "re__card-config-area")]').text
            
            # Vị trí
            try:
                location = ele.find_element(By.XPATH, './/div[@class="re__card-location"]/span[last()]').text
            except:
                location = ""

            # Phòng ngủ
            try:
                bedroom = ele.find_element(By.XPATH, './/span[contains(@class, "re__card-config-bedroom")]').get_attribute("aria-label")
            except:
                bedroom = ""

            # WC
            try:
                toilet = ele.find_element(By.XPATH, './/span[contains(@class, "re__card-config-toilet")]').get_attribute("aria-label")
            except:
                toilet = ""

            # Ngày đăng (từ `aria-label`)
            try:
                posted_date = ele.find_element(By.XPATH, './/span[contains(@class, "re__card-published-info-published-at")]').get_attribute("aria-label")
            except:
                posted_date = ""

            data.append({
                "Tên dự án": name_project,
                "Giá": price_project,
                "Diện tích": area_project,
                "Vị trí": location,
                "Phòng ngủ": bedroom,
                "Nhà vệ sinh": toilet,
                "Ngày đăng": posted_date
            })

        except Exception as e:
            print("❌ Bỏ qua tin bị lỗi:", e)

    browser.quit()

# Lưu Excel
df = pd.DataFrame(data)
df.columns.name = "Thông tin nhà đất Hà Nội "
df.to_excel("nha_dat_batdongsan_HN.xlsx", index=False)

print("✅ Đã crawl xong và lưu vào file Excel.")
