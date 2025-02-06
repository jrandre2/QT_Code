# main.py
import uasyncio as asyncio
import gc
import config
import session
import captive_portal
import speedtest
import network_driver
import logging
import ftp_client

# Global buffer to hold test results (limit to 10 entries)
data_buffer = []

gc.collect()
logging.log("System starting up...")

# Load configuration
cfg = config.load_config()

# Initialize Ethernet hardware via the native module
eth = network_driver.init_ethernet()
if eth is not None:
    logging.log("Ethernet interface initialized.")
    ip_addr = eth.get_ip()
    logging.log("Device IP: " + ip_addr)
else:
    logging.log("Failed to initialize Ethernet.")

# Manage session
sess_id = session.get_session()
logging.log("Session ID: " + sess_id)

# Periodic garbage collection 
async def gc_task():
    while True:
        await asyncio.sleep(60)
        gc.collect()
        logging.log("GC run: Free mem: {} bytes".format(gc.mem_free()))

async def periodic_speedtest():
    interval = cfg.get("speedtest", {}).get("SPEED_TEST_INTERVAL", 300)
    while True:
        result = speedtest.perform_download_test()
        logging.log(result)
        data_buffer.append(result)
        if len(data_buffer) > 10:
            del data_buffer[0]
        await asyncio.sleep(interval)

async def periodic_upload_test():
    interval = cfg.get("speedtest", {}).get("UPLOAD_TEST_INTERVAL", 300)
    while True:
        result = speedtest.perform_upload_test()
        logging.log(result)
        data_buffer.append(result)
        if len(data_buffer) > 10:
            del data_buffer[0]
        await asyncio.sleep(interval)

async def periodic_ping_test():
    interval = cfg.get("speedtest", {}).get("PING_TEST_INTERVAL", 300)
    target = cfg.get("speedtest", {}).get("PING_TARGET", "8.8.8.8")
    while True:
        result = speedtest.perform_ping_test(target)
        logging.log(result)
        data_buffer.append(result)
        if len(data_buffer) > 10:
            del data_buffer[0]
        await asyncio.sleep(interval)

async def ftp_upload_task():
    while True:
        if data_buffer:
            data_to_upload = "\n".join(data_buffer)
            if ftp_client.upload_data(data_to_upload):
                logging.log("FTP upload successful, clearing buffer.")
                data_buffer.clear()
            else:
                logging.log("FTP upload failed, retrying later.")
        await asyncio.sleep(60)

async def main():
    asyncio.create_task(captive_portal.start_server())
    asyncio.create_task(periodic_speedtest())
    asyncio.create_task(periodic_upload_test())
    asyncio.create_task(periodic_ping_test())
    asyncio.create_task(ftp_upload_task())
    asyncio.create_task(gc_task())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
