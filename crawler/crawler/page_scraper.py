from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PageScraper:
    def __init__(self, driver):
        self.driver = driver

    def load_page(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="dv-txt"]'))
            )
            return True
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False

    def scrape_listings(self, page):
        listings = []
        try:
            cards = self.driver.find_elements(By.XPATH, '//div[@class="dv-txt"]')
            if not cards:
                return listings

            for ele in cards:
                try:
                    data = {
                        "Tên dự án": ele.find_element(By.XPATH, './/span[contains(@class, "a-title-0")]').text or "",
                        "Giá": ele.find_element(By.XPATH, './/label[contains(@class, "a-txt-cl1")]').text or "",
                        "Diện tích": ele.find_element(By.XPATH, './/label[contains(@class, "a-txt-cl2")]').text or "",
                        "Loại nhà": "",
                        "Vị trí": "",
                        "Phòng ngủ": "",
                        "Nhà vệ sinh": "",
                        "Ngày đăng": "",
                        "Trang": page
                    }

                    spans = ele.find_elements(By.XPATH, './/span[contains(@class, "ex3")]')
                    if len(spans) >= 1: data["Loại nhà"] = spans[0].text
                    if len(spans) >= 2: data["Vị trí"] = spans[1].text

                    if ele.find_elements(By.XPATH, './/p[contains(@class, "time")]'):
                        data["Ngày đăng"] = ele.find_element(By.XPATH, './/p[contains(@class, "time")]').text
                    if ele.find_elements(By.XPATH, './/i[contains(@class, "fa-bed")]/parent::span'):
                        data["Phòng ngủ"] = ele.find_element(By.XPATH, './/i[contains(@class, "fa-bed")]/parent::span').text
                    if ele.find_elements(By.XPATH, './/i[contains(@class, "fa-bath")]/parent::span'):
                        data["Nhà vệ sinh"] = ele.find_element(By.XPATH, './/i[contains(@class, "fa-bath")]/parent::span').text

                    listings.append(data)

                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Error extracting listings: {e}")
        return listings