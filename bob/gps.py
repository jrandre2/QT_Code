# bob/gps.py

import serial
import datetime
import pytz
import logging
from bob.logger import logger

# Set the serial port for the GPS hat. Adjust as necessary.
GPS_PORT = "/dev/ttyAMA0"  # For Raspberry Pi 2; might be "/dev/ttyS0" on a Pi 3

def open_gps():
    """
    Open the serial connection to the GPS hat.
    Returns a serial object if successful, or None if there's an error.
    """
    try:
        ser = serial.Serial(GPS_PORT, baudrate=9600, timeout=1)
        logger.info("GPS serial connection opened on %s", GPS_PORT)
        return ser
    except Exception as e:
        logger.error("Could not open GPS serial connection: %s", e)
        return None

def decode_gps(coord):
    """
    Convert an NMEA coordinate in the format DDDMM.MMMMM to decimal degrees.
    """
    try:
        # Split into degrees and minutes.
        parts = coord.split(".")
        if len(parts) != 2:
            return None
        head = parts[0]  # DDDMM
        tail = parts[1]  # MMMMM
        if len(head) < 3:
            return None
        degrees = head[:-2]
        minutes = head[-2:] + "." + tail
        decimal_minutes = float(minutes) / 60.0
        return int(degrees) + decimal_minutes
    except Exception as e:
        logger.error("Error decoding GPS coordinate %s: %s", coord, e)
        return None

def parse_gps(data):
    """
    Parse an NMEA sentence (specifically $GPGGA) and extract the GPS coordinates.
    Returns a list with the timestamp, latitude, and longitude or None if parsing fails.
    """
    if "$GPGGA" not in data:
        return None
    parts = data.split(",")
    if len(parts) < 6:
        return None
    try:
        # parts[2] holds latitude, parts[3] holds N/S indicator.
        lat = decode_gps(parts[2])
        if lat is None:
            return None
        if parts[3] == "S":
            lat = -lat

        # parts[4] holds longitude, parts[5] holds E/W indicator.
        lon = decode_gps(parts[4])
        if lon is None:
            return None
        if parts[5] == "W":
            lon = -lon

        # Use a defined timezone (for example, America/Chicago)
        tz = pytz.timezone("America/Chicago")
        timestamp = datetime.datetime.now(tz)
        return [timestamp, lat, lon]
    except Exception as e:
        logger.error("Error parsing GPS data: %s", e)
        return None

def read_gps():
    """
    Attempts to read valid GPS data from the serial connection.
    Tries multiple times before giving up.
    Returns a list [timestamp, latitude, longitude] if successful, or None.
    """
    ser = open_gps()
    if ser is None:
        return None
    attempts = 0
    while attempts < 50:
        try:
            line = ser.readline().decode("utf-8", "ignore")
        except Exception as e:
            logger.error("Error reading GPS serial data: %s", e)
            line = ""
        data = parse_gps(line)
        if data:
            ser.close()
            logger.info("Valid GPS data acquired: %s", data)
            return data
        attempts += 1
    ser.close()
    logger.error("Unable to obtain valid GPS data after %d attempts", attempts)
    return None

# For testing the module independently:
if __name__ == "__main__":
    gps_data = read_gps()
    if gps_data:
        print("GPS Data:", gps_data)
    else:
        print("No valid GPS data obtained.")
