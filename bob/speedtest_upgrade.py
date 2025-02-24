# File: bob/speedtest_upgrade.py
import subprocess
import logging
import re
from bob.config import SPEEDTEST_TARGET_VERSION

logger = logging.getLogger('bob.speedtest_upgrade')

def check_speedtest_version():
    """
    Check if the installed speedtest-cli matches the target version.
    If NOT, perform an upgrade to get the latest version.
    
    Returns:
        bool: True if an upgrade was performed, False otherwise
    """
    try:
        # Get current version using subprocess with proper argument list (no shell=True)
        result = subprocess.run(
            ["speedtest-cli", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            check=True
        )
        
        version_info = result.stdout.strip()
        logger.info("Current speedtest version: %s", version_info)
        
        # Extract version number using regex to be more precise
        match = re.search(r'(\d+\.\d+\.\d+)', version_info)
        if match:
            current_version = match.group(1)
            
            # Use version from config instead of hardcoded value
            target_version = SPEEDTEST_TARGET_VERSION
            
            # Only upgrade if the version doesn't match the target
            if current_version != target_version:
                logger.info("Speedtest version %s doesn't match target %s. Upgrading...", 
                           current_version, target_version)
                
                # Perform upgrade without shell=True for better security
                upgrade_result = subprocess.run(
                    ["sudo", "pip3", "install", "speedtest-cli=="+target_version], 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                
                logger.info("Speedtest upgraded successfully to %s", target_version)
                return True
            else:
                logger.info("Speedtest version already matches target %s. No upgrade needed.", 
                           target_version)
        else:
            logger.error("Could not parse version from: %s", version_info)
            
    except subprocess.CalledProcessError as e:
        logger.error("Error checking/upgrading speedtest-cli: %s", e)
        logger.error("STDERR: %s", e.stderr if hasattr(e, 'stderr') else "N/A")
    except Exception as e:
        logger.error("Unexpected error during speedtest version check: %s", e)
        
    return False


if __name__ == "__main__":
    # This allows the module to be run directly for testing
    if check_speedtest_version():
        print("Speedtest was upgraded")
    else:
        print("No upgrade was performed")
