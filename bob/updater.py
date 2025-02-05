# bob/updater.py

from decimal import Decimal
import glob
import os
import shutil
from .ftp_client import FTPClient
from .config import VERSIONS_DIR, DATA_DIR
from .process_utils import reboot_device
from .logger import logger

def extract_version(filename: str) -> Decimal:
    """
    Assumes a filename like 'mainBOBv2.09.py' and extracts the version number.
    """
    try:
        version_str = filename.rsplit('v', 1)[1].split('.', 1)[0]
        return Decimal(version_str)
    except Exception as e:
        logger.error("Error extracting version: %s", e)
        return Decimal('0.00')

def get_local_main_version() -> (str, Decimal):
    """
    Locate the versioned main file and extract its version.
    """
    files = glob.glob(os.path.join(VERSIONS_DIR, "mainBOBv*"))
    if files:
        filename = files[0]
        version = extract_version(filename)
        return filename, version
    else:
        return None, Decimal('0.00')

def get_remote_version() -> Decimal:
    """
    Check for the remote version.
    (This example uses a fixed version; in production you’d list remote files via FTP.)
    """
    remote_filename = "mainBOBv2.10.py"
    return extract_version(remote_filename)

def download_update() -> str:
    """
    Download the updated main file from FTP and return its local path.
    """
    ftp_client = FTPClient()
    ftp_client.change_directory(FTP_DETAILS['target_down'])
    remote_file = "mainBOBv2.10.py"
    local_file = os.path.join(VERSIONS_DIR, remote_file)
    ftp_client.download_file(remote_file, local_file)
    ftp_client.quit()
    return local_file

def install_update(new_file: str, old_file: str):
    """
    Install the update by copying the new version over the main application file,
    removing the old version, writing an update flag, and rebooting.
    """
    main_app_path = '/opt/BOB/mainBOB.py'
    shutil.copy(new_file, main_app_path)
    if os.path.exists(old_file):
        os.remove(old_file)
    flag_file = os.path.join('/opt/BOB/logs/', f"{os.path.basename(old_file)}-flag.txt")
    with open(flag_file, 'w') as f:
        f.write("UPDATED!")
    reboot_device()

def run_update():
    """
    Main update routine.
    """
    local_file, local_version = get_local_main_version()
    remote_version = get_remote_version()
    logger.info("Local version: %s, Remote version: %s", local_version, remote_version)
    if remote_version > local_version:
        new_file = download_update()
        install_update(new_file, local_file)
    else:
        logger.info("No update required.")
