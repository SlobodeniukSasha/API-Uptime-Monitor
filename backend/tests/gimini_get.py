import requests

API_KEY = 'AIzaSyDncg-ojgVIBVPD1LZhA_oDHfynpaqkdok'

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

payload = {
    "contents": [
        {"parts": [{"text": "ping"}]}
    ]
}

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

response = requests.post(url, json=payload, headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)
