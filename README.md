# QT Device Data Collection and Remote Management

**QT** is a modular Python codebase designed for IoT devices (such as a Raspberry Pi) that performs the following tasks:
- **Data Collection:** Periodically runs internet speed tests and captures GPS data.
- **Data Logging:** Writes the results to CSV files with a persistent session identifier.
- **Remote Management:** Supports activation/deactivation, self-updates, and process monitoring.
- **Status Indication:** Uses LED signals to indicate system status.
- **Captive Portal:** Optionally redirects HTTP traffic (via a built-in Flask server) to a specified URL (for example, a survey).

This project is organized into several modules to keep the code modular, maintainable, and testable.

## Table of Contents

- [Overview](#overview)
- [Modules](#modules)
  - [config.py](#configpy)
  - [captive_portal.py](#captive_portalpy)
  - [__init__.py](#__initpy)
  - [checker.py](#checkerpy)
  - [gps.py](#gpspy)
  - [logger.py](#loggerpy)
  - [main_app.py](#main_apppy)
  - [process_utils.py](#process_utilspy)
  - [session.py](#sessionpy)
  - [updater.py](#updaterpy)
  - [ftp_client.py](#ftp_clientpy)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [License](#license)

## Overview

The project is tailored for remote deployment in environments where robust data collection (internet speed and GPS) and remote management are crucial. It continuously monitors connectivity and hardware, logs results locally, and uses FTP for data upload and software updates. The modular design means that individual components (such as LED control or session management) can be modified or replaced independently.

## Modules

### config.py
- **Purpose:**  
  Provides a central location for configuration parameters.  
- **Details:**  
  - Sets default configuration values (e.g., base directories, FTP settings, logging parameters, GPS settings, speed test interval).
  - Reads an override configuration from an `INI` file (`config.ini`) if present.
  - Exposes module-level constants (like `BASE_DIR`, `LOG_DIR`, `DATA_DIR`, and FTP credentials).
  - Contains a helper function `get_device_id()` to retrieve a unique device identifier from `/proc/cpuinfo`.

### captive_portal.py
- **Purpose:**  
  Implements a simple captive portal using Flask.
- **Details:**  
  - Catches all HTTP requests and redirects them to a survey URL (or any desired URL).
  - Sets up (and clears) iptables rules to redirect traffic from port 80 to the Flask server port.
  - Provides helper functions to start and stop the captive portal (including threading for non-blocking execution).

### __init__.py
- **Purpose:**  
  Initializes the `bob` package.
- **Details:**  
  - Optionally imports key constants and objects (for example, `DEVICE_ID` and `SESSION_FILE`) and the configured logger.

### checker.py
- **Purpose:**  
  Monitors the main application process.
- **Details:**  
  - Uses process utilities to verify if `mainBOB.py` is running.
  - Logs an error and archives log files if the main application is not detected.
  - Triggers a device reboot through functions provided by `process_utils.py` when necessary.

### gps.py
- **Purpose:**  
  Handles GPS device interfacing and data parsing.
- **Details:**  
  - Opens a serial connection to the GPS device (using settings from `config.py`).
  - Reads NMEA sentences, decodes them (converting from DDDMM.MMMMM to decimal degrees), and parses out timestamp, latitude, and longitude.
  - Provides a helper function `read_gps()` that attempts multiple readings before returning valid data (or an error).

### logger.py
- **Purpose:**  
  Configures the logging for the entire codebase.
- **Details:**  
  - Ensures that a designated log directory exists.
  - Sets up logging with a specific format and log level.
  - Provides a package-level logger instance that all other modules import and use.

### main_app.py
- **Purpose:**  
  Serves as the core application loop.
- **Details:**  
  - Performs periodic internet speed tests (using the `speedtest` module) and logs the results to a CSV file.
  - Captures GPS data and writes it to a separate CSV file.
  - Integrates with other modules for LED signaling (startup, status, and data capture), activation verification, FTP data upload, and self-update routines.
  - Uses a persistent session ID (from `session.py`) to group data collected during a deployment cycle.
  - Continuously loops with a configurable delay (via `SPEED_TEST_INTERVAL`).

### process_utils.py
- **Purpose:**  
  Provides utility functions for process management and system commands.
- **Details:**  
  - Contains a function to check if a process is running (using the `psutil` library).
  - Provides a helper function to reboot the device via a system call.

### session.py
- **Purpose:**  
  Manages session data for the deployment period.
- **Details:**  
  - Generates a unique session ID that combines the device ID, a timestamp, and a random UUID.
  - Saves and loads session data to/from a JSON file.
  - Validates if a session is still active based on a configurable duration.
  - Provides a helper function `get_session()` to retrieve or create a session.

### updater.py
- **Purpose:**  
  Handles software update operations.
- **Details:**  
  - Extracts version information from versioned filenames (e.g., `mainBOBv2.10.py`).
  - Compares local and remote versions (the remote version can be simulated or retrieved via FTP).
  - Downloads an update using the FTP client if a newer version is available.
  - Installs the update by replacing the main application file and triggering a reboot.

### ftp_client.py
- **Purpose:**  
  Encapsulates FTP operations using secure FTP (FTP_TLS).
- **Details:**  
  - Provides methods for logging in, changing directories, uploading files, downloading files, and closing the connection.
  - Serves as a common client for uploading activation files, CSV data, and downloading updates.

### setup.py
- **Purpose:**  
  Configures the package for installation.
- **Details:**  
  - Specifies package metadata and dependencies (e.g., `psutil`, `speedtest-cli`, `pyserial`, `Flask`, `pytz`).
  - Defines console script entry points (such as `run-checker`, `run-updater`, and `run-main`) for command-line access.

### run_checker.py
- **Purpose:**  
  A small script to run the checker module.
- **Details:**  
  - Intended as a command-line tool to monitor the main application process.

### run_main.py
- **Purpose:**  
  A lightweight wrapper script to start the main application loop.
- **Details:**  
  - Simply imports and calls `main_loop()` from `main_app.py`.

### Config.ini
- **Purpose:**  
  Allows overriding default configuration values.
- **Details:**  
  - Contains settings for base directories, session duration, FTP credentials, logging, speedtest intervals, GPS configuration, and the captive portal URL.
  - Is read by `config.py` to override the built-in defaults.

## Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/bob.git
   cd bob
