#!/usr/bin/env python3
"""
bob/main_app.py

This is the core application for the Raspberry Pi device.
It performs periodic internet speed tests and records the results,
optionally capturing GPS data as well.
All data is tagged with a persistent session ID that groups data for a
deployment period (e.g., 7-10 days), even if the device reboots.
"""

import time
import csv
import datetime
import os
import speedtest

from bob.logger import logger
from bob.config import DATA_DIR  # DATA_DIR should be defined in config.py (e.g., '/opt/BOB/data/')
from bob.session import get_session
from bob.gps import read_gps

def run_speedtest():
    """
    Perform an internet speed test using the speedtest module.
    Returns:
        download_speed (float): Download speed in Mbps.
        upload_speed (float): Upload speed in Mbps.
        ping (float): Ping in milliseconds.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        # Convert from bits/s to Mbps (1 Mbps = 1048576 bits/s)
        download_speed = st.download() / 1048576  
        upload_speed = st.upload() / 1048576
        ping = st.results.ping
        return download_speed, upload_speed, ping
    except Exception as e:
        logger.error("Speedtest error: %s", e)
        return 0, 0, 0

def write_csv_row(filename, row):
    """
    Append a row of data to a CSV file.
    """
    try:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    except Exception as e:
        logger.error("Error writing to CSV file %s: %s", filename, e)

def initialize_csv(filename, headers):
    """
    Create a new CSV file with the given headers if it doesn't already exist.
    """
    if not os.path.exists(filename):
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            logger.info("Created CSV file: %s", filename)
        except Exception as e:
            logger.error("Error initializing CSV file %s: %s", filename, e)

def main_loop():
    """
    Main application loop.
    
    - Retrieves a persistent session ID.
    - Initializes CSV files for speed test data and GPS data.
    - Every 5 minutes:
      - Performs an internet speed test,
      - Logs the results with a timestamp,
      - Attempts to read GPS data and log it.
    """
    # Retrieve or generate the persistent session ID.
    session_id = get_session()
    logger.info("Session ID for this deployment: %s", session_id)
    
    # Build filenames for data logs using the session ID.
    speed_csv_file = os.path.join(DATA_DIR, f"{session_id}-speed.csv")
    gps_csv_file = os.path.join(DATA_DIR, f"{session_id}-gps.csv")
    
    # Initialize CSV files with headers if they don't already exist.
    initialize_csv(speed_csv_file, ['timestamp', 'download (Mbps)', 'upload (Mbps)', 'ping (ms)'])
    initialize_csv(gps_csv_file, ['timestamp', 'latitude', 'longitude'])
    
    # Define the interval between speed tests (in seconds).
    speed_test_interval = 300  # 300 seconds = 5 minutes
    
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Perform an internet speed test.
        download, upload, ping = run_speedtest()
        logger.info("Speedtest results at %s - Download: %.2f Mbps, Upload: %.2f Mbps, Ping: %.2f ms",
                    current_time, download, upload, ping)
                    
        # Write speed test results to the CSV file.
        write_csv_row(speed_csv_file, [current_time, download, upload, ping])
        
        # Optionally, attempt to record GPS data.
        gps_data = read_gps()  # Expected to return [timestamp, latitude, longitude] or None.
        if gps_data:
            # Format the GPS timestamp as a string.
            gps_timestamp = gps_data[0].strftime("%Y-%m-%d %H:%M:%S")
            latitude = gps_data[1]
            longitude = gps_data[2]
            write_csv_row(gps_csv_file, [gps_timestamp, latitude, longitude])
            logger.info("GPS data recorded at %s - Latitude: %s, Longitude: %s", gps_timestamp, latitude, longitude)
        else:
            logger.error("GPS data unavailable at %s", current_time)
        
        # Wait for the next measurement interval.
        time.sleep(speed_test_interval)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Main application loop terminated by user.")
    except Exception as e:
        logger.error("Unexpected error in main loop: %s", e)
