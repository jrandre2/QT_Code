#!/usr/bin/env python3
"""
bob/main_app.py

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

from bob.logger import logger
from bob.config import DATA_DIR, SPEED_TEST_INTERVAL, DEVICE_ID
from bob.gps import read_gps
from bob.led import ready_red_leds, intled_green, gpsled_green, bluelight_minion
from bob.internet import check_internet, get_public_ip
from bob.data_uploader import upload_csv_files
from bob.activation import download_activation_file, check_activation_status
from bob.speedtest_upgrade import check_speedtest_version
from bob.session import get_session

def main_loop():
    # Signal startup with red LEDs.
    ready_red_leds()

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

    # Define CSV file paths for speed and GPS data.
    speed_csv_file = os.path.join(DATA_DIR, f"{session_id}-speed.csv")
    gps_csv_file = os.path.join(DATA_DIR, f"{session_id}-gps.csv")

    # Initialize CSV files with headers if they do not exist.
    if not os.path.exists(speed_csv_file):
        with open(speed_csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "download (Mbps)", "upload (Mbps)", "ping (ms)"])
        logger.info("Initialized speed CSV: %s", speed_csv_file)
    
    if not os.path.exists(gps_csv_file):
        with open(gps_csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "latitude", "longitude"])
        logger.info("Initialized GPS CSV: %s", gps_csv_file)

    # Change LED to green to indicate that internet is ready.
    intled_green()

    while True:
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
            # Append speed test results to the CSV file.
            with open(speed_csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([current_time, f"{download_speed:.2f}", f"{upload_speed:.2f}", f"{ping:.2f}"])
        except Exception as e:
            logger.error("Error during speedtest: %s", e)

        # Attempt to read GPS data.
        gps_data = read_gps()
        if gps_data:
            gps_timestamp = gps_data[0].strftime("%Y-%m-%d %H:%M:%S")
            latitude = gps_data[1]
            longitude = gps_data[2]
            with open(gps_csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([gps_timestamp, latitude, longitude])
            # Indicate a successful GPS read with a green LED.
            gpsled_green()
            logger.info("GPS data at %s: Latitude=%s, Longitude=%s", gps_timestamp, latitude, longitude)
        else:
            logger.error("GPS data unavailable at %s", current_time)

        # Optionally, upload CSV files to the FTP server and clean up local files.
        try:
            upload_csv_files()
        except Exception as e:
            logger.error("Error uploading CSV files: %s", e)

        # Sleep for the configured speed test interval.
        time.sleep(SPEED_TEST_INTERVAL)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Main loop terminated by user.")
    except Exception as e:
        logger.error("Unexpected error in main loop: %s", e)
