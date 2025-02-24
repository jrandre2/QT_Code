# bob/checker.py

import os
import shutil
import logging
from bob.process_utils import is_process_running, reboot_device
from bob.config import LOG_DIR

# Configure logger directly in this module
logger = logging.getLogger('bob.checker')

def ensure_directory_exists(directory):
    """
    Ensure the specified directory exists, creating it if needed.
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    return True

def check_process(process_name):
    """
    Check if a specific process is running.
    
    Args:
        process_name (str): Name of the process to check
        
    Returns:
        bool: True if the process is running, False otherwise
    """
    try:
        if is_process_running(process_name):
            logger.info(f"Process '{process_name}' is running.")
            return True
        else:
            logger.error(f"Process '{process_name}' is not running.")
            return False
    except Exception as e:
        logger.error(f"Error checking process '{process_name}': {e}")
        return False

def archive_log(source_log, archived_log):
    """
    Archive a log file.
    
    Args:
        source_log (str): Path to the source log file
        archived_log (str): Path to the archived log file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(source_log):
            logger.error(f"Source log file does not exist: {source_log}")
            return False
            
        # Ensure the target directory exists
        log_dir = os.path.dirname(archived_log)
        if not ensure_directory_exists(log_dir):
            return False
            
        shutil.copy2(source_log, archived_log)
        logger.info(f"Log file archived: {source_log} -> {archived_log}")
        return True
    except Exception as e:
        logger.error(f"Error archiving log file: {e}")
        return False

def run_checker():
    """
    Check if the main application is running; if not, log the error,
    archive the log file, and reboot the device.
    """
    # Changed from main_app.py to mainBOB.py to match references in updater.py
    process_name = 'mainBOB.py'
    
    if check_process(process_name):
        logger.info("Main application is running normally.")
    else:
        logger.error(f"Main application ({process_name}) is not running. Preparing to reboot...")
        
        # Define log files
        log_file = os.path.join(LOG_DIR, 'theminion.log')
        archived_log = os.path.join(LOG_DIR, 'archived_theminion.log')
        
        # Archive log file before reboot
        if archive_log(log_file, archived_log):
            logger.info("Log file archived successfully. Rebooting device...")
            # Add a delay to ensure logging completes before reboot
            try:
                import time
                time.sleep(2)  # 2-second delay before rebooting
            except ImportError:
                pass
                
            # Reboot the device
            try:
                reboot_device()
            except Exception as e:
                logger.critical(f"Failed to reboot device: {e}")
        else:
            logger.error("Failed to archive log file. Attempting reboot anyway.")
            try:
                reboot_device()
            except Exception as e:
                logger.critical(f"Failed to reboot device: {e}")

# Allow running this module directly
if __name__ == '__main__':
    # Configure a console logger when running directly
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
    run_checker()
