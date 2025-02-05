# bob/process_utils.py

import psutil
import subprocess

def is_process_running(process_name: str) -> bool:
    """
    Check if a process with the given name is running.
    """
    for proc in psutil.process_iter(attrs=['cmdline']):
        try:
            # Join the command-line arguments into a single string.
            if process_name in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def reboot_device():
    """
    Reboot the device.
    """
    subprocess.call("shutdown -r now", shell=True)
