BOB PROJECT ASSIGNMENTS AND MODULE OVERVIEW
===========================================

1. Configuration & Global Settings
------------------------------------
Module: bob/config.py
  - Define base directories for logs, data, versions.
  - Specify FTP credentials and target directories.
  - Set the survey URL for captive portal redirection.
  - Retrieve the fixed device identifier (from /proc/cpuinfo).
  - Configure session parameters (SESSION_FILE location, SESSION_DURATION_DAYS).

2. Logging
----------
Module: bob/logger.py
  - Configure centralized logging (log file path, logging level, and format).
  - Provide a logger instance for use across the project.

3. FTP Operations
-----------------
Module: bob/ftp_client.py
  - Provide helper functions (or a class) to connect to the FTP server.
  - Implement methods for uploading files (logs, CSV data) and downloading updates.

4. Process Utilities
--------------------
Module: bob/process_utils.py
  - Implement process checking (using psutil) to confirm if specific processes are running.
  - Implement a function to reboot the Raspberry Pi when needed.

5. Session Management
---------------------
Module: bob/session.py
  - Manage a persistent session (or household) ID.
  - Check for an existing session file and verify it is within the valid duration.
  - Generate a new session ID (combining the device ID, current timestamp, and a random UUID) if needed.
  - Save and load the session data for consistent tagging of data across reboots during a deployment.

6. Software Updates
-------------------
Module: bob/updater.py
  - Check for new versions of the main application (comparing local and remote versions).
  - Download updates via FTP if a new version is available.
  - Install updates by copying new files, removing outdated ones, and initiating a reboot.

7. Watchdog / Process Checker
-----------------------------
Module: bob/checker.py
  - Periodically verify that the main application is running.
  - If the main app is not running, log the error, archive logs, and reboot the device.

8. Captive Portal for Survey Redirection
------------------------------------------
Module: bob/captive_portal.py
  - Set iptables rules to redirect all HTTP traffic (port 80) to a local port (e.g., 8080).
  - Start a lightweight Flask server that intercepts all HTTP requests.
  - Immediately respond to every request with an HTTP 302 redirect to the survey URL.
  - Provide functions to start and stop the captive portal (and to clear iptables rules).

9. GPS Functionality
--------------------
Module: bob/gps.py
  - Open and manage the serial connection to the GPS hat (using /dev/ttyAMA0 or similar).
  - Read and parse NMEA sentences (especially $GPGGA) for latitude and longitude.
  - Decode the NMEA format into decimal degrees.
  - Return GPS data (timestamp, latitude, longitude) for logging or FTP upload.

10. Core Application
--------------------
Module: bob/main_app.py
  - Retrieve the persistent session ID and initialize data file names.
  - Initialize CSV files for internet speed test results and GPS data.
  - Run an infinite loop:
      • Perform an internet speed test every 5 minutes using the speedtest module.
      • Log test results (download, upload, ping) along with timestamps.
      • Attempt to capture GPS data via bob/gps.py and log it to a separate CSV.
      • Continue data collection over the extended deployment period.
  - Handle errors and graceful termination (e.g., KeyboardInterrupt).

11. Entry Point Scripts
-----------------------
Directory: scripts/
  - run_main.py: Launch the main application loop (bob/main_app.py).
  - run_checker.py: Launch the watchdog (bob/checker.py).
  - run_updater.py: Launch the updater routine (bob/updater.py).
  - run_captive_portal.py: Launch the captive portal server (bob/captive_portal.py).
  - Ensure these scripts are marked executable and referenced appropriately by systemd/cron.

12. Additional Documentation & Maintenance
--------------------------------------------
- Update this assignments.txt file to reflect changes.
- Document any environment-specific configuration (e.g., serial port differences, iptables rules requirements).
- Keep instructions for deployment, troubleshooting, and updates in a separate README or Wiki.

===========================================


