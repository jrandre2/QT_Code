# bob/main_app.py

import time
import csv
import speedtest
import serial
from .logger import logger
from .config import DATA_DIR
from .session import get_session
from .process_utils import reboot_device

def run_speedtest():
    """
    Run an Internet speed test and return the results.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        down = st.download() / (1048576)  # Convert to Mbps.
        up = st.upload() / (1048576)
        ping = st.results.ping
        return down, up, ping
    except Exception as e:
        logger.error("Speedtest error: %s", e)
        return 0, 0, 0

def write_speed_csv(data, filename):
    """
    Append a row of data to the CSV file.
    """
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def main_loop():
    """
    Main application loop that logs speed test data.
    """
    session_id = get_session()  # Retrieve the persistent session ID.
    logger.info(f"Session ID for this deployment: {session_id}")
    
    # Use the session ID in the filename so each deployment's data is kept separate.
    speed_csv_file = f"{DATA_DIR}{session_id}-speed.csv"
    
    # Write CSV header if the file is new.
    try:
        with open(speed_csv_file, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['time', 'download', 'upload', 'ping'])
    except FileExistsError:
        pass

    while True:
        down, up, ping = run_speedtest()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        write_speed_csv([current_time, down, up, ping], speed_csv_file)
        logger.info("Speedtest recorded: %s, %s, %s", down, up, ping)
        time.sleep(300)  # Wait 5 minutes before the next test.

if __name__ == '__main__':
    main_loop()
