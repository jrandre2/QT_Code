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
from bob.config import DATA_DIR, SPEED_TEST_INTERVAL
from bob.session import get_session
from bob.gps import read_gps


def run_speedtest():
    """
    Perform an internet speed test using the speedtest module.
    Returns download, upload speeds in Mbps and ping in ms.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
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
    Main application loop:
      - Retrieves a persistent session ID.
      - Initializes CSV files for speed test and GPS data.
      - Every configured interval, performs a speed test and logs results.
      - Attempts to record GPS data and logs it.
    """
    session_id = get_session()
    logger.info("Session ID for this deployment: %s", session_id)
    
    speed_csv_file = os.path.join(DATA_DIR, f"{session_id}-speed.csv")
    gps_csv_file = os.path.join(DATA_DIR, f"{session_id}-gps.csv")
    
    initialize_csv(speed_csv_file, ['timestamp', 'download (Mbps)', 'upload (Mbps)', 'ping (ms)'])
    initialize_csv(gps_csv_file, ['timestamp', 'latitude', 'longitude'])
    
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        download, upload, ping = run_speedtest()
        logger.info("Speedtest at %s - Download: %.2f Mbps, Upload: %.2f Mbps, Ping: %.2f ms",
                    current_time, download, upload, ping)
                    
        write_csv_row(speed_csv_file, [current_time, download, upload, ping])
        
        gps_data = read_gps()
        if gps_data:
            gps_timestamp = gps_data[0].strftime("%Y-%m-%d %H:%M:%S")
            latitude = gps_data[1]
            longitude = gps_data[2]
            write_csv_row(gps_csv_file, [gps_timestamp, latitude, longitude])
            logger.info("GPS data at %s - Latitude: %s, Longitude: %s", gps_timestamp, latitude, longitude)
        else:
            logger.error("GPS data unavailable at %s", current_time)
        
        time.sleep(SPEED_TEST_INTERVAL)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Main application loop terminated by user.")
    except Exception as e:
        logger.error("Unexpected error in main loop: %s", e)
