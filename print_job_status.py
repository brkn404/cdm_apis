#!/usr/bin/env python3
import urllib3
import requests
from common import get_session_id, CDM_BASE_URL

# Disable SSL warnings (for testing only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_job_status(session_id):
    """Fetches and displays the current status (IDLE, RUNNING, COMPLETED, etc.) of each job."""
    url = f"{CDM_BASE_URL}/endeavour/job"
    headers = {
        "Accept": "application/json",
        "X-Endeavour-Sessionid": session_id,
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if jobs:
                print("Job Number | Status   | Name")
                print("-" * 40)
                for job in jobs:
                    job_id = job.get('id')
                    job_status = job.get('status')
                    job_name = job.get('name')
                    print(f"{job_id:<11} {job_status:<8} {job_name}")
            else:
                print("No jobs found.")
        else:
            print(f"Failed to retrieve jobs: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while retrieving job statuses: {str(e)}")

if __name__ == "__main__":
    session_id = get_session_id()

    if session_id:
        print("Fetching the current status of all jobs...\n")
        get_job_status(session_id)
    else:
        print("Failed to authenticate.")
