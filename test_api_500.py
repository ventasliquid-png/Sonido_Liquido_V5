import requests
import json

url = "http://127.0.0.1:8080/stats/dashboard"
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response Body:", json.dumps(response.json(), indent=2))
    except:
        print("Response Body (Text):", response.text)
except Exception as e:
    print(f"Request failed: {e}")
