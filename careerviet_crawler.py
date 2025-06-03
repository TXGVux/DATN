import requests
import pandas as pd
import time
import random

from careerviet_crawler_job import create_browser, extract_job_details

# Hàm gọi API lấy danh sách đường dẫn công việc (có debug lỗi)
def fetch_job_links(page=1, page_size=100):
    api_url = f"https://api.careerbuilder.vn/v2/job-search?category=0&keyword=&page={page}&pageSize={page_size}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://careerviet.vn/",
        "Origin": "https://careerviet.vn"
    }
    res = requests.get(api_url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Lỗi HTTP {res.status_code}: {res.text}")
        return []

    try:
        data = res.json()
    except Exception as e:
        print(f"❌ JSON Decode lỗi: {e}")
        print("📄 Nội dung phản hồi:", res.text[:500])
        return []

    jobs = data.get("data", {}).get("jobs", [])
    job_links = [
        f"https://careerviet.vn/vi/tim-viec-lam/{job['seoAlias']}.{job['jobId']}.html"
        for job in jobs
    ]
    return job_links

# Crawl toàn bộ từ API danh sách
if __name__ == "__main__":
    job_urls = fetch_job_links()
    print(f"✅ Đã tìm thấy {len(job_urls)} đường dẫn việc làm")

    browser = create_browser()
    all_jobs = []
    for idx, job_url in enumerate(job_urls):
        print(f"➡️ Đang xử lý job {idx+1}/{len(job_urls)}: {job_url}")
        try:
            job_data = extract_job_details(browser, job_url)
            all_jobs.append(job_data)
        except Exception as e:
            print(f"⚠️ Lỗi khi xử lý {job_url}: {e}")
        time.sleep(random.uniform(2, 4))

    browser.quit()

    # Ghi vào file CSV
    df = pd.DataFrame(all_jobs)
    df.to_csv("all_job_details.csv", index=False, encoding="utf-8-sig")
    print("✅ Đã lưu toàn bộ kết quả vào all_job_details.csv")
