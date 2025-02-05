# File: bob/internet.py
import requests
import logging
import time

logger = logging.getLogger('bob.internet')

def check_internet(timeout=3, retries=10):
    """
    Check connectivity by attempting to access a known website (e.g., http://google.com).
    Use exponential backoff on failures.
    """
    backoff = 1
    for i in range(retries):
        try:
            response = requests.get("http://google.com", timeout=timeout)
            if response.ok:
                logger.info("Internet connection is active.")
                return True
        except requests.RequestException as e:
            logger.warning("Internet check failed: %s", e)
        time.sleep(backoff)
        backoff *= 2
    logger.error("Internet connection not available after %d attempts.", retries)
    return False

def get_public_ip(timeout=3):
    """
    Get the public IP address from an external service.
    """
    try:
        ip = requests.get("http://api.ipify.org", timeout=timeout).text
        logger.info("Public IP retrieved: %s", ip)
        return ip
    except requests.RequestException as e:
        logger.error("Unable to retrieve public IP: %s", e)
        return None
