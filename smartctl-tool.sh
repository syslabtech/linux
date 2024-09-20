#!/bin/sh

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

# Function to run smartctl -a and save the output to a file
run_smartctl_a() {
    DEVICE=$1
    FILENAME=$(basename "$DEVICE")_output.txt
    echo "Saving smartctl output of $DEVICE to $FILENAME"
    $SUDO smartctl -a "$DEVICE" > "$FILENAME"
}


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
        
        # Run Ubuntu-specific commands
        $SUDO apt update
        $SUDO apt install -y smartmontools

    elif [ "$OS_NAME" = "alpine" ]; then
        echo "Alpine Linux detected. Version: $OS_INFO"
        
        # Run Alpine-specific commands
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
    sleep 300

    # Iterate through each line of the smartctl scan output
echo "$SCAN_OUTPUT" | while read -r LINE; do
    # Extract the device path (e.g., /dev/sda or /dev/nvme0)
    DEVICE=$(echo "$LINE" | awk '{print $1}')
    DEVICE_TYPE=$(echo "$LINE" | awk '{print $3}')

    # Run smartctl -a and save the output to a file
    run_smartctl_a "$DEVICE"

    done


else
    echo "The /etc/os-release file does not exist. Unable to detect OS."
fi

