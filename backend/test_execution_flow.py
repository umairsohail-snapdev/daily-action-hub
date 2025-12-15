import requests
import json

BASE_URL = "http://localhost:8000"
# Use the token from the logs if possible, or just login
# For dev, maybe we can assume auth is bypassed or we can login easily
# In api.ts, it uses localStorage "jwt_token".

# Let's try to login as user 2 (from logs)
# Or just use the known dev secret to forge a token if we could, but better to use the API.

def test_flow():
    # 1. Login (assuming we have a test user or can create one)
    # Actually, let's just use the `backend/create_test_user.py` logic if needed, 
    # but let's assume the server is running and we can just hit it.
    # We need a token.
    
    # We'll try to use the token from the logs if valid, or just login.
    # From logs: "sub": "2"
    # Let's try to sign up or login.
    
    email = "test@example.com"
    password = "password123"
    
    # Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
        if resp.status_code != 200:
            # Try signup
            print("Login failed, trying signup...")
            resp = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password, "name": "Test User"})
            if resp.status_code == 200:
                print("Signup successful, logging in...")
                resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
            
        if resp.status_code != 200:
            print(f"Auth failed: {resp.text}")
            return
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in.")
        
        # 2. Get a meeting or create one
        # List today's dashboard
        print("Fetching dashboard...")
        resp = requests.get(f"{BASE_URL}/dashboard/today", headers=headers)
        data = resp.json()
        meetings = data.get("meetings", [])
        
        if not meetings:
            print("No meetings found for today. Cannot test action execution.")
            return

        meeting_id = meetings[0]["id"]
        print(f"Using Meeting ID: {meeting_id}")
        
        # 3. Create an Action Item
        print("Creating Action Item...")
        action_payload = {
            "meeting_id": meeting_id,
            "description": "Test Execution Flow Task",
            "suggested_action": "Create Task"
        }
        resp = requests.post(f"{BASE_URL}/actions/", json=action_payload, headers=headers)
        if resp.status_code != 201:
            print(f"Create Action Failed: {resp.text}")
            return
            
        action_item = resp.json()
        action_id = action_item["id"]
        print(f"Created Action ID: {action_id}")
        
        # 4. Execute Action (Create Task - Notion)
        print("Executing Action (Notion)...")
        # Notion needs API key in env, which should be there
        exec_payload = {
            "params": {
                "action_type": "Create Task"
            }
        }
        resp = requests.post(f"{BASE_URL}/actions/{action_id}/execute", json=exec_payload, headers=headers)
        print(f"Execution Response ({resp.status_code}): {resp.text}")
        
        if resp.status_code == 200:
            print("Notion Execution Success!")
            
        # 5. Execute Action (Calendar)
        # We can re-execute the same item for testing purposes, or create another
        print("Executing Action (Calendar)...")
        exec_payload = {
            "params": {
                "action_type": "Create Calendar Invite"
            }
        }
        resp = requests.post(f"{BASE_URL}/actions/{action_id}/execute", json=exec_payload, headers=headers)
        print(f"Execution Response ({resp.status_code}): {resp.text}")

        # 6. Execute Action (Email)
        print("Executing Action (Email)...")
        exec_payload = {
            "params": {
                "action_type": "Send Email"
            }
        }
        resp = requests.post(f"{BASE_URL}/actions/{action_id}/execute", json=exec_payload, headers=headers)
        print(f"Execution Response ({resp.status_code}): {resp.text}")
        
    except Exception as e:
        print(f"Test Exception: {e}")

if __name__ == "__main__":
    test_flow()