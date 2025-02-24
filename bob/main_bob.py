#!/usr/bin/env python3
"""
bob/main_bob.py

This is the core application for the Raspberry Pi device.
It performs periodic internet speed tests, captures GPS data,
logs the results to CSV files (using a persistent session ID),
and performs ancillary functions such as LED status indications,
internet connectivity checks, activation verification,
and even self-update routines.
"""

import time
import datetime
import os
import csv
import speedtest
import contextlib
import atexit

# First import initialize module and set up the system
from bob.initialize import initialize_system
# Initialize configuration and logging systems
config = initialize_system()

# Now it's safe to import other modules
from bob.config import DATA_DIR, SPEED_TEST_INTERVAL, DEVICE_ID
from bob.logger import logger
from bob.gps import read_gps
from bob.led import ready_red_leds, intled_green, gpsled_green, bluelight_minion
from bob.internet import check_internet, get_public_ip
from bob.data_uploader import upload_csv_files
from bob.activation import download_activation_file, check_activation_status, handle_extinction, is_device_extinct
from bob.speedtest_upgrade import check_speedtest_version
from bob.session import get_session


class FileManager:
    """
    Manages file handles for CSV operations throughout the application lifecycle.
    Opens files once and keeps them open until the application terminates.
    """
    def __init__(self, file_paths, headers):
        """
        Initialize the file manager with file paths and their headers.
        
        Args:
            file_paths (dict): Dictionary mapping file identifiers to file paths
            headers (dict): Dictionary mapping file identifiers to column headers
        """
        self.file_paths = file_paths
        self.file_handles = {}
        self.csv_writers = {}
        self.headers = headers
        
    def initialize_files(self):
        """Initialize all files and open file handles."""
        for file_id, file_path in self.file_paths.items():
            self._initialize_file(file_id, file_path, self.headers[file_id])
    
    def _initialize_file(self, file_id, file_path, headers):
        """
        Initialize a single CSV file with headers if it doesn't exist,
        and open a file handle for writing.
        """
        file_exists = os.path.exists(file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Open file for writing (append mode)
        self.file_handles[file_id] = open(file_path, 'a', newline='')
        self.csv_writers[file_id] = csv.writer(self.file_handles[file_id])
        
        # Write headers if this is a new file
        if not file_exists:
            self.csv_writers[file_id].writerow(headers)
            self.file_handles[file_id].flush()
            logger.info(f"Initialized CSV file: {file_path}")
    
    def write_row(self, file_id, row_data):
        """
        Write a row to the specified CSV file.
        
        Args:
            file_id (str): Identifier for the file
            row_data (list): Data to write as a row
        """
        if file_id in self.csv_writers:
            self.csv_writers[file_id].writerow(row_data)
            self.file_handles[file_id].flush()  # Ensure data is written to disk
            return True
        else:
            logger.error(f"Attempted to write to unknown file ID: {file_id}")
            return False
    
    def close_all(self):
        """Close all open file handles."""
        for file_id, handle in self.file_handles.items():
            try:
                handle.close()
                logger.info(f"Closed file: {self.file_paths[file_id]}")
            except Exception as e:
                logger.error(f"Error closing file {self.file_paths[file_id]}: {e}")
        
        # Clear the dictionaries
        self.file_handles.clear()
        self.csv_writers.clear()


def main_loop():
    """Main application loop that runs continuously."""
    # Signal startup with red LEDs.
    ready_red_leds()

    # Check if device is extinct before proceeding
    if is_device_extinct():
        logger.info("Device is marked as extinct. Entering minimal operation mode.")
        bluelight_minion()
        # You could implement a minimal operation loop here if needed
        # For example, just respond to critical commands but don't collect data
        return

    # Check for active internet connection.
    if not check_internet():
        logger.error("Internet not available. Exiting main loop.")
        return

    # Retrieve and log public IP.
    public_ip = get_public_ip()
    if public_ip:
        logger.info("Public IP: %s", public_ip)
    else:
        logger.warning("Public IP not available.")

    # Check for speedtest-cli upgrade if necessary.
    if check_speedtest_version():
        logger.info("Speedtest upgraded. Device may need to reboot soon.")
        # Optionally, trigger a reboot here.

    # Download activation file from FTP and verify activation.
    download_activation_file(DEVICE_ID)
    if not check_activation_status(DEVICE_ID):
        logger.error("Device %s not activated. Exiting main loop.", DEVICE_ID)
        return

    # Retrieve a persistent session ID for this deployment.
    session_id = get_session()
    logger.info("Session ID: %s", session_id)

    # Define CSV file paths and headers
    file_paths = {
        'speed': os.path.join(DATA_DIR, f"{session_id}-speed.csv"),
        'gps': os.path.join(DATA_DIR, f"{session_id}-gps.csv"),
    }
    
    headers = {
        'speed': ["timestamp", "download (Mbps)", "upload (Mbps)", "ping (ms)"],
        'gps': ["timestamp", "latitude", "longitude"],
    }
    
    # Create file manager and initialize files
    file_manager = FileManager(file_paths, headers)
    file_manager.initialize_files()
    
    # Register cleanup function to ensure files are closed properly
    atexit.register(file_manager.close_all)

    # Change LED to green to indicate that internet is ready.
    intled_green()

    try:
        while True:
            # Check extinction status at the start of each loop
            if handle_extinction():
                logger.info("Extinction detected during operation. Exiting main loop.")
                break
                
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Run an internet speed test.
            try:
                st = speedtest.Speedtest()
                st.get_best_server()
                download_speed = st.download() / 1048576  # Convert to Mbps.
                upload_speed = st.upload() / 1048576      # Convert to Mbps.
                ping = st.results.ping
                logger.info("Speedtest at %s: Download=%.2f Mbps, Upload=%.2f Mbps, Ping=%.2f ms",
                            current_time, download_speed, upload_speed, ping)
                
                # Write speed test results directly to the open file
                file_manager.write_row('speed', [
                    current_time, 
                    f"{download_speed:.2f}", 
                    f"{upload_speed:.2f}", 
                    f"{ping:.2f}"
                ])
            except Exception as e:
                logger.error("Error during speedtest: %s", e)

            # Attempt to read GPS data.
            gps_data = read_gps()
            if gps_data:
                gps_timestamp = gps_data[0].strftime("%Y-%m-%d %H:%M:%S")
                latitude = gps_data[1]
                longitude = gps_data[2]
                
                # Write GPS data directly to the open file
                file_manager.write_row('gps', [gps_timestamp, latitude, longitude])
                
                # Indicate a successful GPS read with a green LED.
                gpsled_green()
                logger.info("GPS data at %s: Latitude=%s, Longitude=%s", 
                           gps_timestamp, latitude, longitude)
            else:
                logger.error("GPS data unavailable at %s", current_time)

            # Optionally, upload CSV files to the FTP server.
            try:
                upload_csv_files()
            except Exception as e:
                logger.error("Error uploading CSV files: %s", e)

            # Sleep for the configured speed test interval.
            time.sleep(SPEED_TEST_INTERVAL)
    finally:
        # Ensure files are closed if the loop exits
        file_manager.close_all()
        # Deregister the atexit handler since we've already cleaned up
        atexit.unregister(file_manager.close_all)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Main loop terminated by user.")
    except Exception as e:
        logger.error("Unexpected error in main loop: %s", e)
