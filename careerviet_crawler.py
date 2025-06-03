from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import pandas as pd
import time
import random
import os


def create_browser(proxy=None, proxy_type='http'):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    if proxy:
        proxy_scheme = proxy_type.lower()
        chrome_options.add_argument(f'--proxy-server={proxy_scheme}://{proxy}')

    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    stealth(browser,
        languages=["vi-VN", "vi"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return browser


def extract_job_details(browser, url):
    browser.get(url)
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "job-title"))
        )
    except:
        print(f"Không tải được trang chi tiết {url}")
        return None

    def safe_xpath(xpath):
        try:
            return browser.find_element(By.XPATH, xpath).text.strip()
        except:
            return "Không rõ"

    def safe_xpaths(xpath):
        try:
            elements = browser.find_elements(By.XPATH, xpath)
            return [el.text.strip() for el in elements if el.text.strip()]
        except:
            return []

    job_data = {
        "URL": url,
        "Tựa đề": safe_xpath('//h1[@id="job-title"]'),
        "Tên công ty": safe_xpath('//p[contains(@class,"org-name")]/a/span'),
        "Mức lương": safe_xpath('//i[contains(@class, "cli-currency-circle-dollar")]/following-sibling::span'),
        "Địa điểm": ", ".join(safe_xpaths('//i[contains(@class, "cli-map-pin-line")]/following-sibling::span//a | //i[contains(@class, "cli-map-pin-line")]/following-sibling::span')),
        "Kinh nghiệm": safe_xpath('//i[contains(@class, "cli-suitcase-simple")]/following-sibling::span'),
        "Tuổi": "",
        "Giới tính": "",
        "Cấp bậc": "",
        "Học vấn": "",
        "Ngành nghề": ""
    }

    summary_items = browser.find_elements(By.XPATH, '//div[contains(@class, "job-summary-item")]')
    for item in summary_items:
        try:
            label = item.find_element(By.CLASS_NAME, 'summary-label').text.strip()
            if label == "Ngành nghề":
                spans = item.find_elements(By.XPATH, './/div[contains(@class,"font-weight-bolder")]//span')
                job_data["Ngành nghề"] = ", ".join([s.text.strip() for s in spans if s.text.strip()])
            else:
                value = item.find_element(By.CLASS_NAME, 'font-weight-bolder').text.strip()
                if "Tuổi" in label:
                    job_data["Tuổi"] = value
                elif "Giới tính" in label:
                    job_data["Giới tính"] = value
                elif "Cấp bậc" in label:
                    job_data["Cấp bậc"] = value
                elif "Học vấn" in label:
                    job_data["Học vấn"] = value
        except:
            continue

    return job_data


def get_all_job_links(browser, start_url):
    all_links = []
    base_url = "https://www.careerlink.vn"
    page_num = 1
    while True:
        url = f"{start_url}?page={page_num}"
        browser.get(url)
        time.sleep(4)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        elements = browser.find_elements(By.XPATH, '//a[contains(@href, "/tim-viec-lam/") and contains(@href, "/")]')
        page_links = []
        for el in elements:
            href = el.get_attribute("href")
            if href:
                full_url = urljoin(base_url, href)
                if full_url.startswith(base_url + "/tim-viec-lam/") and full_url not in all_links:
                    page_links.append(full_url)

        new_links = [link for link in page_links if link not in all_links]
        if not new_links:
            break

        print(f"🔎 Trang {page_num} - tìm thấy {len(new_links)} việc làm")
        all_links.extend(new_links)
        page_num += 1

    return all_links


if __name__ == "__main__":
    proxy = "192.168.2.19:20000"  # Proxy SOCKS5 của bạn
    browser = create_browser(proxy=proxy, proxy_type='socks5')

    list_page_url = "https://www.careerlink.vn/tim-viec-lam-tai/ho-chi-minh/HCM"
    job_urls = get_all_job_links(browser, list_page_url)
    print(f"Tổng cộng {len(job_urls)} việc làm được tìm thấy")

    all_jobs = []
    for idx, url in enumerate(job_urls):
        print(f"➡️ Đang xử lý job {idx+1}/{len(job_urls)}: {url}")
        try:
            job_data = extract_job_details(browser, url)
            if job_data is not None:
                all_jobs.append(job_data)
        except Exception as e:
            print(f"⚠️ Lỗi tại {url}: {e}")
        time.sleep(random.uniform(2, 4))

    browser.quit()

    save_folder = r"C:\Users\Admin\Documents\detaitotnghiep"
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, "all_job_details.csv")

    try:
        df = pd.DataFrame(all_jobs)
        df.to_csv(save_path, index=False, encoding="utf-8")
        print(f"✅ Đã lưu toàn bộ kết quả vào {save_path}")
    except Exception as e:
        print(f"Lỗi khi lưu file CSV: {e}")
