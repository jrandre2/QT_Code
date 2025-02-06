# main.py
import uasyncio as asyncio
import config
import session
import captive_portal
import speedtest
import network_driver
import logging
import ftp_client

# Global buffer to hold data for streaming (in RAM)
data_buffer = []

# Log system startup
logging.log("System starting up...")

# Load configuration
cfg = config.load_config()

# Initialize Ethernet hardware
if network_driver.init_ethernet():
    logging.log("Ethernet interface initialized.")
else:
    logging.log("Failed to initialize Ethernet.")

# Manage session: load or create a session and log its ID
sess_id = session.get_session()
logging.log("Session ID: " + sess_id)

async def periodic_speedtest():
    """Perform a download speed test periodically and buffer the result."""
    interval = cfg.get("speedtest", {}).get("SPEED_TEST_INTERVAL", 300)
    while True:
        result = speedtest.perform_download_test()
        logging.log(result)
        data_buffer.append(result)
        await asyncio.sleep(interval)

async def ftp_upload_task():
    """Periodically attempt to upload buffered data to the FTP server."""
    while True:
        if data_buffer:
            data_to_upload = "\n".join(data_buffer)
            if ftp_client.upload_data(data_to_upload):
                logging.log("FTP upload successful, clearing buffer.")
                data_buffer.clear()
            else:
                logging.log("FTP upload failed, will retry later.")
        await asyncio.sleep(60)  # Retry every minute

async def main():
    # Start the captive portal server, speed test, and FTP upload tasks
    asyncio.create_task(captive_portal.start_server())
    asyncio.create_task(periodic_speedtest())
    asyncio.create_task(ftp_upload_task())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
