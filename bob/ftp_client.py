from ftplib import FTP_TLS
from .config import FTP_DETAILS

class FTPClient:
    def __init__(self):
        """Initialize the secure FTP connection using FTP_TLS."""
        self.ftp = FTP_TLS(FTP_DETAILS['host'])
        self.ftp.login(FTP_DETAILS['user'], FTP_DETAILS['pass'])
        self.ftp.prot_p()  # Secure the data connection.

    def change_directory(self, directory: str) -> None:
        """Change the working directory on the FTP server."""
        self.ftp.cwd(directory)

    def upload_file(self, local_filepath: str, remote_filename: str) -> None:
        """Upload a local file to the FTP server."""
        with open(local_filepath, 'rb') as f:
            self.ftp.storbinary(f'STOR {remote_filename}', f)

    def download_file(self, remote_filename: str, local_filepath: str) -> None:
        """Download a file from the FTP server to a local path."""
        with open(local_filepath, 'wb') as f:
            self.ftp.retrbinary(f'RETR {remote_filename}', f.write)

    def quit(self) -> None:
        """Terminate the FTP connection."""
        self.ftp.quit()
