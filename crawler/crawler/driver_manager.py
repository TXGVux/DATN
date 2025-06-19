import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

class DriverManager:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")

    def create_driver(self):
        try:
            driver = uc.Chrome(options=self.options, version_main=137)
            return driver
        except Exception as e:
            print(f"❌ Error initializing driver: {e}")
            return None