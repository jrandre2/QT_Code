# File: bob/speedtest_upgrade.py
import subprocess
import logging

logger = logging.getLogger('bob.speedtest_upgrade')

TARGET_VERSION = "2.1.1"

def check_speedtest_version():
    """
    Check if the installed speedtest-cli is the target version. If so, perform an upgrade.
    """
    try:
        result = subprocess.run("speedtest-cli --version", stdout=subprocess.PIPE, shell=True, check=True)
        version_info = result.stdout.decode('utf-8')
        logger.info("Speedtest version: %s", version_info.strip())
        if TARGET_VERSION in version_info:
            logger.info("Speedtest version matches target. Upgrading...")
            subprocess.run("sudo pip3 install speedtest-cli --upgrade", shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        logger.error("Error checking/upgrading speedtest-cli: %s", e)
    return False
