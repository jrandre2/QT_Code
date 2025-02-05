QT_Code/
├── bob/
│   ├── __init__.py
│   ├── config.py         # Central configuration (paths, FTP details, device ID)
│   ├── logger.py         # Central logging configuration
│   ├── ftp_client.py     # Encapsulated FTP operations
│   ├── process_utils.py  # Utilities (e.g., process checking, rebooting)
│   ├── session.py        # Persistent session/household ID management
│   ├── updater.py        # Update-checking, downloading, and installation logic
│   ├── checker.py        # Watchdog logic for ensuring the main app is running
│   └── main_app.py       # Core functionality (data collection, speed tests, CSV logging)
├── scripts/
│   ├── run_checker.py    # Entry point for the watchdog
│   ├── run_updater.py    # Entry point for running updates
│   └── run_main.py       # Entry point for running the main application
├── requirements.txt
└── setup.py
