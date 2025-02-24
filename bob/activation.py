# File: bob/activation.py
import os
import logging
import datetime  # Added the missing datetime import
from bob.ftp_client import FTPClient
from bob.config import FTP_DETAILS, DATA_DIR, LOG_DIR
from bob.led import bluelight_minion

logger = logging.getLogger('bob.activation')

ACTIVATION_FILENAME_PATTERN = "activate-{device_id}.txt"
EXTINCTION_FLAG_FILENAME = "minionisdone.log"

def download_activation_file(device_id: str):
    """
    Download the activation file from FTP server.
    
    Args:
        device_id (str): The unique identifier for this device
        
    Returns:
        str: Path to the downloaded activation file
    """
    ftp_client = FTPClient()
    ftp_client.change_directory(FTP_DETAILS['target_activate'])
    remote_filename = ACTIVATION_FILENAME_PATTERN.format(device_id=device_id)
    local_filepath = os.path.join(DATA_DIR, remote_filename)
    try:
        ftp_client.download_file(remote_filename, local_filepath)
        logger.info("Activation file downloaded: %s", local_filepath)
    except Exception as e:
        logger.error("Error downloading activation file: %s", e)
    finally:
        ftp_client.quit()
    return local_filepath

def check_activation_status(device_id: str) -> bool:
    """
    Reads the local activation file to determine if the device is activated.
    
    Args:
        device_id (str): The unique identifier for this device
        
    Returns:
        bool: True if device is activated, False otherwise
    """
    # First check if the device is marked as extinct
    if is_device_extinct():
        logger.warning("Device is marked as extinct. Will not activate.")
        return False
        
    local_filepath = os.path.join(DATA_DIR, ACTIVATION_FILENAME_PATTERN.format(device_id=device_id))
    try:
        with open(local_filepath, 'r') as f:
            status = f.read().strip()
        if status.lower() == "activated":
            logger.info("Device %s is activated.", device_id)
            return True
        else:
            logger.warning("Device %s is not activated.", device_id)
            return False
    except Exception as e:
        logger.error("Activation file for device %s not found: %s", device_id, e)
        return False

def upload_deactivation(device_id: str):
    """
    Upload a deactivation file to signal the device should deactivate.
    
    Args:
        device_id (str): The unique identifier for this device
    """
    local_filepath = os.path.join(DATA_DIR, ACTIVATION_FILENAME_PATTERN.format(device_id=device_id))
    # Overwrite local file with a deactivation message.
    with open(local_filepath, 'w') as f:
        f.write("BOB SAYS DEACTIVATE!!!")
    # Now upload via FTP.
    ftp_client = FTPClient()
    ftp_client.change_directory(FTP_DETAILS['target_activate'])
    try:
        ftp_client.upload_file(local_filepath, os.path.basename(local_filepath))
        logger.info("Deactivation file uploaded for device %s.", device_id)
    except Exception as e:
        logger.error("Error uploading deactivation file: %s", e)
    finally:
        ftp_client.quit()

def mark_extinct(device_id: str, log_filepath: str):
    """
    Archive or copy the log file and mark the device as 'EXTINCT'.
    
    Args:
        device_id (str): The unique identifier for this device
        log_filepath (str): Path to the log file to archive
    """
    extinct_flag_path = os.path.join(os.path.dirname(log_filepath), EXTINCTION_FLAG_FILENAME)
    with open(extinct_flag_path, "w") as f:
        f.write("EXTINCT!")
    logger.info("Device %s marked as EXTINCT.", device_id)
    
    # Turn on blue light to indicate completion/extinction
    bluelight_minion()
    
    # Also upload a notification to FTP
    try:
        notify_filepath = os.path.join(DATA_DIR, f"extinct-{device_id}.txt")
        with open(notify_filepath, "w") as f:
            f.write(f"Device {device_id} marked as EXTINCT at {datetime.datetime.now().isoformat()}")
        
        ftp_client = FTPClient()
        ftp_client.change_directory(FTP_DETAILS['target_up'])
        ftp_client.upload_file(notify_filepath, os.path.basename(notify_filepath))
        logger.info("Extinction notification uploaded for device %s.", device_id)
        ftp_client.quit()
    except Exception as e:
        logger.error("Error uploading extinction notification: %s", e)

def is_device_extinct() -> bool:
    """
    Check if the device has been marked as extinct.
    
    Returns:
        bool: True if device is marked as extinct, False otherwise
    """
    extinct_flag_path = os.path.join(LOG_DIR, EXTINCTION_FLAG_FILENAME)
    return os.path.exists(extinct_flag_path)

def handle_extinction():
    """
    Handle actions when the device is detected as extinct.
    This can be called from the main application loop to perform
    any necessary cleanup or shutdown procedures.
    """
    if is_device_extinct():
        logger.info("Device is marked as extinct. Performing extinction procedures.")
        # Additional extinction procedures can be added here
        # For example, you might want to:
        # - Stop collecting data
        # - Upload any remaining data
        # - Power down non-essential hardware
        # - Modify LED status
        bluelight_minion()  # Set LEDs to blue to indicate extinction status
        return True
    return False
