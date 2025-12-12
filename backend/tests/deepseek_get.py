import requests

from backend.app.core.config import settings

API_KEY = settings.DEEPSEEK_API_KEY

url = "https://api.deepseek.com/v1/chat/completions"

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "ping"}
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(url, json=payload, headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)
