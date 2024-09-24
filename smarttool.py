import re
import argparse
import os
import json
from datetime import datetime, timedelta, timezone

# Define default scan file path
DEFAULT_SCAN_FILE = "sda_output.txt"
SUMMARY_LOG_FILE = "summary_smart_data_log.json"

# Function to extract data using regular expressions
def extract_smart_data(smart_data):
    extracted_data = {}

    # Extract Model Family
    model_family_match = re.search(r'Model Family:\s+(.+)', smart_data)
    if model_family_match:
        extracted_data['Model Family'] = model_family_match.group(1)

    # Extract Device Model
    device_model_match = re.search(r'Device Model:\s+(.+)', smart_data)
    if device_model_match:
        extracted_data['Device Model'] = device_model_match.group(1)

    # Extract Model Number
    model_number_match = re.search(r'Model Number:\s+(.+)', smart_data)
    if model_number_match:
        extracted_data['Model Number'] = model_number_match.group(1).strip()

    # Extract Serial Number
    serial_number_match = re.search(r'Serial Number:\s+(.+)', smart_data)
    if serial_number_match:
        extracted_data['Serial Number'] = serial_number_match.group(1)

    # Extract Power_On_Hours
    power_on_hours_match = re.search(r'Power_On_Hours\s+[\w\s]+-\s*(\d+)', smart_data)
    if power_on_hours_match:
        extracted_data['Power On Hours'] = power_on_hours_match.group(1).replace(',', '').strip()

    # Extract Power On Hours (NVME)
    power_on_hours_match = re.search(r'Power On Hours:\s+([\d,]+)', smart_data)
    if power_on_hours_match:
        extracted_data['Power On Hours'] = power_on_hours_match.group(1).replace(',', '').strip()

    # Extract Lifetime_Writes_GiB
    lifetime_writes_match = re.search(r'Lifetime_Writes_GiB\s+[\w\s]+-\s*(\d+)', smart_data)
    if lifetime_writes_match:
        extracted_data['Lifetime Writes GiB'] = lifetime_writes_match.group(1).strip()

    # Extract Host_Writes_32MiB or Total_LBAs_Written
    host_writes_match = re.search(r'Host_Writes_32MiB\s+[\w\s]+-\s*(\d+)', smart_data)
    if host_writes_match:
        extracted_data['Host Writes (32 MiB)'] = host_writes_match.group(1).strip()

    total_lbas_written_match = re.search(r'Total_LBAs_Written\s+[\w\s]+-\s*(\d+)', smart_data)
    if total_lbas_written_match:
        extracted_data['Total LBAs Written'] = total_lbas_written_match.group(1).strip()

    # Extract Data Units Written (removing content in brackets and commas)
    data_units_written_match = re.search(r'Data Units Written:\s+([\d,]+)', smart_data)
    if data_units_written_match:
        extracted_data['Data Units Written'] = data_units_written_match.group(1).replace(',', '').strip()

    # Extract and convert Local Time to UTC
    local_time_match = re.search(r'Local Time is:\s+(.+)', smart_data)
    if local_time_match:
        local_time_str = local_time_match.group(1).strip()
        extracted_data['Local Time'] = local_time_str
        extracted_data['UTC Time'] = convert_to_utc(local_time_str)

    return extracted_data

# Improved function to convert local time to UTC
def convert_to_utc(local_time_str):
    try:
        # Check for UTC directly, assuming the time is already in UTC
        if "UTC" in local_time_str:
            local_time = datetime.strptime(local_time_str, "%a %b %d %H:%M:%S %Y UTC")
            utc_time = local_time.replace(tzinfo=timezone.utc)
            return utc_time.isoformat()

        # Handle IST conversion (assuming UTC+5:30)
        elif "IST" in local_time_str:
            local_time = datetime.strptime(local_time_str, "%a %b %d %H:%M:%S %Y IST")
            ist_offset = timedelta(hours=5, minutes=30)
            ist = timezone(ist_offset)
            local_time = local_time.replace(tzinfo=ist)
            utc_time = local_time.astimezone(timezone.utc)
            return utc_time.isoformat()

        else:
            # If no known timezone suffix, raise an error or handle it as needed
            raise ValueError(f"Unknown timezone format in time string: {local_time_str}")

    except Exception as e:
        print(f"Error converting time: {e}")
        return "Conversion Error"

# Function to save the extracted data into a summary log file (JSON format)
def save_to_summary_log(extracted_data, log_filename=SUMMARY_LOG_FILE):
    with open(log_filename, 'a') as log_file:
        json.dump(extracted_data, log_file)
        log_file.write('\n')   # Write each JSON object on a new line

# Function to process a single file
def process_file(file_path):
    with open(file_path, 'r') as file:
        smart_data = file.read()

    extracted_data = extract_smart_data(smart_data)
    extracted_data['source_file'] = os.path.basename(file_path)  # Include the source file name in the data
    save_to_summary_log(extracted_data)

# Main function to scan files and process each
def main(directory="."):
    log_files = [f for f in os.listdir(directory) if f.endswith('_output.txt')]

    if not log_files:
        print("No log files found.")
        return
    
    # Clear the summary log file by opening it in write mode at the start of the script

    with open(SUMMARY_LOG_FILE, 'w') as log_file:
        pass  # Just open and close the file to clear its contents

    for log_file in log_files:
        file_path = os.path.join(directory, log_file)
        process_file(file_path)
        print(f"Processed: {file_path}")

    print(f"Data successfully extracted and saved to {SUMMARY_LOG_FILE}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scan all _output.txt files in the directory and extract SMART data.')
    parser.add_argument('directory', nargs='?', default=".",
                        help='The directory to scan for _output.txt files (default: current directory)')

    args = parser.parse_args()
    main(args.directory)
