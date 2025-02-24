# bob/config.py

import os
import configparser
import logging
import socket
from pathlib import Path

# Configure module logger
logger = logging.getLogger('bob.config')

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
        'LOG_DIR': 'logs/',
        'LOG_LEVEL': 'INFO',
        'LOG_ROTATION_SIZE': '10485760',  # 10MB
        'LOG_BACKUP_COUNT': '5'
    },
    'speedtest': {
        'SPEED_TEST_INTERVAL': '300',  # default is 300 seconds (5 minutes)
        'SPEEDTEST_TARGET_VERSION': '2.1.1'
    },
    'gps': {
        'GPS_PORT': '/dev/ttyAMA0',
        'GPS_BAUDRATE': '9600',
        'GPS_TIMEOUT': '1'
    },
    'survey': {
        'SURVEY_URL': 'https://survey.example.com'
    }
}

def get_env_var(name, default=None):
    """
    Get an environment variable with a fallback default value.
    Environment variables are prefixed with BOB_.
    
    Args:
        name (str): Name of the environment variable (without prefix)
        default: Default value if environment variable doesn't exist
        
    Returns:
        The environment variable value or default
    """
    env_name = f"BOB_{name.upper()}"
    return os.environ.get(env_name, default)

def get_config_path():
    """
    Determine the path to the config file.
    
    Returns:
        Path to the config file
    """
    # First check for environment variable
    config_path = get_env_var('CONFIG_PATH')
    if config_path and os.path.exists(config_path):
        return config_path
    
    # Default path in the same directory as this file
    default_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    return default_path

def ensure_directory_exists(directory_path):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to ensure exists
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False

# Load the configuration file
config_file_path = get_config_path()
config = configparser.ConfigParser()
config.read_dict(DEFAULT_CONFIG)  # load defaults first

try:
    if os.path.exists(config_file_path):
        logger.info(f"Loading configuration from {config_file_path}")
        config.read(config_file_path)
    else:
        logger.warning(f"Configuration file not found at {config_file_path}, using defaults")
except Exception as e:
    logger.error(f"Error reading configuration file: {e}")

# Expose configuration values as module-level constants
# Allow environment variables to override config file values

# Base directory
BASE_DIR = get_env_var('BASE_DIR', config.get('base', 'BASE_DIR'))

# Session settings
SESSION_DURATION_DAYS = int(get_env_var('SESSION_DURATION_DAYS', 
                                        config.get('session', 'SESSION_DURATION_DAYS')))
SESSION_FILE = os.path.join(BASE_DIR, 'session_id.json')

# Directory paths
LOG_DIR = os.path.join(BASE_DIR, get_env_var('LOG_DIR', config.get('logging', 'LOG_DIR')))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
VERSIONS_DIR = os.path.join(BASE_DIR, 'versions/')

# Logging settings
LOG_LEVEL = get_env_var('LOG_LEVEL', config.get('logging', 'LOG_LEVEL'))
LOG_ROTATION_SIZE = int(get_env_var('LOG_ROTATION_SIZE', 
                                    config.get('logging', 'LOG_ROTATION_SIZE')))
LOG_BACKUP_COUNT = int(get_env_var('LOG_BACKUP_COUNT', 
                                   config.get('logging', 'LOG_BACKUP_COUNT')))

# Speedtest configuration
SPEED_TEST_INTERVAL = int(get_env_var('SPEED_TEST_INTERVAL', 
                                      config.get('speedtest', 'SPEED_TEST_INTERVAL')))
SPEEDTEST_TARGET_VERSION = get_env_var('SPEEDTEST_TARGET_VERSION',
                                       config.get('speedtest', 'SPEEDTEST_TARGET_VERSION'))

# FTP details - preferably use environment variables for credentials
FTP_DETAILS = {
    'host': get_env_var('FTP_HOST', config.get('ftp', 'host')),
    'user': get_env_var('FTP_USER', config.get('ftp', 'user')),
    'pass': get_env_var('FTP_PASS', config.get('ftp', 'pass')),
    'target_down': get_env_var('FTP_TARGET_DOWN', config.get('ftp', 'target_down')),
    'target_up': get_env_var('FTP_TARGET_UP', config.get('ftp', 'target_up')),
    'target_activate': get_env_var('FTP_TARGET_ACTIVATE', config.get('ftp', 'target_activate'))
}

# GPS configuration
GPS_PORT = get_env_var('GPS_PORT', config.get('gps', 'GPS_PORT'))
GPS_BAUDRATE = int(get_env_var('GPS_BAUDRATE', config.get('gps', 'GPS_BAUDRATE')))
GPS_TIMEOUT = int(get_env_var('GPS_TIMEOUT', config.get('gps', 'GPS_TIMEOUT')))

# Survey URL for the captive portal
SURVEY_URL = get_env_var('SURVEY_URL', config.get('survey', 'SURVEY_URL'))

def get_device_id() -> str:
    """
    Retrieve a hardware-specific device id (e.g., from /proc/cpuinfo).
    Falls back to hostname if cpuinfo is not available.
    
    Returns:
        str: Device ID string
    """
    # Try to get from environment variable first
    env_device_id = get_env_var('DEVICE_ID')
    if env_device_id:
        return env_device_id
        
    # Try to get from cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except Exception as e:
        logger.warning(f"Could not retrieve device ID from /proc/cpuinfo: {e}")
    
    # Fall back to hostname
    try:
        return socket.gethostname()
    except Exception as e:
        logger.error(f"Could not retrieve hostname: {e}")
    
    # Last resort fallback
    return "UNKNOWN_DEVICE"


# Create necessary directories
for directory in [BASE_DIR, LOG_DIR, DATA_DIR, VERSIONS_DIR]:
    ensure_directory_exists(directory)

# Set the device ID
DEVICE_ID = get_device_id()

def print_config():
    """
    Print current configuration for debugging purposes.
    Masks sensitive information.
    """
    config_dict = {
        'BASE_DIR': BASE_DIR,
        'SESSION_DURATION_DAYS': SESSION_DURATION_DAYS,
        'SESSION_FILE': SESSION_FILE,
        'LOG_DIR': LOG_DIR,
        'DATA_DIR': DATA_DIR,
        'VERSIONS_DIR': VERSIONS_DIR,
        'SPEED_TEST_INTERVAL': SPEED_TEST_INTERVAL,
        'GPS_PORT': GPS_PORT,
        'GPS_BAUDRATE': GPS_BAUDRATE,
        'SURVEY_URL': SURVEY_URL,
        'DEVICE_ID': DEVICE_ID,
        'FTP_HOST': FTP_DETAILS['host'],
        'FTP_USER': FTP_DETAILS['user'],
        'FTP_PASS': '********',  # Masked for security
    }
    
    logger.info("Current configuration:")
    for key, value in config_dict.items():
        logger.info(f"  {key}: {value}")

# Print config on module load if DEBUG env var is set
if get_env_var('DEBUG') == '1':
    print_config()
