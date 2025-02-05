# bob/config.py

import os

# Base directory for storing logs, session files, data, etc.
BASE_DIR = '/opt/BOB/'

# File that will store the session id and its creation time.
SESSION_FILE = os.path.join(BASE_DIR, 'session_id.json')

# Define how many days a session is valid (e.g., 10 days).
SESSION_DURATION_DAYS = 10

# FTP credentials and targets
FTP_DETAILS = {
    'host': 'ftp.example.com',
    'user': 'username',
    'pass': 'password',
    'target_down': '/download_dir',
    'target_up': '/upload_dir',
    'target_activate': '/activate_dir'
}

# Directories for logs, data, and versioned files.
LOG_DIR = os.path.join(BASE_DIR, 'logs/')
DATA_DIR = os.path.join(BASE_DIR, 'data/')
VERSIONS_DIR = os.path.join(BASE_DIR, 'versions/')

# Device ID retrieval function.
def get_device_id() -> str:
    """
    Retrieve a hardware-specific device id (e.g., from /proc/cpuinfo).
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except Exception:
        pass
    return "UNKNOWN_DEVICE"

# Export the device id as a constant.
DEVICE_ID = get_device_id()
