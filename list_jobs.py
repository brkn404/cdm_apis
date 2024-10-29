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
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if jobs:
                print("Current Job Statuses:\n")
                for job in jobs:
                    job_id = job.get('id')
                    job_status = job.get('status')  # This shows IDLE, RUNNING, COMPLETED, etc.
                    job_name = job.get('name')
                    policy_name = job.get('policyName', "No policy assigned")

                    # Format output to make status more visible
                    print(f"[{job_status}] Job ID: {job_id}")
                    print(f"  Name: {job_name}")
                    print(f"  Associated SLA Policy: {policy_name}\n")
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
