from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from twocaptcha import TwoCaptcha
import pandas as pd
import time
import random
import os


solver = TwoCaptcha('530a28a37a5a788e2a06315b2d5d17e2')  # API key 2Captcha


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


def solve_recaptcha(site_key, url):
    print("🧩 Đang giải reCAPTCHA bằng 2Captcha...")
    try:
        result = solver.recaptcha(sitekey=site_key, url=url)
        code = result['code']
        print("✅ Giải captcha thành công")
        return code
    except Exception as e:
        print(f"❌ Lỗi khi giải captcha: {e}")
        return None


def handle_captcha(browser):
    try:
        # Đợi iframe captcha hiện ra
        WebDriverWait(browser, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
        )
        iframe_src = browser.execute_script("return document.querySelector('iframe[src*=\"recaptcha\"]').src")
        parsed = urlparse(iframe_src)
        site_key = parse_qs(parsed.query)['k'][0]

        browser.switch_to.default_content()
        current_url = browser.current_url

        token = solve_recaptcha(site_key, current_url)
        if token:
            # Inject token vào textarea ẩn của reCAPTCHA
            browser.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{token}";')
            browser.execute_script("""
                var el = document.getElementById("g-recaptcha-response");
                el.style.display = "";
                el.dispatchEvent(new Event('change'));
            """)
            time.sleep(2)
            return True
        else:
            print("❌ Không thể giải captcha.")
            return False
    except Exception:
        browser.switch_to.default_content()
        return True  # Nếu không thấy captcha, trả về True


def extract_job_details(browser, url):
    browser.get(url)

    # Nếu trang có captcha, xử lý
    if not handle_captcha(browser):
        print(f"⚠️ Không thể vượt captcha tại {url}")
        return None, False

    try:
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, "job-title"))
        )
    except:
        print(f"⚠️ Không tải được trang chi tiết {url}")
        return None, False  # Trả về False nếu lỗi

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
        "Địa điểm": ", ".join(safe_xpaths(
            '//i[contains(@class, "cli-map-pin-line")]/following-sibling::span//a | //i[contains(@class, "cli-map-pin-line")]/following-sibling::span')),
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

    return job_data, True  # Thành công


def add_page_param(url, page_num):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query['page'] = [str(page_num)]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))


if __name__ == "__main__":
    proxy = "192.168.2.19:20000"  # Proxy SOCKS5 của bạn
    browser = create_browser(proxy=proxy, proxy_type='socks5')

    list_page_url = "https://www.careerlink.vn/tim-viec-lam-tai/ho-chi-minh/HCM"

    try:
        max_pages = int(input("🔢 Nhập số trang muốn thu thập (nhập 0 để thu thập toàn bộ): "))
    except:
        max_pages = 0

    max_pages = max_pages if max_pages > 0 else None

    all_jobs = []  # Tổng dữ liệu thu thập

    save_folder = r"C:\Users\Admin\Documents\detaitotnghiep"
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, "all_job_details.csv")

    base_url = "https://www.careerlink.vn"
    page_num = 1

    while True:
        if max_pages and page_num > max_pages:
            print("📌 Đã đạt đến số trang tối đa.")
            break

        page_url = add_page_param(list_page_url, page_num)
        browser.get(page_url)
        time.sleep(5)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        elements = browser.find_elements(By.XPATH, '//a[contains(@href, "/tim-viec-lam/") and contains(@href, "/")]')
        page_links = []
        for el in elements:
            href = el.get_attribute("href")
            if href:
                full_url = urljoin(base_url, href)
                if full_url.startswith(base_url + "/tim-viec-lam/") and full_url not in page_links:
                    page_links.append(full_url)

        if not page_links:
            print("⛔ Không tìm thấy việc làm mới trên trang này, dừng lại.")
            break

        print(f"🔎 Trang {page_num} - tìm thấy {len(page_links)} việc làm")

        # Quét chi tiết từng job của page hiện tại
        for idx, url in enumerate(page_links):
            print(f"➡️ Trang {page_num}, job {idx + 1}/{len(page_links)}: {url}")
            success = False
            retries = 0
            max_retries = 1  # Số lần thử lại mở trình duyệt mới khi lỗi

            while not success and retries <= max_retries:
                try:
                    job_data, success = extract_job_details(browser, url)
                    if success and job_data is not None:
                        all_jobs.append(job_data)
                    elif not success:
                        print("♻️ Restart trình duyệt do lỗi tải trang chi tiết...")
                        browser.quit()
                        time.sleep(3)
                        browser = create_browser(proxy=proxy, proxy_type='socks5')
                        retries += 1
                except Exception as e:
                    print(f"⚠️ Lỗi tại {url}: {e}")
                    break

            time.sleep(random.uniform(2, 4))

        # Lưu dữ liệu sau khi quét xong page
        try:
            if len(all_jobs) == 0:
                print("❌ Không có dữ liệu để lưu.")
            else:
                df = pd.DataFrame(all_jobs)
                df.to_csv(save_path, index=False, encoding="utf-8-sig")
                print(f"✅ Đã lưu dữ liệu sau trang {page_num} vào {save_path}")
        except Exception as e:
            print(f"Lỗi khi lưu file CSV: {e}")

        page_num += 1

    browser.quit()
