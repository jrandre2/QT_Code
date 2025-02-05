# File: bob/data_uploader.py
import os
import glob
import logging
from bob.ftp_client import FTPClient
from bob.config import FTP_DETAILS, DATA_DIR

logger = logging.getLogger('bob.data_uploader')

def upload_csv_files():
    ftp_client = FTPClient()
    ftp_client.change_directory(FTP_DETAILS['target_up'])
    # Look for CSV files in the DATA_DIR.
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    for file in files:
        try:
            ftp_client.upload_file(file, os.path.basename(file))
            logger.info("Uploaded file: %s", file)
            # Optionally, delete file after upload.
            os.remove(file)
            logger.info("Deleted local file: %s", file)
        except Exception as e:
            logger.error("Failed to upload %s: %s", file, e)
    ftp_client.quit()
