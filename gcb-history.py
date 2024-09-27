from google.cloud.devtools.cloudbuild_v1 import CloudBuildClient
import datetime
import pandas as pd

# Initialize the Cloud Build client
client = CloudBuildClient()

# Project ID
project_id = "################"  # Replace with your actual project ID

def get_builds(start_time=None, end_time=None):
    """
    Retrieve a list of builds with detailed information.
    Optional start_time and end_time can be used to filter builds within a specific time range.
    """
    request = {
        "project_id": project_id,
    }

    # Filter by time range if specified
    if start_time or end_time:
        filters = []
        if start_time:
            filters.append(f'create_time>="{start_time.isoformat()}Z"')  # Ensure UTC format
        if end_time:
            filters.append(f'create_time<="{end_time.isoformat()}Z"')  # Ensure UTC format
        request["filter"] = " AND ".join(filters)

    # Call the Cloud Build API to get the builds
    response = client.list_builds(request=request)

    return response

def make_naive(dt):
    """ Convert a timezone-aware datetime to a timezone-naive datetime. """
    return dt.replace(tzinfo=None) if dt else dt

def build_report(builds):
    """
    Generate a detailed report of builds with all relevant fields.
    """
    report = []
    
    for build in builds:
        build_info = {
            "id": build.id,
            "status": build.status.name,
            "create_time": make_naive(build.create_time.ToDatetime()) if hasattr(build.create_time, "ToDatetime") else make_naive(build.create_time),
            "start_time": make_naive(build.start_time.ToDatetime()) if build.start_time and hasattr(build.start_time, "ToDatetime") else make_naive(build.start_time),
            "finish_time": make_naive(build.finish_time.ToDatetime()) if build.finish_time and hasattr(build.finish_time, "ToDatetime") else make_naive(build.finish_time),
            "log_url": build.log_url,
            "repo_source": build.source.repo_source.repo_name if build.source.repo_source else None,
            "branch_name": build.source.repo_source.branch_name if build.source.repo_source else None,
            "commit_sha": build.source.repo_source.commit_sha if build.source.repo_source else None,
            "steps": [{"name": step.name, "status": step.status.name, "args": step.args, "dir": step.dir, "env": step.env} for step in build.steps],
            "images": build.images,
            "artifacts": build.artifacts,
            "timeout": build.timeout,
            "service_account": build.service_account,
            "project_id": build.project_id,
            "substitutions": build.substitutions,
            "tags": build.tags,
            "options": build.options,
            "status_detail": build.status_detail,
        }
        report.append(build_info)
    
    return report

def save_to_excel(report, filename):
    """
    Save the report to an Excel file.
    """
    # Create a DataFrame from the report
    df = pd.DataFrame(report)

    # Normalize 'steps' column
    df_steps = df['steps'].apply(lambda x: pd.Series(x))
    df_steps = df_steps.rename(columns={0: 'steps'})

    # Concatenate the DataFrame with steps
    final_df = pd.concat([df.drop(columns=['steps']), df_steps], axis=1)

    # Write to Excel file
    final_df.to_excel(filename, index=False, engine='openpyxl')

def print_report(report):
    """
    Print the report in a human-readable format.
    """
    for build in report:
        print(f"Build ID: {build['id']}")
        print(f"  Status: {build['status']}")
        print(f"  Created at: {build['create_time']}")
        print(f"  Started at: {build['start_time']}")
        print(f"  Finished at: {build['finish_time']}")
        print(f"  Log URL: {build['log_url']}")
        print(f"  Source Repository: {build['repo_source']}")
        print(f"  Branch: {build['branch_name']}")
        print(f"  Commit SHA: {build['commit_sha']}")
        print(f"  Steps: {[step['name'] for step in build['steps']]}")
        for step in build['steps']:
            print(f"    Step Name: {step['name']}, Status: {step['status']}, Args: {step['args']}, Dir: {step['dir']}, Env: {step['env']}")
        print(f"  Images: {', '.join(build['images'])}")
        print(f"  Artifacts: {build['artifacts']}")
        print(f"  Timeout: {build['timeout']}")
        print(f"  Service Account: {build['service_account']}")
        print(f"  Project ID: {build['project_id']}")
        print(f"  Substitutions: {build['substitutions']}")
        print(f"  Tags: {build['tags']}")
        print(f"  Options: {build['options']}")
        print(f"  Status Detail: {build['status_detail']}")
        print("-" * 40)

if __name__ == "__main__":
    # Define the date range for 2023 to 2024
    start_time = datetime.datetime(2024, 6, 1)
    end_time = datetime.datetime(2024, 12, 31)

    try:
        builds = get_builds(start_time=start_time, end_time=end_time)
        report = build_report(builds)
        
        # Print the report to the console
        print_report(report)

        # Save the report to Excel
        output_filename = "cloud_build_history.xlsx"
        save_to_excel(report, output_filename)
        print(f"Build report saved to {output_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
