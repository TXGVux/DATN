from crawler.driver_manager import DriverManager
from crawler.page_scraper import PageScraper
from crawler.data_saver import DataSaver
import time

BASE_URL = "https://nhadat24h.net/nha-dat-ban-dong-nai/page{}"

def main():
    driver_manager = DriverManager()
    driver = driver_manager.create_driver()

    if not driver:
        return

    scraper = PageScraper(driver)
    saver = DataSaver("Nha_dat_DongNai.csv", "Nha_dat_DongNai.json")

    all_data = []
    error_pages = []
    page = 1

    while True:
        url = BASE_URL.format(page)
        print(f"📄 Crawling page {page}: {url}")

        if not scraper.load_page(url):
            error_pages.append(page)
            page += 1
            continue

        listings = scraper.scrape_listings(page)

        if not listings:
            print("⚠️ No listings found. Stopping.")
            break

        all_data.extend(listings)
        saver.save(all_data)

        page += 1
        time.sleep(3)

    try:
        driver.quit()
        print("✅ Browser closed.")
    except Exception as e:
        print(f"❌ Error closing browser: {e}")

    if error_pages:
        print("⚠️ Error pages:", error_pages)
    else:
        print("✅ No errors during crawl.")

if __name__ == "__main__":
    main()