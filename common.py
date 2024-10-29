import requests
from requests.auth import HTTPBasicAuth

# Base Configuration
#CDM_BASE_URL = "https://lbsvm29.tuc.stglabs.ibm.com:8443/api"
#API_URL = "https://192.168.72.50:8443/api/endeavour"
#USERNAME = "apiuser"
#PASSWORD = "tucsonAPIpa$$w0rd"
CDM_BASE_URL = "https://192.168.72.50:8443/api"
USERNAME = "admin"
PASSWORD = "CDM!ATSP@ssw0rd"  # Updated password

def get_session_id():
    """Logs in and returns the session ID."""
    url = f"{CDM_BASE_URL}/endeavour/session"

    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            verify=False,  # SSL verification disabled
        )
        response.raise_for_status()  # Raise exception for HTTP errors

        session_id = response.json().get("sessionid")
        if session_id:
            print(f"Session ID obtained: {session_id}")
            return session_id
        else:
            print("No session ID returned.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to obtain session ID: {str(e)}")
        return None
