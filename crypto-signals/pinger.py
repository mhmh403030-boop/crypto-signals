import requests
import time

def run():
    URL = "https://6d5be66f-50ad-491a-a44e-a71a967b87bb-00-ll92pl8n1xqc.kirk.replit.dev/health"
    while True:
        try:
            r = requests.get(URL, timeout=10)
            print("Ping:", r.status_code)
        except Exception as e:
            print("Error:", e)
        time.sleep(300)
