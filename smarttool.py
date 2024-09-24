import re
import argparse
import os

# Define default scan file path
DEFAULT_SCAN_FILE = "sda_output.txt"

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

    # Extract Serial Number
    serial_number_match = re.search(r'Serial Number:\s+(.+)', smart_data)
    if serial_number_match:
        extracted_data['Serial Number'] = serial_number_match.group(1)

    # Extract Power_On_Hours
    power_on_hours_match = re.search(r'Power_On_Hours\s+[\w\s]+-\s*(\d+)', smart_data)
    if power_on_hours_match:
        extracted_data['Power On Hours'] = power_on_hours_match.group(1).strip()

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

    return extracted_data

# Function to save the extracted data into a log file
def save_to_log(extracted_data, log_filename="smart_data_log.txt"):
    with open(log_filename, 'a') as log_file:
        for key, value in extracted_data.items():
            log_file.write(f"{key}: {value}\n")

# Main function to extract and save data
def main(input_file):
    # Read the SMART data from the input file
    if os.path.isfile(input_file):
        with open(input_file, 'r') as file:
            smart_data = file.read()

        extracted_data = extract_smart_data(smart_data)
        save_to_log(extracted_data)
        print(f"Data successfully extracted and saved to log file.")
    else:
        print(f"Error: File '{input_file}' not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract SMART data from a text file.')
    parser.add_argument('input_file', nargs='?', default=DEFAULT_SCAN_FILE,
                        help=f'The path to the input SMART data file (default: {DEFAULT_SCAN_FILE})')
    
    args = parser.parse_args()
    main(args.input_file)
