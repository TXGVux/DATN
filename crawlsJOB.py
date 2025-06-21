import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def mainjoblink(driver):
    job = []
    main_url = "https://kstudy.edu.vn/bang-luong-cac-nganh-nghe/"
    driver.get(main_url)
    try:
        rows = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr")))
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                job_name = cells[0].text.strip()
                try:
                    job_link = cells[2].find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if job_name and job_link:
                        job.append({'name': job_name, 'url': job_link})
                except: continue
    except Exception as e:
        print("Lỗi")
    return job

def ITpage(driver, url):
    driver.get(url)
    data = []
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h3')))
        job_heading = driver.find_elements(By.XPATH, "//h3[strong]")
        for heading in job_heading:
            job_title = heading.text.strip()
            if not job_title or "kỹ năng" in job_title.lower(): continue
            try:
                data_list = heading.find_element(By.XPATH, "following-sibling::ul[1]")
                salary = data_list.find_elements(By.CSS_SELECTOR, "ul > li > span")
                for span in salary:
                    raw_text = span.text.strip()
                    if raw_text:
                        data.append({'Cong_viec': job_title, 'Muc_luong': raw_text})
            except NoSuchElementException: continue
    except Exception as e:
        print("Lỗi")
    return data

def medicinepage(driver, url):
    driver.get(url)
    data = []
    wait = WebDriverWait(driver, 15)
    try:
        content = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        elements = content.find_elements(By.XPATH, "./*")
        job_title = "Không xác định"
        h2_counter = 0 
        for element in elements:
            tag_name = element.tag_name
            if tag_name == 'h2':
                h2_counter += 1
                if h2_counter > 1:
                    job_title = element.text.strip()
            if h2_counter > 1:
                if tag_name == 'ul':
                    list_items = element.find_elements(By.TAG_NAME, 'li')
                    for item in list_items:
                        raw_text = item.text.strip()
                        if raw_text:
                            data.append({'Cong_viec': job_title, 'Muc_luong': raw_text})
                if tag_name == 'p':
                    try:
                        span = element.find_element(By.TAG_NAME, 'span')
                        raw_text = span.text.strip()
                        if raw_text and "triệu" in raw_text:
                            data.append({'Cong_viec': job_title, 'Muc_luong': raw_text})
                    except NoSuchElementException:
                        continue
    except Exception as e:
        print("Lỗi")
    return data

def Allpage(driver, url):
    driver.get(url)
    data = []
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h2')))
        content = driver.find_element(By.TAG_NAME, 'article')
        elements = content.find_elements(By.XPATH, "./*")
        job_title = "Không xác định"
        for element in elements:
            if element.tag_name in ['h2']:
                 job_title = element.text.strip()
            if element.tag_name == 'p':
                raw_text = element.text.strip()
                if raw_text and "triệu" in raw_text:
                     data.append({'Cong_viec': job_title, 'Muc_luong': raw_text})
    except Exception as e:
        print("Lỗi")
    return data

def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    final_data = []
    try:
        scrape = mainjoblink(driver)
        for jobs in scrape:
            job_name = jobs['name']
            job_url = jobs['url']
            if "khoa học dữ liệu" in job_name.lower():
                continue
            scraped_details = []
            if "công nghệ thông tin" in job_name.lower():
                scraped_details = ITpage(driver, job_url)
            elif "y dược" in job_name.lower(): 
                scraped_details = medicinepage(driver, job_url)
            else:
                scraped_details = Allpage(driver, job_url)
            for detail in scraped_details:
                detail['Nganh_nghe'] = job_name
                final_data.append(detail)
            time.sleep(1)
    finally:
        driver.quit()
    if final_data:
        fieldnames = ['Nganh_nghe', 'Cong_viec', 'Muc_luong']
        with open('luongcuatungnganh.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_data)

if __name__ == "__main__":
    main()