import requests
import random
import time
import os

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"
TOKEN_URL = f"{API_URL}/token"
DATA_URL = f"{API_URL}/data/"

# Use a user you have already registered through the API docs
# In a real application, these would come from a secure place, not be hardcoded.
USER_CREDENTIALS = {
    "username": "testuser",
    "password": "password123"
}

def get_auth_token():
    """Logs in to the API and returns an access token."""
    try:
        response = requests.post(TOKEN_URL, data=USER_CREDENTIALS)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        token = response.json().get("access_token")
        print("Successfully authenticated.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Failed to authenticate: {e}")
        return None

def send_data(token):
    """Sends a single data point to the API."""
    try:
        cpu_temp = round(random.uniform(40.0, 90.0), 2)
        data_payload = {"name": "cpu_temp", "value": cpu_temp}
        
        # Include the token in the Authorization header. This is the standard way.
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(DATA_URL, json=data_payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Successfully sent data: {data_payload}")
            return True
        else:
            print(f"Failed to send data. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error while sending data: {e}")
        return False

# --- Main Loop ---
if __name__ == "__main__":
    print("Starting data simulator...")
    access_token = get_auth_token()

    while True:
        if not access_token:
            print("No access token. Retrying authentication in 10 seconds...")
            time.sleep(10)
            access_token = get_auth_token()
            continue

        success = send_data(access_token)
        
        # If sending data fails (e.g., token expired), try re-authenticating.
        if not success:
            print("Attempting to re-authenticate...")
            access_token = get_auth_token()

        time.sleep(3)