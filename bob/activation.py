# File: bob/activation.py
import os
import logging
from bob.ftp_client import FTPClient
from bob.config import FTP_DETAILS, DATA_DIR

logger = logging.getLogger('bob.activation')

ACTIVATION_FILENAME_PATTERN = "activate-{device_id}.txt"

def download_activation_file(device_id: str):
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
    """
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
    """
    extinct_flag_path = os.path.join(os.path.dirname(log_filepath), "minionisdone.log")
    with open(extinct_flag_path, "w") as f:
        f.write("EXTINCT!")
    logger.info("Device %s marked as EXTINCT.", device_id)
