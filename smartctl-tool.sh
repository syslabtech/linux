#!/bin/sh

# Function to log messages using logger (which sends output to the system log)
log_message() {
    # logger --size 1MiB -t smartctl_script "$1"
    logger -t smartctl_script "$1"
}

# Function to check if sudo is installed
check_sudo() {
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        SUDO=""
    fi
}

# Function to run smartctl short test
run_smartctl_test() {
    DEVICE=$1
    echo "Running smartctl test on $DEVICE"
    $SUDO smartctl -t short "$DEVICE"
}

# Function to run smartctl -a and save the output to a single file
run_smartctl_a() {
    DEVICE=$1
    OUTPUT=$($SUDO smartctl -a "$DEVICE")

    # Remove newlines, carriage returns, and spaces to create a single string
    # MODIFIED_OUTPUT=$(echo "$OUTPUT" | tr -d '\n\r '
    MODIFIED_OUTPUT=$(echo "$OUTPUT" | tr '\n' '|' | tr '\r' '|' | sed 's/||/||/g')

    # Append the output to the single output file
    echo "Drive Scanning Output for $DEVICE: $OUTPUT" >> smartctl_drivescan_normal_output.log
    echo "Drive Scanning Output for $DEVICE: $MODIFIED_OUTPUT" >> smartctl_drivescan_output.log
    log_message "$OUTPUT"
}

# Clear the file at the beginning of the script
echo "Clearing output file..."
> smartctl_drivescan_output.log  # This clears the file at the start of each run

# Check if /etc/os-release file exists
if [ -f /etc/os-release ]; then
    # Source the /etc/os-release file to get environment variables
    . /etc/os-release

    # Extract the OS name and version, and store the version in OS_INFO
    OS_NAME=$(echo "$NAME" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
    OS_INFO="$VERSION_ID"

    # Check if sudo is available
    check_sudo

    # Check if the system is Ubuntu or Alpine
    if [ "$OS_NAME" = "ubuntu" ]; then
        echo "Ubuntu detected. Version: $OS_INFO"
        $SUDO apt update
        $SUDO apt install -y smartmontools

    elif [ "$OS_NAME" = "alpine" ]; then
        echo "Alpine Linux detected. Version: $OS_INFO"
        $SUDO apk update
        $SUDO apk add smartmontools

    else
        echo "Unsupported operating system: $OS_NAME"
    fi

    # Run the smartctl --scan command and store the output in a temporary variable
    SCAN_OUTPUT=$(smartctl --scan)

    # Iterate through each line of the smartctl scan output
    echo "$SCAN_OUTPUT" | while read -r LINE; do
        # Extract the device path (e.g., /dev/sda or /dev/nvme0)
        DEVICE=$(echo "$LINE" | awk '{print $1}')
        DEVICE_TYPE=$(echo "$LINE" | awk '{print $3}')

        # If the device type is nvme, skip the test
        if [ "$DEVICE_TYPE" = "nvme" ]; then
            echo "Skipping NVMe device: $DEVICE"
        else
            # Run the smartctl short test on non-NVMe devices
            run_smartctl_test "$DEVICE"
        fi
    done

    echo "Sleeping for 5 minutes..."
    sleep 300  # Adjust the sleep time as needed for the tests to complete

    # Iterate through each line of the smartctl scan output
    echo "$SCAN_OUTPUT" | while read -r LINE; do
        # Extract the device path (e.g., /dev/sda or /dev/nvme0)
        DEVICE=$(echo "$LINE" | awk '{print $1}')
        DEVICE_TYPE=$(echo "$LINE" | awk '{print $3}')

        # Run smartctl -a and append the output to the combined output file
        run_smartctl_a "$DEVICE"
    done

else
    echo "The /etc/os-release file does not exist. Unable to detect OS."
fi
