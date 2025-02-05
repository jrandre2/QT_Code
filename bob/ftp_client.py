# bob/ftp_client.py

from ftplib import FTP_TLS
from .config import FTP_DETAILS

class FTPClient:
    def __init__(self):
        self.ftp = FTP_TLS(FTP_DETAILS['host'])
        self.ftp.login(FTP_DETAILS['user'], FTP_DETAILS['pass'])
        self.ftp.prot_p()  # Secure the data connection.

    def change_directory(self, directory):
        self.ftp.cwd(directory)

    def upload_file(self, local_filepath, remote_filename):
        with open(local_filepath, 'rb') as f:
            self.ftp.storbinary(f'STOR {remote_filename}', f)

    def download_file(self, remote_filename, local_filepath):
        with open(local_filepath, 'wb') as f:
            self.ftp.retrbinary(f'RETR {remote_filename}', f.write)

    def quit(self):
        self.ftp.quit()
