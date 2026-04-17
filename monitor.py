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
        "Referer": "https://www.google.com/"
    }
    try:
        # 加上隨機參數避免快取
        response = requests.get(f"{URL}?t={datetime.now().timestamp()}", headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- 根據你提供的截圖精確定位 ---
            # 尋找 class 為 'sector-list' 下面的 'icon' 裡面的 'img'
            img_element = soup.select_one(".sector-list li.icon img")
            
            if img_element and 'src' in img_element.attrs:
                src = img_element['src'].lower()
                
                # 透過圖片檔名判斷顏色
                if "green-flag" in src:
                    return "FLY (Green)"
                elif "yellow-flag" in src:
                    return "WAIT (Yellow)"
                elif "red-flag" in src:
                    return "CANCEL (Red)"
                else:
                    return f"Unknown_Flag_Image: {src}"
            
            return "Flag_Image_Not_Found"
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
