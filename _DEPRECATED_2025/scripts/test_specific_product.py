import requests

pid = 289
url = f'http://localhost:8000/productos/{pid}'
print(f"Testing {url}...")
try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print("Response Text:")
        print(response.text)
    else:
        print("Success")
        print(response.json())
except Exception as e:
    print(f"Connection Failed: {e}")
