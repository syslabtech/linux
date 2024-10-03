import requests
import json
import openpyxl
from openpyxl import Workbook

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Replace with your GitHub organization name
ORGANIZATION = "your-organization-name"

# GitHub Token (For authentication, especially for private repos or higher rate limits)
GITHUB_TOKEN = "your_github_token"

# Headers for GitHub API requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Initialize Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "GitHub Data"
# Define headers for the Excel sheet
ws.append(["Repository", "Branch", "Commit SHA", "Commit Message", "Workflow File URL", "Runner Information"])

def get_org_repositories(org_name):
    """Get all repositories for the organization."""
    url = f"{GITHUB_API_URL}/orgs/{org_name}/repos"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        repos = response.json()
        return [repo['name'] for repo in repos]
    else:
        print(f"Failed to fetch repositories. Status Code: {response.status_code}")
        return []

def get_branches(owner, repo):
    """Get all branches of the repository."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        branches = response.json()
        return [branch['name'] for branch in branches]
    else:
        print(f"Failed to fetch branches for repo '{repo}'. Status Code: {response.status_code}")
        return []

def get_metadata_for_branch(owner, repo, branch):
    """Get metadata for a specific branch."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs/heads/{branch}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for branch '{branch}' in repo '{repo}'. Status Code: {response.status_code}")
        return None

def get_workflow_file(owner, repo, branch):
    """Fetch the workflow files from the .github/workflows directory of a specific branch."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/.github/workflows?ref={branch}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        workflows = response.json()
        workflow_files = []
        for workflow in workflows:
            if workflow['name'].endswith('.yml') or workflow['name'].endswith('.yaml'):
                file_url = workflow['download_url']
                workflow_files.append(file_url)
        return workflow_files
    else:
        print(f"Failed to fetch workflows for branch '{branch}' in repo '{repo}'. Status Code: {response.status_code}")
        return []

def get_runner_info_from_workflow_file(workflow_url):
    """Extract runner information from a workflow file."""
    response = requests.get(workflow_url)
    
    if response.status_code == 200:
        content = response.text
        # Searching for runner type (e.g., 'runs-on: ubuntu-latest' or 'runs-on: self-hosted')
        runners = []
        for line in content.splitlines():
            if 'runs-on:' in line:
                runners.append(line.strip())
        return runners
    else:
        print(f"Failed to fetch workflow file from {workflow_url}. Status Code: {response.status_code}")
        return []

def scan_organization_repos(org_name):
    """Scan all repositories in the organization and fetch branch metadata and runner info."""
    repos = get_org_repositories(org_name)
    print(f"Repositories in organization '{org_name}': {repos}")
    
    for repo in repos:
        print(f"\nScanning repository: {repo}")
        
        # Get all branches for the repo
        branches = get_branches(org_name, repo)
        print(f"  Branches: {branches}")
        
        for branch in branches:
            print(f"\n  Fetching metadata for branch: {branch}")
            metadata = get_metadata_for_branch(org_name, repo, branch)
            
            # Check if metadata is None before proceeding
            if metadata is not None:
                commit_sha = metadata['object']['sha']
                commit_message = metadata['object'].get('message', 'No commit message available')

                # Get workflow files for the branch
                workflow_files = get_workflow_file(org_name, repo, branch)
                
                if workflow_files:
                    for wf_url in workflow_files:
                        # Extract runner information from each workflow file
                        runner_info = get_runner_info_from_workflow_file(wf_url)
                        runner_info_str = ', '.join(runner_info) if runner_info else 'No runner info'
                        
                        # Append the data into Excel sheet
                        ws.append([repo, branch, commit_sha, commit_message, wf_url, runner_info_str])
                else:
                    # If no workflow files, add a row with basic branch metadata
                    ws.append([repo, branch, commit_sha, commit_message, "No workflows", "No runner info"])
            else:
                print(f"  No metadata found for branch '{branch}'.")

if __name__ == "__main__":
    # Scan repositories in the organization
    scan_organization_repos(ORGANIZATION)
    
    # Save Excel file
    excel_filename = "github_metadata.xlsx"
    wb.save(excel_filename)
    print(f"\nData has been saved to {excel_filename}")
