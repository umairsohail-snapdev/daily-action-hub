import requests

# Token from logs
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzY1NzU1NTE0fQ.WUi01iniUNs30pUnfIfhEAQ_5nLZu_x6MmZwmr_gFTc"
MEETING_ID = 23
URL = f"http://localhost:8000/meetings/{MEETING_ID}/fetch-notes"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

try:
    print(f"Testing Fetch Notes for Meeting ID: {MEETING_ID}")
    response = requests.get(URL, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(response.json())
    else:
        print("Error Response:")
        print(response.text)

except Exception as e:
    print(f"Request failed: {e}")