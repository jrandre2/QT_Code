# bob/gps.py

import serial
import datetime
import pytz
from bob.logger import logger
from bob.config import GPS_PORT, GPS_BAUDRATE

def open_gps():
    """
    Open the serial connection to the GPS hat.
    """
    try:
        ser = serial.Serial(GPS_PORT, baudrate=GPS_BAUDRATE, timeout=1)
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
    Parse an NMEA sentence ($GPGGA) and extract timestamp, latitude, and longitude.
    """
    if "$GPGGA" not in data:
        return None
    parts = data.split(",")
    if len(parts) < 6:
        return None
    try:
        lat = decode_gps(parts[2])
        if lat is None:
            return None
        if parts[3] == "S":
            lat = -lat
        lon = decode_gps(parts[4])
        if lon is None:
            return None
        if parts[5] == "W":
            lon = -lon
        tz = pytz.timezone("America/Chicago")
        timestamp = datetime.datetime.now(tz)
        return [timestamp, lat, lon]
    except Exception as e:
        logger.error("Error parsing GPS data: %s", e)
        return None

def read_gps():
    """
    Attempt to read valid GPS data from the serial connection.
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

if __name__ == '__main__':
    gps_data = read_gps()
    if gps_data:
        print("GPS Data:", gps_data)
    else:
        print("No valid GPS data obtained.")
