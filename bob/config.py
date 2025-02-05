# bob/config.py

import os
import configparser

# Default configuration values
DEFAULT_CONFIG = {
    'base': {
        'BASE_DIR': '/opt/BOB/'
    },
    'session': {
        'SESSION_DURATION_DAYS': '10'
    },
    'ftp': {
        'host': 'ftp.example.com',
        'user': 'username',
        'pass': 'password',
        'target_down': '/download_dir',
        'target_up': '/upload_dir',
        'target_activate': '/activate_dir'
    },
    'logging': {
        'LOG_DIR': 'logs/'
    },
    'speedtest': {
        'SPEED_TEST_INTERVAL': '300'  # default is 300 seconds (5 minutes)
    },
    'gps': {
        'GPS_PORT': '/dev/ttyAMA0',
        'GPS_BAUDRATE': '9600'
    },
    'survey': {
        'SURVEY_URL': 'https://survey.example.com'
    }
}

# Load the configuration file
# Assumes config.ini is located in the same directory as this config.py file.
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read_dict(DEFAULT_CONFIG)  # load defaults first

if os.path.exists(config_file_path):
    config.read(config_file_path)

# Expose configuration values as module-level constants
BASE_DIR = config.get('base', 'BASE_DIR')
SESSION_DURATION_DAYS = config.getint('session', 'SESSION_DURATION_DAYS')
SESSION_FILE = os.path.join(BASE_DIR, 'session_id.json')
LOG_DIR = os.path.join(BASE_DIR, config.get('logging', 'LOG_DIR'))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
VERSIONS_DIR = os.path.join(BASE_DIR, 'versions/')

# Speedtest interval in seconds.
SPEED_TEST_INTERVAL = config.getint('speedtest', 'SPEED_TEST_INTERVAL')

# FTP details
FTP_DETAILS = {
    'host': config.get('ftp', 'host'),
    'user': config.get('ftp', 'user'),
    'pass': config.get('ftp', 'pass'),
    'target_down': config.get('ftp', 'target_down'),
    'target_up': config.get('ftp', 'target_up'),
    'target_activate': config.get('ftp', 'target_activate')
}

# GPS configuration
GPS_PORT = config.get('gps', 'GPS_PORT')
GPS_BAUDRATE = config.getint('gps', 'GPS_BAUDRATE')

# Survey URL for the captive portal.
SURVEY_URL = config.get('survey', 'SURVEY_URL')


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


DEVICE_ID = get_device_id()
