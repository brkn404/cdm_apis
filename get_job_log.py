#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import urllib3
from common import CDM_BASE_URL, USERNAME, PASSWORD  # Importing from common.py

# Suppress SSL warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def list_jobs(session_id):
    """Lists available job IDs and names."""
    url = f"{CDM_BASE_URL}/endeavour/job"
    headers = {
        "Accept": "application/json",
        "X-Endeavour-Sessionid": session_id,
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
        
        print("\nAvailable Jobs:")
        for job in jobs:
            print(f"ID: {job.get('id')}, Name: {job.get('name')}")
            
        return jobs

    except requests.exceptions.RequestException as e:
        print(f"Failed to list jobs: {str(e)}")
        return []

def get_latest_job_log_via_lastrunlog(session_id, job_id):
    """Fetches and displays logs for a specified job ID in a readable format."""
    job_details_url = f"{CDM_BASE_URL}/endeavour/job/{job_id}"
    headers = {
        "Accept": "application/json",
        "X-Endeavour-Sessionid": session_id,
    }

    try:
        # Retrieve job details to access the lastrunlog link
        response = requests.get(job_details_url, headers=headers, verify=False)
        response.raise_for_status()
        job_details = response.json()
        
        lastrunlog_link = job_details["links"].get("lastrunlog", {}).get("href")
        
        if not lastrunlog_link:
            print("No lastrunlog link found in job details.")
            return
        
        print(f"\nRetrieved lastrunlog link: {lastrunlog_link}")
        
        # Retrieve logs from the lastrunlog link
        response_logs = requests.get(lastrunlog_link, headers=headers, verify=False)
        response_logs.raise_for_status()
        logs_response = response_logs.json()
        
        logs = logs_response.get("logs", [])
        
        if logs:
            print("\nLogs for the latest session:")
            for idx, log in enumerate(logs, start=1):
                # Convert logTime to readable format
                timestamp = datetime.utcfromtimestamp(log.get('logTime') / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{idx}. Time: {timestamp} | Type: {log.get('type')} | Message: {log.get('message')}")
        else:
            print("No logs found for the latest session.")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    # Step 1: Obtain session ID
    session_id = get_session_id()
    if not session_id:
        print("Unable to obtain session ID. Exiting.")
        return

    # Step 2: List jobs and prompt for selection
    jobs = list_jobs(session_id)
    if not jobs:
        print("No jobs available. Exiting.")
        return

    try:
        # Get job ID from user input
        job_id = input("\nEnter Job ID to retrieve the latest logs: ")
        
        # Step 3: Retrieve and display logs for selected job ID
        get_latest_job_log_via_lastrunlog(session_id, job_id)
    
    except ValueError:
        print("Invalid input. Please enter a valid Job ID.")

if __name__ == "__main__":
    main()
