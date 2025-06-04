import requests

BOT_TOKEN = 'PASTE_YOUR_BOT_TOKEN_HERE'  # Replace with your token

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
print(response.json())
