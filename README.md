# BOB IoT Device Data Collection & Remote Management

**BOB** is a modular Python-based codebase designed for remote IoT deployments (e.g., on a Raspberry Pi). It provides robust data collection, local logging, remote management (activation/deactivation, self-update), and visual status indication via LEDs. Originally written as a monolithic script, the functionality has now been refactored into separate, testable modules.

This repository includes modules for:
- **Configuration Management**
- **Data Collection (Internet Speed & GPS)**
- **LED Status Control**
- **Remote Activation/Deactivation**
- **FTP Data Upload & Local Cleanup**
- **Internet Connectivity & Public IP Check**
- **Self-Update**
- **Process Monitoring & System Reboot**
- **Session Management**
- **A Captive Portal** (optional)

## Table of Contents

- [Overview](#overview)
- [Modules](#modules)
  - [config.py](#configpy)
  - [captive_portal.py](#captive_portalpy)
  - [__init__.py](#__initpy)
  - [checker.py](#checkerpy)
  - [gps.py](#gpspy)
  - [led.py](#ledpy)
  - [internet.py](#internetpy)
  - [data_uploader.py](#data_uploaderpy)
  - [activation.py](#activationpy)
  - [speedtest_upgrade.py](#speedtest_upgradepy)
  - [process_utils.py](#process_utilspy)
  - [session.py](#sessionpy)
  - [updater.py](#updaterpy)
  - [ftp_client.py](#ftp_clientpy)
  - [main_app.py](#main_apppy)
  - [setup.py](#setuppy)
  - [run_checker.py](#run_checkerpy)
  - [run_main.py](#run_mainpy)
  - [Config.ini](#configini)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [License](#license)

## Overview

The BOB project is tailored for deployments where:
- **Data Collection:** Periodically perform internet speed tests and capture GPS data.
- **Data Logging:** Write the results to CSV files with a persistent session ID.
- **Visual Feedback:** Use LED indicators to signal system status (startup, internet active, GPS lock, completion).
- **Remote Management:** Check for remote activation, perform self-updates, and monitor the main process.
- **Connectivity:** Verify internet access and retrieve the public IP address.
- **FTP Operations:** Upload collected CSV data and download software updates.

The modular design allows each function to be maintained and tested separately.

## Modules

### config.py
- **Purpose:**  
  Centralizes configuration parameters.
- **Details:**  
  - Provides default settings (directories, FTP credentials, logging, GPS, speedtest interval, etc.).
  - Loads overrides from `Config.ini` if available.
  - Exposes key constants (e.g., `BASE_DIR`, `LOG_DIR`, `DATA_DIR`, `FTP_DETAILS`).
  - Contains `get_device_id()` to extract a unique device identifier from `/proc/cpuinfo`.

### captive_portal.py
- **Purpose:**  
  Implements a captive portal using Flask.
- **Details:**  
  - Catches all HTTP requests and redirects them to a predefined URL (e.g., a survey).
  - Sets up and clears iptables rules to redirect port 80 traffic to the captive portal.
  - Provides functions to start and stop the portal in a non-blocking thread.

### __init__.py
- **Purpose:**  
  Initializes the package.
- **Details:**  
  - Imports key constants and objects (such as `DEVICE_ID` and the logger) for easy package-wide access.

### checker.py
- **Purpose:**  
  Monitors whether the main application is running.
- **Details:**  
  - Uses functions from `process_utils.py` (with `psutil`) to check for the main process.
  - Archives logs and reboots the device if the main process isn’t found.

### gps.py
- **Purpose:**  
  Manages GPS device interfacing and data parsing.
- **Details:**  
  - Opens a serial connection using parameters from `config.py`.
  - Reads NMEA sentences (e.g., `$GPGGA`), decodes coordinates from DDDMM.MMMMM format into decimal degrees, and timestamps the reading.
  - Provides a helper function `read_gps()` that makes several attempts to obtain valid data.

### led.py
- **Purpose:**  
  Provides functions for controlling status LEDs.
- **Details:**  
  - Wraps low-level LED functions using the APA102 driver.
  - Offers functions like `ready_red_leds()`, `intled_green()`, `gpsled_green()`, and `bluelight_minion()` to set LED colors.
  - Allows visual signaling for startup, internet readiness, GPS lock, and completion.

### internet.py
- **Purpose:**  
  Checks internet connectivity and retrieves the public IP address.
- **Details:**  
  - Contains `check_internet()` which performs connectivity tests (e.g., accessing google.com) with exponential backoff.
  - Provides `get_public_ip()` to fetch the public IP from an external service (such as ipify).

### data_uploader.py
- **Purpose:**  
  Handles FTP upload and cleanup of CSV data files.
- **Details:**  
  - Uses the FTP client to change directories, upload CSV files, and then delete them locally.
  - Ensures that both speed test and GPS CSV files are transmitted to the remote server.

### activation.py
- **Purpose:**  
  Manages remote activation/deactivation.
- **Details:**  
  - Downloads an activation file from the FTP server.
  - Checks if the activation file indicates that the device is “activated.”
  - Provides functions to upload a deactivation file and to mark the device as “EXTINCT” by archiving log files.

### speedtest_upgrade.py
- **Purpose:**  
  Checks the installed version of `speedtest-cli` and upgrades it if needed.
- **Details:**  
  - Compares the current version with a target version.
  - If the target version matches, triggers an upgrade via a subprocess call.
  - Can optionally trigger a reboot after upgrading.

### process_utils.py
- **Purpose:**  
  Contains utilities for process management and system commands.
- **Details:**  
  - Uses the `psutil` library to check if a specific process is running.
  - Provides a `reboot_device()` function that calls the system reboot command.

### session.py
- **Purpose:**  
  Manages session creation and persistence.
- **Details:**  
  - Generates a unique session ID based on the device ID, timestamp, and a random UUID.
  - Saves session data to a JSON file and validates its expiration based on a configured duration.
  - Provides `get_session()` to retrieve or create a session for grouping data.

### updater.py
- **Purpose:**  
  Handles software updates.
- **Details:**  
  - Extracts version information from filenames (e.g., `mainBOBv2.10.py`).
  - Compares the local and remote versions.
  - Uses the FTP client (via `ftp_client.py`) to download new versions.
  - Installs the update (replacing the main file and removing old files) and triggers a reboot.

### ftp_client.py
- **Purpose:**  
  Encapsulates secure FTP operations.
- **Details:**  
  - Uses `FTP_TLS` for secure connections.
  - Provides methods for logging in, changing directories, uploading, and downloading files.
  - Serves both the update and activation modules.

### main_app.py
- **Purpose:**  
  Contains the main application loop.
- **Details:**  
  - Initializes system state (LEDs, connectivity, activation, and session).
  - Performs periodic internet speed tests (using the `speedtest` module) and logs results to a CSV file.
  - Captures GPS data and logs it to a separate CSV file.
  - Calls functions from `led.py` to indicate status.
  - Checks for speedtest upgrades and triggers them if necessary.
  - Periodically uploads CSV files using `data_uploader.py`.
  - Runs continuously with a sleep interval defined by `SPEED_TEST_INTERVAL`.

### setup.py
- **Purpose:**  
  Sets up the package for installation.
- **Details:**  
  - Specifies package metadata and dependencies (e.g., `psutil`, `speedtest-cli`, `pyserial`, `Flask`, `pytz`).
  - Defines entry points for console scripts such as `run-checker`, `run-updater`, and `run-main`.

### run_checker.py
- **Purpose:**  
  A small utility to execute the process checker.
- **Details:**  
  - Runs the `checker.py` module to verify that the main application is active.

### run_main.py
- **Purpose:**  
  A wrapper to start the main application loop.
- **Details:**  
  - Simply imports and runs `main_app.py`.

### Config.ini
- **Purpose:**  
  Allows overriding default configuration settings.
- **Details:**  
  - Contains settings for base directories, FTP credentials, logging, session duration, GPS configuration, speedtest intervals, and the captive portal URL.
  - Is read by `config.py` to override built-in defaults.

## Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/bob.git
   cd bob
