#!/usr/bin/env python3
import urllib3
import requests
import json
import time
from common import CDM_BASE_URL, get_session_id  # Import CDM_BASE_URL and get_session_id from common.py

# Constants
JOB_1031 = "1031"  # Job 1031 ID
JOB_1044 = "1044"  # Job 1044 ID
SLA_POLICY_ID = "15"  # SLA policy ID for both jobs (update if different per job)
CHECK_INTERVAL = 30  # Interval to wait between status checks (in seconds)

# Disable SSL warnings (for testing only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_job_status(session_id, job_id):
    """Fetches the status of a specific job by ID."""
    url = f"{CDM_BASE_URL}/job/{job_id}"
    headers = {"Accept": "application/json", "X-Endeavour-Sessionid": session_id}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            job_info = response.json()
            return job_info.get("status", "UNKNOWN")
        else:
            print(f"Failed to fetch job status: {response.status_code} - {response.text}")
            return "UNKNOWN"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching job status: {str(e)}")
        return "UNKNOWN"

def start_job(session_id, job_id, sla_policy_id):
    """Starts a specific job by ID."""
    url = f"{CDM_BASE_URL}/job/{job_id}?action=start"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Endeavour-Sessionid": session_id
    }
    data = {
        "actionname": sla_policy_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"Job {job_id} started successfully.")
        else:
            print(f"Failed to start job {job_id}: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while starting the job: {str(e)}")

def wait_for_completion(session_id, job_id):
    """Waits for a job to complete and returns True if it succeeded, otherwise False."""
    while True:
        status = get_job_status(session_id, job_id)
        print(f"Job {job_id} current status: {status}")
        
        if status in ["COMPLETED", "IDLE"]:
            print(f"Job {job_id} completed successfully.")
            return True
        elif status in ["FAILED", "CANCELLED"]:
            print(f"Job {job_id} did not complete successfully. Status: {status}")
            return False
        elif status in ["RUNNING", "ACTIVE"]:
            print(f"Job {job_id} is still in progress. Checking again in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
        else:
            print(f"Unexpected job status: {status}")
            return False

def main():
    session_id = get_session_id()  # Use get_session_id from common.py
    if not session_id:
        print("Unable to obtain session. Exiting.")
        return

    # Start job 1031 and wait for its completion
    start_job(session_id, JOB_1031, SLA_POLICY_ID)
    if wait_for_completion(session_id, JOB_1031):
        # If job 1031 completes successfully, start job 1044
        start_job(session_id, JOB_1044, SLA_POLICY_ID)
    else:
        print("Job 1031 did not complete successfully. Job 1044 will not be started.")

if __name__ == "__main__":
    main()
