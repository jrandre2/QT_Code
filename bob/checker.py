# bob/checker.py

import os
import shutil
from .process_utils import is_process_running, reboot_device
from .logger import logger
from .config import LOG_DIR

def run_checker():
    """
    Check if the main application is running; if not, log the error,
    archive the log file, and reboot the device.
    """
    if is_process_running('mainBOB.py'):
        logger.info("mainBOB is running.")
        # Optionally: upload the log file via FTP here.
    else:
        logger.error("mainBOB is not running. Rebooting...")
        log_file = os.path.join(LOG_DIR, 'theminion.log')
        archived_log = os.path.join(LOG_DIR, 'archived_theminion.log')
        shutil.copy(log_file, archived_log)
        reboot_device()

if __name__ == '__main__':
    run_checker()
