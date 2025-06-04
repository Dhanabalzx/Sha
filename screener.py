import requests
import time

BOT_TOKEN = '7853206716:AAGMWNSMeNyyS6OjZPujo8nMnqDjWCjo1LY'

def get_chat_id():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    response = requests.get(url)
    data = response.json()
    if not data.get('ok'):
        print("❌ Error: Check your bot token or internet connection.")
        return None
    try:
        result = data['result']
        if not result:
            return None
        chat_id = result[-1]['message']['chat']['id']
        return chat_id
    except Exception as e:
        print("Error parsing chat_id:", e)
        return None

print("📨 Waiting for message to your bot... (Send a 'Hi' to your bot in Telegram)")
chat_id = None
while not chat_id:
    chat_id = get_chat_id()
    if chat_id:
        print(f"✅ Your chat ID is: {chat_id}")
        break
    time.sleep(5)
