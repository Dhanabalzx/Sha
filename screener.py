import requests

BOT_TOKEN = '7853206716:AAGMWNSMeNyyS6OjZPujo8nMnqDjWCjo1LY' # Replace with your token

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
print(response.json())
