import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

# 設定
URL = "https://shmkapadokya.kapadokya.edu.tr/en/"
LOG_FILE = "flight_events.log"
TR_TZ = pytz.timezone('Europe/Istanbul')

def get_current_status():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(f"{URL}?t={datetime.now().timestamp()}", headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- 診斷邏輯：嘗試多種可能的 Selector ---
            # 1. 直接找包含狀態的 div
            status_element = soup.select_one(".slot-status, .status-info, .slot-info b")
            
            if status_element:
                status_text = status_element.get_text(strip=True)
                return status_text
            
            # 2. 如果找不到文字，檢查是否是透過圖片 (例如 flag_green.png)
            img_element = soup.find("img", class_="flag") # 假設 class 是 flag
            if img_element and 'src' in img_element.attrs:
                src = img_element['src'].lower()
                if 'green' in src: return "FLY (Green)"
                if 'yellow' in src: return "WAIT (Yellow)"
                if 'red' in src: return "CANCEL (Red)"
            
            # 3. 如果還是 Unknown，印出網頁 Title 幫助除錯
            title = soup.title.string if soup.title else "No Title"
            return f"Unknown (Title: {title})"
            
        return f"HTTP_Error_{response.status_code}"
    except Exception as e:
        return f"Exception_{str(e)[:50]}"

def run():
    now_tr = datetime.now(TR_TZ).strftime("%Y-%m-%d %H:%M:%S")
    current_status = get_current_status()
    
    # 讀取最後一次記錄
    last_status = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_status = lines[-1].split("] ")[-1].strip()

    # 如果狀態變更，寫入紀錄
    if current_status != last_status:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now_tr}] {current_status}\n")
        print(f"Status changed to: {current_status}")
    else:
        print("No status change.")

if __name__ == "__main__":
    run()
