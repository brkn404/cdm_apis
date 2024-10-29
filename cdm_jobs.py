#!/usr/bin/env python3
import urllib3
import requests
import json
from common import get_session_id, CDM_BASE_URL

# Disable SSL warnings (for testing only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def list_jobs(session_id):
    """Lists all available jobs and returns their IDs."""
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
                print("Available Jobs:")
                for job in jobs:
                    print(f"ID: {job['id']}, Name: {job['name']}, Status: {job['status']}")
                return [job['id'] for job in jobs]
            else:
                print("No jobs found.")
                return []
        else:
            print(f"Failed to retrieve jobs: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while listing jobs: {str(e)}")
        return []

def list_sla_policies(session_id):
    """Lists all available SLA policies and returns their IDs."""
    url = f"{CDM_BASE_URL}/spec/storageprofile"
    headers = {
        "Accept": "application/json",
        "X-Endeavour-Sessionid": session_id,
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            policies = response.json().get("storageprofiles", [])
            if policies:
                print("Available SLA policies:")
                for policy in policies:
                    print(f"ID: {policy['id']}, Name: {policy['name']}")
                return [policy['id'] for policy in policies]
            else:
                print("No SLC policies found.")
                return []
        else:
            print(f"Failed to retrieve SLA policies: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while listing SLA policies: {str(e)}")
        return []

def get_job_by_id(session_id, job_id):
    """Fetches and displays key details of a specific job using its ID."""
    url = f"{CDM_BASE_URL}/endeavour/job/{job_id}"
    headers = {"Accept": "application/json", "X-Endeavour-Sessionid": session_id}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            job_info = response.json()

            # Clean and display relevant job details
            print(f"\nJob Details for ID: {job_id}")
            print(f"Name: {job_info.get('name')}")
            print(f"Description: {job_info.get('description')}")
            print(f"Policy Name: {job_info.get('policyName')}")
            print(f"Status: {job_info.get('status')}")
            print(f"Last Session Status: {job_info.get('lastSessionStatus')}")
            print(f"Type: {job_info.get('type')}")
            print(f"Sub-Type: {job_info.get('subType')}")
            print(f"Last Run Time: {job_info.get('lastrun', {}).get('start')}")
            print(f"Last Session Duration: {job_info.get('lastSessionDuration')} seconds")
            print(f"Results: {job_info.get('lastrun', {}).get('results')}")
        else:
            print(f"Failed to fetch job: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching job details: {str(e)}")

def start_job(session_id, job_id, sla_policy_id):
    """Starts a specific job by ID and provides meaningful feedback."""
    url = f"{CDM_BASE_URL}/endeavour/job/{job_id}?action=start"
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
        if response.status_code == 200:
            print(f"Job {job_id} started successfully.")
        elif response.status_code == 400:
            print(f"Failed to start job {job_id}: Bad request. {response.text}")
        elif response.status_code == 403:
            print(f"Permission denied to start job {job_id}.")
        elif response.status_code == 404:
            print(f"Job {job_id} not found.")
        elif response.status_code == 409:
            print(f"Job {job_id} is already running or in progress.")
        else:
            print(f"Failed to start job {job_id}: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while starting the job: {str(e)}")

def get_job_logs(session_id, log_id):
    """Fetches logs associated with a particular job."""
    url = f"{CDM_BASE_URL}/endeavour/log/job/{log_id}"
    headers = {"Accept": "application/json", "X-Endeavour-Sessionid": session_id}

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        print(f"Job Logs: {response.json()}")
    else:
        print(f"Failed to fetch logs: {response.status_code} - {response.text}")

if __name__ == "__main__":
    session_id = get_session_id()

    if session_id:
        print("Fetching available jobs...")
        job_ids = list_jobs(session_id)

        if not job_ids:
            print("No jobs available. Exiting.")
        else:
            print("Select an operation:")
            print("1. Get Job by ID")
            print("2. Start a Job")
            print("3. Get Job Logs")

            choice = input("Enter your choice (1-3): ")

            if choice in ["1", "2"]:
                print(f"Available Job IDs: {job_ids}")
                selected_job_id = input("Enter Job ID from the above list: ")

                if selected_job_id in job_ids:
                    if choice == "1":
                        get_job_by_id(session_id, selected_job_id)
                    elif choice == "2":
                        sla_policy_ids = list_sla_policies(session_id)
                        selected_sla_policy_id = input("Enter SLA Policy ID from the above list: ")
                        if selected_sla_policy_id in sla_policy_ids:
                            start_job(session_id, selected_job_id, selected_sla_policy_id)
                        else:
                            print("Invalid SLA policy ID selected.")
                else:
                    print("Invalid Job ID selected.")
            elif choice == "3":
                log_id = input("Enter Log ID: ")
                get_job_logs(session_id, log_id)
            else:
                print("Invalid choice.")
    else:
        print("Failed to authenticate.")
