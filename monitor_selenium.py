
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime

ITEM_URL = "https://shop1211059689.v.weidian.com/item.html?itemID=7516892425"
TARGET_SKU_ID = "125284642294"
CHROMEDRIVER_PATH = "/Users/xiechenyang/Documents/CHENYANG XIE/weidian/chromedriver-mac-arm64/chromedriver"

def get_stock():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(ITEM_URL)
    time.sleep(2)
    html = driver.page_source
    driver.quit()
    match = re.search(f'{TARGET_SKU_ID}.*?stock(?:&quot;|"):(\d+)', html)
    if match:
        return int(match.group(1))
    else:
        print("❌ 正则未匹配到库存")
        return None

def save_log(data):
    with open("sales_log.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_html(data):
    rows = "".join(f"<tr><td>{d['time']}</td><td>{d['stock']}</td><td>{d['diff']:+}</td></tr>" for d in data)
    html = f"""
    <html><head><meta charset="utf-8">
    <meta http-equiv="refresh" content="60">
    <title>李帝努库存监控</title></head>
    <body><h2>李帝努库存监控</h2>
    <table border="1"><tr><th>时间</th><th>库存</th><th>变化</th></tr>{rows}</table></body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def monitor(interval_sec=300):
    log_data = []
    last_stock = None
    try:
        while True:
            stock = get_stock()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if stock is not None:
                if last_stock is None or stock != last_stock:
                    diff = 0 if last_stock is None else stock - last_stock
                    print(f"[{now}] 当前李帝努库存: {stock}（变化: {diff:+})")
                    log_data.append({"time": now, "stock": stock, "diff": diff})
                    save_log(log_data)
                    update_html(log_data)
                    last_stock = stock
                else:
                    pass  # 什么都不做
            else:
                print(f"[{now}] ❌ 无法获取库存信息")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("🛑 监控已手动停止。")

monitor(60)
