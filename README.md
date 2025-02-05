                        +----------------------+
                        |      GitHub Repo     |
                        |  (project_root/)     |
                        +----------+-----------+
                                   │
                                   ▼
                     +-----------------------------+
                     |       scripts/              |
                     |  run_main.py, run_checker.py |
                     |     run_updater.py           |
                     +--------------+--------------+
                                    │
                    +---------------+---------------+
                    |         bob Package         |
                    +---------------+---------------+
                                    │
        ┌───────────────────────────┼────────────────────────────┐
        │                           │                            │
        ▼                           ▼                            ▼
+---------------+         +-------------------+         +-----------------+
| config.py     |         | logger.py         |         | process_utils.py|
| - Global      |         | - Logging setup   |         | - Process check |
|   settings,   |         |                   |         | - Reboot        |
|   FTP,        |         |                   |         +-----------------+
|   DEVICE_ID   |         +-------------------+                
+---------------+                          
                                    │
                                    ▼
                           +---------------------+
                           | session.py          |
                           | - Generate/check    |
                           |   persistent        |
                           |   session ID        |
                           +---------------------+
                                    │
                                    ▼
         +-----------------------------------------------------+
         |                    main_app.py                      |
         | - Calls session.get_session() to get session ID     |
         | - Performs speed tests and writes CSV files         |
         |   (named using session ID)                          |
         | - Logs events via logger                            |
         +-----------------------------------------------------+
                                    │
                                    ▼
                           +---------------------+
                           | updater.py          |
                           | - Checks for updates|
                           | - Uses ftp_client   |
                           |   to download update|
                           | - Reboots device    |
                           +---------------------+
                                    │
                                    ▼
                           +---------------------+
                           | checker.py          |
                           | - Checks if main_app|
                           |   is running        |
                           | - Reboots if necessary|
                           +---------------------+
                                    │
                                    ▼
                           +---------------------+
                           | ftp_client.py       |
                           | - FTP operations    |
                           |   (upload/download) |
                           +---------------------+
